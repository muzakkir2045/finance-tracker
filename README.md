# MyFinance

A secure and scalable **Personal Finance Management REST API** built with **FastAPI**, **SQLAlchemy 2.0**, and **JWT Authentication**.

MyFinance is a secure and intelligent Personal Finance Management REST API built with FastAPI. It enables users to manage income, expenses, budgets, and categories while providing AI-generated financial insights powered by Google Gemini. The project demonstrates modern backend development practices including JWT authentication, asynchronous database operations, RESTful API design, and Large Language Model (LLM) integration.

---

## Features

* JWT Authentication & Authorization
* User Registration & Login
* Secure Password Hashing using Argon2
* Income & Expense Management
* Category-based Transaction Organization
* Budget Management
* Financial Summary Dashboard
* AI-generated Financial Summaries and Spending Insights
* Asynchronous Database Operations
* Request & Response Validation with Pydantic
* Automatic Interactive API Documentation (Swagger & ReDoc)

---

## Tech Stack

| Category         | Technology             |
| ---------------- | ---------------------- |
| Backend          | FastAPI                |
| ORM              | SQLAlchemy 2.0 (Async) |
| Database         | SQLite                 |
| Validation       | Pydantic v2            |
| Authentication   | JWT (PyJWT)            |
| Password Hashing | Argon2 (pwdlib)        |
| AI               | Google Gemini API      |
| Server           | Uvicorn                |

---

## Project Structure

```text
MyFinance/
│
├── routers/
│   ├── users.py
│   ├── transactions.py
│   ├── budgets.py
│   └── categories.py
├── prompts/
│   └── summary_prompt.txt
|
├── auth.py
├── config.py
├── database.py
├── models.py
├── schemas.py
├── main.py
├── summary.py
├── requirements.txt
└── transactions.db
```

---

## Database Schema

The application consists of four primary entities:

* **Users**
* **Transactions**
* **Budgets**
* **Categories**

### Relationships

```text
User
├── Transactions
├── Budgets
└── Categories

Category
├── Transactions
└── Budgets
```

Each user has complete ownership of their financial data, ensuring proper data isolation and security.

---

## Authentication

The API uses **JWT Bearer Authentication**.

### Authentication Flow

1. Register a new account.
2. Login using your email and password.
3. Receive a JWT access token.
4. Include the token in the Authorization header.

```http
Authorization: Bearer <your_access_token>
```

Protected endpoints automatically authenticate the currently logged-in user.

---

# API Endpoints

## Users

| Method | Endpoint              | Description                    |
| ------ | --------------------- | ------------------------------ |
| POST   | `/api/users/register` | Register a new user            |
| POST   | `/api/users/token`    | Login and obtain JWT token     |
| GET    | `/api/users/me`       | Get current authenticated user |
| PATCH  | `/api/users/update`   | Update user profile            |
| DELETE | `/api/users/delete`   | Delete current user            |

---

## Transactions

| Method | Endpoint                                |
| ------ | --------------------------------------- |
| GET    | `/api/transactions`                     |
| GET    | `/api/transactions/{id}`                |
| POST   | `/api/transactions`                     |
| PUT    | `/api/transactions/full/{id}/update`    |
| PATCH  | `/api/transactions/partial/{id}/update` |
| DELETE | `/api/transactions/delete/{id}`         |

### Supported Filters

* Transaction Type (Income / Expense)
* Category ID

---

## Budgets

| Method | Endpoint                           |
| ------ | ---------------------------------- |
| GET    | `/api/budgets`                     |
| GET    | `/api/budgets/{id}`                |
| POST   | `/api/budgets`                     |
| PUT    | `/api/budgets/full/{id}/update`    |
| PATCH  | `/api/budgets/partial/{id}/update` |
| DELETE | `/api/budgets/delete/{id}`         |

---

## Categories

| Method | Endpoint          |
| ------ | ----------------- |
| GET    | `/api/categories` |
| POST   | `/api/categories` |

---

## Financial Summary

| Method | Endpoint               | Description                                                   |
| ------ | ---------------------- | --------------------------------------------------------------|
| GET    | `/category_summary`    | Retrieve overall financial summary                            |
| GET    | `/ai_summary`          | Generate an AI-powered financial analysis and recommendations |

The category summary endpoint provides:

* Total Income
* Total Budget
* Remaining Balance
* Budget Allocation by Category
* Total Spending by Category
* Remaining Budget per Category


# AI Financial Summary

MyFinance integrates the **Google Gemini API** to transform raw financial data into actionable insights.

Instead of returning only numerical statistics, the AI analyzes the user's:

- Total Income
- Total Budget
- Remaining Budget
- Category-wise Spending
- Budget Utilization

and generates a structured financial summary that includes:

- Spending analysis
- Budget performance
- Financial observations
- Personalized recommendations
- Areas where overspending is detected

The AI receives structured financial data from the backend and produces a JSON response, making it easy for frontend applications to display intelligent financial insights.

This feature demonstrates practical integration of Large Language Models (LLMs) into a production-style REST API.

---

# Getting Started

## Clone the Repository

```bash
git clone https://github.com/yourusername/MyFinance.git

cd MyFinance
```

---

## Create a Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root.

```env
SECRET_KEY=your_super_secret_key
GEMINI_API_KEY=your_google_ai_studio_api_key
```

---

## Run the Application

```bash
uvicorn main:app --reload
```

The server will start at:

```
http://127.0.0.1:8000
```

---

## API Documentation

Swagger UI

```
http://127.0.0.1:8000/docs
```

ReDoc

```
http://127.0.0.1:8000/redoc
```

---

# Security

MyFinance includes several security best practices:

* JWT-based authentication
* Argon2 password hashing
* Protected API endpoints
* User-specific data isolation
* Pydantic request validation
* Centralized exception handling
* Environment variable configuration for secrets
* Secure AI API key management using environment variables

---

# Default Categories

Upon registration, every user automatically receives the following categories.

### Income

* Salary
* Freelancing

### Expense

* Rent
* Groceries

