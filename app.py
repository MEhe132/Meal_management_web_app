"""
Hostel Meal Management System - Flask Application
"""
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
from functools import wraps
from datetime import datetime, date, timedelta
from config import config
from models import db, User, Meal, Transaction, MealRate, get_current_meal_rate, get_hostel_stats, get_monthly_meal_rate, get_monthly_hostel_stats, Expense, MealLock, DailyMenu, ChatMessage
import subprocess
import sys
import queue
import json

class MessageAnnouncer:
    def __init__(self):
        self.listeners = []

    def listen(self):
        q = queue.Queue(maxsize=100)
        self.listeners.append(q)
        return q

    def disconnect(self, q):
        if q in self.listeners:
            try:
                self.listeners.remove(q)
            except ValueError:
                pass

    def announce(self, msg):
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(msg)
            except queue.Full:
                del self.listeners[i]

announcer = MessageAnnouncer()

# The rest of your app code...
def create_app(config_name='development'):
    """Application Factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config.get(config_name, config['default']))
    
    # Initialize database
    db.init_app(app)
    
    # Register context processor with request-scoped caching
    @app.context_processor
    def inject_user():
        if 'current_user' not in g:
            g.current_user = User.query.get(session['user_id']) if 'user_id' in session else None
        return {'current_user': g.current_user}
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Ensure chat messages table exists (since db.create_all() will handle it if entirely new,
        # but if we need a safe migration similar to others, we can do it)
        try:
            db.session.execute(db.text("SELECT id FROM chat_messages LIMIT 1"))
        except Exception:
            db.session.rollback()
            try:
                # Actually create_all handles missing tables, but just in case
                db.create_all()
            except Exception as e:
                print(f"Error checking chat messages: {e}")
                db.session.rollback()
                
        # Safe migration: Add user_id column to expenses table if it doesn't exist
        try:
            db.session.execute(db.text("SELECT user_id FROM expenses LIMIT 1"))
        except Exception:
            db.session.rollback()
            try:
                db.session.execute(db.text("ALTER TABLE expenses ADD COLUMN user_id INTEGER REFERENCES users(id)"))
                db.session.commit()
            except Exception as e:
                print(f"Error migrating database user_id: {e}")
                db.session.rollback()

        # Safe migration: Add breakfast, lunch, dinner columns to meals table if they don't exist
        for col_name in ['breakfast', 'lunch', 'dinner']:
            try:
                db.session.execute(db.text(f"SELECT {col_name} FROM meals LIMIT 1"))
            except Exception:
                db.session.rollback()
                try:
                    db.session.execute(db.text(f"ALTER TABLE meals ADD COLUMN {col_name} BOOLEAN DEFAULT 0"))
                    db.session.commit()
                except Exception as e:
                    print(f"Error migrating database column {col_name}: {e}")
                    db.session.rollback()

        # Backfill existing meals where breakfast, lunch, or dinner are NULL
        try:
            uninitialized_meals = Meal.query.filter((Meal.breakfast == None) | (Meal.lunch == None) | (Meal.dinner == None)).all()
            if uninitialized_meals:
                for meal in uninitialized_meals:
                    if meal.meal_count == 2.5:
                        meal.breakfast = True
                        meal.lunch = True
                        meal.dinner = True
                    elif meal.meal_count == 2.0:
                        meal.breakfast = False
                        meal.lunch = True
                        meal.dinner = True
                    elif meal.meal_count == 1.5:
                        meal.breakfast = True
                        meal.lunch = True
                        meal.dinner = False
                    elif meal.meal_count == 1.0:
                        meal.breakfast = False
                        meal.lunch = True
                        meal.dinner = False
                    elif meal.meal_count == 0.5:
                        meal.breakfast = True
                        meal.lunch = False
                        meal.dinner = False
                    else:
                        meal.breakfast = False
                        meal.lunch = False
                        meal.dinner = False
                db.session.commit()
                print(f"[Migration] Backfilled {len(uninitialized_meals)} legacy meal entries.")
        except Exception as e:
            print(f"Error backfilling meals: {e}")
            db.session.rollback()
            
        # Safe migration: Add avatar_seed column to users table if it doesn't exist
        try:
            db.session.execute(db.text("SELECT avatar_seed FROM users LIMIT 1"))
        except Exception:
            db.session.rollback()
            try:
                db.session.execute(db.text("ALTER TABLE users ADD COLUMN avatar_seed VARCHAR(100)"))
                db.session.commit()
            except Exception as e:
                print(f"Error migrating database avatar_seed: {e}")
                db.session.rollback()

        # Safe migration: Add reply_to_id column to chat_messages table if it doesn't exist
        try:
            db.session.execute(db.text("SELECT reply_to_id FROM chat_messages LIMIT 1"))
        except Exception:
            db.session.rollback()
            try:
                db.session.execute(db.text("ALTER TABLE chat_messages ADD COLUMN reply_to_id INTEGER REFERENCES chat_messages(id)"))
                db.session.commit()
            except Exception as e:
                print(f"Error migrating database reply_to_id: {e}")
                db.session.rollback()
                
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
    @app.route('/api/potential-managers', methods=['GET'])
    @manager_required
    def get_potential_managers():
        """API endpoint to fetch eligible members for manager role transfer"""
        members = User.query.filter_by(role='member', is_active=True).all()
        return jsonify({
            'success': True,
            'members': [{'id': m.id, 'name': m.name, 'email': m.email} for m in members]
        })

    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Dashboard - Main page for both members and managers"""
        current_user = User.query.get(session['user_id'])
        
        # FIX 1: Get ALL active users (members + manager) for dashboard
        all_users = User.query.filter_by(is_active=True).all()
        
        month_param = request.args.get('month', type=int)
        year_param = request.args.get('year', type=int)
        today_real = date.today()
        
        if month_param and year_param:
            first_day = date(year_param, month_param, 1)
            if month_param == 12:
                next_month = date(year_param + 1, 1, 1)
            else:
                next_month = date(year_param, month_param + 1, 1)
            last_day = next_month - timedelta(days=1)
            
            if first_day.year == today_real.year and first_day.month == today_real.month:
                target_end_date = today_real
            else:
                target_end_date = last_day
        else:
            first_day = date(today_real.year, today_real.month, 1)
            target_end_date = today_real
        
        # Get all meals for this month
        meals_data = {}
        for user in all_users:
            user_meals = Meal.query.filter(
                Meal.user_id == user.id,
                Meal.date >= first_day,
                Meal.date <= target_end_date
            ).all()
            meals_data[user.id] = {user_meal.date: user_meal.meal_count for user_meal in user_meals}
        
        # Get all dates in current month
        all_dates = []
        current_date = first_day
        while current_date <= target_end_date:
            all_dates.append(current_date)
            current_date += timedelta(days=1)
            
        target_year = first_day.year
        target_month = first_day.month
        
        # Pre-calculate monthly meal rate once to eliminate N+1 queries in user loop
        current_monthly_rate = get_monthly_meal_rate(target_year, target_month)
        
        # Calculate stats for each user (strictly monthly for meals and cost, overall for balance)
        user_stats = []
        for user in all_users:
            monthly_meals = user.get_monthly_meals(target_year, target_month)
            monthly_cost = user.get_monthly_cost(target_year, target_month)
            total_deposited = user.get_total_deposited() # Overall
            balance = user.get_balance() # Overall running balance
            
            # Check if user is manager
            is_manager = user.is_manager()
            
            user_stats.append({
                'user': user,
                'daily_meals': [meals_data.get(user.id, {}).get(d, 0) for d in all_dates],
                'total_meals': monthly_meals,
                'meal_rate': current_monthly_rate,
                'total_deposited': total_deposited,
                'total_cost': monthly_cost,
                'balance': balance,
                'is_manager': is_manager  # Add manager flag for display
            })
        
        # Sort user_stats so logged-in user always appears at the top (first row)
        user_stats.sort(key=lambda s: (0 if s['user'].id == current_user.id else 1, s['user'].id))
        
        # Get hostel stats
        hostel_stats = get_monthly_hostel_stats(target_year, target_month)
        
        # Show month end warning on dashboard for manager if it's late in the month
        show_month_end_warning = False
        if current_user.is_manager() and today_real.day >= 25 and today_real.year == target_year and today_real.month == target_month:
            show_month_end_warning = True
        
        return render_template(
            'dashboard.html',
            current_user=current_user,
            user_stats=user_stats,
            all_dates=all_dates,
            hostel_stats=hostel_stats,
            show_month_end_warning=show_month_end_warning,
            target_year=target_year,
            target_month=target_month
        )

    @app.route('/meal-status', methods=['GET'])
    @login_required
    def meal_status():
        """Meal Status - Members toggle their meals, Manager views all and locks slots"""
        current_user = User.query.get(session['user_id'])
        
        # Manager can view and edit other members' status by passing user_id query param
        target_user_id = request.args.get('user_id', type=int)
        if target_user_id and current_user.is_manager():
            target_user = User.query.get(target_user_id)
        else:
            target_user = current_user
            target_user_id = current_user.id
            
        # Display today + next 6 days
        today = date.today()
        dates_range = [today + timedelta(days=i) for i in range(7)]
        
        # Get existing meals for these dates
        meals = Meal.query.filter(
            Meal.user_id == target_user_id,
            Meal.date >= today,
            Meal.date <= dates_range[-1]
        ).all()
        meals_by_date = {m.date: m for m in meals}
        
        # Get locks for these dates
        locks = MealLock.query.filter(
            MealLock.date >= today,
            MealLock.date <= dates_range[-1]
        ).all()
        locks_by_date = {l.date: l for l in locks}
        
        # All active users for selector in manager mode
        all_users = User.query.filter_by(is_active=True).all() if current_user.is_manager() else []
        
        return render_template(
            'meal_status.html',
            current_user=current_user,
            target_user=target_user,
            dates_range=dates_range,
            meals_by_date=meals_by_date,
            locks_by_date=locks_by_date,
            all_users=all_users,
            today=today
        )

    @app.route('/api/toggle-meal-status', methods=['POST'])
    @login_required
    def toggle_meal_status():
        """API endpoint to toggle a user's breakfast/lunch/dinner status"""
        current_user = User.query.get(session['user_id'])
        data = request.json or {}
        
        target_user_id = data.get('user_id')
        meal_date_str = data.get('date')
        meal_type = data.get('meal_type')  # 'breakfast', 'lunch', or 'dinner'
        is_checked = data.get('checked', False)
        
        if not all([target_user_id, meal_date_str, meal_type]):
            return {'success': False, 'message': 'Missing parameters'}, 400
            
        try:
            meal_date = datetime.strptime(meal_date_str, '%Y-%m-%d').date()
        except ValueError:
            return {'success': False, 'message': 'Invalid date format'}, 400
            
        # Check permissions: members can only edit their own status
        if target_user_id != current_user.id and not current_user.is_manager():
            return {'success': False, 'message': 'Unauthorized to change this meal status'}, 403
            
        # Check if locked for this date and type
        lock = MealLock.query.filter_by(date=meal_date).first()
        if lock:
            if meal_type == 'breakfast' and lock.breakfast_locked:
                return {'success': False, 'message': 'Breakfast is locked for this date'}, 403
            elif meal_type == 'lunch' and lock.lunch_locked:
                return {'success': False, 'message': 'Lunch is locked for this date'}, 403
            elif meal_type == 'dinner' and lock.dinner_locked:
                return {'success': False, 'message': 'Dinner is locked for this date'}, 403
                
        # Find or create meal
        meal = Meal.query.filter_by(user_id=target_user_id, date=meal_date).first()
        if not meal:
            meal = Meal(user_id=target_user_id, date=meal_date)
            db.session.add(meal)
            
        if meal_type == 'breakfast':
            meal.breakfast = is_checked
        elif meal_type == 'lunch':
            meal.lunch = is_checked
        elif meal_type == 'dinner':
            meal.dinner = is_checked
            
        meal.update_meal_count()
        meal.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {
            'success': True,
            'message': f'{meal_type.capitalize()} updated',
            'meal_count': meal.meal_count
        }

    @app.route('/api/toggle-meal-lock', methods=['POST'])
    @manager_required
    def toggle_meal_lock():
        """API endpoint for manager to lock/unlock breakfast/lunch/dinner"""
        data = request.json or {}
        meal_date_str = data.get('date')
        meal_type = data.get('meal_type')
        is_locked = data.get('locked', False)
        
        if not all([meal_date_str, meal_type]):
            return {'success': False, 'message': 'Missing parameters'}, 400
            
        try:
            meal_date = datetime.strptime(meal_date_str, '%Y-%m-%d').date()
        except ValueError:
            return {'success': False, 'message': 'Invalid date format'}, 400
            
        lock = MealLock.query.filter_by(date=meal_date).first()
        if not lock:
            lock = MealLock(date=meal_date)
            db.session.add(lock)
            
        if meal_type == 'breakfast':
            lock.breakfast_locked = is_locked
        elif meal_type == 'lunch':
            lock.lunch_locked = is_locked
        elif meal_type == 'dinner':
            lock.dinner_locked = is_locked
            
        db.session.commit()
        
        action = "locked" if is_locked else "unlocked"
        return {
            'success': True,
            'message': f'{meal_type.capitalize()} is now {action} for {meal_date_str}.',
            'locked': is_locked
        }

    @app.route('/todays-meals')
    @login_required
    def todays_meals():
        """Today's Meal List - Displays breakfast, lunch, dinner statuses and totals for today"""
        current_user = User.query.get(session['user_id'])
        today = date.today()
        
        all_users = User.query.filter_by(is_active=True).all()
        meals = Meal.query.filter_by(date=today).all()
        meals_by_user = {m.user_id: m for m in meals}
        
        lock = MealLock.query.filter_by(date=today).first()
        
        user_list = []
        total_breakfasts = 0
        total_lunches = 0
        total_dinners = 0
        total_meal_count = 0.0
        
        for user in all_users:
            meal = meals_by_user.get(user.id)
            b = meal.breakfast if meal else False
            l = meal.lunch if meal else False
            d = meal.dinner if meal else False
            m_count = meal.meal_count if meal else 0.0
            
            if b: total_breakfasts += 1
            if l: total_lunches += 1
            if d: total_dinners += 1
            total_meal_count += m_count
            
            user_list.append({
                'user': user,
                'breakfast': b,
                'lunch': l,
                'dinner': d,
                'meal_count': m_count
            })
            
        return render_template(
            'todays_meals.html',
            current_user=current_user,
            user_list=user_list,
            today=today,
            lock=lock,
            total_breakfasts=total_breakfasts,
            total_lunches=total_lunches,
            total_dinners=total_dinners,
            total_meal_count=total_meal_count
        )

    @app.route('/menu')
    @login_required
    def menu():
        """Today's and Weekly Menu Planner"""
        current_user = User.query.get(session['user_id'])
        today = date.today()
        dates_range = [today + timedelta(days=i) for i in range(7)]
        
        menus = DailyMenu.query.filter(
            DailyMenu.date >= today,
            DailyMenu.date <= dates_range[-1]
        ).all()
        menus_by_date = {m.date: m for m in menus}
        
        return render_template(
            'menu.html',
            current_user=current_user,
            dates_range=dates_range,
            menus_by_date=menus_by_date,
            today=today
        )

    @app.route('/api/update-menu', methods=['POST'])
    @manager_required
    def update_menu():
        """API endpoint to set daily menus"""
        data = request.json or {}
        menu_date_str = data.get('date')
        breakfast_menu = data.get('breakfast', '').strip()
        lunch_menu = data.get('lunch', '').strip()
        dinner_menu = data.get('dinner', '').strip()
        
        if not menu_date_str:
            return {'success': False, 'message': 'Missing date'}, 400
            
        try:
            menu_date = datetime.strptime(menu_date_str, '%Y-%m-%d').date()
        except ValueError:
            return {'success': False, 'message': 'Invalid date format'}, 400
            
        menu = DailyMenu.query.filter_by(date=menu_date).first()
        if not menu:
            menu = DailyMenu(date=menu_date)
            db.session.add(menu)
            
        menu.breakfast_menu = breakfast_menu
        menu.lunch_menu = lunch_menu
        menu.dinner_menu = dinner_menu
        menu.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {
            'success': True,
            'message': f'Menu for {menu_date_str} updated successfully!'
        }

    @app.route('/transactions')
    @login_required
    def transactions_page():
        """Transactions Page - Shows expenses and user deposits/withdrawals for transparent auditing"""
        current_user = User.query.get(session['user_id'])
        all_transactions = Transaction.query.order_by(Transaction.date.desc()).all()
        all_expenses = Expense.query.order_by(Expense.date.desc()).all()
        all_users = User.query.filter_by(is_active=True).all()
        
        return render_template(
            'transactions.html',
            current_user=current_user,
            transactions=all_transactions,
            expenses=all_expenses,
            all_users=all_users
        )

    @app.route('/members')
    @login_required
    def members_page():
        """Members Page - Lists all members with unique auto-generated IDs"""
        current_user = User.query.get(session['user_id'])
        all_users = User.query.filter_by(is_active=True).order_by(User.id.asc()).all()
        
        return render_template(
            'members.html',
            current_user=current_user,
            members=all_users
        )
    
    @app.route('/history')
    @login_required
    def history_page():
        """History - View past months sheets"""
        current_user = User.query.get(session['user_id'])
        
        # Get distinct months from Meal dates
        meals = Meal.query.with_entities(Meal.date).all()
        months_set = set((m.date.year, m.date.month) for m in meals)
        
        # Ensure current month is always available
        today = date.today()
        months_set.add((today.year, today.month))
        
        history_months = sorted(list(months_set), key=lambda x: (x[0], x[1]), reverse=True)
        
        month_names = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        
        return render_template('history.html', 
                               current_user=current_user,
                               history_months=history_months,
                               month_names=month_names)
                               
    @app.route('/chat')
    @login_required
    def chat_page():
        """Chat Page - Real-time messaging"""
        current_user = User.query.get(session['user_id'])
        all_users = User.query.filter_by(is_active=True).all()
        all_users_json = [{'id': u.id, 'name': u.name} for u in all_users]
        return render_template('chat.html', current_user=current_user, all_users_json=all_users_json)
        
    @app.route('/api/chat/history', methods=['GET'])
    @login_required
    def chat_history():
        """Get past chat messages"""
        # Get the last 50 messages
        messages = ChatMessage.query.order_by(ChatMessage.created_at.desc()).limit(50).all()
        messages.reverse()
        
        history = []
        for msg in messages:
            reply_to_snippet = None
            reply_to_name = None
            if msg.reply_to_id and msg.reply_to:
                reply_to_snippet = msg.reply_to.message[:50] + ('...' if len(msg.reply_to.message) > 50 else '')
                reply_to_name = msg.reply_to.user.name
                
            history.append({
                'id': msg.id,
                'user_id': msg.user_id,
                'user_name': msg.user.name,
                'user_initial': msg.user.name[0].upper() if msg.user.name else '?',
                'user_avatar_seed': msg.user.avatar_seed or msg.user.name,
                'message': msg.message,
                'reply_to_id': msg.reply_to_id,
                'reply_to_snippet': reply_to_snippet,
                'reply_to_name': reply_to_name,
                'created_at': msg.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
            })
            
        return jsonify({'success': True, 'messages': history})
        
    @app.route('/api/chat/send', methods=['POST'])
    @login_required
    def chat_send():
        """Send a new chat message"""
        current_user = User.query.get(session['user_id'])
        data = request.json or {}
        message_text = data.get('message', '').strip()
        reply_to_id = data.get('reply_to_id')
        
        if not message_text:
            return jsonify({'success': False, 'message': 'Message cannot be empty'}), 400
            
        msg = ChatMessage(user_id=current_user.id, message=message_text, reply_to_id=reply_to_id)
        db.session.add(msg)
        db.session.commit()
        
        # Parse mentions
        mentioned_users = []
        all_active = User.query.filter_by(is_active=True).all()
        for u in all_active:
            if f"@{u.name}" in message_text:
                mentioned_users.append(u.id)
                
        reply_to_snippet = None
        reply_to_name = None
        if msg.reply_to_id and msg.reply_to:
            reply_to_snippet = msg.reply_to.message[:50] + ('...' if len(msg.reply_to.message) > 50 else '')
            reply_to_name = msg.reply_to.user.name
        
        msg_data = {
            'id': msg.id,
            'user_id': msg.user_id,
            'user_name': msg.user.name,
            'user_initial': msg.user.name[0].upper() if msg.user.name else '?',
            'user_avatar_seed': msg.user.avatar_seed or msg.user.name,
            'message': msg.message,
            'reply_to_id': msg.reply_to_id,
            'reply_to_snippet': reply_to_snippet,
            'reply_to_name': reply_to_name,
            'mentioned_users': list(set(mentioned_users)),
            'created_at': msg.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        
        # Broadcast message
        announcer.announce(msg_data)
        
        return jsonify({'success': True, 'message': 'Message sent'})
        
    @app.route('/api/set-avatar-seed', methods=['POST'])
    @login_required
    def set_avatar_seed():
        current_user = User.query.get(session['user_id'])
        data = request.json or {}
        seed = data.get('seed', '').strip()
        
        if not seed:
            return jsonify({'success': False, 'message': 'Seed is required'}), 400
            
        current_user.avatar_seed = seed
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Avatar updated successfully', 'seed': seed})

    @app.route('/api/chat/stream')
    @login_required
    def chat_stream():
        """Non-blocking SSE stream for receiving chat notifications"""
        from flask import Response
        def stream():
            messages = announcer.listen()
            try:
                while True:
                    try:
                        msg = messages.get(timeout=2.0)
                        yield f"data: {json.dumps(msg)}\n\n"
                    except queue.Empty:
                        # Send keep-alive heartbeat comment to detect disconnects and unblock threads
                        yield ": keep-alive\n\n"
            finally:
                announcer.disconnect(messages)
                
        return Response(stream(), mimetype='text/event-stream')
   
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
        user_id = request.json.get('user_id')
        expense_date_str = request.json.get('date')
        
        # Handle custom date or default to today
        expense_date = datetime.utcnow()
        if expense_date_str:
            try:
                # Convert string 'YYYY-MM-DD' to datetime
                expense_date = datetime.strptime(expense_date_str, '%Y-%m-%d')
            except ValueError:
                return {'success': False, 'message': 'Invalid date format'}, 400
        
        # Check if amount is negative, which we allow for selling leftover stock
        # But we don't allow zero
        if float(amount) == 0:
            return {'success': False, 'message': 'Invalid amount'}, 400
        
        if not description:
            return {'success': False, 'message': 'Description is required'}, 400
            
        # Validate user_id if provided
        if user_id:
            user_exists = User.query.get(user_id)
            if not user_exists:
                return {'success': False, 'message': 'Selected member does not exist'}, 400
        else:
            user_id = None
        
        expense = Expense(
            amount=float(amount),
            description=description,
            user_id=user_id,
            date=expense_date
        )
        
        db.session.add(expense)
        db.session.commit()
        
        # Recalculate meal rate for that specific month
        year = expense_date.year
        month = expense_date.month
        new_rate = get_monthly_meal_rate(year, month)
        
        # Also save the rate to meal_rates table for history
        meal_rate = MealRate(
            rate=new_rate,
            effective_date=expense_date.date(),
            description=f"Auto-calculated from expenses"
        )
        db.session.add(meal_rate)
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Expense added successfully',
            'new_rate': new_rate,
            'total_expenses': get_monthly_hostel_stats(year, month)['total_expenses']
        }


    @app.route('/api/get-expenses', methods=['GET'])
    @login_required
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
                    'user_id': e.user_id,
                    'user_name': e.user.name if e.user else 'System',
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

    @app.route('/api/get-all-transactions', methods=['GET'])
    @login_required
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
    
    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='127.0.0.1', port=5000)