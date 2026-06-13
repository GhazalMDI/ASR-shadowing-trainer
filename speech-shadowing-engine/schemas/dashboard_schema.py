from datetime import datetime

from pydantic import BaseModel

class ListeningLogItemSchema(BaseModel):
    wrong_count:int
    score:int
    status:str
    audio_title:str
    listened_date:datetime
    
    
class ListeningLogSchema(BaseModel):
    performances: list[ListeningLogItemSchema]
        
class UserAudioSchema(BaseModel):
    user_id:str
    audio_id:str
    created_at:datetime
    
