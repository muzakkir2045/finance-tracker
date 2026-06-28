
import models
from typing import Annotated
from schemas import UserResponse, UserCreate, UserUpdate
from schemas import Token
from fastapi import status, Depends, HTTPException, APIRouter
from sqlalchemy import select, insert, func
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from auth import create_access_token, hash_password, verify_password, CurrentUser

from config import settings

router = APIRouter()


@router.post(
        "/register",
        response_model=UserResponse,
        status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.User).where(models.User.username == user.username)
    )
    username = result.scalars().first()
    if username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username already exists"
        )

    result = await db.execute(
        select(models.User).where(models.User.email == user.email)
    )
    
    email = result.scalars().first()
    if email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    new_user = models.User(
        username = user.username,
        email = user.email.lower(),
        password_hash = hash_password(user.password)
    )


    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    await db.execute(
        insert(models.Categories),[
            {"user_id" : new_user.id , "category_name" : "Salary", "type" : "Income"},
            {"user_id" : new_user.id , "category_name" : "Rent", "type" : "Expense"},
            {"user_id" : new_user.id , "category_name" : "Groceries", "type" : "Expense"},
            {"user_id" : new_user.id , "category_name" : "Freelancing", "type" : "Income"}
        ]
    )
    await db.commit()
    return new_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data : Annotated[OAuth2PasswordRequestForm, Depends()],
    db:Annotated[AsyncSession, Depends(get_db)]
):
    
    result = await db.execute(
        select(models.User).where(
            func.lower(models.User.email) == form_data.username.lower()
        )
    )
    user = result.scalars().first()


    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub" : str(user.id)},
        expires_delta=access_token_expires
    )
    return Token(access_token = access_token, token_type="bearer")



@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user : CurrentUser):
    return current_user


@router.patch("/update",response_model=UserResponse)
async def update_user(
    # user_id: int ,
    current_user : CurrentUser,
    user_update: UserUpdate, 
    db: Annotated[AsyncSession, Depends(get_db)]
):
    
    user = current_user
    
    if user_update.username is not None and user_update.username != user.username:
        result = await db.execute(
            select(models.User).where(models.User.username == user_update.username)
        )

        existing_user = result.scalars().all()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="username already exists"
            )
        
    if user_update.email is not None and user_update.email != user.email:
        result = await db.execute(
            select(models.User).where(models.User.email == user_update.email)
        )

        existing_email = result.scalars().all()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    update_data = user_update.model_dump(exclude_unset=True)

    for field,value in update_data.items():
        setattr(user, field, value)    


    """
    The above can also be done by using if conditions:
    if user_update.username is not None:
        user.username = user_update.username
    if user_update.email is not None:
        user.email = user_update.email

    """

    await db.commit()
    await db.refresh(user)
    return user



# delete user
@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(current_user : CurrentUser, db:Annotated[AsyncSession, Depends(get_db)]):

    user = current_user
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await db.delete(user)
    await db.commit()