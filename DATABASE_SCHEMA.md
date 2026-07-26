"""
DATABASE SCHEMA & DOCUMENTATION
Hostel Meal Management System
"""

# ============================================================================
# DATABASE OVERVIEW
# ============================================================================

"""
Database Type: SQLite
Database File: hostel_meals.db (created automatically on first run)
Location: hostel_meal_system/hostel_meals.db

The database stores all data for the meal management system including:
- User accounts (members and manager)
- Daily meal entries
- Financial transactions
- Historical meal rates
"""

# ============================================================================
# TABLES
# ============================================================================

"""
TABLE: users
=============

Purpose: Store user accounts and authentication info

Columns:
  - id (INTEGER, PRIMARY KEY)
    User unique identifier
    Auto-incremented
    
  - name (VARCHAR(100), NOT NULL)
    User's full name
    Example: "Mehedi Hasan"
    
  - email (VARCHAR(120), UNIQUE, NOT NULL)
    User's email address
    Must be unique across system
    Used for login
    Example: "mehedi@example.com"
    
  - password_hash (VARCHAR(255), NOT NULL)
    Hashed password using Werkzeug security
    Never store plain text passwords
    Verified using check_password() method
    
  - role (VARCHAR(20), DEFAULT 'member')
    User's role in system
    Values: 'member' or 'manager'
    'member' = Normal hostel resident
    'manager' = Admin with full control
    
  - is_active (BOOLEAN, DEFAULT TRUE)
    Account active status
    TRUE = Account is active
    FALSE = Account is deactivated
    
  - created_at (DATETIME, DEFAULT CURRENT_TIMESTAMP)
    Account creation timestamp
    Set automatically

Indexes:
  - PRIMARY KEY on id
  - UNIQUE on email

Sample Data:
  id | name           | email                  | role    | is_active | created_at
  1  | Manager User   | manager@example.com    | manager | TRUE      | 2026-04-22
  2  | Mehedi Hasan   | mehedi@example.com     | member  | TRUE      | 2026-04-22
  3  | Arefin Ahmed   | arefin@example.com     | member  | TRUE      | 2026-04-22

Relationships:
  - One-to-Many with meals (user has many meals)
  - One-to-Many with transactions (user has many transactions)
"""

"""
TABLE: meals
=============

Purpose: Track daily meal consumption for each member

Columns:
  - id (INTEGER, PRIMARY KEY)
    Meal entry unique identifier
    Auto-incremented
    
  - user_id (INTEGER, NOT NULL, FOREIGN KEY)
    Reference to users.id
    Identifies which member the meal belongs to
    Cannot be NULL
    
  - date (DATE, NOT NULL)
    Date of meal entry
    Format: YYYY-MM-DD
    Example: 2026-04-22
    
  - meal_count (FLOAT, DEFAULT 0)
    Number of meals consumed
    Can be decimal (e.g., 2.5 meals)
    Represents fraction of meals per day
    
  - created_at (DATETIME, DEFAULT CURRENT_TIMESTAMP)
    When meal entry was created
    
  - updated_at (DATETIME, DEFAULT CURRENT_TIMESTAMP)
    When meal entry was last updated
    Automatically updated on changes

Constraints:
  - UNIQUE (user_id, date)
    Only one meal entry per user per date
    Prevents duplicate entries for same date

Indexes:
  - PRIMARY KEY on id
  - FOREIGN KEY on user_id → users.id
  - UNIQUE on (user_id, date)

Sample Data:
  id | user_id | date       | meal_count | created_at
  1  | 2       | 2026-04-18 | 2.5        | 2026-04-22
  2  | 2       | 2026-04-19 | 2.0        | 2026-04-22
  3  | 2       | 2026-04-20 | 2.5        | 2026-04-22
  4  | 3       | 2026-04-18 | 2.0        | 2026-04-22

Relationships:
  - Many-to-One with users (many meals per user)

Business Logic:
  - User can have multiple meal entries on different dates
  - Only one entry per user per date (enforced by UNIQUE constraint)
  - Manager can update meal counts anytime
"""

