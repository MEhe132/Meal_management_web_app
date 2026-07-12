"""
PROJECT SUMMARY & ARCHITECTURE
Hostel Meal Management System
"""

# ============================================================================
# PROJECT OVERVIEW
# ============================================================================

"""
Project Name: Hostel Meal Management System
Purpose: Manage meal consumption, finances, and member accounts in a hostel
Stack: Flask + SQLite + Tailwind CSS
Created For: College Project (Educational)
Status: Production-Ready for Small to Medium Scale Deployment
"""

# ============================================================================
# SYSTEM ARCHITECTURE
# ============================================================================

"""
Architecture Layers:

┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│                    (HTML + CSS + JavaScript)                │
│  - Login/Register Pages                                     │
│  - Dashboard (Read-only for members)                        │
│  - Manager Panel (Full control)                             │
│  - Responsive Tailwind CSS UI                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│                      (Flask Routes)                          │
│  - Authentication Routes (login, register, logout)          │
│  - Dashboard Routes (display data)                          │
│  - API Routes (add meals, add money, set rates)             │
│  - Role-Based Access Control                                │
│  - Session Management                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                     BUSINESS LOGIC LAYER                      │
│                  (Models & Calculations)                     │
│  - User model with balance calculations                     │
│  - Meal tracking and aggregation                            │
│  - Transaction management                                    │
│  - Meal rate calculations                                    │
│  - Hostel statistics                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                     DATA ACCESS LAYER                         │
│                    (SQLAlchemy ORM)                          │
│  - User queries                                              │
│  - Meal queries                                              │
│  - Transaction queries                                       │
│  - Meal rate queries                                         │
│  - Relationship management                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                     DATABASE LAYER                            │
│                      (SQLite Database)                       │
│  - users table                                               │
│  - meals table                                               │
│  - transactions table                                        │
│  - meal_rates table                                          │
└─────────────────────────────────────────────────────────────┘
"""

# ============================================================================
# FILE STRUCTURE & RESPONSIBILITIES
# ============================================================================

"""
hostel_meal_system/
│
├── config.py                    Configuration Management
│   └─ Database URI, Secret Key, Session Settings
│
├── models.py                    Data Models & Business Logic
│   ├─ User model
│   ├─ Meal model
│   ├─ Transaction model
│   ├─ MealRate model
│   └─ Helper functions (get_current_meal_rate, get_hostel_stats)
│
├── app.py                       Main Flask Application & Routes
│   ├─ App factory
│   ├─ Decorators (@login_required, @manager_required)
│   ├─ Authentication routes
│   ├─ View routes (dashboard, manager panel)
│   └─ API endpoints
│
├── requirements.txt             Python Dependencies
│
├── init_demo.py                Demo Data Initialization Script
│
├── setup.py                     Automated Setup Script
│
├── templates/                   HTML Templates with Tailwind CSS
│   ├─ base.html               Base template with navbar
│   ├─ login.html              Login form
│   ├─ register.html           Registration form
│   ├─ dashboard.html          Member & Manager dashboard
│   └─ manager.html            Manager control panel
│
├── static/                      Static Assets (CSS, JS, Images)
│   └─ (Custom CSS if needed)
│
├── hostel_meals.db             SQLite Database (auto-created)
│
├── README.md                    Comprehensive Documentation
├── QUICKSTART.md               Quick Start Guide
├── API_DOCUMENTATION.md        API Reference
├── DATABASE_SCHEMA.md          Database Documentation
└── .gitignore                  Git Ignore File
"""

# ============================================================================
# TECHNOLOGY STACK JUSTIFICATION
# ============================================================================

"""
Why These Technologies?

1. Flask (Backend)
   ✓ Lightweight and easy to learn
   ✓ Perfect for college projects
   ✓ Excellent documentation
   ✓ Flexible and extensible
   ✓ Easy to debug and understand
   
   Alternatives considered: Django (too heavy), FastAPI (overkill)

2. SQLite (Database)
   ✓ Zero configuration
   ✓ File-based (easy backup)
   ✓ Perfect for small to medium projects
   ✓ No separate server needed
   ✓ Good for education/learning
   
   When to upgrade to PostgreSQL:
   - Concurrent users > 50
   - Required data persistence across restarts
   - Complex transactions needed
   - Production deployment required

3. Tailwind CSS (Frontend)
   ✓ Utility-first framework
   ✓ Minimal setup via CDN
   ✓ Professional looking UI quickly
   ✓ Responsive design out of box
   ✓ No npm/build process needed
   
   Why not Bootstrap? Tailwind is more modern and flexible

4. SQLAlchemy ORM
   ✓ Type-safe database operations
   ✓ Prevents SQL injection
   ✓ Easy relationship management
   ✓ Built-in data validation
   ✓ Works with any SQL database

5. Session-Based Authentication
   ✓ Simple to implement
   ✓ Suitable for web apps
   ✓ Good security with proper setup
   ✓ No JWT complexity needed
   
   For mobile apps: Would use JWT or OAuth instead
"""

