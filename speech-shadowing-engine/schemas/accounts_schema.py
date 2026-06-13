from typing import Optional
from pydantic import BaseModel,EmailStr

class UserSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    level:int = 0
    
    
class UserCreateSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    
class UserUpdateSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    
class refreshTokenSchema(BaseModel):
    refresh_token: str

    
class UserWithTokenSchema(BaseModel):
    user: UserSchema
    tokens: TokenResponse
    
class LoginSchema(BaseModel):
    email:EmailStr
    password:str