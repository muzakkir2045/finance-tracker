
from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from enum import Enum

class types(str, Enum):
    Income = "Income"
    Expense = "Expense"

class UserBase(BaseModel):
    email : EmailStr
    username : str

class UserCreate(UserBase):
    pass 

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id : int
    date : datetime
    

class TransBase(BaseModel):
    amount : int
    category_id : int
    type : types
    description : str

class TransCreate(TransBase):
    user_id: int # TEMPORARY
    pass 

class TransUpdate(BaseModel):
    amount : int | None = None
    category_id : int | None = None
    type : types | None = None 
    description : str | None = None

class TransResponse(TransBase):
    model_config = ConfigDict(from_attributes=True)

    id : int
    user_id : int
    date : datetime




class BudgetBase(BaseModel):
    category_id : int
    amount : int

class BudgetCreate(BudgetBase):
    user_id: int # TEMPORARY
    pass 

class BudgetUpdate(BaseModel):
    category_id : int | None = None
    amount : int | None = None

class BudgetResponse(BudgetBase):
    model_config = ConfigDict(from_attributes=True)

    id : int
    user_id : int
    month : datetime
