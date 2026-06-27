import models

from contextlib import asynccontextmanager
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi import FastAPI, HTTPException, Depends, status, Request
from sqlalchemy import select, func, and_
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import Base, engine, get_db
from sqlalchemy.orm import selectinload
from summary import category_summary, ai_summary
from typing import Annotated
from routers import users, transactions, budgets
from auth import CurrentUser


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
async def home(current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Transactions).where(models.Transactions.user_id == current_user.id)
    )
    transactions = result.scalars().all()

    result = await db.execute(
        select(models.Budgets).where(models.Budgets.user_id == current_user.id)
    )
    budgets = result.scalars().all()

    return {
        "Transactions" : transactions,
        "Budgets" : budgets
    }



@app.get("/category_summary")
async def monthly_summary(current_user: CurrentUser ,db: Annotated[AsyncSession, Depends(get_db)]):
    user_id = current_user.id
    summary = await category_summary(user_id, db)
    return summary


@app.get("/ai_summary")
async def monthly_ai_summary(current_user: CurrentUser ,db: Annotated[AsyncSession, Depends(get_db)]):
    user_id = current_user.id
    summary = await ai_summary(user_id, db )
    return summary


@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    return await http_exception_handler(request, exception)



@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    return await request_validation_exception_handler(request, exception)

