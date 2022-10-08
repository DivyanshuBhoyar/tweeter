from fastapi import APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from utils.bson_encoder import reformat_id

from database import db
from schema.auth_schema import SigninRequest, SignupRequest, AuthResponse
from utils.password import gen_hash_pw, verify_pw
from utils.jwt import signJWT, decodeJWT

router = APIRouter(
    prefix="/auth"
)


security = HTTPBearer()


@router.get("/me", response_description="Get current user")
def demo(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    decoded = decodeJWT(token)

    if not decoded:
        raise HTTPException(status_code=400, detail="Not authorized")

    return {"message": "Authorized"}


@router.post("/signup", description="creates a new user", response_model=AuthResponse)
async def signup(body: SignupRequest):
    # check if user already exists with username or email
    exists = db.users.find_one(
        {"$or": [{"username": body.username}, {"email": body.email}]})
    if exists:
        raise HTTPException(
            detail="username or email already exists", status_code=409)

    # create a new user
    new_user = {
        "username": body.username,
        "email": body.email,
        "password": gen_hash_pw(body.password)
    }
    # insert the new user into the database
    db_res = db.users.insert_one(new_user)
    # get the new user from the database
    new_user = db.users.find_one({"_id": db_res.inserted_id})

    new_user.pop("password")
    reformat_id(new_user)

    # create a new token for the new user
    token = signJWT(new_user["username"], new_user["id"])

    return AuthResponse(
        msg="user created successfully",
        user=new_user,
        token=token
    )

    # check if user already exists


@router.post("/signin", description="signs in a user", response_model=AuthResponse)
async def signin(body: SigninRequest):
    # check if user exists
    user = db.users.find_one({"username": body.username})
    if not user:
        raise HTTPException(
            detail="user does not exist", status_code=404)

    # check if password is correct
    if not verify_pw(body.password, user["password"]):
        raise HTTPException(
            detail="incorrect password", status_code=401)

    user.pop("password")
    reformat_id(user)

    # create a new token for the user
    token = signJWT(user["username"], user["id"])

    return AuthResponse(
        msg="user signed in successfully",
        user=user,
        token=token
    )
