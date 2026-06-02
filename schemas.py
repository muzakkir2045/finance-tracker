
from pydantic import BaseModel, ConfigDict
from datetime import datetime
# Transactions
# Budgets



class TransBase(BaseModel):
    amount : int
    category_id : int
    type : str
    description : str

class TransCreate(TransBase):
    pass 

class TransUpdate(BaseModel):
    amount : int | None = None
    category_id : int | None = None
    type : str | None = None 
    description : str | None = None

class TransResponse(TransBase):
    model_config = ConfigDict(from_attributes=True)

    id : int
    date : datetime




class BudgetBase(BaseModel):
    category_id : int
    amount : int

class BudgetCreate(BudgetBase):
    pass 

class BudgetUpdate(BaseModel):
    category_id : int | None = None
    amount : int | None = None

class BudgetResponse(BudgetBase):
    model_config = ConfigDict(from_attributes=True)

    id : int
    month : datetime
