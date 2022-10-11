from asyncio.log import logger
from datetime import datetime
from typing import Dict, List
from fastapi import APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from bson.objectid import ObjectId

from schema.tweet_schema import LikeRequestBody, ReplyTweetRequestBody, Tweet, TweetRequest, TweetList
from database import db
from utils.jwt import decodeJWT
from utils.bson_encoder import JSONEncoder, reformat_id

router = APIRouter(
    prefix="/tweets"
)
security = HTTPBearer()


@router.post("/new")
def new_tweet(body: TweetRequest, credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    userctx = decodeJWT(token)
    if not userctx:
        raise HTTPException(status_code=403, detail="Not authorized")

    new_tweet = {
        "text": body.text,
        "user_id": userctx["user_id"],
        "time": datetime.utcnow(),
        "hearts": [],
        "retweets": [],
        "replies": [],
        "replied_to": None,
        "media": body.media
    }
    try:
        db_res = db.tweets.insert_one(new_tweet)
        new_tweet = db.tweets.find_one({"_id": db_res.inserted_id})
        reformat_id(new_tweet)
        # print(new_tweet)
        return new_tweet
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.get("/", response_model=TweetList)
def get_user_tweets(by_user: str):

    user_id = str(db.users.find_one({"username": by_user}, {"_id": 1})["_id"])
    if not user_id:
        return HTTPException(status_code=404, detail="username not found")

    tweets = db.tweets.find(
        {"user_id": user_id, "replied_to": None})
    tweets = [reformat_id(ele) for ele in list(tweets)]

    return tweets


# ---

@router.get("/{tweet_id}", response_model=Tweet)
def get_tweet(tweet_id: str):

    tweet = db.tweets.find_one({"_id": ObjectId(tweet_id)})
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    reformat_id(tweet)
    return tweet


@router.post("/reply", response_model=Tweet)
def reply_tweet(body: ReplyTweetRequestBody, credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    userctx = decodeJWT(token)
    if not userctx:
        raise HTTPException(status_code=403, detail="Not authorized")

    new_tweet = {
        "text": body.text,
        "user_id": userctx["user_id"],
        "time": datetime.utcnow(),
        "hearts": [],
        "retweets": [],
        "replies": [],
        "replied_to": ObjectId(body.reply_to),
        "media": body.media
    }

    try:
        db_res = db.tweets.insert_one(new_tweet)
        new_tweet = db.tweets.find_one({"_id": db_res.inserted_id})
        reformat_id(new_tweet)

        org_tweet = db.tweets.find_one_and_update({"_id": ObjectId(body.reply_to)}, {
            "$push": {"replies": {
                "$each": [ObjectId(new_tweet["id"])],
                "$position": 0
            }},
        })

    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Something went wrong")

    #  add notification to user who's tweet was replied to
    new_notification = {
        "user_id": org_tweet["user_id"],
        "link": f"/tweet/{new_tweet['id']}",
        "client": "web",
        "text": f"{userctx['user_name']} replied to your tweet",
        "time": datetime.utcnow(),
        "read": False
    }
    db.notifications.insert_one(new_notification)

    return new_tweet


# __


@router.post("/like", response_model=Tweet)
def like_tweet(body: LikeRequestBody, credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    userctx = decodeJWT(token)
    if not userctx:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        tweet = db.tweets.find_one_and_update({"_id": ObjectId(body.tweet_id)}, {
            "$addToSet": {"hearts": ObjectId(userctx["user_id"])},
        })
        if not tweet:
            raise HTTPException(status_code=404, detail="Tweet not found")
        # print(tweet)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Something went wrong")

    print("tweet", tweet, "\n")

    # @TODO add notification to user who's tweet was replied to
    new_notification = {
        "user_id": tweet["user_id"],
        "link": f"/tweet/{tweet['_id']}",
        "client": "web",
        "text": f"{userctx['user_name']} liked your tweet",
        "time": datetime.utcnow(),
        "read": False
    }
    print("notif gen", new_notification, "\n")
    db.notifications.insert_one(new_notification)
    reformat_id(tweet)

    return tweet

# __


@router.post("/unlike")
def unlike_tweet(body: LikeRequestBody, credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    userctx = decodeJWT(token)
    if not userctx:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        tweet = db.tweets.find_one_and_update({"_id": ObjectId(body.tweet_id)}, {
            "$pull": {"hearts": ObjectId(userctx["user_id"])},
        })
        if not tweet:
            raise HTTPException(status_code=404, detail="Tweet not found")
        reformat_id(tweet)
        return tweet
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.get("/replies/{tweet_id}", response_model=TweetList)
def get_replies(tweet_id: str):
    tweet = db.tweets.find_one({"_id": ObjectId(tweet_id)})
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    replies = db.tweets.find({
        "replied_to": ObjectId(tweet_id)
    })
    replies = [reformat_id(ele) for ele in list(replies)]

    return replies


@router.get("/feed/news", response_model=TweetList | Dict[str, str])
def newsfeed(creds: HTTPAuthorizationCredentials = Security(security)):
    token = creds.credentials
    userctx = decodeJWT(token)
    if not userctx:
        raise HTTPException(status_code=403, detail="Not authorized")

    user = db.users.find_one({"_id": ObjectId(userctx["user_id"])})
    if not user:
        raise HTTPException(
            status_code=409, detail="Could not process request")

    if "follwing" not in user:
        return {"msg": "No news to show"}

    tweets = db.tweets.find(
        {"user_id": {"$in": user["following"]}, "replied_to": "null"}
    ).sort("time", -1)
    tweets = [reformat_id(ele) for ele in list(tweets)]

    return tweets
