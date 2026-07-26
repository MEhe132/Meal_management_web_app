"""
Database Models for Hostel Meal Management System
"""
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

db = SQLAlchemy()

class User(db.Model):
    """User Model - for Members and Manager"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='member')  # 'member' or 'manager'
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)
    avatar_seed = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    meals = db.relationship('Meal', backref='user', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_manager(self):
        """Check if user is manager"""
        return self.role == 'manager'
    
    def get_total_deposited(self):
        """Get total deposited money"""
        deposited = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == self.id,
            Transaction.type == 'deposit'
        ).scalar() or 0
        
        return deposited
    
    def get_balance(self, current_date=None):
        """Calculate current balance (Continuous Rollover)"""
        if current_date is None:
            current_date = date.today()
        
        # Get total deposited money
        deposited = self.get_total_deposited()
        
        # Get total expenses across all months accurately
        expenses = self.get_total_cost(current_date)

        
        # Get withdrawals
        withdrawn = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == self.id,
            Transaction.type == 'withdrawal'
        ).scalar() or 0
        
        return deposited - expenses - withdrawn
    
    def get_total_meals(self, current_date=None):
        """Get total meals for user"""
        if current_date is None:
            current_date = date.today()
        
        total = db.session.query(db.func.sum(Meal.meal_count)).filter(
            Meal.user_id == self.id,
            Meal.date <= current_date
        ).scalar() or 0
        
        return total
    
    def get_monthly_meals(self, year, month):
        """Get total meals for user in a specific month"""
        total = db.session.query(db.func.sum(Meal.meal_count)).filter(
            Meal.user_id == self.id,
            db.extract('year', Meal.date) == year,
            db.extract('month', Meal.date) == month
        ).scalar() or 0
        return total
        
    def get_monthly_cost(self, year, month):
        """Get total cost for user in a specific month"""
        meal_rate = get_monthly_meal_rate(year, month)
        total_meals = self.get_monthly_meals(year, month)
        return total_meals * meal_rate if meal_rate > 0 else 0
        
    def get_total_cost(self, current_date=None):
        """Get total cost across all months by calculating month-by-month"""
        if current_date is None:
            current_date = date.today()
        
        # Find all distinct year-months for this user up to current_date
        months_query = db.session.query(
            db.extract('year', Meal.date).label('year'),
            db.extract('month', Meal.date).label('month')
        ).filter(
            Meal.user_id == self.id,
            Meal.date <= current_date
        ).distinct().all()
        
        total_cost = 0.0
        for row in months_query:
            # row.year and row.month might be returned as strings or ints depending on DB dialect
            y = int(row.year)
            m = int(row.month)
            total_cost += self.get_monthly_cost(y, m)
            
        return total_cost
    
    def __repr__(self):
        return f'<User {self.name}>'


class Meal(db.Model):
    """Meal Model - tracks daily meal counts"""
    __tablename__ = 'meals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    breakfast = db.Column(db.Boolean, default=False)
    lunch = db.Column(db.Boolean, default=False)
    dinner = db.Column(db.Boolean, default=False)
    meal_count = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', name='unique_user_date'),
        db.Index('idx_meals_date', 'date'),
        db.Index('idx_meals_user_date', 'user_id', 'date'),
    )
    
    def update_meal_count(self):
        """Update meal count based on breakfast, lunch, and dinner flags"""
        self.meal_count = (0.5 if self.breakfast else 0.0) + (1.0 if self.lunch else 0.0) + (1.0 if self.dinner else 0.0)
        
    def __repr__(self):
        return f'<Meal {self.user_id} - {self.date}: {self.meal_count} (B:{self.breakfast}, L:{self.lunch}, D:{self.dinner})>'


class Transaction(db.Model):
    """Transaction Model - tracks deposits and withdrawals"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'deposit' or 'withdrawal'
    description = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    __table_args__ = (
        db.Index('idx_transactions_user_type', 'user_id', 'type'),
        db.Index('idx_transactions_date', 'date'),
    )

    def __repr__(self):
        return f'<Transaction {self.user_id} - {self.type}: {self.amount}>'


