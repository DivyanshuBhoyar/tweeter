from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class Notification (BaseModel):
    user_id: str
    link: str
    client: str
    text: str
    time: str | datetime
    read: bool
    id: str


class NotificationList (BaseModel):
    __root__: List[Notification]


class NotificationReadBody (BaseModel):
    id: str
