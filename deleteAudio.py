import os
import sys
import json
import base64
import uuid
import random
import pymongo
import datetime
import bson
from random import randint
from bson import ObjectId
from os import listdir

audios = []
albums = []
audioIds = []

devAccess = "XXXX-XXXXX"
prodAccess = "XXXX-XXXXX"


totalDuration = 0

try:
    mdbc = pymongo.MongoClient(prodAccess)
    # CONNNECTING TO MONGODB
    mdb = mdbc["ssweb"]
    print("Connected to MongoDB...")

    # INITIALIZING COLLECTIONS
    albumCol = mdb["albums"]
    audioCol = mdb["audios"]
    vachanaCol = mdb["vachanas"]
except Exception as e:
    print(e)

try:
    print("Updating Data...")
    print(audioCol.estimated_document_count())
    for document in audioCol.find():
        totalDuration = totalDuration + document["duration"]
    print(totalDuration)

    print("Updated Data...")

except Exception as e:
    print(e)
