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

audios=[]
albums=[]
audioIds=[]
audioDocs = []
migrationStatusList = []
ifAlbumExists = False
devAccess = "XXXXX-XXXXX"
prodAccess = "XXXXX-XXXXX"
def reportSave(album, status):
    # REPORT GENERATOR FOR EACH ALBUM
    migrationStatusList.append({
        "album": album,
        "status": status,
    })
    os.chdir("..")

try:
  mdbc = pymongo.MongoClient(
    prodAccess
    )
  #CONMNECTING TO MONGODB
  mdb = mdbc["ssweb"]
  print("Connected to MongoDB...")

  #INITIALIZING COLLECTIONS
  albumCol = mdb['albums']
  audioCol = mdb['audios']
except Exception as e: print(e)

try:
  print("Uploading Data...")
  os.chdir(os.getcwd()+"/Albums")
  albums=os.listdir()
  for album in albums:
    if not albumCol.count_documents({ "name": album }):
      albumDuration = 0
      albumId = ObjectId()
      audioIds = []
      os.chdir(os.getcwd()+"/"+str(album))
      if(os.path.isfile('./info_out.json')):
        with open('info_out.json', 'r', encoding='utf-8') as myfile:
          data=myfile.read()
        infoObj = json.loads(data)
      else:
        reportSave(album, "info_out.json not found!")
        continue

      #IF INFO FILE ISN'T PARSED PROPERLY
      if(not infoObj):
        reportSave(album, "info_out.json empty!")
        continue

      if(len(infoObj['audios']) == 0):
        reportSave(album, "No audio Present!")
        continue

      for audio in infoObj['audios']:
        audioId = ObjectId()
        audioIds.append({
                          "audioId":audioId,
                          "addedOn":datetime.datetime.now()
                        })

        if(audio['duration'] == 0):
          reportSave(album, "Audio with Zero length found!")
          break
        else:
          albumDuration = albumDuration + audio['duration']

        audioDocs.append (
          {
            '_id': audioId,
            'name': audio['name'],
            'artist': audio['artist'],
            'url':audio['url'],
            'albumId': str(albumId),
            'type': audio['type'],
            'duration': audio['duration'],
            'language': audio['language'],
            'shortUrl': "SHORT_URL",
            'creatorType': audio['creatorType'],
            'audioType': audio['audioType'],
            "uid": audio['uid'],
            "createdOn": datetime.datetime.now(),
            "modifiedOn": datetime.datetime.now(),
            "albumArt": audio['albumArt'],
            "taggedVachanas": []
          }
        )
      try:
        # print(audioDocs)
        # pass
        audioCol.insert_many(audioDocs)
      except Exception as e: print(e)
          
      try:
        albumDoc = {
          '_id': albumId,
          "name": infoObj['name'],
          "desc": infoObj['desc'],
          'type': infoObj['type'],
          'albumArt': infoObj['albumArt'],
          'coverArt': infoObj['coverArt'],
          'shortUrl': "SHORT_URL",
          'creatorType': infoObj['creatorType'],
          'duration': infoObj['duration'],
          "uid":infoObj['uid'],
          'audios': audioIds
        }
        # print(albumDoc)
        albumCol.insert_one(albumDoc)
      except Exception as e:
        reportSave(album, "MetaData Build Failed!")
        continue
      reportSave(album, "Imported Successfully")
      continue
    else:
      reportSave(album, "Album Already Exists")
      continue
    
  print("\n\n\n\n\n\nMongoDB processing complete:)")

  for item in migrationStatusList:
    print(item['album']+"..."+item['status'])
except Exception as e: print(e)