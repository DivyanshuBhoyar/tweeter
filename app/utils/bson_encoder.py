import json
from bson import ObjectId


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


def reformat_id(obj):
    obj["id"] = str(obj["_id"])
    if "replies" in obj:
        obj["replies"] = [str(ele) for ele in obj["replies"]]
    if "hearts" in obj:
        obj["hearts"] = [str(ele) for ele in obj["hearts"]]
    if "replied_to" in obj:
        obj["replied_to"] = str(obj["replied_to"])
    if "followers" in obj:
        obj["followers"] = [str(ele) for ele in obj["followers"]]
    if "following" in obj:
        obj["following"] = [str(ele) for ele in obj["following"]]

    obj.pop("_id")
    return obj