# ============================================================================
# KEY FEATURES & IMPLEMENTATION
# ============================================================================

"""
Feature 1: Role-Based Access Control
───────────────────────────────────────
Implementation:
  - User.role field ('member' or 'manager')
  - @login_required decorator (requires authentication)
  - @manager_required decorator (requires manager role)
  - Context processor injects current_user to templates

Member Features:
  ✓ View-only dashboard
  ✓ See all members' data
  ✓ Check personal balance
  ✗ Cannot edit any data

Manager Features:
  ✓ All member permissions
  ✓ Add/update daily meals
  ✓ Manage member money
  ✓ Set meal rates
  ✓ View all transactions
  ✗ Cannot delete records (audit trail)

---

Feature 2: Automatic Financial Calculations
────────────────────────────────────────────
Calculation Chain:
  1. Get total meals from meals table
  2. Get current meal rate from meal_rates table
  3. Calculate cost = total_meals × meal_rate
  4. Get deposits from transactions (type='deposit')
  5. Get withdrawals from transactions (type='withdrawal')
  6. Calculate balance = deposits - cost - withdrawals

Implementation in models.py:
  - User.get_total_meals()
  - User.get_total_cost()
  - User.get_balance()
  - get_current_meal_rate()
  - get_hostel_stats()

Real-time Updates:
  - Dashboard shows latest data
  - Calculations based on most current meal rate
  - No batch processing needed

---

Feature 3: Session Management
──────────────────────────────
Implementation:
  - Flask session stores user_id
  - Session timeout: 7 days
  - Auto-refresh on each request
  - Secure password hashing (Werkzeug)

Security:
  - Passwords never stored in plain text
  - check_password() for verification
  - Session cookie (HttpOnly recommended in production)
  - CSRF protection on forms

---

Feature 4: Data Integrity
──────────────────────────
Constraints:
  - UNIQUE(users.email) - No duplicate emails
  - UNIQUE(meals.user_id, meals.date) - One meal per user per day
  - FOREIGN KEY integrity
  - NOT NULL constraints on critical fields

Validation:
  - Email validation on registration
  - Password confirmation matching
  - Amount validation (> 0)
  - Role validation ('member' or 'manager')
  - Date validation

---

Feature 5: Dashboard Data Aggregation
──────────────────────────────────────
For Dashboard Display:
  1. Get all active members
  2. For current month:
     - Fetch all meals per member per date
     - Calculate totals and costs
     - Get balances
  3. Calculate hostel statistics
  4. Format for table display

Performance:
  - Single query per member for meals
  - Use relationships to avoid N+1 queries
  - Cache calculations during request
"""

# ============================================================================
# BUSINESS LOGIC & CALCULATIONS
# ============================================================================

