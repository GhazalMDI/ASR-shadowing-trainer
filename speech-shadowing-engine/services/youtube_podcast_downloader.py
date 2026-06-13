import os
import isodate
import random
import time
import subprocess


from dotenv import load_dotenv
from googleapiclient.discovery import  build
from core.database import getCollection

print("FILE LOADED")


load_dotenv()
API_KEY = os.getenv("API_KEY")
FULL_PATH_AUDIO = r"D:\Machine learning\speech-shadowing-engine"


def requestYoutube():
    youtube = build(
        "youtube",
        "v3",
        developerKey=API_KEY
    )
    return youtube


def downloadAudio(video_id):
    import yt_dlp
    url = f'https://www.youtube.com/watch?v={video_id}'
    output_path = f'audio/{video_id}.mp3'
    ydl_opts = {
        'format':'bestaudio/best',
        'outtmpl':f'audio/{video_id}.%(ext)s',
        'postprocessors':[{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet':True,
        'sleep_interval': 5,
        'max_sleep_interval': 10,
        'noplaylist': True,     
        'cookies': 'cookies.txt'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                url,
                download=True
            )
            time.sleep(random.randint(4, 7))
            ydl.prepare_filename(info)
        return output_path
    except Exception as e:
        print(e)
        return None
       
       
# convert time and accepted time for save in db and transcaript 
def convertDuration(ISO):
    if not ISO:
        return False, 0

    duration = isodate.parse_duration(ISO)
    minutes = round(duration.total_seconds() / 60, 2)
    return 5 <= minutes <= 10, minutes

# Get Video and Find From YouTube 
def getDetailMovie(limit):
    db = getCollection()
    youtube = requestYoutube()
    Audio = db['Audio']
    
    saved_count = 0
    nextPageToken = None

    while saved_count < limit:
        search_res = youtube.search().list(
            q='english podcast',
            part='snippet',
            type='video',
            maxResults=50,         
            pageToken=nextPageToken
        ).execute()

        video_map = {}
        for i in search_res.get('items', []):
            Audio_id = i['id']['videoId']
            Audio_title = i['snippet']['title']

            if Audio.find_one({"Audio_id": Audio_id}):
                continue
            video_map[Audio_id] = Audio_title

        if not video_map:
            print("No new videos in this page")
        else:
            detail_req = youtube.videos().list(
                part='contentDetails',
                id=",".join(video_map.keys())
            ).execute()

            for item in detail_req.get('items', []):
                Audio_id = item['id']
                Audio_title = video_map[Audio_id]
                ISO_Duration = item['contentDetails']['duration']
                time_accept, minutes = convertDuration(ISO_Duration)

                print(Audio_title, minutes)

                if not time_accept: 
                    continue

                if Audio.find_one({"Audio_id": Audio_id}):
                    continue

                audio_path = downloadAudio(Audio_id)
                if not audio_path:
                    continue

                Audio.insert_one({
                    "Audio_id": Audio_id,
                    "Audio_title": Audio_title,
                    "duration": minutes,
                    "sound": audio_path,
                    "created_at": time.time()
                })

                createTrnscript(audio_path)
                saved_count += 1
                print(f"Saved count: {saved_count}")

                if saved_count >= limit:
                    break

        nextPageToken = search_res.get('nextPageToken')
        if not nextPageToken:
            print("No more pages to search")
            break

# create transcaript from save audio in db
def createTrnscript(audio_path):
    import whisper
    
    db = getCollection()
    audios = db["Audio"]

    audio = audios.find_one({"sound": audio_path})
    if not audio or not audio["sound"].endswith(".mp3"):
        return False

    audio_file = audio["sound"]
    full_path = os.path.join("/app", audio_file)  # ✅ مسیر داخل container

    model = whisper.load_model("base")
    result = model.transcribe(full_path, language="en")
    
    # ✅ timestamp دار مثل قبل
    segments = result.get("segments", [])
    clean_lines = []
    for seg in segments:
        start = format_time(seg["start"])
        end = format_time(seg["end"])
        text = seg["text"].strip()
        clean_lines.append(f"[{start} --> {end}]  {text}")
    
    transcript = " ".join(clean_lines)

    audios.update_one(
        {"_id": audio["_id"]},
        {"$set": {"transcript": transcript}}
    )
    return transcript


def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"

createTrnscript("audio/GVhLUyoB5KA.mp3")
# if __name__ == "__main__":
#     getDetailMovie(10)
    













