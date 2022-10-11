from asyncio.log import logger
from logging import fatal
from fastapi import FastAPI

from routers import auth_router, tweet_router, user_router, notif_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(tweet_router)
app.include_router(user_router)
app.include_router(notif_router)


# @app.on_event("startup")
# async def startup():
#     try:
#         await db_conn.connect()
#     except Exception as e:
#         logger.error(e)
#         fatal("Failed to connect to database")


# @app.on_event("shutdown")
# async def shutdown():
#     await db_conn.disconnect()


@app.get("/")
async def root():
    return {"message": "Hello World"}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}
