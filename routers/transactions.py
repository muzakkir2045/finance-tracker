import models
from typing import Annotated
from schemas import TransCreate, TransResponse, TransUpdate
from fastapi import status, Depends, HTTPException, APIRouter
from sqlalchemy import select, insert
from sqlalchemy.orm import joinedload
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()



# Transaction Endpoints
# To be deleted
@router.get("", response_model=list[TransResponse])
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


@router.get("/{trans_id}",response_model=TransResponse)
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

    result = await db.execute(stmt)

    transaction = result.scalars().first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    return transaction



@router.post(
        "",
        response_model=TransResponse,
        status_code=status.HTTP_201_CREATED)
async def add_transaction(transaction: TransCreate, db: Annotated[AsyncSession, Depends(get_db)]):

    result = await db.execute(
        select(models.User).where(models.User.id == transaction.user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )   

    result = await db.execute(
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
    await db.commit()
    await db.refresh(new_transaction)

    return new_transaction


@router.put("/full/{trans_id}/update", response_model=TransResponse)
async def update_transaction_full(trans_id : int, trans_data : TransCreate, db: Annotated[AsyncSession, Depends(get_db)]):

    result = await db.execute(
        select(models.Transactions).where(models.Transactions.id == trans_id)
    )
    transaction = result.scalars().first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    result = await db.execute(
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

    await db.commit()
    await db.refresh(transaction)
    
    return transaction
    


@router.patch("/partial/{trans_id}/update", response_model=TransResponse)
async def update_transaction_partial(trans_id : int, trans_data : TransUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    
    result = await db.execute(
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

    await db.commit()
    await db.refresh(transaction)
    return transaction


@router.delete("/delete/{trans_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(trans_id:int , db: Annotated[AsyncSession, Depends(get_db)]):

    result = await db.execute(
        select(models.Transactions).where(models.Transactions.id == trans_id)
    )
    transaction = result.scalars().first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    await db.delete(transaction)
    await db.commit()