from beanie import Document,PydanticObjectId
from datetime import datetime




class Episode(Document):
    Audio_id:str
    Audio_title:str
    duration:float
    sound:str
    created_at:datetime
    transcript:str
    
    class Settings:
        name="Audio"
    