"""
Core Formula 1: Meal Rate
═════════════════════════

Definition:
  Meal Rate = Price per meal (e.g., ৳50 per meal)
  
How it works:
  - Manager sets meal rate
  - Applies to ALL members
  - Can be changed anytime
  - New rate affects future calculations
  - Historical rates are preserved

Example:
  If meal rate = ৳50
  And member ate 10 meals
  Then cost = 10 × ৳50 = ৳500

---

Core Formula 2: Member Cost
═══════════════════════════

Definition:
  Member Cost = Total Meals × Current Meal Rate

Calculation:
  1. Sum all meal_count values for user (up to today)
  2. Get current meal rate
  3. Multiply: total_meals × meal_rate

Example:
  User's meals:
    2026-04-20: 2.5 meals
    2026-04-21: 2.0 meals
    2026-04-22: 3.0 meals
    Total: 7.5 meals
  
  Current meal rate: ৳50
  Cost = 7.5 × ৳50 = ৳375

---

Core Formula 3: Member Balance
═══════════════════════════════

Definition:
  Balance = Deposits - Cost - Withdrawals

Where:
  - Deposits = Sum of all positive transactions
  - Cost = Calculated as above
  - Withdrawals = Sum of withdrawal transactions

Example:
  Deposits:      ৳5000
  - Cost:        ৳375
  - Withdrawal:  ৳200
  ──────────────────────
  Balance:       ৳4425

Interpretation:
  - Positive = Member has money remaining
  - Negative = Member owes money to hostel
  - Zero = Exact balance (rare)

---

Core Formula 4: Hostel Statistics
═════════════════════════════════

Total Meals:
  Sum of all meal_count values from all members

Meal Rate:
  Current meal rate (latest by effective_date)

Total Cost:
  Total Meals × Meal Rate
  Represents total hostel expense

Total Deposited:
  Sum of all deposit transactions

Example Calculation:
  Member A: 7.5 meals
  Member B: 8.0 meals
  Member C: 6.5 meals
  ─────────────────────
  Total: 22 meals
  
  Rate: ৳50
  Total Cost = 22 × ৳50 = ৳1100
"""

# ============================================================================
# USER WORKFLOWS
# ============================================================================

"""
Workflow 1: Member Login & View Dashboard
──────────────────────────────────────────

1. User lands on home page
2. Redirects to login (if not authenticated)
3. Member enters email & password
4. System validates credentials
5. Session created (user_id stored)
6. Redirects to dashboard
7. Dashboard displays:
   - All members' data in table format
   - Daily meal counts by date
   - Total meals, costs, balances for each member
   - Hostel-wide statistics at bottom
8. Member can only view (no edit buttons)
9. Member can logout (clears session)

---

Workflow 2: Manager Setting Up System
─────────────────────────────────────

1. Manager logs in
2. Navigates to Manager Panel
3. Sets Initial Meal Rate:
   - Enters rate (e.g., ৳50)
   - Optional description
   - Clicks "Set Rate"
4. System creates MealRate record
5. Adds Initial Deposits:
   - For each member, clicks "Add Money"
   - Enters amount (e.g., ৳5000)
   - Selects "Deposit"
   - Adds description
   - Clicks "Save"
6. System creates Transaction records
7. Balances calculated immediately

---

Workflow 3: Manager Daily Meal Update
──────────────────────────────────────

1. Manager goes to Manager Panel
2. For each member:
   - Enters meal count for today
   - Clicks "Update Meal"
3. System creates/updates Meal record
4. Member's calculations update:
   - New total meals
   - New cost (meals × rate)
   - New balance (deposits - cost)
5. All visible in dashboard immediately

---

Workflow 4: Manager Financial Transaction
─────────────────────────────────────────

1. Manager opens Manager Panel
2. Clicks "Add Money" for member
3. Modal dialog appears with options:
   - Transaction Type: Deposit or Withdrawal
   - Amount: Enter rupees
   - Description: Why this transaction
4. Manager fills in and clicks "Save"
5. System creates Transaction record
6. Member's balance updated
   - If deposit: increases
   - If withdrawal: decreases
7. Transaction visible in history

---

Workflow 5: Resolving Negative Balance
──────────────────────────────────────

If member has negative balance (owes money):

1. Manager identifies negative balance
2. Manager checks transaction history
3. Options:
   a. Member adds money (deposits)
   b. Manager adjusts meals down (if data error)
   c. Manager withdraws owed amount
4. Balance becomes positive
5. Issues resolved

---

Workflow 6: Month-End Settlement
────────────────────────────────

At month end:

1. Manager reviews all balances
2. Members settle outstanding amounts (deposits)
3. Manager records deposits
4. All balances become positive (or reset)
5. Manager updates meal rate for new month (optional)
6. New month begins

Next month:
1. New manager can be assigned
2. Or same manager continues
3. System continues tracking
"""

# ============================================================================
# SECURITY CONSIDERATIONS
# ============================================================================

