"""
Hostel Meal Management System - Flask Application
"""
# At the top of app.py, add this import

import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from datetime import datetime, date, timedelta
from config import config
from models import db, User, Meal, Transaction, MealRate, get_current_meal_rate, get_hostel_stats,Expense
import subprocess
import sys


from waitress import serve

# The rest of your app code...
def create_app(config_name='development'):
    """Application Factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config.get(config_name, config['default']))
    
    # Initialize database
    db.init_app(app)
    
    # Register context processor
    @app.context_processor
    def inject_user():
        user = None
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
        return {'current_user': user}
    
    # Create database tables
    with app.app_context():
        db.create_all()
        # Create default meal rate if doesn't exist
        if MealRate.query.first() is None:
            default_rate = MealRate(rate=50, effective_date=date.today(), description="Initial meal rate")
            db.session.add(default_rate)
            db.session.commit()
    
    # ============== DECORATORS ==============
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first', 'warning')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def manager_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first', 'warning')
                return redirect(url_for('login'))
            
            user = User.query.get(session['user_id'])
            if not user or not user.is_manager():
                flash('You do not have permission to access this page', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    
    # ============== ROUTES ==============
    
    @app.route('/')
    def index():
        """Redirect to login or dashboard"""
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login Route"""
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            
            if not email or not password:
                flash('Email and password are required', 'danger')
                return redirect(url_for('login'))
            
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password) and user.is_active:
                session['user_id'] = user.id
                session.permanent = True
                flash(f'Welcome back, {user.name}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password', 'danger')
        
        return render_template('login.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Register Route - for creating test users"""
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            password_confirm = request.form.get('password_confirm', '')
            role = request.form.get('role', 'member')
            
            if not all([name, email, password, password_confirm]):
                flash('All fields are required', 'danger')
                return redirect(url_for('register'))
            
            if password != password_confirm:
                flash('Passwords do not match', 'danger')
                return redirect(url_for('register'))
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'danger')
                return redirect(url_for('register'))
            
            # Only allow one manager
            if role == 'manager' and User.query.filter_by(role='manager').first():
                flash('Manager already exists', 'danger')
                return redirect(url_for('register'))
            
            user = User(name=name, email=email, role=role)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Dashboard - Main page for both members and managers"""
        current_user = User.query.get(session['user_id'])
        
        # FIX 1: Get ALL active users (members + manager) for dashboard
        all_users = User.query.filter_by(is_active=True).all()
        
        # Get meals for current month
        today = date.today()
        first_day = date(today.year, today.month, 1)
        
        # Get all meals for this month
        meals_data = {}
        for user in all_users:
            user_meals = Meal.query.filter(
                Meal.user_id == user.id,
                Meal.date >= first_day,
                Meal.date <= today
            ).all()
            meals_data[user.id] = {user_meal.date: user_meal.meal_count for user_meal in user_meals}
        
        # Get all dates in current month
        all_dates = []
        current_date = first_day
        while current_date <= today:
            all_dates.append(current_date)
            current_date += timedelta(days=1)
        
        # Calculate stats for each user
        user_stats = []
        for user in all_users:
            total_meals = user.get_total_meals()
            total_cost = user.get_total_cost()
            balance = user.get_balance()
            
            # Check if user is manager
            is_manager = user.is_manager()
            
            user_stats.append({
                'user': user,
                'daily_meals': [meals_data.get(user.id, {}).get(d, 0) for d in all_dates],
                'total_meals': total_meals,
                'meal_rate': get_current_meal_rate(),
                'total_cost': total_cost,
                'balance': balance,
                'is_manager': is_manager  # Add manager flag for display
            })
        
        # Get hostel stats
        hostel_stats = get_hostel_stats()
        
        return render_template(
            'dashboard.html',
            current_user=current_user,
            user_stats=user_stats,  # Renamed from member_stats
            all_dates=all_dates,
            hostel_stats=hostel_stats
        )
    
    @app.route('/manager')
    @manager_required
    def manager_panel():
        """Manager Panel"""
        current_user = User.query.get(session['user_id'])
        
        # FIX 1: Get ALL active users (members + manager) for manager panel
        all_users = User.query.filter_by(is_active=True).all()
        
        # Get today's date
        today = date.today()
        
        # Get meal entries for today
        today_meals = {}
        for user in all_users:
            meal = Meal.query.filter_by(user_id=user.id, date=today).first()
            today_meals[user.id] = meal.meal_count if meal else 0
        
        # Get all users with their balances and recent transactions
        user_info = []
        for user in all_users:
            balance = user.get_balance()
            total_meals = user.get_total_meals()
            
            # Get recent transactions
            recent_trans = Transaction.query.filter_by(user_id=user.id).order_by(
                Transaction.date.desc()
            ).limit(5).all()
            
            user_info.append({
                'user': user,
                'today_meals': today_meals.get(user.id, 0),
                'total_meals': total_meals,
                'balance': balance,
                'recent_transactions': recent_trans,
                'is_manager': user.is_manager()
            })
        
        # Get hostel stats
        hostel_stats = get_hostel_stats()
        
        # Get all members (non-manager) for transfer list
        potential_managers = User.query.filter_by(role='member', is_active=True).all()
        
        return render_template(
            'manager.html',
            current_user=current_user,
            user_info=user_info,  # Renamed from member_info
            hostel_stats=hostel_stats,
            today=today,
            potential_managers=potential_managers  # For transfer dropdown
        )
    
    @app.route('/api/add-meal', methods=['POST'])
    @manager_required
    def add_meal():
        """API endpoint to add meal entry"""
        user_id = request.json.get('user_id')
        meal_count = request.json.get('meal_count', 0)
        meal_date = request.json.get('date', str(date.today()))
        
        # Parse date
        try:
            meal_date = datetime.strptime(meal_date, '%Y-%m-%d').date()
        except ValueError:
            return {'success': False, 'message': 'Invalid date format'}, 400
        
        # Get or create meal entry
        meal = Meal.query.filter_by(user_id=user_id, date=meal_date).first()
        
        if meal:
            meal.meal_count = float(meal_count)
            meal.updated_at = datetime.utcnow()
        else:
            meal = Meal(user_id=user_id, date=meal_date, meal_count=float(meal_count))
            db.session.add(meal)
        
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Meal entry updated',
            'meal_count': meal.meal_count
        }
    
    @app.route('/api/add-money', methods=['POST'])
    @manager_required
    def add_money():
        """API endpoint to add money for member"""
        user_id = request.json.get('user_id')
        amount = request.json.get('amount', 0)
        transaction_type = request.json.get('type', 'deposit')  # deposit or withdrawal
        description = request.json.get('description', '')
        
        if not user_id or amount <= 0:
            return {'success': False, 'message': 'Invalid input'}, 400
        
        transaction = Transaction(
            user_id=user_id,
            amount=float(amount),
            type=transaction_type,
            description=description
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        user = User.query.get(user_id)
        new_balance = user.get_balance()
        
        return {
            'success': True,
            'message': f'{transaction_type.capitalize()} recorded',
            'new_balance': new_balance
        }
    
    @app.route('/api/set-meal-rate', methods=['POST'])
    @manager_required
    def set_meal_rate():
        """API endpoint to set meal rate"""
        rate = request.json.get('rate', 0)
        description = request.json.get('description', '')
        
        if rate <= 0:
            return {'success': False, 'message': 'Invalid rate'}, 400
        
        meal_rate = MealRate(
            rate=float(rate),
            effective_date=date.today(),
            description=description
        )
        
        db.session.add(meal_rate)
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Meal rate updated',
            'rate': rate
        }
    # ============== NEW: Expense Management Routes ==============

    @app.route('/api/add-expense', methods=['POST'])
    @manager_required
    def add_expense():
        """API endpoint to add expense for meal rate calculation"""
        amount = request.json.get('amount', 0)
        description = request.json.get('description', '').strip()
        
        if amount <= 0:
            return {'success': False, 'message': 'Invalid amount'}, 400
        
        if not description:
            return {'success': False, 'message': 'Description is required'}, 400
        
        expense = Expense(
            amount=float(amount),
            description=description
        )
        
        db.session.add(expense)
        db.session.commit()
        
        # Recalculate meal rate
        new_rate = get_current_meal_rate()
        
        # Also save the rate to meal_rates table for history
        meal_rate = MealRate(
            rate=new_rate,
            effective_date=date.today(),
            description=f"Auto-calculated from expenses"
        )
        db.session.add(meal_rate)
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Expense added successfully',
            'new_rate': new_rate,
            'total_expenses': get_hostel_stats()['total_expenses']
        }


    @app.route('/api/get-expenses', methods=['GET'])
    @manager_required
    def get_expenses():
        """API endpoint to get all expenses"""
        expenses = Expense.query.order_by(Expense.date.desc()).all()
        
        return {
            'success': True,
            'expenses': [
                {
                    'id': e.id,
                    'amount': e.amount,
                    'description': e.description,
                    'date': e.date.strftime('%Y-%m-%d %H:%M')
                } for e in expenses
            ]
        }


    @app.route('/api/delete-expense/<int:expense_id>', methods=['DELETE'])
    @manager_required
    def delete_expense(expense_id):
        """API endpoint to delete an expense"""
        expense = Expense.query.get(expense_id)
        
        if not expense:
            return {'success': False, 'message': 'Expense not found'}, 404
        
        db.session.delete(expense)
        db.session.commit()
        
        # Recalculate meal rate
        new_rate = get_current_meal_rate()
        
        # Save the new rate to history
        meal_rate = MealRate(
            rate=new_rate,
            effective_date=date.today(),
            description=f"Auto-calculated after expense deletion"
        )
        db.session.add(meal_rate)
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Expense deleted successfully',
            'new_rate': new_rate
        }
    # ============== NEW: Transfer Manager Role ==============
    @app.route('/api/transfer-manager', methods=['POST'])
    @manager_required
    def transfer_manager():
        """API endpoint to transfer manager role to another user"""
        new_manager_id = request.json.get('new_manager_id')
        
        if not new_manager_id:
            return {'success': False, 'message': 'Please select a member'}, 400
        
        # Get the new manager
        new_manager = User.query.get(new_manager_id)
        if not new_manager:
            return {'success': False, 'message': 'User not found'}, 404
        
        if new_manager.is_manager():
            return {'success': False, 'message': 'User is already a manager'}, 400
        
        # Get current manager
        current_manager = User.query.filter_by(role='manager').first()
        if not current_manager:
            return {'success': False, 'message': 'No current manager found'}, 400
        
        # Demote current manager to member
        current_manager.role = 'member'
        
        # Promote new user to manager
        new_manager.role = 'manager'
        
        db.session.commit()
        
        # ✅ FIX: Clear the session (force re-login)
        session.clear()
        
        return {
            'success': True,
            'message': f'Manager role transferred to {new_manager.name}. Please login again.',
            'redirect': '/login'
        }
    @app.route('/logout')
    def logout():
        """Logout Route"""
        session.clear()
        flash('You have been logged out', 'info')
        return redirect(url_for('login'))
    
    return app
    @app.route('/api/get-all-transactions', methods=['GET'])
    @manager_required
    def get_all_transactions():
        """API endpoint to get all transactions for all users"""
        transactions = Transaction.query.order_by(Transaction.date.desc()).limit(100).all()
        
        return {
            'success': True,
            'transactions': [
                {
                    'id': t.id,
                    'user_id': t.user_id,
                    'user_name': t.user.name,
                    'amount': t.amount,
                    'type': t.type,
                    'description': t.description,
                    'date': t.date.strftime('%Y-%m-%d %H:%M')
                } for t in transactions
            ]
        }

# Replace the bottom section (around line 254-256)
if __name__ == '__main__':
    app = create_app('development')
    # Remove this line:
    app.run(debug=True, host='0.0.0.0', port=5000)
    # Add this instead:
    # serve(app, host='127.0.0.1', port=5000)