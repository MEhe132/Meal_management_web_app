"""
API Documentation
Hostel Meal Management System
"""

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

"""
POST /login
-----------
Login a user

Request:
  - email: User email address (required)
  - password: User password (required)

Response:
  - Redirects to /dashboard on success
  - Redirects to /login on failure with error message
  - Sets session['user_id']

Example:
  POST /login
  Data: {
    "email": "user@example.com",
    "password": "password123"
  }
"""

"""
POST /register
--------------
Register a new user

Request:
  - name: User full name (required)
  - email: User email address (required, must be unique)
  - password: User password (required)
  - password_confirm: Confirm password (required)
  - role: 'member' or 'manager' (optional, default: 'member')

Response:
  - Redirects to /login on success with success message
  - Redirects to /register on failure with error message

Restrictions:
  - Only one manager allowed
  - Email must be unique

Example:
  POST /register
  Data: {
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "role": "member"
  }
"""

"""
GET /logout
-----------
Logout current user

Response:
  - Clears session
  - Redirects to /login
  - Displays logout message

Example:
  GET /logout
"""

# ============================================================================
# VIEW ENDPOINTS (Require Authentication)
# ============================================================================

"""
GET /
-----
Home page

Response:
  - Redirects to /dashboard if user is logged in
  - Redirects to /login if user is not logged in

Permissions: None required
"""

"""
GET /dashboard
--------------
View meal management dashboard

Response:
  - HTML dashboard page with member statistics table
  - Shows daily meal counts for current month
  - Shows member balances and costs
  - Shows hostel-wide statistics

Permissions: Member, Manager

Members see: Read-only view of all data
Managers see: Same dashboard + can access Manager Panel

Data included:
  - All members with meal data
  - Daily meal counts (columns by date)
  - Total meals per member
  - Meal rate
  - Total cost per member
  - Account balance per member
  - Hostel totals (total meals, cost, rate)

Example:
  GET /dashboard
"""

"""
GET /manager
------------
Manager control panel

Response:
  - HTML manager panel with control options
  - Member management interface
  - Transaction history
  - Meal rate settings

Permissions: Manager only

Features:
  - Update daily meal counts
  - Add/withdraw money for members
  - Set meal rate
  - View member transactions
  - View all member balances

Example:
  GET /manager
"""

# ============================================================================
# API ENDPOINTS (JSON, Manager Only)
# ============================================================================

"""
POST /api/add-meal
------------------
Add or update meal entry for a member on a specific date

Requires: Manager authentication

Request (JSON):
  - user_id: User ID (required, integer)
  - meal_count: Number of meals (required, float)
  - date: Date in YYYY-MM-DD format (optional, default: today)

Response (JSON):
  Success:
    {
      "success": true,
      "message": "Meal entry updated",
      "meal_count": 2.5
    }
  
  Error:
    {
      "success": false,
      "message": "Invalid date format"
    }

Status Codes:
  - 200: Success
  - 400: Invalid input
  - 403: Unauthorized (not manager)
  - 401: Unauthenticated

Example:
  POST /api/add-meal
  Content-Type: application/json
  
  {
    "user_id": 2,
    "meal_count": 2.5,
    "date": "2026-04-22"
  }

Notes:
  - Creates new meal entry if doesn't exist
  - Updates existing entry if already present
  - Only one entry per user per date
"""

"""
POST /api/add-money
-------------------
Add deposit or withdrawal transaction for a member

Requires: Manager authentication

Request (JSON):
  - user_id: User ID (required, integer)
  - amount: Transaction amount (required, float, must be > 0)
  - type: 'deposit' or 'withdrawal' (required, string)
  - description: Transaction description (optional, string)

Response (JSON):
  Success:
    {
      "success": true,
      "message": "Deposit recorded",
      "new_balance": 4750.0
    }
  
  Error:
    {
      "success": false,
      "message": "Invalid input"
    }

Status Codes:
  - 200: Success
  - 400: Invalid input
  - 403: Unauthorized (not manager)
  - 401: Unauthenticated

Example:
  POST /api/add-money
  Content-Type: application/json
  
  {
    "user_id": 2,
    "amount": 1000,
    "type": "deposit",
    "description": "Monthly payment from parents"
  }

Transaction Types:
  - 'deposit': Add money to member's account
  - 'withdrawal': Subtract money from member's account

Notes:
  - Amount must be positive number
  - Type determines whether money is added or removed
  - Description is for record-keeping
  - Returns updated balance after transaction
"""

"""
POST /api/set-meal-rate
-----------------------
Set the meal rate for all members

Requires: Manager authentication

Request (JSON):
  - rate: Meal rate per unit (required, float, must be > 0)
  - description: Rate description (optional, string)

Response (JSON):
  Success:
    {
      "success": true,
      "message": "Meal rate updated",
      "rate": 50
    }
  
  Error:
    {
      "success": false,
      "message": "Invalid rate"
    }

Status Codes:
  - 200: Success
  - 400: Invalid input
  - 403: Unauthorized (not manager)
  - 401: Unauthenticated

Example:
  POST /api/set-meal-rate
  Content-Type: application/json
  
  {
    "rate": 55,
    "description": "Increased due to food cost rise"
  }

Notes:
  - Sets new effective date as today
  - Historical rates are preserved in database
  - New rate applies to all calculations immediately
  - Rate must be positive number
  - If multiple rates set on same day, last one is used
"""

# ============================================================================
# ERROR RESPONSES
# ============================================================================

