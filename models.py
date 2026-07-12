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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    
    def get_balance(self, current_date=None):
        """Calculate current balance"""
        if current_date is None:
            current_date = date.today()
        
        # Get total deposited money
        deposited = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == self.id,
            Transaction.type == 'deposit'
        ).scalar() or 0
        
        # Get total expenses
        meal_rate = get_current_meal_rate()
        total_meals = db.session.query(db.func.sum(Meal.meal_count)).filter(
            Meal.user_id == self.id,
            Meal.date <= current_date
        ).scalar() or 0
        
        expenses = total_meals * meal_rate if meal_rate > 0 else 0
        
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
    
    def get_total_cost(self, current_date=None):
        """Get total cost for user"""
        if current_date is None:
            current_date = date.today()
        
        meal_rate = get_current_meal_rate()
        total_meals = self.get_total_meals(current_date)
        return total_meals * meal_rate if meal_rate > 0 else 0
    
    def __repr__(self):
        return f'<User {self.name}>'


class Meal(db.Model):
    """Meal Model - tracks daily meal counts"""
    __tablename__ = 'meals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    meal_count = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='unique_user_date'),)
    
    def __repr__(self):
        return f'<Meal {self.user_id} - {self.date}: {self.meal_count}>'


class Transaction(db.Model):
    """Transaction Model - tracks deposits and withdrawals"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'deposit' or 'withdrawal'
    description = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaction {self.user_id} - {self.type}: {self.amount}>'


class Expense(db.Model):
    """Expense Model - tracks hostel expenses for meal rate calculation"""
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Expense {self.amount} - {self.description}>'


class MealRate(db.Model):
    """Meal Rate Model - tracks the meal rate (rate per meal)"""
    __tablename__ = 'meal_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    rate = db.Column(db.Float, nullable=False)
    effective_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MealRate {self.rate} - {self.effective_date}>'


# Helper Functions
def get_current_meal_rate():
    """Get the current meal rate (dynamic calculation)"""
    # Get total meals from ALL users (including manager)
    total_meals = db.session.query(db.func.sum(Meal.meal_count)).scalar() or 1  # Avoid division by zero
    
    # Get total expenses
    total_expenses = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    
    # Calculate rate = total_expenses / total_meals
    rate = total_expenses / total_meals if total_meals > 0 else 0
    
    return rate


def get_hostel_stats(current_date=None):
    """Get statistics for entire hostel"""
    if current_date is None:
        current_date = date.today()
    
    # Total meals - include ALL users (members + manager)
    total_meals = db.session.query(db.func.sum(Meal.meal_count)).filter(
        Meal.date <= current_date
    ).scalar() or 0
    
    # Meal rate (dynamic)
    meal_rate = get_current_meal_rate()
    
    # Total cost
    total_cost = total_meals * meal_rate if meal_rate > 0 else 0
    
    # Total deposited - include ALL users
    total_deposited = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.type == 'deposit'
    ).scalar() or 0
    
    # Total expenses
    total_expenses = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    
    return {
        'total_meals': total_meals,
        'meal_rate': meal_rate,
        'total_cost': total_cost,
        'total_deposited': total_deposited,
        'total_expenses': total_expenses
    }