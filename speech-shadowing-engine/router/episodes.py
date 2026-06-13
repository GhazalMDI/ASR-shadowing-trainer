import datetime
import json
import numpy as np

from bson import ObjectId
from fastapi import APIRouter,Depends,HTTPException, Query, WebSocket, WebSocketDisconnect
from core.auth import decode_access_token
from core.database import getCollection
from models.accounts import Listening_Logs, User_Audio
from models.episodes import Episode
from core.security import get_current_user
from schemas.episodes_schema import EpisodeSchema,EpisodeItemSchema
from services.compare_create_transcript_calculate import compare, get_expected_text, parse_transcript,transcribe_audio


router = APIRouter(prefix='/episodes',tags=['episodes'])


@router.get("/",response_model=EpisodeSchema)
async def getEpisodesAPI(page:int=Query(1,ge=1),limit:int=Query(10,ge=1,le=50)):
    
    skip = (page-1) *limit
    episodes = await Episode.find_all(
        projection_model=EpisodeItemSchema).skip(skip).limit(limit).to_list()
    
    total = await Episode.count()
    return EpisodeSchema(
        episodes=episodes,
        page=page,
        limit=limit,
        total=total
    )
        
@router.get("/{episode_id}", response_model=EpisodeItemSchema)
async def getEPisodeIdAPI(episode_id: str, current_user=Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="not found user please login or register")

    episode = await Episode.find_one(Episode.id == ObjectId(episode_id))
    print(episode.id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    is_completed = False
    audio_user = await User_Audio.find_one(
        User_Audio.user_id == ObjectId(current_user.id),  
        User_Audio.audio_id == ObjectId(episode_id)
    )

    if audio_user:
        print("AUDIO_USER:",audio_user.id)
        existing_log = await Listening_Logs.find_one(
            Listening_Logs.audio_user_id == audio_user.id
        )
        print("status=========",existing_log)
        if existing_log and existing_log.status == 'success':  
            is_completed=True

    return EpisodeItemSchema(
        id=episode.id,
        Audio_title=episode.Audio_title,
        duration=episode.duration,
        sound=episode.sound,
        created_at=episode.created_at,
        is_completed=is_completed
    )
        
@router.websocket("/audio")
async def websocket_audio(ws: WebSocket, token: str = Query(None)):

    await ws.accept()
    payload = decode_access_token(token)
    if not payload:
        await ws.send_json({"error": "Invalid or expired token"})
        await ws.close(code=1008)
        return

    user_id = payload.get("user_id")
    episode_id = None
    chunks = None
    total_chunks = 0
    current_chunk_index = 0 
    created_record = None
    total_score = 0.0
    total_missed = 0
    chunk_count = 0

    try:
        while True:
            message = await ws.receive()

            if message.get("text") is not None:
                data = json.loads(message["text"])
                action = data.get("action")

                if action == "start":
                    episode_id = data.get("episode_id")

                    audio_user = await User_Audio.find_one(
                        User_Audio.user_id == ObjectId(user_id),
                        User_Audio.audio_id == ObjectId(episode_id)
                    )
                    if audio_user:
                        existing_log = await Listening_Logs.find_one(
                            Listening_Logs.audio_user_id == audio_user.id
                        )
                        if existing_log:
                            await ws.send_json({"error": "You already completed this episode."})
                            await ws.close()
                            return

                    episode = await Episode.find_one(Episode.id == ObjectId(episode_id))
                    if not episode:
                        await ws.send_json({"error": "Episode not found"})
                        continue

                    chunks = parse_transcript(episode.transcript)
                    total_chunks = len(chunks)
                    await ws.send_json({
                        "action": "ready",
                        "chunks": [{"start": c["start"], "end": c["end"]} for c in chunks]
                    })
                    current_chunk_index = 0
                    total_score = 0.0
                    total_missed = 0
                    chunk_count = 0
                    created_record = None
                    print(f"Episode loaded: {total_chunks} chunks")
                    continue

                elif action == "finish":
                    print(f"FINISH received | chunk_count: {chunk_count} | created_record: {created_record}")
                    if created_record and chunk_count > 0:
                        avg_score = int(round(total_score / chunk_count, 1))
                        await Listening_Logs(
                            audio_user_id=created_record.id,
                            wrong_count=total_missed,
                            score=avg_score,
                            status="success"
                        ).insert()
                        print(f"LOG SAVED | score: {avg_score} | missed: {total_missed}")

                    await ws.send_json({"message": "Episode completed"})
                    await ws.close()
                    return

            elif message.get("bytes") is not None:
                if chunks is None or current_chunk_index >= total_chunks:
                    continue

                audio_chunk = message["bytes"]
                try:
                    user_text = transcribe_audio(audio_chunk)

                    current_chunk = chunks[current_chunk_index]
                    expected_words = current_chunk["text"].lower().split()
                    result = compare(expected_words, user_text)

                    total_score += result["score"]
                    total_missed += result["missed"]
                    chunk_count += 1
                    current_chunk_index += 1 

                    half_point = max(1, total_chunks // 2)
                    if chunk_count == half_point and created_record is None:
                        audio_user = await User_Audio.find_one(
                            User_Audio.user_id == ObjectId(user_id),
                            User_Audio.audio_id == ObjectId(episode_id)
                        )
                        if audio_user:
                            created_record = audio_user
                            print("USER_AUDIO EXISTS:", created_record.id)
                        else:
                            created_record = await User_Audio(
                                user_id=user_id,
                                audio_id=ObjectId(episode_id),
                                created_at=datetime.datetime.utcnow()
                            ).insert()
                            print("USER_AUDIO CREATED:", created_record.id)

                    await ws.send_json({
                        "user_text": user_text,
                        "score": result["score"],
                        "missed": result["missed"],
                        "expected": result["expected"]
                    })

                except Exception as e:
                    print("Transcription error:", e)

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print("Error:", e)