"""
Current Security Measures:
═════════════════════════

1. Authentication
   ✓ Password hashing (Werkzeug security)
   ✓ Session-based auth (user_id stored securely)
   ✓ Login required decorators

2. Authorization
   ✓ Role-based access control (member vs manager)
   ✓ Manager-only routes restricted
   ✓ Cannot bypass auth (all routes check)

3. Data Validation
   ✓ Email validation
   ✓ Password confirmation
   ✓ Amount validation (> 0)
   ✓ Type checking

4. Database
   ✓ SQLAlchemy prevents SQL injection
   ✓ Foreign key constraints
   ✓ Unique constraints

5. No Deletions
   ✓ Audit trail preserved
   ✓ All changes recorded
   ✓ Can't delete historical data

---

For Production Deployment:
═════════════════════════

BEFORE deploying to production:

1. Change SECRET_KEY
   config.py: SECRET_KEY = 'your-unique-secret-key'

2. Enable HTTPS
   Use Let's Encrypt or paid SSL certificate
   Update Flask to use SSL

3. Set DEBUG = False
   Prevent error pages from exposing code

4. Move to PostgreSQL
   Better for concurrent users
   More reliable than SQLite

5. Add CSRF Protection
   Use Flask-WTF for forms
   Add csrf_token to all forms

6. Rate Limiting
   Prevent brute force attacks
   Implement using Flask-Limiter

7. Input Sanitization
   Validate all user inputs
   Use Werkzeug.security for strings

8. Logging
   Log all authentication attempts
   Log all financial transactions
   Monitor for suspicious activity

9. Backup Strategy
   Daily database backups
   Offsite storage
   Test restores regularly

10. Use Environment Variables
    Load sensitive data from .env file
    Never commit secrets to git
"""

# ============================================================================
# PERFORMANCE & SCALABILITY
# ============================================================================

"""
Current Performance Characteristics:
═════════════════════════════════════

Suitable for:
  ✓ Hostels with 100-500 members
  ✓ College projects
  ✓ Single department deployment
  ✓ Educational purposes

Limitations:
  ✗ SQLite has connection limits
  ✗ Not suitable for 1000+ concurrent users
  ✗ Single file database not ideal for clusters
  ✗ No horizontal scaling possible

Database Performance:
  - User queries: O(1) with email index
  - Meal queries: O(log n) with user_id index
  - Transaction queries: O(log n)
  - Full table scans: O(n) - acceptable for hostel scale

---

Scaling Strategies:
═══════════════════

For 500 members:
  - Keep using SQLite
  - Add indexes as needed
  - Regular backups

For 500-2000 members:
  - Migrate to PostgreSQL
  - Add query caching
  - Implement pagination

For 2000+ members:
  - Use PostgreSQL
  - Implement Redis caching
  - Load balancing with multiple app instances
  - Separate read/write databases

---

Optimization Opportunities:
════════════════════════════

1. Query Optimization
   - Use select_related for foreign keys
   - Use exists() for large joins
   - Batch queries where possible

2. Caching
   - Cache meal rates (change rarely)
   - Cache hostel statistics
   - Use Redis for session storage

3. Async Processing
   - Use Celery for heavy calculations
   - Process reports asynchronously
   - Send emails in background

4. Database Indexing
   - Add composite indexes
   - Analyze query plans
   - Remove unused indexes
"""

# ============================================================================
# DEPLOYMENT OPTIONS
# ============================================================================

"""
Deployment Option 1: Local / College Network
═════════════════════════════════════════════

Setup:
  1. Install Python on server machine
  2. Install dependencies
  3. Run app.py
  4. Access via http://server-ip:5000

Pros:
  ✓ Simple setup
  ✓ No external services
  ✓ Good for LAN

Cons:
  ✗ Not accessible externally
  ✗ Manual restart required
  ✗ No HTTPS

---

Deployment Option 2: Heroku
════════════════════════════

Setup:
  1. Create Heroku account
  2. Install Heroku CLI
  3. Create app on Heroku
  4. Add Procfile with: web: gunicorn app:create_app()
  5. Push code to Heroku

Pros:
  ✓ Free tier available
  ✓ Automatic HTTPS
  ✓ Auto-scaling
  ✓ Easy deployment

Cons:
  ✗ Database restarts daily (free tier)
  ✗ Limited free hours
  ✗ Paid plans required for production

---

Deployment Option 3: AWS / Digital Ocean
═════════════════════════════════════════

Setup:
  1. Create VPS instance
  2. Install dependencies
  3. Setup Nginx reverse proxy
  4. Use Gunicorn as app server
  5. Use Supervisor to manage process
  6. Setup SSL with Let's Encrypt
  7. Configure PostgreSQL database

Pros:
  ✓ Full control
  ✓ Scalable
  ✓ Good performance
  ✓ Production-ready

Cons:
  ✗ More complex setup
  ✗ Requires Linux knowledge
  ✗ Manual maintenance

---

Recommended for College Project:
─────────────────────────────────
Use Option 1 (Local) for:
  - Learning and development
  - Classroom deployment
  - College LAN only

Use Option 2 (Heroku) for:
  - Public demo
  - Portfolio showcase
  - Easy sharing

Use Option 3 (AWS/DO) for:
  - Real production
  - Multiple campuses
  - Enterprise use
"""

