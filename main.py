import models
from fastapi import FastAPI, HTTPException, Depends, status
from schemas import TransCreate, TransResponse, TransUpdate, BudgetCreate, BudgetResponse, BudgetUpdate
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from typing import Annotated


Base.metadata.create_all(bind=engine)

app = FastAPI()

# CRUD for both transactions and budgets
@app.get("/")
def home(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.Transactions)
    )
    transactions = result.scalars().all()

    result = db.execute(
        select(models.Budgets)
    )
    budgets = result.scalars().all()

    return {
        "Transactions" : transactions,
        "Budgets" : budgets
    }



# Transaction Endpoints
@app.get("/transactions")
def get_transactions(db: Annotated[Session, Depends(get_db)], 
    type: str | None = None, category_id: int | None = None):
    
    stmt = select(models.Transactions)
    if type:
        stmt = stmt.where(models.Transactions.type == type)
    if category_id:
        stmt = stmt.where(models.Transactions.category_id == category_id)
    
    result = db.execute(stmt)
    transactions = result.scalars().all()

    return transactions


@app.get("/transactions/{trans_id}")
def get_transaction(
    trans_id:int ,
    db: Annotated[Session, Depends(get_db)],
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
def add_transaction(transaction: TransCreate, db: Annotated[Session, Depends(get_db)]):

    new_transaction = models.Transactions(
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
def update_transaction_full(trans_id : int, trans_data : TransCreate, db: Annotated[Session, Depends(get_db)]):

    result = db.execute(
        select(models.Transactions).where(models.Transactions.id == trans_id)
    )
    transaction = result.scalars().first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    transaction.amount = trans_data.amount
    transaction.category_id = trans_data.category_id
    transaction.type = trans_data.type
    transaction.description = trans_data.description

    db.commit()
    db.refresh(transaction)
    
    return transaction
    


@app.patch("/transactions/{trans_id}", response_model=TransResponse)
def update_transaction_partial(trans_id : int, trans_data : TransUpdate, db: Annotated[Session, Depends(get_db)]):
    
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
def delete_transaction(trans_id:int , db: Annotated[Session, Depends(get_db)]):

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
@app.get("/budgets")
def get_budgets(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.Budgets)
    )

    budgets = result.scalars().all()
    return budgets


@app.get("/budgets/{budget_id}")
def get_budget(budget_id: int, db: Annotated[Session, Depends(get_db)]):
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
def add_budget(budget:BudgetCreate, db: Annotated[Session, Depends(get_db)]):

    new_budget = models.Budgets(
        category_id = budget.category_id,
        amount = budget.amount
    )

    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)

    return new_budget


@app.put("/budgets/{budget_it}", response_model=BudgetResponse)
def budget_update_full(budget_id:int, budget_data: BudgetCreate, db: Annotated[Session, Depends(get_db)]):
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
def budget_update_partial(budget_id:int, budget_data: BudgetUpdate, db: Annotated[Session, Depends(get_db)]):
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
def remove_budget(budget_id:int, db:Annotated[Session, Depends(get_db)]):
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

