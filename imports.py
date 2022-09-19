# IMPORT FROM VENV
import os
import fnmatch
import sys
import pathlib
import mutagen
import imghdr
import wave
import contextlib
import json
import base64
import uuid
import random
from pathlib import Path
from random import randint
from os import listdir
from mutagen.mp3 import MP3
import builtins

# INITIAL DATA REQUIRED
language = "Kannada"
rootFolder = "/Albums"
migrationStatusList = []
audios = []
albums = []
infoObj = {}
isAlbumSkip = False
allTypes = ["song", "vachana", "pravachana", "devotional"]
bucket = "ssweb_prod"
defaultArtists = "unknown artist"
allTypes = ["song", "vachana", "pravachana", "devotional"]
oceanBaseURL = "https://basava.sgp1.cdn.digitaloceanspaces.com/"

# DEFAULT ALBUM ARTS WHEN NO IMAGES ARE AVAILABLE
defaultAlbumArts = [
    oceanBaseURL + "DefaultAlbumArts/basava.jpg",
    oceanBaseURL + "DefaultAlbumArts/brand_logo.jpg",
    oceanBaseURL + "DefaultAlbumArts/defaultAlbum.jpg",
]

# DEFAULT COVERS WHEN NO IMAGES ARE AVAILABLE
defaultCoverArts = [
    oceanBaseURL + "DefaultCoverArts/cover1.jpg",
    oceanBaseURL + "DefaultCoverArts/cover2.jpg",
]

# CHECK IF THE IMAGE IS PRESENT AS THE PATTERN
def findImage(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


def reportSave(album, status):
    # REPORT GENERATOR FOR EACH ALBUM
    migrationStatusList.append(
        {
            "album": album,
            "status": status,
        }
    )
    os.chdir("..")


try:

    # ENTER THE ROOT FOLDER
    os.chdir(os.getcwd() + rootFolder)
    albums = os.listdir()

    # IF NO ALBUMS ARE PRESENT
    if len(albums) == 0:
        print("No Albums Found!")
        sys.exit()

    # ITERATE THROUGH THE ALBUMS
    for album in albums:
        albumDuration = 0

        # NAVIGATE INSIDE ALBUM
        os.chdir(os.getcwd() + "/" + str(album))
        audios = os.listdir()

        # IF NO FILES IN ALBUM
        if len(audios) == 0:
            reportSave(album, "No Files Found!")
            continue

        # RETURNS TRUE IF FILE INFO.JSON EXISTS
        if os.path.isfile("./info.json"):
            with open("info.json", "r", encoding="utf-8") as myfile:
                data = myfile.read()
            infoObj = json.loads(data)
        else:
            reportSave(album, "info.json not found!")
            continue

        # IF INFO FILE ISN'T PARSED PROPERLY
        if not infoObj:
            reportSave(album, "info.json empty!")
            continue

        # TO FIND IF FILE COVERART.* IS PRESENT
        ifCover = findImage("coverArt.*", os.getcwd())
        if len(ifCover) > 0:
            infoObj["coverArt"] = (
                oceanBaseURL + bucket + "/albums/" + album + "/" + Path(ifCover[0]).name
            )
        else:
            infoObj["coverArt"] = defaultCoverArts[
                randint(0, len(defaultCoverArts) - 1)
            ]

        # TO FIND IF FILE ALBUMART.* IS PRESENT
        ifAlbum = findImage("albumArt.*", os.getcwd())
        if len(ifAlbum) > 0:
            infoObj["albumArt"] = (
                oceanBaseURL + bucket + "/albums/" + album + "/" + Path(ifAlbum[0]).name
            )
        else:
            # SETTING DEFAULT
            infoObj["albumArt"] = defaultAlbumArts[
                randint(0, len(defaultAlbumArts) - 1)
            ]

        # ALBUM NAME
        infoObj["name"] = album

        # BY DEFAULT WE ADD ALL TYPES AS A LIST
        if infoObj["type"] == []:
            infoObj["type"] = allTypes

        if infoObj["artists"].strip() == "":
            infoObj["artists"] = defaultArtists

        trackCount = 0

        # ITERATION ON EACH AUDIO
        for audio in audios:

            # IF THE FILE IS NOT JSON OR IMAGE [AUDIO FILES ONLY]
            if (
                str(os.path.splitext(audio)[1][1:]) != "json"
                and imghdr.what(audio) == None
            ):

                trackCount = trackCount + 1

                # GENERATE UNIQUE ID FOR FILE NAME EMCYRPTION
                encodedName = uuid.uuid4()
                trackDuration = 0

                # TO FIND THE TYPE OF TRACK TO GET DURATION
                trackExtension = os.path.splitext(audio)[1][1:]

                # IF THE TRACK IS MP3 TYPE

                if trackExtension == "mp3":
                    try:
                        trackDuration = MP3(audio).info.length
                        albumDuration = int(albumDuration + trackDuration)
                    except Exception as e:
                        albumDuration = 0

                # IF THE FILE IS WAV TYPE - COMPUTE FRAMES AND GET DURATION

                elif trackExtension == "wav":
                    try:
                        with contextlib.closing(wave.open(audio, "r")) as f:
                            frames = f.getnframes()
                            rate = f.getframerate()
                            trackDuration = frames / float(rate)
                            albumDuration = int(albumDuration + trackDuration)
                    except Exception as e:
                        albumDuration = 0

                else:
                    reportSave(album, "Unknown Audio Type!")
                    trackCount = trackCount - 1
                    break

                # APPENDING TO THE LIST OF AUDIOS
                try:
                    infoObj["audios"].append(
                        {
                            "name": audio.rsplit(".", 1)[0],
                            "artist": infoObj["artists"],
                            "desc": infoObj["desc"],
                            "type": allTypes
                            if infoObj["type"] == []
                            else infoObj["type"],
                            "audioType": "audio/" + trackExtension,
                            "duration": int(trackDuration),
                            "albumArt": infoObj["albumArt"],
                            "encodedName": str(encodedName),
                            "creatorType": infoObj["creatorType"],
                            "url": oceanBaseURL
                            + bucket
                            + "/albums"
                            + "/"
                            + infoObj["name"]
                            + "/"
                            + str(encodedName)
                            + "."
                            + trackExtension,
                            "uid": infoObj["uid"],
                            "language": language,
                        }
                    )
                except Exception as e:
                    reportSave(album, "Error In Audio Meta Processing!")
                    break

                # RENAME THE FILE WITH THE UUID GENERATED
                try:
                    os.rename(audio, str(encodedName) + "." + trackExtension)
                    # pass
                except Exception as e:
                    reportSave(album, "Couldn't Rename Audio File!")
                    break

        # TOTAL DURATION OF ALBUM
        infoObj["duration"] = albumDuration
        infoObj["trackCount"] = trackCount
        # print(infoObj)

        # WRITE THE OUTPUT TO INFO_OUT.JSON
        try:
            with open("info_out.json", "w", encoding="utf8") as fp:
                json.dump(infoObj, fp, ensure_ascii=False)
        except Exception as e:
            reportSave(album, "Failed to write output data!")
            continue

        # GO TO PARENT DIRECTORY
        # for migrationStatus in migrationStatusList:
        #   if(not album in migrationStatus.values()):
        reportSave(album, "Extracted.")

    # AFTER ALL THE ALBUMS ARE PROCESSED
    print("All Albums Processed.")
    os.chdir(os.getcwd() + rootFolder)
    if os.path.exists("info_out.json"):
        os.remove("info_out.json")
    for item in migrationStatusList:
        print(item["album"] + "..." + item["status"])

except Exception as e:
    print(e)
