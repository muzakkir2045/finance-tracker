
from pydantic import BaseModel, ConfigDict, EmailStr , Field
from datetime import datetime
from enum import Enum

class types(str, Enum):
    Income = "Income"
    Expense = "Expense"

class UserBase(BaseModel):
    username : str = Field(min_length=1, max_length=50)
    email : EmailStr = Field(max_length=120)

class UserCreate(UserBase):
    password : str = Field(min_length=8)

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id : int
    date : datetime

class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50) 
    email: EmailStr | None = Field(default=None, max_length=120)

class Token(BaseModel):
    access_token : str
    token_type : str   

class TransBase(BaseModel):
    amount : int
    category_id : int
    type : types
    description : str

class TransCreate(TransBase):
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
    pass 

class BudgetUpdate(BaseModel):
    category_id : int | None = None
    amount : int | None = None

class BudgetResponse(BudgetBase):
    model_config = ConfigDict(from_attributes=True)

    id : int
    user_id : int
    month : datetime


class CategoryBase(BaseModel):
    category_name : str
    type : str

class CategoryCreate(CategoryBase):
    pass 

class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    # id : int
    user_id : int

class Summary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    category : str # categories
    budget : float # budgets
    total_spent : float # transactions
    remaining : float # budget - (sum of transactions)