class Expense(db.Model):
    """Expense Model - tracks hostel expenses for meal rate calculation"""
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    date = db.Column(db.DateTime, default=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationship
    user = db.relationship('User', backref='expenses')
    
    __table_args__ = (
        db.Index('idx_expenses_date', 'date'),
        db.Index('idx_expenses_user', 'user_id'),
    )

    def __repr__(self):
        return f'<Expense {self.amount} - {self.description}>'


class MealRate(db.Model):
    """Meal Rate Model - tracks the meal rate (rate per meal)"""
    __tablename__ = 'meal_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    rate = db.Column(db.Float, nullable=False)
    effective_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<MealRate {self.rate} - {self.effective_date}>'


class MealLock(db.Model):
    """Meal Lock Model - tracks locked meal times per date"""
    __tablename__ = 'meal_locks'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    breakfast_locked = db.Column(db.Boolean, default=False, nullable=False)
    lunch_locked = db.Column(db.Boolean, default=False, nullable=False)
    dinner_locked = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<MealLock {self.date} - B:{self.breakfast_locked}, L:{self.lunch_locked}, D:{self.dinner_locked}>'


class DailyMenu(db.Model):
    """Daily Menu Model - tracks the menu for each date"""
    __tablename__ = 'daily_menus'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    breakfast_menu = db.Column(db.String(255), default="", nullable=False)
    lunch_menu = db.Column(db.String(255), default="", nullable=False)
    dinner_menu = db.Column(db.String(255), default="", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<DailyMenu {self.date}>'


class ChatMessage(db.Model):
    """Chat Message Model - for real-time hostel chat"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    reply_to_id = db.Column(db.Integer, db.ForeignKey('chat_messages.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('chat_messages', lazy=True, cascade='all, delete-orphan'))
    reply_to = db.relationship('ChatMessage', remote_side=[id], backref=db.backref('replies', lazy=True))
    
    __table_args__ = (
        db.Index('idx_chat_created_at', 'created_at'),
        db.Index('idx_chat_user', 'user_id'),
    )

    def __repr__(self):
        return f'<ChatMessage {self.id} - {self.message[:20]}>'


# Helper Functions
def get_current_meal_rate():
    """Get the current meal rate (All-time dynamic calculation)"""
    total_meals = db.session.query(db.func.sum(Meal.meal_count)).scalar() or 1
    total_expenses = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    return total_expenses / total_meals if total_meals > 0 else 0

def get_monthly_meal_rate(year, month):
    """Get the meal rate for a specific month"""
    total_meals = db.session.query(db.func.sum(Meal.meal_count)).filter(
        db.extract('year', Meal.date) == year,
        db.extract('month', Meal.date) == month
    ).scalar() or 0
    
    if total_meals == 0:
        total_meals = 1 # Avoid division by zero
        
    total_expenses = db.session.query(db.func.sum(Expense.amount)).filter(
        db.extract('year', Expense.date) == year,
        db.extract('month', Expense.date) == month
    ).scalar() or 0
    
    return total_expenses / total_meals if total_meals > 0 else 0

def get_hostel_stats(current_date=None):
    """Get statistics for entire hostel (All-time)"""
    if current_date is None:
        current_date = date.today()
    
    total_meals = db.session.query(db.func.sum(Meal.meal_count)).filter(
        Meal.date <= current_date
    ).scalar() or 0
    
    meal_rate = get_current_meal_rate()
    total_cost = total_meals * meal_rate if meal_rate > 0 else 0
    
    total_deposited = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.type == 'deposit'
    ).scalar() or 0
    
    total_expenses = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    
    return {
        'total_meals': total_meals,
        'meal_rate': meal_rate,
        'total_cost': total_cost,
        'total_deposited': total_deposited,
        'total_expenses': total_expenses
    }

def get_monthly_hostel_stats(year, month):
    """Get statistics for entire hostel for a specific month"""
    total_meals = db.session.query(db.func.sum(Meal.meal_count)).filter(
        db.extract('year', Meal.date) == year,
        db.extract('month', Meal.date) == month
    ).scalar() or 0
    
    meal_rate = get_monthly_meal_rate(year, month)
    total_cost = total_meals * meal_rate if meal_rate > 0 else 0
    
    total_deposited = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.type == 'deposit',
        db.extract('year', Transaction.date) == year,
        db.extract('month', Transaction.date) == month
    ).scalar() or 0
    
    total_expenses = db.session.query(db.func.sum(Expense.amount)).filter(
        db.extract('year', Expense.date) == year,
        db.extract('month', Expense.date) == month
    ).scalar() or 0
    
    return {
        'total_meals': total_meals,
        'meal_rate': meal_rate,
        'total_cost': total_cost,
        'total_deposited': total_deposited,
        'total_expenses': total_expenses
    }

def get_bulk_user_monthly_stats(target_year, target_month):
    """
    Get monthly stats (monthly_meals, monthly_cost) for all users in batch in 1-2 aggregate queries.
    Returns: (stats_by_user dict mapping user_id -> {'monthly_meals': float, 'monthly_cost': float}, current_monthly_rate)
    """
    meal_rate = get_monthly_meal_rate(target_year, target_month)
    
    results = db.session.query(
        Meal.user_id,
        db.func.sum(Meal.meal_count).label('sum_meals')
    ).filter(
        db.extract('year', Meal.date) == target_year,
        db.extract('month', Meal.date) == target_month
    ).group_by(Meal.user_id).all()
    
    stats_by_user = {}
    for user_id, sum_meals in results:
        meals = float(sum_meals or 0.0)
        cost = meals * meal_rate if meal_rate > 0 else 0.0
        stats_by_user[user_id] = {
            'monthly_meals': meals,
            'monthly_cost': cost
        }
    return stats_by_user, meal_rate

def get_bulk_user_balances(all_user_ids, current_date=None):
    """
    Batch compute total deposited and running balance for a list of user IDs in aggregated SQL queries.
    Returns: dict mapping user_id -> {'total_deposited': float, 'balance': float}
    """
    if current_date is None:
        current_date = date.today()
    if not all_user_ids:
        return {}
        
    tx_results = db.session.query(
        Transaction.user_id,
        Transaction.type,
        db.func.sum(Transaction.amount).label('sum_amount')
    ).filter(
        Transaction.user_id.in_(all_user_ids)
    ).group_by(Transaction.user_id, Transaction.type).all()
    
    tx_map = {uid: {'deposit': 0.0, 'withdrawal': 0.0} for uid in all_user_ids}
    for uid, tx_type, amt in tx_results:
        if uid in tx_map and tx_type in tx_map[uid]:
            tx_map[uid][tx_type] = float(amt or 0.0)

    expense_rows = db.session.query(
        db.extract('year', Expense.date).label('year'),
        db.extract('month', Expense.date).label('month'),
        db.func.sum(Expense.amount).label('total_exp')
    ).group_by('year', 'month').all()
    
    monthly_expenses = {}
    for r in expense_rows:
        y, m = int(r.year), int(r.month)
        monthly_expenses[(y, m)] = float(r.total_exp or 0.0)

    monthly_all_meals_rows = db.session.query(
        db.extract('year', Meal.date).label('year'),
        db.extract('month', Meal.date).label('month'),
        db.func.sum(Meal.meal_count).label('tot_meals')
    ).filter(Meal.date <= current_date).group_by('year', 'month').all()

    monthly_rates = {}
    for r in monthly_all_meals_rows:
        y, m = int(r.year), int(r.month)
        tot_m = float(r.tot_meals or 0.0)
        exp = monthly_expenses.get((y, m), 0.0)
        monthly_rates[(y, m)] = (exp / tot_m) if tot_m > 0 else 0.0

    user_monthly_meals_rows = db.session.query(
        Meal.user_id,
        db.extract('year', Meal.date).label('year'),
        db.extract('month', Meal.date).label('month'),
        db.func.sum(Meal.meal_count).label('u_meals')
    ).filter(
        Meal.user_id.in_(all_user_ids),
        Meal.date <= current_date
    ).group_by(Meal.user_id, 'year', 'month').all()

    user_total_costs = {uid: 0.0 for uid in all_user_ids}
    for r in user_monthly_meals_rows:
        uid = r.user_id
        y, m = int(r.year), int(r.month)
        u_m = float(r.u_meals or 0.0)
        rate = monthly_rates.get((y, m), 0.0)
        user_total_costs[uid] += (u_m * rate)

    balances_by_user = {}
    for uid in all_user_ids:
        dep = tx_map[uid]['deposit']
        wth = tx_map[uid]['withdrawal']
        cst = user_total_costs.get(uid, 0.0)
        bal = dep - cst - wth
        balances_by_user[uid] = {
            'total_deposited': dep,
            'balance': bal
        }
        
    return balances_by_user