"""
Common Error Responses:

401 Unauthorized (Not Authenticated)
---
Response:
  {
    "success": false,
    "message": "Please log in first"
  }
  
When: User session is not valid

---

403 Forbidden (Not Authorized)
---
Response:
  {
    "success": false,
    "message": "You do not have permission to access this page"
  }

When: User is authenticated but lacks required role

---

400 Bad Request
---
Response:
  {
    "success": false,
    "message": "Invalid input" or specific error message
  }

When: Request data is malformed or invalid
"""

# ============================================================================
# DATA MODELS
# ============================================================================

"""
User Model
----------
Attributes:
  - id: Integer (Primary Key)
  - name: String (100 chars)
  - email: String (120 chars, unique)
  - password_hash: String (255 chars)
  - role: String ('member' or 'manager')
  - is_active: Boolean (default: True)
  - created_at: DateTime

Methods:
  - set_password(password): Hash and store password
  - check_password(password): Verify password
  - is_manager(): Check if user is manager
  - get_balance(): Get current account balance
  - get_total_meals(): Get total meals consumed
  - get_total_cost(): Get total expense

Relationships:
  - meals: Many Meal entries
  - transactions: Many Transaction entries
"""

"""
Meal Model
----------
Attributes:
  - id: Integer (Primary Key)
  - user_id: Integer (Foreign Key to User)
  - date: Date
  - meal_count: Float (default: 0)
  - created_at: DateTime
  - updated_at: DateTime

Unique Constraint: (user_id, date)

Notes:
  - One entry per user per day
  - Meal count can be decimal (e.g., 2.5)
"""

"""
Transaction Model
-----------------
Attributes:
  - id: Integer (Primary Key)
  - user_id: Integer (Foreign Key to User)
  - amount: Float
  - type: String ('deposit' or 'withdrawal')
  - description: String (255 chars, optional)
  - date: DateTime (auto-set to now)
  - created_at: DateTime

Notes:
  - Records all money transactions
  - Positive amount for both deposit and withdrawal
  - Type field determines operation
"""

"""
MealRate Model
--------------
Attributes:
  - id: Integer (Primary Key)
  - rate: Float
  - effective_date: Date
  - description: String (255 chars, optional)
  - created_at: DateTime

Notes:
  - Historical record of all rates
  - Latest rate by effective_date is used
  - Allows tracking rate changes over time
"""

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

"""
get_current_meal_rate()
-----------------------
Returns the current meal rate

Returns: Float (latest rate as of today)

Usage:
  from models import get_current_meal_rate
  rate = get_current_meal_rate()
"""

"""
get_hostel_stats(current_date=None)
-----------------------------------
Get statistics for entire hostel

Parameters:
  - current_date: Date (optional, default: today)

Returns: Dictionary
  {
    'total_meals': float,
    'meal_rate': float,
    'total_cost': float,
    'total_deposited': float
  }

Usage:
  from models import get_hostel_stats
  stats = get_hostel_stats()
  print(f"Total meals: {stats['total_meals']}")
"""

# ============================================================================
# BUSINESS LOGIC
# ============================================================================

"""
Calculations:

1. Meal Rate
   - Current rate from MealRate table (latest by date)
   - Set by manager
   - Applies to all members

2. User's Total Meals
   - Sum of all meal_count entries for user
   - Includes meals up to current date

3. User's Total Cost
   - User's Total Meals × Current Meal Rate
   - Rounded to 0 decimals

4. User's Balance
   - Deposited money - Total Cost - Withdrawn money
   - Can be negative (member owes money)
   - Positive = money remaining
   - Negative = money owed

5. Hostel Statistics
   - Total Meals: Sum of all meals from all members
   - Meal Rate: Current rate
   - Total Cost: Total Meals × Meal Rate
   - Total Deposited: Sum of all deposits
"""

# ============================================================================
# AUTHENTICATION & SECURITY
# ============================================================================

"""
Session Management:
  - Session-based authentication
  - session['user_id'] stores authenticated user ID
  - Sessions expire after 7 days (configurable)
  - Session refreshed on each request (optional)

Password Security:
  - Passwords hashed using Werkzeug security
  - Never stored in plain text
  - check_password() for verification

Role-Based Access Control:
  - @login_required decorator: Requires authentication
  - @manager_required decorator: Requires manager role
  
CSRF Protection:
  - Form-based endpoints require proper session
  - API endpoints validate content-type

Production Recommendations:
  - Enable HTTPS
  - Change SECRET_KEY
  - Use environment variables
  - Enable CSRF tokens
  - Add rate limiting
  - Use PostgreSQL instead of SQLite
"""

# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
Example 1: Login and View Dashboard
-----------------------------------

# Step 1: POST to login
POST /login
Data: {
  "email": "member@example.com",
  "password": "password"
}

# Step 2: Browser automatically stores session cookie

# Step 3: GET dashboard
GET /dashboard
# Returns HTML dashboard page
"""

"""
Example 2: Manager Adding Meals
-------------------------------

# Manager logs in first
POST /login
Data: {
  "email": "manager@example.com",
  "password": "password"
}

# Manager updates meal count
POST /api/add-meal
Content-Type: application/json
{
  "user_id": 2,
  "meal_count": 2.5,
  "date": "2026-04-22"
}

# Manager sets meal rate
POST /api/set-meal-rate
Content-Type: application/json
{
  "rate": 50,
  "description": "Current rate"
}
"""

"""
Example 3: Manager Managing Finances
-----------------------------------

# Add deposit
POST /api/add-money
Content-Type: application/json
{
  "user_id": 2,
  "amount": 1000,
  "type": "deposit",
  "description": "Monthly payment"
}

# Record expense (withdrawal)
POST /api/add-money
Content-Type: application/json
{
  "user_id": 2,
  "amount": 50,
  "type": "withdrawal",
  "description": "Service charge"
}
"""
