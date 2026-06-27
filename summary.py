import os
from dotenv import load_dotenv
from google import genai
from pathlib import Path
import models
import json
from fastapi import Depends
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from typing import Annotated

load_dotenv()

MODEL_NAME = "gemini-3.1-flash-lite"
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


async def category_summary(user_id : int, db : Annotated[AsyncSession, Depends(get_db)] ):
    result = await db.execute(
        select(func.coalesce(func.sum(models.Transactions.amount), 0))
        .where(models.Transactions.user_id == user_id , models.Transactions.type == "Income")
    )
    total_income = result.scalar()

    result = await db.execute(
        select(func.coalesce(func.sum(models.Budgets.amount), 0))
        .where(models.Budgets.user_id == user_id)
    )
    total_budget = result.scalar()



    st = await db.execute(
        select(
            models.Categories.category,
            func.coalesce(models.Budgets.amount, 0).label("budget"),
            func.coalesce(func.sum(models.Transactions.amount), 0).label("total_spent"),
            (func.coalesce(models.Budgets.amount, 0) - func.coalesce(func.sum(models.Transactions.amount), 0)).label("remaining")
        )
        .select_from(models.Categories)
        .outerjoin(models.Budgets, and_(models.Categories.id == models.Budgets.category_id, models.Budgets.user_id == user_id))
        .outerjoin(models.Transactions, and_(models.Categories.id == models.Transactions.category_id, models.Transactions.user_id == user_id))
        .where(models.Categories.user_id == user_id, models.Categories.type == "Expense")
        .group_by(models.Categories.id, models.Categories.category, models.Budgets.amount)
    )

    result = st.mappings().all()
    if total_budget:
        total_remaining = (total_income - total_budget)
    else:
        total_remaining = "Budget not added, Add a budget to get the remaining amount"

    return {
        "summary" : result,
        "total_income" : total_income,
        "total_budget" : total_budget,
        "total_remaining" : total_remaining
    }

async def ai_summary(user_id : int, db : Annotated[AsyncSession, Depends(get_db)] ):

    cat_summary = await category_summary(user_id, db)
    PROMPT_PATH = Path(__file__).parent / "prompts" / "summary_prompt.txt"

    SUMMARY_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")

    prompt = f"""{SUMMARY_PROMPT}

Financial Data:
{cat_summary}
"""
    
    response = await client.aio.models.generate_content(model=MODEL_NAME, contents=prompt)

    result = json.loads(response.text)

    return result