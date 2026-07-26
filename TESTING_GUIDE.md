"""
TESTING GUIDE & QA CHECKLIST
Hostel Meal Management System
"""

# ============================================================================
# TESTING OVERVIEW
# ============================================================================

"""
Testing Strategy:

1. Manual Testing (Recommended for college project)
   - User workflow testing
   - UI/UX testing
   - Edge case testing
   - Cross-browser testing

2. Automated Testing (Optional for production)
   - Unit tests (pytest)
   - Integration tests
   - API tests

3. Load Testing
   - Test with multiple concurrent users
   - Monitor performance
   - Identify bottlenecks

4. Security Testing
   - SQL injection attempts
   - XSS attack prevention
   - Session hijacking prevention
   - Role-based access control

This guide focuses on manual testing (practical for college project).
"""

# ============================================================================
# TEST ENVIRONMENT SETUP
# ============================================================================

"""
Before Testing:

1. Fresh Database
   - Delete hostel_meals.db if exists
   - Run: python init_demo.py
   - Creates demo accounts with sample data

2. Test Accounts
   Manager:
     Email: manager@example.com
     Password: password
     Role: Manager
   
   Members:
     Email: mehedi@example.com / password
     Email: arefin@example.com / password
     Email: ali@example.com / password
     Email: karim@example.com / password

3. Run App
   python app.py
   
   Expected:
   WARNING in app.runserver (werkzeug): This is a development server...
   Running on http://127.0.0.1:5900/

4. Browser
   Use: Chrome, Firefox, Safari, or Edge
   Open: http://localhost:5900
"""

# ============================================================================
# TEST CASE 1: AUTHENTICATION
# ============================================================================

"""
TEST 1.1: Member Login
───────────────────────

Steps:
  1. Go to http://localhost:5900
  2. Should redirect to /login
  3. See login form
  4. Enter email: mehedi@example.com
  5. Enter password: password
  6. Click "Sign In"

Expected Results:
  ✓ Redirects to dashboard
  ✓ Shows "Welcome back, Mehedi Hasan!" message
  ✓ User name displayed in navbar
  ✓ "Member" role shown if applicable
  ✓ Session cookie set in browser

---

TEST 1.2: Manager Login
───────────────────────

Steps:
  1. Logout if logged in
  2. Go to login page
  3. Enter email: manager@example.com
  4. Enter password: password
  5. Click "Sign In"

Expected Results:
  ✓ Redirects to dashboard
  ✓ Shows "Manager" badge in navbar
  ✓ Manager Panel link appears in navbar
  ✓ Can access both Dashboard and Manager Panel

---

TEST 1.3: Invalid Login - Wrong Password
─────────────────────────────────────────

Steps:
  1. Go to login page
  2. Enter email: mehedi@example.com
  3. Enter password: wrongpassword
  4. Click "Sign In"

Expected Results:
  ✓ Stays on login page
  ✓ Shows error: "Invalid email or password"
  ✓ Form fields cleared
  ✓ No session created

---

TEST 1.4: Invalid Login - Non-existent Email
────────────────────────────────────────────

Steps:
  1. Go to login page
  2. Enter email: nonexistent@example.com
  3. Enter password: password
  4. Click "Sign In"

Expected Results:
  ✓ Stays on login page
  ✓ Shows error: "Invalid email or password"
  ✓ No session created

---

TEST 1.5: Empty Form Submission
──────────────────────────────

Steps:
  1. Go to login page
  2. Click "Sign In" without entering data

Expected Results:
  ✓ Browser validation prevents submission
  OR
  ✓ Shows error: "Email and password are required"

---

TEST 1.6: Member Registration
──────────────────────────────

Steps:
  1. Go to login page
  2. Click "Register here"
  3. Fill form:
     - Name: Test User
     - Email: testuser@example.com (unique)
     - Password: testpass123
     - Confirm: testpass123
     - Role: Member
  4. Click "Create Account"

Expected Results:
  ✓ Account created successfully
  ✓ Shows success message
  ✓ Redirects to login
  ✓ Can now login with new account

---

TEST 1.7: Registration - Duplicate Email
──────────────────────────────────────────

Steps:
  1. Try to register with email: mehedi@example.com
  2. Fill other fields
  3. Submit

Expected Results:
  ✓ Shows error: "Email already registered"
  ✓ Account not created
  ✓ Redirects back to register

---

TEST 1.8: Registration - Password Mismatch
───────────────────────────────────────────

Steps:
  1. Go to register page
  2. Enter password: password123
  3. Confirm password: different123
  4. Submit

Expected Results:
  ✓ Shows error: "Passwords do not match"
  ✓ Account not created

---

TEST 1.9: Logout
────────────────

Steps:
  1. Login as any user
  2. Click "Logout" button in navbar

Expected Results:
  ✓ Session cleared
  ✓ Redirects to login
  ✓ Shows message: "You have been logged out"
  ✓ Cannot access dashboard without re-login

---

TEST 1.10: Session Expiration
────────────────────────────

Steps:
  1. Login
  2. Wait > 7 days (or modify config)
  3. Try to access dashboard

Expected Results:
  ✓ Session expired
  ✓ Redirects to login
  ✓ Shows message: "Please log in first"
"""

