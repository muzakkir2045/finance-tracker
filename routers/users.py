
import models
from typing import Annotated
from schemas import UserResponse, UserCreate, UserUpdate, TransResponse, BudgetResponse
from fastapi import status, Depends, HTTPException, APIRouter
from sqlalchemy import select, insert
from sqlalchemy.orm import joinedload
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post(
        "",
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
        email = user.email,
        username = user.username
    )


    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    await db.execute(
        insert(models.Categories),[
            {"user_id" : new_user.id , "category" : "Salary", "type" : "Income"},
            {"user_id" : new_user.id , "category" : "Rent", "type" : "Expense"},
            {"user_id" : new_user.id , "category" : "Groceries", "type" : "Expense"},
            {"user_id" : new_user.id , "category" : "Freelancing", "type" : "Income"}
        ]
    )
    await db.commit()


    return new_user



@router.get("/{user_id}",response_model=UserResponse)
async def get_user(user_id:int ,db: Annotated[AsyncSession, Depends(get_db)]):

    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )

    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.get("/{user_id}/transactions",response_model=list[TransResponse])
async def get_user_transactions(user_id:int ,db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.User)
        .where(models.User.id == user_id)
    )

    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    result = await db.execute(
        select(models.Transactions)
        .where(models.Transactions.user_id == user_id)
        .options(joinedload(models.Transactions.category))
    )

    transactions = result.scalars().all()
    return transactions



@router.get("/{user_id}/budgets",response_model=list[BudgetResponse])
async def get_user_budgets(user_id:int ,db: Annotated[AsyncSession, Depends(get_db)]):

    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )

    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    result = await db.execute(
        select(models.Budgets)
        .where(models.Budgets.user_id == user_id)
        .options(joinedload(models.Budgets.category))
    )
    budgets = result.scalars().all()
    return budgets


@router.patch("/update/{user_id}",response_model=UserResponse)
async def update_user(user_id: int , user_update: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
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
        result = db.execute(
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
@router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db:Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )

    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    await db.commit()