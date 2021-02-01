import pymongo
from decouple import config
client = pymongo.MongoClient(f"mongodb://{config('DB_HOST')}:{config('DB_PORT')}/{config('DB_NAME')}")
db = client.lauc2t
movies_collection = db.movies
demo = movies_collection.find().sort("createAt.timestamp", -1)
for x in demo:
  print(x)

