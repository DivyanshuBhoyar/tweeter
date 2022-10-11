from fastapi import APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from bson.objectid import ObjectId
from schema.notification_schema import NotificationList, NotificationReadBody

from database import db
from utils.jwt import decodeJWT
from utils.bson_encoder import reformat_id

router = APIRouter(prefix="/notifications")
security = HTTPBearer()


@router.get("/")
def get_notifications(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    userctx = decodeJWT(token)
    if not userctx:
        raise HTTPException(status_code=403, detail="Not authorized")
    user_id = userctx["user_id"]

    notifications = db.notifications.find({"user_id": ObjectId(user_id)})
    notifications = [reformat_id(ele) for ele in list(notifications)]

    return notifications


@router.post("/read", response_model=NotificationList)
def read_by_id(body: NotificationReadBody, credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    userctx = decodeJWT(token)
    if not userctx:
        raise HTTPException(status_code=403, detail="Not authorized")
    user_id = userctx["user_id"]

    db.notifications.update_one(
        {"_id": ObjectId(body.id)},
        {"$set": {"read": True}}
    )

    notifications = db.notifications.find({"user_id": ObjectId(user_id)})
    notifications = [reformat_id(ele) for ele in list(notifications)]

    return notifications
