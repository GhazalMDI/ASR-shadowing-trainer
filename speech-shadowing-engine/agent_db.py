import traceback
import schedule
import time

from datetime import datetime,timedelta
from bson import ObjectId
from core.database import getCollection
from services.youtube_podcast_downloader import getDetailMovie

from models.accounts import RefreshToken



def getUserInfo(user_id):
    try:
        db = getCollection()
        Collection_user = db["User"]
        user_info=Collection_user.find_one({"_id":ObjectId(user_id)})
        if user_info:
            return user_info
        return None
    except Exception as e:
        print(e)

    
def lastAudioForAllUsers():
    db = getCollection()
    collection = db['User_Audio']
    pipeline = [
        {"$sort":{"created_at":-1}},
        {
            "$group":{
                "_id":"$user_id",
                "last_audio":{"$first":"$$ROOT"}
            }
        }
    ]
    return list(collection.aggregate(pipeline))

def lastMovie():
    db = getCollection()
    audios = list(db.Audio.find().sort("created_at",-1).limit(5))
    return {a['_id']for a in audios}

def agentDecisionDownload():
    try:
        last_audio_users = lastAudioForAllUsers()
        last_audio_ids = lastMovie()
        for u in last_audio_users:
            last_user_heard = u['last_audio']['Audio_id']
            print(last_user_heard)
            if last_user_heard in last_audio_ids:
                print("the system need to download")
                getDetailMovie()
                return
            print("the system no need to download")
            
    except Exception as e:
        print("Error in downloadAudio")
        print(e)
        traceback.print_exc()
        
        
async def cleanup_token():
    now = datetime.now()
    expired_tokens = await RefreshToken.find(RefreshToken.expired_at<now)
    for token in expired_tokens:
        await token.delete()
    print(f"Deleted token {len(expired_tokens)} at {now}")
    

    

