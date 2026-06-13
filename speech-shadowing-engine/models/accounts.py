from pydantic import EmailStr
from beanie  import  Document, PydanticObjectId
from passlib.context import CryptContext
from datetime import datetime
import bcrypt

pwd_context = CryptContext(schemes=['bcrypt'])


def hash_password(password:str)->str:
    pw_bytes = password.encode('utf-8')[:72]  
    hashed = bcrypt.hashpw(pw_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),   
        hashed_password.encode("utf-8")   
    )
    
    

        
class RefreshToken(Document):
    user_id: str
    token:str
    created_at:datetime
    expired_at:datetime
    
    class Settings:
        name="RefreshToken"
        
class User(Document):
    first_name:str
    last_name:str
    email:EmailStr
    password:str
    level:int=0
    
    class Settings:
        name="User"

class Listening_Logs(Document):
    audio_user_id:PydanticObjectId   
    wrong_count:int
    score:int=0
    status:str
    
    class Settings:
        name="Listening_Logs"
        
class User_Audio(Document):
    user_id:PydanticObjectId
    audio_id:PydanticObjectId
    created_at:datetime
    
    class Settings:
        name="User_Audio"
        indexes = [
            [("user_id", 1), ("audio_id", 1)]  
        ]


    
