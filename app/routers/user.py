from asyncio.log import logger
from fastapi import APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from bson.objectid import ObjectId
from pymongo import TEXT
from datetime import datetime

from database import db
from utils.jwt import decodeJWT
from utils.bson_encoder import reformat_id

router = APIRouter(prefix="/users")
security = HTTPBearer()

db.users.create_index([('username', TEXT)], default_language="english")


@router.post("/follow/{uid}")
def follow_user(uid: str, credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    userctx = decodeJWT(token)
    if not userctx:
        raise HTTPException(status_code=403, detail="Not authorized")
    user_id = userctx["user_id"]

    try:
        res = db.users.find_one_and_update(
            {"_id": ObjectId(uid)},
            {"$addToSet": {"followers": ObjectId(user_id)}},
            {"projection": {"_id": 1}}
        )
        if not res:
            raise HTTPException(status_code=404, detail="User not found")

        res = db.users.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$addToSet": {"following": ObjectId(uid)}},
        )

    except Exception as e:
        logger.log(e)
        raise HTTPException(status_code=500, detail="Something went wrong")

    # notify user
    new_notification = {
        "user_id": ObjectId(uid),
        "link": f"/{userctx['user_name']}",
        "client": "web",
        "text": f"{userctx['user_name']} started following you",
        "time": datetime.utcnow(),
        "read": False
    }
    db.notifications.insert_one(new_notification)

    return {"success": True}


# __

@router.post("/unfollow/{uid}")
def unfollow_user(uid: str, credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    userctx = decodeJWT(token)
    if not userctx:
        raise HTTPException(status_code=403, detail="Not authorized")
    user_id = userctx["user_id"]

    try:
        res = db.users.find_one_and_update(
            {"_id": ObjectId(uid)},
            {"$pull": {"followers": ObjectId(user_id)}},
            {"projection": {"_id": 1}}
        )
        if not res:
            raise HTTPException(status_code=404, detail="User not found")

        res = db.users.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$pull": {"following": ObjectId(uid)}},
        )
    except Exception as e:
        logger.log(e)
        raise HTTPException(status_code=500, detail="Something went wrong")

    return {"message": "success"}


@router.get("/search/{q}")
def search_user(q: str):
    user = db.users.find({"$text": {"$search": q}})
    user = [reformat_id(ele) for ele in list(user)]
    return user


@router.get("/randomuser")
def random_user():
    users = db.users.aggregate([{"$sample": {"size": 3}}])
    userlist = []
    for user in users:
        user = reformat_id(user)
        user.pop("password")
        userlist.append(user)

    return userlist


@router.post("/editprofile")
def edit_profile():
    pass


"""
route.post("/upload", verifyToken, upload.array("image"), uploadRoute);
"""
