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


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

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




@app.post("/users",response_model=UserResponse,
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



@app.get("/users/{user_id}",response_model=UserResponse)
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


@app.get("/users/{user_id}/transactions",response_model=list[TransResponse])
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

# update user
# ============= to be made

# delete user
@app.delete("/users/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
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



@app.get("/users/{user_id}/budgets",response_model=list[BudgetResponse])
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
        select(models.Budgets).where(models.Budgets.user_id == user_id)
    )
    budgets = result.scalars().all()
    return budgets



# Transaction Endpoints
@app.get("/transactions", response_model=list[TransResponse])
async def get_transactions(db: Annotated[AsyncSession, Depends(get_db)], 
    type: str | None = None, category_id: int | None = None):
    
    stmt = select(models.Transactions)
    if type:
        stmt = stmt.where(models.Transactions.type == type)
    if category_id:
        stmt = stmt.where(models.Transactions.category_id == category_id)
    
    result = db.execute(stmt)
    transactions = result.scalars().all()

    return transactions


@app.get("/transactions/{trans_id}",response_model=TransResponse)
async def get_transaction(
    trans_id:int ,
    db: Annotated[AsyncSession, Depends(get_db)],
    type: str | None = None, category_id: int | None = None
):
    stmt = select(models.Transactions).where(models.Transactions.id == trans_id)

    if type:
        stmt = stmt.where(models.Transactions.type == type)
    if category_id:
        stmt = stmt.where(models.Transactions.category_id == category_id)

    result = db.execute(stmt)

    transaction = result.scalars().first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    return transaction



@app.post(
        "/transactions",
        response_model=TransResponse,
        status_code=status.HTTP_201_CREATED)
async def add_transaction(transaction: TransCreate, db: Annotated[AsyncSession, Depends(get_db)]):

    result = db.execute(
        select(models.User).where(models.User.id == transaction.user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )   

    result = db.execute(
        select(models.Categories).where(models.Categories.id == transaction.category_id)
    )    
    category = result.scalars().first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category id not found, Please enter a valid category Id"
        )   


    new_transaction = models.Transactions(
        user_id = transaction.user_id,
        amount = transaction.amount,
        category_id = transaction.category_id,
        type = transaction.type,
        description = transaction.description
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


@app.put("/transactions/{trans_id}", response_model=TransResponse)
async def update_transaction_full(trans_id : int, trans_data : TransCreate, db: Annotated[AsyncSession, Depends(get_db)]):

    result = db.execute(
        select(models.Transactions).where(models.Transactions.id == trans_id)
    )
    transaction = result.scalars().first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    result = db.execute(
        select(models.Categories).where(models.Categories.id == transaction.category_id)
    )    
    category = result.scalars().first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category id not found, Please enter a valid category Id"
        ) 
    
    transaction.amount = trans_data.amount
    transaction.category_id = trans_data.category_id
    transaction.type = trans_data.type
    transaction.description = trans_data.description

    db.commit()
    db.refresh(transaction)
    
    return transaction
    


@app.patch("/transactions/{trans_id}", response_model=TransResponse)
async def update_transaction_partial(trans_id : int, trans_data : TransUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    
    result = db.execute(
        select(models.Transactions).where(models.Transactions.id == trans_id)
    )
    transaction = result.scalars().first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    update_data = trans_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(transaction, field, value)

    db.commit()
    db.refresh(transaction)
    return transaction


@app.delete("/transactions/{trans_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(trans_id:int , db: Annotated[AsyncSession, Depends(get_db)]):

    result = db.execute(
        select(models.Transactions).where(models.Transactions.id == trans_id)
    )
    transaction = result.scalars().first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    db.delete(transaction)
    db.commit()




# Budget Endpoints
@app.get("/budgets", response_model=BudgetResponse)
async def get_budgets(db: Annotated[AsyncSession, Depends(get_db)]):
    result = db.execute(
        select(models.Budgets)
    )

    budgets = result.scalars().all()
    return budgets


@app.get("/budgets/{budget_id}", response_model=BudgetResponse)
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



@app.post("/budgets", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def add_budget(budget:BudgetCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.id == budget.user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )   

    result = db.execute(
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
    db.commit()
    db.refresh(new_budget)

    return new_budget


@app.put("/budgets/{budget_it}", response_model=BudgetResponse)
async def budget_update_full(budget_id:int, budget_data: BudgetCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = db.execute(
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

    db.commit()
    db.refresh(budget)
    return budget


@app.patch("/budgets/{budget_it}", response_model=BudgetResponse)
async def budget_update_partial(budget_id:int, budget_data: BudgetUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = db.execute(
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

    db.commit()
    db.refresh(budget)
    return budget


@app.delete("/budgets/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_budget(budget_id:int, db:Annotated[AsyncSession, Depends(get_db)]):
    result = db.execute(
        select(models.Budgets).where(models.Budgets.id == budget_id)
    )

    budget = result.scalars().all()

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    db.delete(budget)
    db.commit()


@app.get("/summary/{user_id}")
async def monthly_summary(user_id:int ,db: Annotated[AsyncSession, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    result = db.execute(
        select(func.sum(models.Transactions.amount))
        .select_from(models.Transactions)
        .where(models.Transactions.user_id == user_id , models.Transactions.type == "Income")
    ).scalar()
    total_income = result

    result = db.execute(
        select(func.sum(models.Budgets.amount))
        .select_from(models.Budgets)
        .where(models.Budgets.user_id == user_id)
    ).scalar()
    total_budget = result



    st = db.execute(
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
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    return JSONResponse(
        status_code=exception.status_code,
        content={"detail": message},
    )



@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": exception.errors()},
    )

