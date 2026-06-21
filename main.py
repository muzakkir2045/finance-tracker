import models

from contextlib import asynccontextmanager
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi import FastAPI, HTTPException, Depends, status, Request
from schemas import UserCreate, UserResponse, Summary
from schemas import TransCreate, TransResponse, TransUpdate, BudgetCreate, BudgetResponse, BudgetUpdate
from sqlalchemy import select, insert, func, and_
from fastapi.exceptions import RequestValidationError

from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from database import Base, engine, get_db
from typing import Annotated
from routers import users, transactions, budgets, categories


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(lifespan=lifespan)


app.include_router(users.router, prefix = "/api/users", tags=["users"])
app.include_router(transactions.router, prefix = "/api/transactions", tags=["transactions"])
app.include_router(budgets.router, prefix = "/api/budgets", tags=["budgets"])


# CRUD for both transactions and budgets
@app.get("/")
async def home(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Transactions)
    )
    transactions = result.scalars().all()

    result = await db.execute(
        select(models.Budgets)
    )
    budgets = result.scalars().all()

    return {
        "Transactions" : transactions,
        "Budgets" : budgets
    }





@app.get("/summary/{user_id}")
async def monthly_summary(user_id:int ,db: Annotated[AsyncSession, Depends(get_db)]):
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
        select(func.sum(models.Transactions.amount))
        .select_from(models.Transactions)
        .where(models.Transactions.user_id == user_id , models.Transactions.type == "Income")
    ).scalar()
    total_income = result

    result = await db.execute(
        select(func.sum(models.Budgets.amount))
        .select_from(models.Budgets)
        .where(models.Budgets.user_id == user_id)
    ).scalar()
    total_budget = result



    st = await db.execute(
        select(
            models.Categories.category,
            (models.Budgets.amount).label("budget"),
            func.sum(models.Transactions.amount).label("total_spent"),
            (models.Budgets.amount - func.sum(models.Transactions.amount)).label("remaining")
        )
        .select_from(models.Categories)
        .join(models.Budgets, models.Categories.id == models.Budgets.category_id, isouter=True)
        .join(models.Transactions, and_(models.Categories.id == models.Transactions.category_id, models.Categories.type == "Expense"), isouter=True)
        .where(models.Transactions.user_id == user_id)
        .group_by(models.Categories.category, models.Budgets.amount)
    )

    result = st.mappings().all()
    return {
        "summary" : result,
        "total_income" : total_income,
        "total_budget" : total_budget,
        "total_remaining" : (total_income - total_budget)
    }


@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    return await http_exception_handler(request, exception)



@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):

    return await request_validation_exception_handler(request, exception)

