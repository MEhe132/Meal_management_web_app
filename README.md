# 🏠 Hostel Meal Management System

A complete web application for managing hostel meals, finances, and member accounts. Built with Flask, SQLite, and Tailwind CSS.

## Features

### 👥 For Members (Normal Users)
- ✅ Login with email and password
- ✅ View dashboard with all members' meal data
- ✅ See daily meal counts in a beautiful table
- ✅ View personal meal statistics
- ✅ Check account balance
- ✅ View personal cost calculations
- ❌ **No edit permissions** (read-only access)

### 🔧 For Manager (Admin)
- ✅ Manage all features
- ✅ Add daily meal entries for each member
- ✅ Add/withdraw money for members
- ✅ Set and adjust meal rates
- ✅ View all transactions and history
- ✅ Access complete financial analytics
- ✅ View member balances and statistics

### 📊 Core Features
- **Dashboard**: Professional table UI showing all members
- **Meal Tracking**: Daily meal counts with automatic totals
- **Financial Management**: Deposit/withdrawal transactions
- **Rate Calculation**: Dynamic meal rate and cost calculations
- **Session-based Authentication**: Secure login system
- **Role-based Access Control**: Member vs Manager permissions

## Business Logic

```
Meal Rate = Total Expense / Total Meals
Each User's Cost = Total Meals × Meal Rate
Balance = Deposited Money - Total Cost - Withdrawals
```

## Tech Stack

- **Backend**: Flask 2.3.3
- **Database**: SQLite
- **Frontend**: HTML + Tailwind CSS + Vanilla JavaScript
- **ORM**: SQLAlchemy
- **Authentication**: Session-based with password hashing

## Project Structure

```
hostel_meal_system/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── hostel_meals.db        # SQLite database (created on first run)
├── templates/
│   ├── base.html          # Base template with navbar
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── dashboard.html     # Member/Manager dashboard
│   └── manager.html       # Manager control panel
└── static/                # Static files (CSS, JS, images)
```

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Step 1: Clone or Download
Navigate to the project directory:
```bash
cd hostel_meal_system
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

The application will start at `http://localhost:5000`

## First Time Setup

### Create Demo Accounts

1. **Go to Registration Page**: http://localhost:5000/register

2. **Create a Manager Account**:
   - Name: Manager User
   - Email: `manager@example.com`
   - Password: `password`
   - Role: Manager (Admin)

3. **Create Member Accounts** (at least 2):
   - Name: Member 1
   - Email: `member1@example.com`
   - Password: `password`
   - Role: Member

   - Name: Member 2
   - Email: `member2@example.com`
   - Password: `password`
   - Role: Member

### Initialize System

1. **Login as Manager**: `manager@example.com` / `password`
2. **Go to Manager Panel**: Click "Manager Panel" in navbar
3. **Set Initial Meal Rate**: Enter meal rate (e.g., 50) in the "Set Meal Rate" section
4. **Add Member Money**: Use "Add Money" button to deposit initial funds for each member
5. **Add Today's Meals**: Update meal counts for each member in the member management table

## Usage

### For Members
1. Login with member credentials
2. View the dashboard
3. See all members' meal counts and balances
4. Monitor your own statistics
5. Cannot edit any data

### For Manager
1. Login with manager credentials
2. Use **Dashboard** to view member information
3. Use **Manager Panel** to:
   - Update daily meal counts
   - Add deposits or withdrawals
   - Set meal rates
   - View transaction history
4. Changes are reflected immediately in the dashboard

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'member',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Meals Table
```sql
CREATE TABLE meals (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    meal_count FLOAT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);
```

### Transactions Table
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    amount FLOAT NOT NULL,
    type VARCHAR(20) NOT NULL,
    description VARCHAR(255),
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Meal Rates Table
```sql
CREATE TABLE meal_rates (
    id INTEGER PRIMARY KEY,
    rate FLOAT NOT NULL,
    effective_date DATE NOT NULL,
    description VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

### Views
- `GET /` - Redirect to dashboard or login
- `GET /dashboard` - Main dashboard (Members & Manager)
- `GET /manager` - Manager control panel

### API Routes (Manager Only)
- `POST /api/add-meal` - Add/update meal entry
- `POST /api/add-money` - Add transaction
- `POST /api/set-meal-rate` - Set meal rate

## Configuration

Edit `config.py` to customize:
- Database location: `SQLALCHEMY_DATABASE_URI`
- Session lifetime: `PERMANENT_SESSION_LIFETIME`
- Secret key: `SECRET_KEY` (change for production!)

```python
# config.py
SQLALCHEMY_DATABASE_URI = 'sqlite:///hostel_meals.db'
SECRET_KEY = 'your-secret-key-change-in-production'
PERMANENT_SESSION_LIFETIME = timedelta(days=7)
```

## Security Notes

⚠️ **For Production Use**:
1. Change `SECRET_KEY` in `config.py`
2. Use environment variables for sensitive data
3. Enable HTTPS
4. Use PostgreSQL instead of SQLite for better concurrency
5. Add CSRF protection
6. Implement rate limiting
7. Add logging and monitoring

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'flask'"
**Solution**: Ensure virtual environment is activated and dependencies are installed
```bash
pip install -r requirements.txt
```

### Issue: "sqlite3.OperationalError: database is locked"
**Solution**: This is normal. Close other connections or wait a moment before retrying.

### Issue: Port 5000 already in use
**Solution**: Change the port in app.py
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use port 5001
```

## Future Enhancements

- [ ] SMS notifications for members
- [ ] Excel export for financial reports
- [ ] Monthly settlement system
- [ ] Member payment QR codes
- [ ] Automated monthly reset
- [ ] Data visualization charts
- [ ] Meal preference tracking
- [ ] Guest meal tracking
- [ ] Multi-month history reports
- [ ] Mobile app

## Author

Mehedi & Arefin - College Project 2026

## License

MIT License - Free to use for educational purposes

---

**Made with ❤️ for hostel management**