# ============================================================================
# TEST CASE 2: MEMBER DASHBOARD
# ============================================================================

"""
TEST 2.1: Access Dashboard as Member
──────────────────────────────────────

Steps:
  1. Login as member (mehedi@example.com)
  2. Should be on dashboard

Expected Results:
  ✓ Dashboard displays
  ✓ Title: "Dashboard"
  ✓ Subtitle: "View hostel meal details"
  ✓ Shows statistics cards (Total Members, Total Meals, Rate, Cost)
  ✓ Members table displayed

---

TEST 2.2: Dashboard Data Accuracy
───────────────────────────────────

In the members table, check:
  1. All active members listed
  2. Daily meal columns show dates
  3. Meal counts match database
  4. Total meals calculated correctly
  5. Meal rate displayed
  6. Total cost = Total meals × Meal rate
  7. Balance = Deposits - Cost - Withdrawals

Steps:
  1. Verify with sample data:
     - 4 members: Mehedi, Arefin, Ali, Karim
     - Each has 5 meal entries (past 5 days)
     - Meal rate: ৳50
     - Each member: 5 days × (2.0 or 2.5) ≈ 10-12 meals
     - Cost ≈ 10×50 = ৳500
     - Each deposited: ৳5000
     - Balance ≈ ৳5000 - ৳500 = ৳4500

Expected Results:
  ✓ All calculations correct
  ✓ Numbers match database
  ✓ Formatting clean and readable

---

TEST 2.3: Member Cannot Edit Data
───────────────────────────────────

Expected Observations:
  ✓ No "Edit" buttons in table
  ✓ No input fields for meals
  ✓ No "Add Money" buttons
  ✓ Read-only interface

---

TEST 2.4: Member Cannot Access Manager Panel
─────────────────────────────────────────────

Steps:
  1. Login as member
  2. Try to access: http://localhost:5900/manager
  3. Or check if Manager Panel link appears in navbar

Expected Results:
  ✓ Manager Panel link NOT in navbar
  ✓ If try to access directly: redirected to dashboard
  ✓ Shows error: "You do not have permission"

---

TEST 2.5: Responsive Design - Mobile
──────────────────────────────────────

Steps:
  1. Login to dashboard
  2. Open Developer Tools (F12)
  3. Select mobile device (iPhone 12)
  4. Check layout

Expected Results:
  ✓ Table scrolls horizontally on mobile
  ✓ Text readable
  ✓ Buttons functional
  ✓ Navigation works
  ✓ No layout breaks
"""

# ============================================================================
# TEST CASE 3: MANAGER PANEL
# ============================================================================

