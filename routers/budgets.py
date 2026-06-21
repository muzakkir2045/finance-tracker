


import models
from typing import Annotated
from schemas import BudgetCreate, BudgetResponse, BudgetUpdate
from fastapi import status, Depends, HTTPException, APIRouter
from sqlalchemy import select
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


# Budget Endpoints
# to be deleted
@router.get("/", response_model=BudgetResponse)
async def get_budgets(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Budgets)
    )

    budgets = result.scalars().all()
    return budgets


@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(budget_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = db.execute(
        select(models.Budgets).where(models.Budgets.id == budget_id)
    )

    budget = result.scalars().all()

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    return budget



@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def add_budget(budget:BudgetCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.User).where(models.User.id == budget.user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )   

    result = await db.execute(
        select(models.Categories.type).where(models.Categories.id == budget.category_id)
    )
    cat = result.scalars().first()
    if cat == "Income":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budgets can only be created for expense categories."
        )

    new_budget = models.Budgets(
        category_id = budget.category_id,
        amount = budget.amount,
        user_id = budget.user_id
    )

    db.add(new_budget)
    await db.commit()
    await db.refresh(new_budget)

    return new_budget


@router.put("/full/{budget_id}/update", response_model=BudgetResponse)
async def budget_update_full(budget_id:int, budget_data: BudgetCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Budgets).where(models.Budgets.id == budget_id)
    )

    budget = result.scalars().first()

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    budget.category_id = budget_data.category_id
    budget.amount = budget_data.amount

    await db.commit()
    await db.refresh(budget)
    return budget


@router.patch("/partial/{budget_id}/update", response_model=BudgetResponse)
async def budget_update_partial(budget_id:int, budget_data: BudgetUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Budgets).where(models.Budgets.id == budget_id)
    )

    budget = result.scalars().first()

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    update_data = budget_data.model_dump(exclude_unset=True)

    for field,value in update_data.items():
        setattr(budget, field, value)

    await db.commit()
    await db.refresh(budget)
    return budget


@router.delete("/delete/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_budget(budget_id:int, db:Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Budgets).where(models.Budgets.id == budget_id)
    )

    budget = result.scalars().all()

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    await db.delete(budget)
    await db.commit()