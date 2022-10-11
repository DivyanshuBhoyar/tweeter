from datetime import datetime
from typing import Any, List, Optional

from pydantic import Field, BaseModel


class TweetRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=280)
    media: Optional[str]


class Tweet(BaseModel):
    text: str
    user_id: str
    time: str | datetime
    hearts: List
    retweets: List
    replies: List
    replied_to: Any
    id: str
    media: Optional[str]


class TweetList(BaseModel):
    __root__: List[Tweet]


class ReplyTweetRequestBody(BaseModel):
    text: str
    reply_to: str
    media: Optional[str]


class LikeRequestBody(BaseModel):
    tweet_id: str