"""
TEST 3.1: Access Manager Panel
────────────────────────────────

Steps:
  1. Login as manager
  2. Click "Manager Panel" in navbar
  3. Should see manager.html

Expected Results:
  ✓ Title: "Manager Panel"
  ✓ Subtitle: "Manage meals, finances, and system settings"
  ✓ Statistics cards displayed
  ✓ Members management table shown
  ✓ Set Meal Rate section visible

---

TEST 3.2: Set Meal Rate
────────────────────────

Steps:
  1. In "Set Meal Rate" section
  2. Enter rate: 60
  3. Enter description: "Increased rate"
  4. Click "Set Rate"

Expected Results:
  ✓ Success alert shown
  ✓ Meal rate in statistics updates to ৳60
  ✓ Dashboard recalculates all costs
  ✓ Can verify in database: meal_rates table

---

TEST 3.3: Update Daily Meals
────────────────────────────

Steps:
  1. In Members Management table
  2. For first member, update "Today Meals" field
  3. Enter: 3 meals
  4. Click "Update Meal"

Expected Results:
  ✓ Success alert shown
  ✓ Meal saved to database
  ✓ Member's total meals increased
  ✓ Member's cost recalculated
  ✓ Balance updated immediately

---

TEST 3.4: Add Deposit Transaction
──────────────────────────────────

Steps:
  1. In Members Management table
  2. Click "Add Money" button for a member
  3. Modal dialog opens
  4. Leave Transaction Type as "Deposit"
  5. Enter Amount: 1000
  6. Enter Description: "Additional payment"
  7. Click "Save"

Expected Results:
  ✓ Modal closes
  ✓ Success alert shown
  ✓ Member's balance increases by ৳1000
  ✓ Page refreshes
  ✓ Transaction visible in history section

---

TEST 3.5: Add Withdrawal Transaction
──────────────────────────────────────

Steps:
  1. Click "Add Money" for member
  2. Select Type: "Withdrawal"
  3. Enter Amount: 200
  4. Enter Description: "Service charge"
  5. Click "Save"

Expected Results:
  ✓ Modal closes
  ✓ Success alert shown
  ✓ Member's balance decreases by ৳200
  ✓ Page refreshes
  ✓ Transaction recorded correctly

---

TEST 3.6: Transaction History
──────────────────────────────

Expected Observations:
  ✓ Each member's recent transactions displayed
  ✓ Shows: Type (Deposit/Withdrawal)
  ✓ Shows: Amount with ৳ symbol
  ✓ Shows: Description (if provided)
  ✓ Maximum 5 recent transactions shown per member

---

TEST 3.7: Meal Rate Affects All Calculations
──────────────────────────────────────────────

Steps:
  1. Set meal rate to ৳50
  2. Check a member's cost: 10 meals × ৳50 = ৳500
  3. Set meal rate to ৳60
  4. Check same member's cost: 10 meals × ৳60 = ৳600
  5. Balance should also change

Expected Results:
  ✓ All calculations update with new rate
  ✓ Historical meals use new rate
  ✓ Hostel total cost updated
"""

# ============================================================================
# TEST CASE 4: CALCULATIONS & BUSINESS LOGIC
# ============================================================================

"""
TEST 4.1: Basic Calculation
─────────────────────────────

Setup:
  - Meal Rate: ৳50
  - Member: Mehedi
  - Initial Deposit: ৳5000
  
Test Data:
  Meals: 10 total
  Cost = 10 × ৳50 = ৳500
  Balance = ৳5000 - ৳500 = ৳4500

Steps:
  1. View dashboard
  2. Check Mehedi's row

Expected Results:
  ✓ Total Meals: 10
  ✓ Rate: 50
  ✓ Total Cost: 500
  ✓ Balance: 4500

---

TEST 4.2: Calculation with Multiple Deposits
───────────────────────────────────────────────

Setup:
  - Member: Arefin
  - Initial Deposit: ৳5000
  - Add deposit: ৳1000
  - Total deposits: ৳6000
  - Total meals: 12
  - Cost: 12 × ৳50 = ৳600
  - Balance: ৳6000 - ৳600 = ৳5400

Steps:
  1. Add ৳1000 deposit for Arefin
  2. Check balance in dashboard

Expected Results:
  ✓ Balance correctly shows ৳5400

---

TEST 4.3: Negative Balance
────────────────────────

Setup:
  - Member: Ali
  - Deposit: ৳1000
  - Meals: 30 (high meals)
  - Cost: 30 × ৳50 = ৳1500
  - Balance: ৳1000 - ৳1500 = -৳500

Steps:
  1. Add 30 meals for Ali
  2. Check balance in dashboard

Expected Results:
  ✓ Balance shows: -500 (in red)
  ✓ Indicates member owes money

---

TEST 4.4: Zero Balance
────────────────────

Setup:
  - Member: Karim
  - Deposit: ৳1000
  - Meals: 20
  - Cost: 20 × ৳50 = ৳1000
  - Balance: ৳1000 - ৳1000 = ৳0

Steps:
  1. Setup meals to get exactly zero
  2. Check dashboard

Expected Results:
  ✓ Balance shows: 0
  ✓ No color highlighting (neutral)

---

TEST 4.5: Hostel Statistics
─────────────────────────────

Setup with demo data:
  4 members × 10-12 meals = ~44 meals total
  Rate: ৳50
  Total Cost: 44 × ৳50 = ৳2200

Steps:
  1. View dashboard
  2. Check statistics cards
  3. Check table footer row

Expected Results:
  ✓ Total Members: 4
  ✓ Total Meals: ~44
  ✓ Meal Rate: 50
  ✓ Total Cost: ~2200
  ✓ Footer row matches statistics
"""