"""
TABLE: transactions
====================

Purpose: Track all financial transactions (deposits/withdrawals)

Columns:
  - id (INTEGER, PRIMARY KEY)
    Transaction unique identifier
    Auto-incremented
    
  - user_id (INTEGER, NOT NULL, FOREIGN KEY)
    Reference to users.id
    Identifies which member the transaction belongs to
    
  - amount (FLOAT, NOT NULL)
    Transaction amount
    Always positive number
    Actual amount added or subtracted determined by 'type' field
    Example: 1000
    
  - type (VARCHAR(20), NOT NULL)
    Transaction type
    Values: 'deposit' or 'withdrawal'
    'deposit' = Money added to account
    'withdrawal' = Money removed from account
    
  - description (VARCHAR(255))
    Human-readable description of transaction
    Optional field for record-keeping
    Example: "Monthly payment from parents"
    
  - date (DATETIME, DEFAULT CURRENT_TIMESTAMP)
    When transaction occurred
    Set automatically to current time
    
  - created_at (DATETIME, DEFAULT CURRENT_TIMESTAMP)
    When transaction record was created

Indexes:
  - PRIMARY KEY on id
  - FOREIGN KEY on user_id → users.id

Sample Data:
  id | user_id | amount | type       | description                    | date
  1  | 2       | 5000   | deposit    | Initial deposit                | 2026-04-22
  2  | 2       | 1000   | deposit    | Monthly payment                | 2026-04-22
  3  | 3       | 5000   | deposit    | Initial deposit                | 2026-04-22
  4  | 2       | 200    | withdrawal | Service charge                 | 2026-04-22

Relationships:
  - Many-to-One with users (many transactions per user)

Business Logic:
  - All amounts stored as positive numbers
  - Type determines if amount is added or subtracted
  - Historical record of all financial activity
  - No transaction can be deleted (audit trail)
"""

"""
TABLE: meal_rates
===================

Purpose: Track meal rate history (price per meal)

Columns:
  - id (INTEGER, PRIMARY KEY)
    Meal rate entry unique identifier
    Auto-incremented
    
  - rate (FLOAT, NOT NULL)
    Price per meal in currency (e.g., ৳)
    Example: 50 (means ৳50 per meal)
    
  - effective_date (DATE, NOT NULL)
    Date when this rate becomes effective
    Format: YYYY-MM-DD
    Used to find current rate
    
  - description (VARCHAR(255))
    Reason or note for rate change
    Optional field
    Example: "Increased due to food cost rise"
    
  - created_at (DATETIME, DEFAULT CURRENT_TIMESTAMP)
    When rate record was created

Indexes:
  - PRIMARY KEY on id

Sample Data:
  id | rate | effective_date | description
  1  | 50   | 2026-04-22     | Initial rate
  2  | 55   | 2026-05-01     | Increased due to inflation

Relationships:
  - No direct foreign keys
  - Logically related to calculations

Business Logic:
  - Latest rate (by effective_date) is used for calculations
  - Historical rates preserved for auditing
  - Manager can set new rate anytime
  - Multiple rates on different dates allowed
  - Only one rate per date (latest is used)
"""

# ============================================================================
# RELATIONSHIPS & DEPENDENCIES
# ============================================================================

"""
Entity Relationship Diagram (Text):

┌─────────────┐
│   users     │
│─────────────│
│ id (PK)     │
│ name        │
│ email (UQ)  │
│ password    │
│ role        │
│ is_active   │
│ created_at  │
└──────┬──────┘
       │
       ├──────────1:N────────────┬──────────────┐
       │                         │              │
       V                         V              V
   ┌─────────────┐          ┌──────────────┐
   │   meals     │          │ transactions │
   │─────────────│          │──────────────│
   │ id (PK)     │          │ id (PK)      │
   │ user_id(FK) │          │ user_id(FK)  │
   │ date        │          │ amount       │
   │ meal_count  │          │ type         │
   │ created_at  │          │ description  │
   └─────────────┘          │ date         │
                            └──────────────┘

┌──────────────────┐
│   meal_rates     │
│──────────────────│
│ id (PK)          │
│ rate             │
│ effective_date   │
│ description      │
│ created_at       │
└──────────────────┘

(meal_rates is referenced indirectly for calculations)
"""

