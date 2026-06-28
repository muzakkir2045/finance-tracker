from __future__ import annotations
from enum import Enum
from datetime import UTC, datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class types(str, Enum):
    Income = "Income"
    Expense = "Expense"

class User(Base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username : Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email : Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    date : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    transactions : Mapped[list["Transactions"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    budgets: Mapped[list["Budgets"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    categories: Mapped[list["Categories"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Transactions(Base):
    __tablename__ = "transactions"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    amount : Mapped[int] = mapped_column(Integer, nullable=False)
    category_id : Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
        index=True 
    )
    type : Mapped[types] = mapped_column(SQLEnum(types), nullable=False)

    date : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    description : Mapped[str | None] = mapped_column(Text)


    user : Mapped[User] = relationship(
        back_populates="transactions"
    )
    category : Mapped["Categories"] = relationship(
        back_populates="transactions")





class Budgets(Base):
    __tablename__ = "budgets"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    category_id : Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
        index=True 
    )
    amount : Mapped[int] = mapped_column(
        Integer, nullable=False 
    )
    month : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    user: Mapped["User"] = relationship(back_populates="budgets")
    category : Mapped["Categories"] = relationship(
        back_populates="budgets")


class Categories(Base):
    __tablename__ = "categories"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    category_name : Mapped[str] = mapped_column(String, nullable=False)
    type : Mapped [str] = mapped_column(String, nullable=False)

    user: Mapped["User"] = relationship(back_populates="categories")
    transactions: Mapped[list["Transactions"]] = relationship(
        back_populates="category"
    )
    budgets: Mapped[list["Budgets"]] = relationship(
        back_populates="category"
    )