# ============================================================================
# TEST CASE 5: DATA INTEGRITY & EDGE CASES
# ============================================================================

"""
TEST 5.1: One Meal Entry Per Day Per User
──────────────────────────────────────────

Setup:
  - Try to add meal for Mehedi on 2026-04-22

Steps:
  1. In manager panel, update meals for Mehedi
  2. Enter: 2.5
  3. Click "Update Meal"
  4. Try to add meal again
  5. Enter: 3.0
  6. Click "Update Meal"

Expected Results:
  ✓ First entry: 2.5 meals
  ✓ Second entry overwrites to: 3.0 meals
  ✓ No duplicate entries created
  ✓ Database has only one entry for that date

---

TEST 5.2: Decimal Meal Counts
──────────────────────────────

Steps:
  1. Add meal: 2.5 meals
  2. Add meal: 1.75 meals
  3. Total: 4.25 meals

Expected Results:
  ✓ Accepts decimal values
  ✓ Calculations correct: 4.25 × ৳50 = ৳212.5

---

TEST 5.3: Concurrent Updates
──────────────────────────────

Steps:
  1. Open dashboard in Chrome
  2. Open same dashboard in Firefox
  3. In Chrome: Add meal
  4. In Firefox: Add different meal for same member
  5. Refresh both

Expected Results:
  ✓ Both updates preserved
  ✓ No data loss
  ✓ Calculations correct

---

TEST 5.4: Empty Database Reset
────────────────────────────────

Steps:
  1. Delete hostel_meals.db file
  2. Restart Flask app
  3. Try to access http://localhost:5900

Expected Results:
  ✓ New database created automatically
  ✓ No errors
  ✓ Tables created
  ✓ Default meal rate initialized
  ✓ Can create new users

---

TEST 5.5: Large Numbers
────────────────────────

Steps:
  1. Add very large deposit: 999999
  2. Add very large meal count: 1000
  3. Check calculations

Expected Results:
  ✓ Calculations accurate
  ✓ No overflow errors
  ✓ Display formatting correct
  ✓ Numbers display with ৳ symbol

---

TEST 5.6: Special Characters in Description
──────────────────────────────────────────────

Steps:
  1. Add transaction with description: "Monthly fee (Oct) - 25% off!"
  2. Check database

Expected Results:
  ✓ Special characters preserved
  ✓ No SQL injection
  ✓ Displays correctly
"""

# ============================================================================
# TEST CASE 6: UI/UX & PRESENTATION
# ============================================================================

"""
TEST 6.1: Color Coding
───────────────────────

Check dashboard for color usage:

Positive Balance:
  ✓ Displayed in green
  ✓ Easy to identify

Negative Balance:
  ✓ Displayed in red
  ✓ Alerts user to debt

Neutral Elements:
  ✓ Gray/blue for normal data
  ✓ Good contrast for readability

---

TEST 6.2: Form Validation Messages
──────────────────────────────────

Steps:
  1. Try invalid email on register
  2. Try mismatched passwords
  3. Try empty fields
  4. Try duplicate email

Expected Results:
  ✓ Clear error messages
  ✓ User knows what went wrong
  ✓ Instructions provided
  ✓ Helpful feedback

---

TEST 6.3: Navbar Responsiveness
─────────────────────────────────

On Desktop:
  ✓ Horizontal navbar
  ✓ All links visible
  ✓ Logo on left, user on right
  ✓ Manager Panel link if manager

On Mobile:
  ✓ Navbar adapts
  ✓ Links still accessible
  ✓ No text overflow

---

TEST 6.4: Table Readability
─────────────────────────────

Expected:
  ✓ Clear column headers
  ✓ Alternating row colors (hover effect)
  ✓ Data aligned properly (text left, numbers right)
  ✓ Borders clear
  ✓ Font readable
  ✓ Sufficient spacing

---

TEST 6.5: Modal Dialog
───────────────────────

Steps:
  1. Click "Add Money" button
  2. Modal appears

Expected Results:
  ✓ Modal centered on screen
  ✓ Dark overlay behind
  ✓ Close button works
  ✓ Click outside closes modal
  ✓ Form fields functional
  ✓ Save/Cancel buttons work
"""