# ============================================================================
# DATA CALCULATIONS & DERIVED VALUES
# ============================================================================

"""
These values are calculated from base data:

1. User's Total Meals
   SQL: SELECT SUM(meal_count) FROM meals 
        WHERE user_id = ? AND date <= ?
   
   Python: user.get_total_meals()
   
   Used for: Cost calculation, statistics

2. User's Total Cost
   Formula: Total Meals × Current Meal Rate
   SQL: SELECT SUM(meal.meal_count * rate) FROM ...
   
   Python: user.get_total_cost()
   
   Example: 10 meals × ৳50 = ৳500

3. User's Deposited Money
   SQL: SELECT SUM(amount) FROM transactions 
        WHERE user_id = ? AND type = 'deposit'
   
   Used for: Balance calculation

4. User's Withdrawals
   SQL: SELECT SUM(amount) FROM transactions 
        WHERE user_id = ? AND type = 'withdrawal'
   
   Used for: Balance calculation

5. User's Balance
   Formula: Deposits - Costs - Withdrawals
   Python: user.get_balance()
   
   Example:
     Deposits:    ৳5000
     - Costs:     ৳500
     - Withdraw:  ৳200
     = Balance:   ৳4300

6. Current Meal Rate
   SQL: SELECT rate FROM meal_rates 
        WHERE effective_date <= TODAY()
        ORDER BY effective_date DESC
        LIMIT 1
   
   Python: get_current_meal_rate()
   
   Used for: All cost calculations

7. Hostel Total Meals
   SQL: SELECT SUM(meal_count) FROM meals 
        WHERE date <= TODAY()
   
   Used for: Statistics, dashboard

8. Hostel Total Cost
   Formula: Total Meals × Current Meal Rate
   
   Used for: Financial overview

9. Hostel Total Deposited
   SQL: SELECT SUM(amount) FROM transactions 
        WHERE type = 'deposit'
   
   Used for: Financial overview
"""

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

"""
Common Database Operations:

1. GET CURRENT USER INFO
   SQL: SELECT * FROM users WHERE id = ?
   Python: User.query.get(user_id)

2. GET ALL MEMBERS
   SQL: SELECT * FROM users WHERE role = 'member' AND is_active = TRUE
   Python: User.query.filter_by(role='member', is_active=True).all()

3. GET USER'S MEALS FOR DATE
   SQL: SELECT * FROM meals WHERE user_id = ? AND date = ?
   Python: Meal.query.filter_by(user_id=uid, date=date).first()

4. ADD MEAL ENTRY
   SQL: INSERT INTO meals (user_id, date, meal_count) 
        VALUES (?, ?, ?)
        OR UPDATE IF EXISTS (UNIQUE CONSTRAINT)
   Python: db.session.add(meal_obj); db.session.commit()

5. ADD TRANSACTION
   SQL: INSERT INTO transactions (user_id, amount, type, description)
        VALUES (?, ?, ?, ?)
   Python: db.session.add(transaction_obj); db.session.commit()

6. SET NEW MEAL RATE
   SQL: INSERT INTO meal_rates (rate, effective_date, description)
        VALUES (?, ?, ?)
   Python: db.session.add(rate_obj); db.session.commit()

7. GET USER BALANCE
   Query: Sum deposits - Sum costs - Sum withdrawals
   Method: user.get_balance()

8. GET ALL TRANSACTIONS FOR USER
   SQL: SELECT * FROM transactions WHERE user_id = ?
        ORDER BY date DESC
   Python: Transaction.query.filter_by(user_id=uid).order_by(
           Transaction.date.desc()).all()
"""

# ============================================================================
# INTEGRITY CONSTRAINTS
# ============================================================================

