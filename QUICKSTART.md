# 🚀 QUICK START GUIDE

## ⚡ 5-Minute Setup

### Automated Setup (Recommended)
Run the automated setup script to set up virtual environment, dependencies, and demo data:

#### Windows:
```bash
python setup.py
```

#### Linux/Mac:
```bash
python3 setup.py
```

---

### Manual Setup

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

---

## 🌐 Accessing the Application

Open your browser at: **http://localhost:5000** (or http://127.0.0.1:5000)

---

## 🔐 Default Demo Credentials

### Manager (Admin)
- **Email**: `manager@example.com`
- **Password**: `password`
- **Permissions**: Full management access (Meal locks, Menu, Deposits, Expenses, Role Transfer)

### Members
- **Mehedi Hasan** → `mehedi@example.com` / `password`
- **Arefin Ahmed** → `arefin@example.com` / `password`
- **Ali Hassan** → `ali@example.com` / `password`
- **Karim Khan** → `karim@example.com` / `password`

---

## 🛠️ Main Features & Navigation

1. **📊 Dashboard**: Real-time member attendance totals, monthly filters, running balances, and hostel statistics.
2. **🍽️ Meal Status**: Toggle daily Breakfast (0.5), Lunch (1.0), and Dinner (1.0) status. Managers can lock meal slots.
3. **📋 Today's Meals**: Live breakdown of today's attendance and meal totals.
4. **🍲 Today's Menu**: Weekly breakfast, lunch, and dinner menu planner.
5. **💳 Transactions**: Complete expense log and member deposit/withdrawal history audit modal.
6. **👥 Member List**: Unique auto-generated member IDs and manager role transfer tool.
7. **🕰️ History**: Access past month sheets and record archives.
8. **💬 Real-Time Chat**: Live chat room with audio notifications, `@mentions`, replies, custom avatars, and background SSE notifications.

---

## 🆘 Troubleshooting

### Error: `ModuleNotFoundError: No module named 'flask'`
Ensure your virtual environment is activated and run:
```bash
pip install -r requirements.txt
```

### Error: `Port 5000 already in use`
Change the port at the bottom of `app.py`:
```python
app.run(debug=True, host='127.0.0.1', port=5001)
```

### How to reset database completely:
```bash
# Delete existing database file
# Windows:
del instance\hostel_meals.db
# Linux/Mac:
rm instance/hostel_meals.db

# Re-run demo initializer
python init_demo.py
```
