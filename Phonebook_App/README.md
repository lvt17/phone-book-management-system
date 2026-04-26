# 📱 Phonebook Management System (CLI)

A professional personal phonebook management application running on a Command Line Interface (CLI), supporting multi-user authentication, contact categorization, and fast search.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [System Requirements](#-system-requirements)
- [Installation Guide](#-installation-guide)
- [How to Run](#-how-to-run)
- [Usage Guide](#-usage-guide)
- [Advanced Configuration](#-advanced-configuration)

---

## ✨ Features

### User Authentication
- **Register** accounts with username and password.
- **Login** to access personal phonebooks.
- Passwords are encrypted using SHA-256 before being stored in the database.
- Each user has a completely separate phonebook and category list.

### Contact Management
- **Add** new contacts (Name, Phone, Email, Address, Category).
- **Edit** contact information (displays old values as defaults).
- **Delete** contacts with a confirmation prompt.
- **Search** by name or phone number.
- **Display** all contacts in a professional table format.

### Category Management
- **Create** custom categories (e.g., Family, Friends, Work...).
- **View** all created categories.
- **Delete** categories (contacts in deleted categories become "Uncategorized").
- **Select categories** when creating/editing contacts from an existing list.

### Filtering by Category
- Display category list → select → view only contacts in that category.

### Data Validation
- **Phone Number**: Accepts Vietnamese formats (starting with `0` or `+84`, 10 digits).
- **Email**: Validates email format (optional field).
- **Username**: ≥ 3 characters, alphanumeric + underscore only.
- **Password**: ≥ 6 characters.

---

## 🛠 Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.10+ |
| Database | MySQL 8.0+ |
| CLI Interface | [Rich](https://github.com/Textualize/rich) — tables, colors, interactive prompts |
| DB Connector | [mysql-connector-python](https://dev.mysql.com/doc/connector-python/en/) |
| Encryption | `hashlib` (SHA-256, built-in Python) |

---

## 📂 Project Structure

```
phonebook/
├── main.py             # Entry point — Auth flow + Main menu
├── database.py         # DatabaseManager — All CRUD logic
├── models.py           # Dataclasses: User, Category, Contact
├── validators.py       # Validation for Phone, Email, Username, Password
├── phonebook.sql       # SQL schema to initialize the database
├── requirements.txt    # Dependencies
└── README.md           # This documentation
```

---

## 🗄 Database Schema

### ERD Diagram

```
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│      users       │       │   categories     │       │    contacts      │
├──────────────────┤       ├──────────────────┤       ├──────────────────┤
│ userid (PK, AI)  │──┐    │ cate_id (PK, AI) │──┐    │ contact_id (PK)  │
│ user_name (UQ)   │  │    │ cate_name        │  │    │ contact_name     │
│ password         │  │    │ userid (FK)──────►│  │    │ phone (UQ)       │
└──────────────────┘  │    └──────────────────┘  │    │ email            │
                      │                          │    │ address          │
                      └──────────────────────────►│    │ userid (FK)──────►│
                                                 └───►│ cate_id (FK)     │
                                                      └──────────────────┘
```

### Relations
- **users → contacts**: 1—N (Each user has many contacts)
- **users → categories**: 1—N (Each user creates many categories)
- **categories → contacts**: 1—N (Each category contains many contacts)

---

## 📌 System Requirements

- **Python**: 3.10 or higher
- **MySQL Server**: 8.0 or higher
- **pip**: Python package manager

---

## 🚀 Installation Guide

### Step 1: Install MySQL
Ensure MySQL Server is installed and running on your system.

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run with Docker (Recommended)
```bash
docker-compose up --build
```

---

## ▶️ How to Run

### Basic Run (Localhost, no password)
```bash
python main.py
```

### With Custom MySQL Configuration
Use environment variables:
```bash
export MYSQL_HOST="localhost"
export MYSQL_USER="root"
export MYSQL_PASSWORD="your_password"
python main.py
```

---

## 👨‍💻 Authors

Developed as a CLI Phonebook Management application using Python and MySQL.
**Group 02 - Programming & Testing**