"""
Data Integrity Rules Enforced:

1. Email Uniqueness
   - No two users can have same email
   - Enforced at database level: UNIQUE(email)

2. Only One Meal Entry Per Day Per User
   - Enforced by UNIQUE constraint on (user_id, date)
   - Prevents duplicate entries

3. Foreign Key Constraints
   - meals.user_id must reference users.id
   - transactions.user_id must reference users.id
   - Prevents orphaned records

4. Not Null Constraints
   - user.name, user.email, user.password_hash
   - meals.user_id, meals.date
   - transactions.user_id, transactions.amount, transactions.type
   - meal_rates.rate, meal_rates.effective_date

5. Role Validation
   - role must be 'member' or 'manager'
   - Enforced in application logic
   - Default is 'member'

6. Amount Validation
   - All amounts must be > 0
   - Enforced in application logic
   - Type field determines + or -
"""

# ============================================================================
# PERFORMANCE CONSIDERATIONS
# ============================================================================

"""
Query Optimization:

1. Indexes on Frequently Queried Columns
   - users.email (for login)
   - meals.user_id + meals.date (for getting meal for specific date)
   - transactions.user_id (for user's transaction history)

2. Avoiding N+1 Queries
   - Use SQLAlchemy relationships with lazy loading
   - Batch queries when possible
   - Use joins for related data

3. Large Dataset Handling
   - For large member list: Use pagination
   - For historical data: Archive old records
   - Consider migration to PostgreSQL if needed

4. Current Limitations (SQLite)
   - Limited concurrent access
   - Not suitable for thousands of users
   - Single-file database
   - Good for: College/hostel project (100s of users)
"""

# ============================================================================
# BACKUP & MAINTENANCE
# ============================================================================

"""
Database Maintenance:

1. Backup Procedure
   - Copy hostel_meals.db to safe location
   - Use Version Control (Git) to track changes
   - Export data to CSV/Excel for safety

2. Export Data
   Example Python script to export to CSV:
   
   import csv
   from models import db, User, Meal, Transaction
   
   # Export users
   users = User.query.all()
   with open('users.csv', 'w') as f:
       writer = csv.DictWriter(f, ['id', 'name', 'email', 'role'])
       writer.writeheader()
       for user in users:
           writer.writerow({...})

3. Reset Database
   - Delete hostel_meals.db
   - Run: python init_demo.py
   - Or manually create tables

4. Migration
   - To move to PostgreSQL:
     1. Install PostgreSQL
     2. Update config.py: SQLALCHEMY_DATABASE_URI
     3. Run db.create_all() with new database
     4. Migrate data (dump and restore)

5. Monitoring & Performance
   - Explicit Indexes:
     - `idx_meals_date`: `meals(date)`
     - `idx_meals_user_date`: `meals(user_id, date)`
     - `idx_transactions_user_type`: `transactions(user_id, type)`
     - `idx_transactions_date`: `transactions(date)`
     - `idx_expenses_date`: `expenses(date)`
     - `idx_expenses_user`: `expenses(user_id)`
     - `idx_chat_created_at`: `chat_messages(created_at)`
     - `idx_chat_user`: `chat_messages(user_id)`
   - Monitor database file size
   - Regular backups
   - Check transaction logs
"""

# ============================================================================
# EXAMPLE QUERIES
# ============================================================================

"""
Examples using SQLAlchemy:

1. Get user by email:
   user = User.query.filter_by(email='user@example.com').first()

2. Get all active members:
   members = User.query.filter_by(role='member', is_active=True).all()

3. Get meals for user in date range:
   meals = Meal.query.filter(
       Meal.user_id == user_id,
       Meal.date >= start_date,
       Meal.date <= end_date
   ).all()

4. Get transactions for user, newest first:
   transactions = Transaction.query.filter_by(
       user_id=user_id
   ).order_by(Transaction.date.desc()).all()

5. Sum of meals for user:
   total = db.session.query(
       db.func.sum(Meal.meal_count)
   ).filter(Meal.user_id == user_id).scalar() or 0

6. Get current meal rate:
   rate = MealRate.query.filter(
       MealRate.effective_date <= date.today()
   ).order_by(MealRate.effective_date.desc()).first()

7. Count total members:
   count = User.query.filter_by(role='member').count()

8. Get member with highest balance:
   member = User.query.filter_by(role='member').order_by(
       User.get_balance().desc()
   ).first()
"""
