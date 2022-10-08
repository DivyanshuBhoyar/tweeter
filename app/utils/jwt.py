import time
import jwt
from typing import Dict
from dotenv import dotenv_values

config = dotenv_values(".env")

JWT_SECRET = config["JWT_SECRET"]
JWT_ALGORITHM = config["JWT_ALGORITHM"]


def signJWT(username: str, user_id: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "user_name": username,
        "expires": time.time() + 3600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(
            token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}
