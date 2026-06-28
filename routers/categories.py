

import models
from typing import Annotated
from schemas import CategoryResponse, CategoryCreate
from fastapi import status, Depends, HTTPException, APIRouter
from sqlalchemy import select
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from auth import CurrentUser

router = APIRouter()

@router.get("", response_model=list[CategoryResponse])
async def get_categories(current_user : CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):

    result = await db.execute(
        select(models.Categories).where(models.Categories.user_id == current_user.id)
    )

    categories = result.scalars().all()
    return categories

@router.post("", status_code=status.HTTP_201_CREATED, response_model=CategoryResponse)
async def add_category(category:CategoryCreate ,current_user : CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):

    result = await db.execute(
        select(models.Categories)
        .where(
            models.Categories.category_name == category.category_name.capitalize() ,
            models.Categories.user_id == current_user.id
        )
    )
    ctg = result.scalars().first()
    if ctg:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category already exists"
        )
    
    new_category = models.Categories(
        user_id = current_user.id,
        category_name = category.category_name.capitalize(),
        type = category.type.capitalize()
    )

    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    return new_category

