# 🚀 QUICK START GUIDE

## 5-Minute Setup

### Option 1: Automated Setup (Recommended)

#### Windows:
```bash
python setup.py
```

#### Linux/Mac:
```bash
python3 setup.py
```

This will:
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Initialize demo database with sample data
- ✅ Display credentials

### Option 2: Manual Setup

#### Step 1: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Initialize Demo Data
```bash
python init_demo.py
```

#### Step 4: Run Application
```bash
python app.py
```

## Access the Application

1. Open browser: **http://localhost:5000**
2. Login with demo credentials (see below)

## 🔐 Default Demo Credentials

### Manager (Admin)
- **Email**: `manager@example.com`
- **Password**: `password`
- **Permissions**: Full access to manager panel

### Members
- **Mehedi Hasan** → mehedi@example.com / password
- **Arefin Ahmed** → arefin@example.com / password
- **Ali Hassan** → ali@example.com / password
- **Karim Khan** → karim@example.com / password

**Permission**: View-only access to dashboard

---

## 📚 Features Overview

### 👥 Member Features
- ✅ View dashboard with all members
- ✅ Check daily meal counts
- ✅ View personal statistics
- ✅ Check account balance
- ❌ Cannot edit any data

### 🔧 Manager Features
- ✅ Add daily meal counts for members
- ✅ Add/withdraw money for members
- ✅ Set meal rates dynamically
- ✅ View financial reports
- ✅ Manage all transactions
- ✅ View member balances

---

## 📊 Sample Data

The demo automatically creates:
- 1 Manager account
- 4 Member accounts
- ৳5000 initial deposit for each member
- 5 days of sample meal data
- Meal rate: ৳50 per meal

---

## 💡 Common Tasks

### Change Meal Rate (Manager)
1. Login as manager
2. Go to "Manager Panel"
3. Enter new rate in "Set Meal Rate"
4. Click "Set Rate"

### Add Money for Member (Manager)
1. Go to "Manager Panel"
2. Click "Add Money" next to member name
3. Select transaction type (Deposit/Withdrawal)
4. Enter amount
5. Click "Save"

### Update Daily Meals (Manager)
1. Go to "Manager Panel"
2. Update meal count in the table
3. Click "Update Meal"

### View Statistics (Any User)
1. Login
2. Go to "Dashboard"
3. View the table with all member data

---

## 🔧 Configuration

Edit `config.py` to change:
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///hostel_meals.db'  # Database location
SECRET_KEY = 'change-this-key'  # Change for production!
PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # Session duration
DEBUG = True  # Set to False for production
```

---

## 🆘 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'flask'"
**Solution**: 
```bash
pip install -r requirements.txt
```

### Error: "Port 5000 already in use"
**Solution**: Edit `app.py` and change port:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Error: "database is locked"
**Solution**: Close other connections and try again. This is a SQLite limitation.

### Need to reset database?
```bash
# Delete the database
rm hostel_meals.db  # or del hostel_meals.db on Windows

# Reinitialize
python init_demo.py
```

---

## 📁 File Structure

```
hostel_meal_system/
├── app.py                 # Main Flask app
├── config.py              # Configuration
├── models.py              # Database models
├── init_demo.py           # Demo data generator
├── setup.py               # Setup script
├── requirements.txt       # Dependencies
├── README.md              # Full documentation
├── QUICKSTART.md          # This file
├── hostel_meals.db        # SQLite database (created)
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── manager.html
└── static/                # CSS, JavaScript, images
```

---

## 🎯 Next Steps

1. **Explore the Dashboard**: Login as a member and view all data
2. **Try Manager Panel**: Login as manager and update meals/money
3. **Test Calculations**: Check how meal rate affects costs
4. **Create Custom Data**: Register new users and add transactions

---

## ✨ Key Features Explained

### Meal Rate Calculation
```
Meal Rate = Total Expense / Total Meals
```
- Automatically calculated by the system
- Manager can update at any time
- Applied to all members

### Cost Calculation
```
User's Cost = Total Meals × Meal Rate
```
- Updated in real-time
- Shown in dashboard

### Balance Calculation
```
Balance = Deposits - Cost - Withdrawals
```
- Updated instantly
- Negative balance shows in red
- Positive balance shows in green

---

## 📞 Support

For issues or questions:
1. Check README.md for detailed documentation
2. Review QUICKSTART.md (this file)
3. Check application logs in terminal

---

**Happy Hostel Managing! 🏠**
