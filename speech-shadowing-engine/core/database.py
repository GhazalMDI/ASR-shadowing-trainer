from pymongo import MongoClient
import os

from dotenv import load_dotenv

load_dotenv()

MONGO_IP = os.getenv("MONGO_IP")

def getCollection():
    client = MongoClient(MONGO_IP)
    db = client['speech_shadowing']
    return db