from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field, field_validator
from schemas.common import PyObjectId 

class EpisodeItemSchema(BaseModel):
    id:PyObjectId = Field(..., alias="_id")
    Audio_title:str
    duration:float
    sound:str
    created_at:datetime
    is_completed : bool = False
    
    @field_validator("id", mode="before")
    @classmethod
    def validate_object_id(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True
    
    
class EpisodeSchema(BaseModel):
    episodes: list[EpisodeItemSchema]
    page:int
    limit:int
    total:int
    
    
    