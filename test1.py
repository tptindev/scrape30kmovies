import re
import pymongo
from imdb import IMDb
from datetime import datetime
import time
from lxml import html
import json
from bs4 import BeautifulSoup
from bson import ObjectId
from decouple import config
import requests

client = pymongo.MongoClient(f"mongodb://{config('DB_HOST')}:{config('DB_PORT')}/{config('DB_NAME')}")
# client = pymongo.MongoClient("mongodb+srv://vku:vku@lauc2t.4pp7l.mongodb.net/lauc2t?retryWrites=true&w=majority")
db = client.lauc2t
movies_collection = db.movies
demo = movies_collection.find()
# for i in demo:
#     print(i)
apiGetAllIdMovies = requests.get("https://hls.hdv.fun/api/oldlist")
allMovies = json.loads(apiGetAllIdMovies.text)

for i, x in enumerate(demo):
    idDriveVideo = allMovies[i]["imdb"]
    ia = IMDb()
    movie = ia.get_movie(re.sub("tt", '', idDriveVideo))
    cover = movie['full-size cover url']
    movies_collection.find_one_and_update({"_id": dict(x)["_id"]},
                                          {"$set": {"photo": cover}})
    # timestamp = datetime.now().timestamp()
    # if len(dict(x)["photos"]) > 0:
    # movies_collection.find_one_and_update({"_id": dict(x)['_id']},
    #                                       {"$rename": {"pointsVoted": "votes"},
    #                                        "$set": {"demo": [{"link": dict(x)['episode']}],
    #                                                 "photo": dict(x)['photos'][0],
    #                                                 "createAt": timestamp,
    #                                                 "updateAt": timestamp}})
    # movies_collection.find_one_and_update({"_id": dict(x)['_id']},
    #                                       {"$rename": {"pointsVoted": "votes"},
    #                                        "$set": {"demo": [{"link": dict(x)['episode']}]}})
    print(i)
    # time.sleep(0.00001)
