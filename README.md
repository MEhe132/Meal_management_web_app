# 🍽️ Plate & Spoon - Hostel Meal Management System

A modern, high-performance, real-time web application for managing hostel meals, financial accounting, daily menus, member accounts, and real-time chat. Built with Flask, SQLAlchemy, Tailwind CSS, and Server-Sent Events (SSE).

---

## 📑 Table of Contents
- [Features](#-features)
  - [👥 Member Capabilities](#-for-members-normal-users)
  - [👑 Manager (Admin) Capabilities](#-for-managers-admin)
  - [⚡ Performance & Real-Time Enhancements](#-performance--real-time-enhancements)
- [Business Logic & Formulas](#-business-logic--formulas)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start Guide](#-quick-start-guide)
- [API Endpoints](#-api-endpoints)
- [Performance & Navigation Guidelines](#-performance--navigation-guidelines)
- [License & Author](#-license--author)

---

## ✨ Features

### 👥 For Members (Normal Users)
- **📊 Interactive Dashboard**: View real-time personal & hostel meal statistics, monthly filtering, and overall running balance.
- **🍽️ Meal Status Toggle**: Enable or disable personal Breakfast (0.5 meal), Lunch (1.0 meal), and Dinner (1.0 meal) slots for today and upcoming 6 days (unless locked by manager).
- **📋 Today's Meals & Menu**: View today's total meal attendance breakdown and daily menu schedules.
- **💳 Financial Transparency**: Audit complete credit/debit history and overall hostel expenses.
- **💬 Real-Time Chat**: Send messages, reply to specific messages, mention members (`@Name`), customize avatar seed, and receive non-blocking push notifications with sound.

### 👑 For Managers (Admin)
- **🔒 Meal Locking**: Lock or unlock specific meal slots (Breakfast, Lunch, Dinner) per date to prevent late modifications.
- **🍲 Menu Management**: Set and update daily breakfast, lunch, and dinner menus for the week.
- **💳 Expense & Deposit Management**: Record hostel expenses, process member deposits/withdrawals, and trigger dynamic meal rate recalculation.
- **🔄 Manager Role Transfer**: Securely transfer manager administrative privileges to any active member via modal.

### ⚡ Performance & Real-Time Enhancements
- **Non-Blocking SSE Streaming**: Uses `queue.get(timeout=2.0)` with keep-alive heartbeats so background chat notification streams never lock WSGI worker threads.
- **Zero-Hang Page Navigation**: Includes client-side `beforeunload` event listeners to immediately close streaming sockets when clicking sidebar links rapidly.
- **Request-Scoped Caching**: Caches user context in `flask.g` and pre-computes monthly rates once to eliminate N+1 SQL queries.

---

## 📐 Business Logic & Formulas

All calculations run automatically in real-time without altering system rules:

$$ \text{Meal Count} = (0.5 \text{ if Breakfast}) + (1.0 \text{ if Lunch}) + (1.0 \text{ if Dinner}) $$

$$ \text{Monthly Meal Rate} = \frac{\text{Total Monthly Hostel Expenses}}{\text{Total Monthly Hostel Meals}} $$

$$ \text{Member Monthly Cost} = \text{Member Monthly Meals} \times \text{Monthly Meal Rate} $$

$$ \text{Running Balance} = \text{Total Deposits} - \text{Total Expenses/Cost} - \text{Total Withdrawals} $$

---

## 🛠️ Tech Stack

- **Backend**: Python 3.7+ | Flask 2.3+ | SQLAlchemy ORM
- **Database**: SQLite (Production configurable to PostgreSQL)
- **Frontend**: HTML5 | Vanilla JavaScript (ES6+) | Tailwind CSS
- **Real-Time Communication**: Server-Sent Events (SSE) with `MessageAnnouncer`
- **WSGI Server**: Waitress / Werkzeug

---

## 📁 Project Structure

```
test_hostel_management/
├── app.py                 # Main Flask application factory & endpoints
├── config.py              # Application configurations (Development/Production)
├── models.py              # SQLAlchemy database models & calculation logic
├── init_demo.py           # Demo seed data generator
├── setup.py               # Automated environment & dependency setup script
├── requirements.txt       # Python package requirements
├── static/
│   └── favicon.svg        # Application branding icon
├── templates/
│   ├── base.html          # Main responsive glassmorphism base layout & sidebar
│   ├── dashboard.html     # Real-time statistics & user breakdown table
│   ├── meal_status.html   # Member meal toggle & manager lock controls
│   ├── todays_meals.html  # Today's attendance overview & meal totals
│   ├── menu.html          # Weekly menu planner
│   ├── transactions.html  # Expense & financial auditing history
│   ├── members.html       # Member list & user IDs
│   ├── history.html       # Archived past monthly sheets
│   ├── chat.html          # Real-time hostel chat room
│   ├── login.html         # Login page
│   └── register.html      # Account registration page
└── necessaries/           # Developer cheatsheets & UI documentation
```

---

## 🚀 Quick Start Guide

### Automated Setup (Recommended)
Run the automated setup script to create a virtual environment, install dependencies, and seed demo data:

```bash
# 1. Navigate to the project directory
cd test_hostel_management

# 2. Run setup script
# Windows
python setup.py

# Linux/Mac
python3 setup.py
```

### Manual Setup
```bash
# 1. Navigate to the project directory
cd test_hostel_management

# 2. Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Seed demo database
python init_demo.py

# 4. Start application
python app.py
```

Open your browser at **http://localhost:5900** (or http://127.0.0.1:5900).

### 🔑 Default Demo Credentials
- **Manager**: `manager@example.com` / `password`
- **Member**: `mehedi@example.com` / `password`

---

## 📡 API Endpoints

### 🔐 Authentication & Session
- `POST /login` - User authentication
- `POST /register` - Register new user
- `GET /logout` - Clear session & logout

### 🍽️ Meal & Lock Management
- `POST /api/toggle-meal-status` - Toggle breakfast, lunch, or dinner for a date
- `POST /api/toggle-meal-lock` - (Manager) Lock/unlock meal slots for a date
- `POST /api/add-meal` - (Manager) Add/edit manual meal entries

### 💳 Financial & Menu Management
- `POST /api/update-menu` - (Manager) Update daily menu schedules
- `POST /api/add-money` - (Manager) Record deposit or withdrawal
- `GET /api/get-all-transactions` - Fetch complete transaction history
- `DELETE /api/delete-expense/<id>` - (Manager) Delete an expense entry

### 💬 Chat & Role Management
- `GET /api/chat/history` - Fetch recent chat messages
- `POST /api/chat/send` - Send chat message / mention users
- `GET /api/chat/stream` - Non-blocking SSE stream for live updates
- `GET /api/potential-managers` - (Manager) Fetch members eligible for role transfer
- `POST /api/transfer-manager` - (Manager) Transfer manager role to another member

---

## ⚙️ Performance & Navigation Guidelines

To prevent browser freeze / thread lock when navigating rapidly:
1. **Streaming Connections**: Background SSE connections close cleanly on `beforeunload` to free WSGI threads.
2. **Thread-Safe SSE Announcer**: `MessageAnnouncer` utilizes a `threading.Lock()` to prevent race conditions during rapid client disconnects/reconnects.
3. **Optimized SQL Query Architecture**: Uses `get_bulk_user_monthly_stats` and `get_bulk_user_balances` to aggregate user stats in 3-4 bulk queries instead of 100+ individual queries per dashboard load.
4. **Database Indexing**: Comprehensive SQLite indexes (`idx_meals_user_date`, `idx_transactions_user_type`, `idx_expenses_date`, `idx_chat_created_at`) ensure sub-millisecond filtering.
5. **Clean Schema Inspection**: Database startup migrations inspect table columns cleanly with `sqlalchemy.inspect` without throwing or rolling back failing SQL statements.

---

## 👨‍💻 Author & License

Developed by **MeHas** | College Project 2026  
Released under the **MIT License**. Free for educational & non-commercial use.