# ============================================================================
# TEST CASE 7: SECURITY
# ============================================================================

"""
TEST 7.1: SQL Injection Prevention
─────────────────────────────────

Steps:
  1. Try to login with email: ' OR '1'='1
  2. Try to login with password: ' OR '1'='1

Expected Results:
  ✓ Login fails
  ✓ Treated as literal strings
  ✓ No SQL injection
  ✓ SQLAlchemy prevents attack

---

TEST 7.2: Session Hijacking
─────────────────────────────

Setup:
  1. Login as member
  2. Note the session cookie

Steps:
  1. Clear browser data
  2. Try to manually set session cookie
  3. Access dashboard

Expected Results:
  ✓ Session invalid
  ✓ Redirects to login
  ✓ Cannot bypass authentication

---

TEST 7.3: Role-Based Access Control
───────────────────────────────────

Member trying to access manager routes:

Steps:
  1. Login as member
  2. Try to access: /manager
  3. Try to access: /api/add-meal
  4. Try to access: /api/add-money

Expected Results:
  ✓ Access denied
  ✓ Redirected to dashboard
  ✓ Error message shown
  ✓ Cannot perform manager operations

---

TEST 7.4: Password Security
────────────────────────────

Steps:
  1. Check database (don't do this in production!)
  2. Password should NOT be readable text
  3. Should be hash (40+ character random string)

Expected Results:
  ✓ Passwords hashed
  ✓ Different for each user
  ✓ Cannot reverse to plain text
  ✓ Werkzeug security used

---

TEST 7.5: No Data Deletion
──────────────────────────

Expected:
  ✓ No delete buttons in UI
  ✓ No way to delete meal entries
  ✓ No way to delete transactions
  ✓ Audit trail preserved
  ✓ Historical data permanent

---

TEST 7.6: HTTPS Readiness
──────────────────────────

Production checklist:
  ✓ Enable HTTPS (Let's Encrypt)
  ✓ Set secure cookies
  ✓ Set httponly flag
  ✓ Update SECRET_KEY
  ✓ Disable DEBUG mode
  ✓ Use strong passwords
"""

# ============================================================================
# PERFORMANCE TESTING
# ============================================================================

"""
TEST 8.1: Dashboard Load Time
──────────────────────────────

With demo data:
  - 4 members
  - 5 days of meal data
  - Some transactions

Expected:
  ✓ Page loads < 1 second
  ✓ Table renders quickly
  ✓ No lag or freezing

---

TEST 8.2: Large Dataset
────────────────────────

Setup:
  - Add 100 members (simulation)
  - Add 100 days of meal data
  - Add 1000 transactions

Test:
  1. Load dashboard
  2. Check load time
  3. Check memory usage
  4. Check CPU usage

Expected:
  ✓ Still responds < 2 seconds
  ✓ No significant lag
  ✓ Can handle college-scale data

---

TEST 8.3: Concurrent Users
────────────────────────────

Setup:
  - Open 10 browser tabs
  - All accessing dashboard/manager simultaneously

Expected:
  ✓ No crashes
  ✓ All respond correctly
  ✓ No data corruption
  ✓ May see "database locked" at scale (SQLite limitation)
"""

# ============================================================================
# REGRESSION TESTING
# ============================================================================

"""
After any code changes, run these tests:

1. Authentication Tests (1.1 - 1.10)
2. Dashboard Tests (2.1 - 2.5)
3. Manager Panel Tests (3.1 - 3.7)
4. Calculations Tests (4.1 - 4.5)
5. Data Integrity Tests (5.1 - 5.6)

Report any failures immediately.
"""

# ============================================================================
# TEST REPORT TEMPLATE
# ============================================================================

"""
PROJECT: Hostel Meal Management System
DATE: [Date]
TESTER: [Name]
BUILD VERSION: [Version]

TEST SUMMARY:
─────────────
Total Tests: 60+
Passed: ___
Failed: ___
Blocked: ___
Pass Rate: __%

CRITICAL ISSUES:
─────────────────
[List any critical bugs that block functionality]

MAJOR ISSUES:
─────────────
[List significant bugs but workarounds exist]

MINOR ISSUES:
─────────────
[List cosmetic or low-impact issues]

RECOMMENDATIONS:
─────────────────
[Recommendations for improvements]

SIGN-OFF:
─────────
Tested by: _______________
Approved by: ______________
Date: ____________________

NOTES:
──────
[Any additional notes or observations]
"""
