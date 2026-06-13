from fastapi import APIRouter, Depends, HTTPException
from models.accounts import User_Audio,Listening_Logs,User
from beanie.operators import In

from core.security import get_current_user
from schemas.dashboard_schema import ListeningLogItemSchema, ListeningLogSchema
from schemas.accounts_schema import UserSchema,UserUpdateSchema

router = APIRouter(prefix="/dashboard",tags=["dashboard"])

@router.get("/information", response_model=UserSchema)
async def informationAPI(current_user=Depends(get_current_user)):
    try:
        return UserSchema(
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            email=current_user.email,
            level=current_user.level
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# for update base information in profile
@router.patch('/information',response_model=UserSchema)
async def editInformationAPI(user_update:UserUpdateSchema,current_user=Depends(get_current_user)):
    try:
        update_data = user_update.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400,datail='not field for update')
        
        user =  await User.find_one(User.id==current_user.id)
        if not user:
            raise HTTPException(status_code=404,detail='not user found for update!')
        
        for filed,value in update_data.items():
            setattr(user,filed,value)
            
        await user.save()
        return user
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))


async def get_performance_data(audio_ids: list):
    pipeline = [
        {
            "$match": {
                "audio_user_id": {"$in": audio_ids}
            }
        },
        {
            "$lookup": {
                "from": "User_Audio",
                "localField": "audio_user_id",
                "foreignField": "_id",
                "as": "ua"
            }
        },
        {"$unwind": "$ua"},
        {
            "$lookup": {
                "from": 'Audio',
                "localField": "ua.audio_id",
                "foreignField": "_id",
                "as": "audio"
            }
        },
        {"$unwind": "$audio"},
        {
            "$project": {
                "wrong_count": 1,
                "score": 1,
                "status": 1,
                "audio_title": "$audio.Audio_title",
                "listened_date":"$ua.created_at"
            }
        }
    ]
    collection = Listening_Logs.get_pymongo_collection()
    cursor = collection.aggregate(pipeline)
    return  await cursor.to_list(None)
    
@router.get("/performance", response_model=ListeningLogSchema)
async def dashboardAPI(current_user=Depends(get_current_user)):

    user_audios = await User_Audio.find(
        User_Audio.user_id == current_user.id
    ).to_list()
    
    

    if not user_audios:
        raise HTTPException(
            status_code=404,
            detail="not found record for this user"
        )

    audio_ids = [ua.id for ua in user_audios]
    result = await get_performance_data(audio_ids)
    print(result)
    return ListeningLogSchema(
        performances=[
            ListeningLogItemSchema(
                wrong_count=p["wrong_count"],
                score=p["score"],
                status=p["status"],
                audio_title=p["audio_title"],
                listened_date=p['listened_date']
            )
            for p in result
        ]
    )