# ============================================================================
# FUTURE ENHANCEMENTS
# ============================================================================

"""
Potential Features to Add:

1. Notifications
   - Email notifications for balance alerts
   - SMS alerts for important updates
   - In-app notifications

2. Reports
   - PDF financial reports
   - Excel export
   - Monthly settlement reports
   - Member statements

3. Advanced Features
   - Guest meal tracking
   - Meal preferences
   - Complaint system
   - Feedback forms

4. Multi-hostel Support
   - Support multiple hostels
   - Manager per hostel
   - Inter-hostel transfers

5. Mobile App
   - React Native or Flutter
   - Member app (view only)
   - Manager app (full control)

6. Analytics
   - Charts and graphs
   - Spending trends
   - Member demographics
   - Meal consumption patterns

7. API
   - REST API for external integrations
   - Third-party app support
   - Mobile app backend

8. Automation
   - Automatic settlement at month-end
   - Recurring payments
   - Budget alerts
   - Automatic rate adjustments
"""

# ============================================================================
# TROUBLESHOOTING GUIDE
# ============================================================================

"""
Common Issues & Solutions:

Issue: "sqlite3.OperationalError: database is locked"
─────────────────────────────────────────────────────
Cause: Multiple connections to SQLite
Solution:
  - Restart Flask app
  - Close other connections
  - Switch to PostgreSQL if recurring

---

Issue: "ModuleNotFoundError: No module named 'flask'"
─────────────────────────────────────────────────────
Cause: Dependencies not installed
Solution:
  - pip install -r requirements.txt
  - Verify virtual environment is active

---

Issue: "Port 5000 already in use"
────────────────────────────────
Cause: Another app on port 5000
Solution:
  - Change port: app.run(port=5001)
  - Or kill process: lsof -ti:5000 | xargs kill

---

Issue: "Login fails with correct credentials"
──────────────────────────────────────────────
Cause: User account issue or password hash problem
Solution:
  - Verify user exists: python
    from models import User
    User.query.filter_by(email='test@example.com').first()
  - Re-create demo data: python init_demo.py

---

Issue: "Balance calculation wrong"
──────────────────────────────────
Cause: Query or calculation logic error
Solution:
  - Check meal rate: get_current_meal_rate()
  - Verify meals in database: SELECT * FROM meals
  - Check transactions: SELECT * FROM transactions
  - Review calculation in models.py:get_balance()
"""

# ============================================================================
# LEARNING OUTCOMES
# ============================================================================

"""
Skills Learned from This Project:

1. Web Development
   ✓ Flask basics (routes, templates, sessions)
   ✓ HTML/CSS/JavaScript
   ✓ HTTP request/response cycle
   ✓ Form handling and validation

2. Database Design
   ✓ Database schema design
   ✓ Entity relationships
   ✓ Normalization concepts
   ✓ SQL queries (via SQLAlchemy)

3. Backend Development
   ✓ RESTful API design
   ✓ Authentication & authorization
   ✓ Business logic implementation
   ✓ Data aggregation and calculations

4. Security
   ✓ Password hashing
   ✓ Session management
   ✓ Input validation
   ✓ OWASP principles

5. Software Engineering
   ✓ Project structure & organization
   ✓ Version control (Git)
   ✓ Documentation
   ✓ Debugging & troubleshooting

6. UI/UX
   ✓ Responsive design
   ✓ User experience design
   ✓ Accessibility considerations
   ✓ Modern CSS frameworks

Recommended Next Steps:
  1. Add more features (notifications, reports)
  2. Deploy to cloud (Heroku, AWS)
  3. Build mobile app
  4. Migrate to Django for larger projects
  5. Learn advanced concepts (Redis, Celery, microservices)
"""
