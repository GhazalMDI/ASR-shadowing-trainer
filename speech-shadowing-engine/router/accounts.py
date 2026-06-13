from fastapi import APIRouter,HTTPException,Depends
from models.accounts import User,RefreshToken,hash_password,verify_password
from schemas.accounts_schema import UserWithTokenSchema,TokenResponse,UserSchema,UserCreateSchema,LoginSchema,refreshTokenSchema
from core.auth import create_access_token, create_refresh_token
from datetime import datetime,timedelta
from core.security import get_current_user

import os
router = APIRouter(prefix="/accounts",tags=["accounts"])


JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS"))

@router.post("/register", response_model=UserWithTokenSchema)
async def register_user(user: UserCreateSchema):
    try:
        existing_user = await User.find_one(User.email == user.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered. Please go to login page."
            )
                    
        hashed_pw = hash_password(user.password)
        new_user = User(
            first_name=user.first_name, 
            last_name=user.last_name,
            email=user.email,
            password=hashed_pw,
            level=0,
        )
        await new_user.insert()
        token_data = {"user_id": str(new_user.id), "email": new_user.email}
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)        
        refresh_doc = RefreshToken(
            user_id=str(new_user.id),
            token=refresh_token,
            created_at=datetime.utcnow(),
            expired_at=datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS))
        
        await refresh_doc.insert()

        return UserWithTokenSchema(
            user=UserSchema(
                first_name=new_user.first_name,
                last_name=new_user.last_name,
                email=new_user.email,
                level=new_user.level
            ),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/login")
async def login_user(user:LoginSchema):
    try:
        exsiting_user = await User.find_one(User.email==user.email)
        print(exsiting_user)
        if not exsiting_user:
            raise HTTPException(status_code=400, detail="Email not found please register")
        print("ok")
        if not verify_password(user.password, exsiting_user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        print("ok")

        exsiting_refresh_token = await RefreshToken.find_one(RefreshToken.user_id==str(exsiting_user.id))
        if exsiting_refresh_token:
            access_token = create_access_token(data={"user_id":str(exsiting_user.id),"email":exsiting_user.email})
            return {"access_token":access_token,"refresh_token":exsiting_refresh_token.token,"token_type":"bearer"}
        print("ok")
        refresh_token = create_refresh_token(data={"user_id":str(exsiting_user.id),"email":exsiting_user.email})
        print("ok")
        access_token = create_access_token(data={"user_id":str(exsiting_user.id),"email":exsiting_user.email})
        print("ok")
        refresh_doc = RefreshToken(
        user_id=str(exsiting_user.id),
        token=refresh_token,
        created_at=datetime.utcnow(),
        expired_at=datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        )
        print("ok")

        await refresh_doc.insert()
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/logout')
async def logout_user(data:refreshTokenSchema,current_user=Depends(get_current_user)):
    refresh_doc = await RefreshToken.find_one(
        RefreshToken.token ==data.refresh_token,
        RefreshToken.user_id == str(current_user.id)
    )
    
    if not refresh_doc:
        raise HTTPException(
            status_code=404,
            detail="not found Refresh Token"
        )
    await refresh_doc.delete()
    return {"detail":'your logout!'}