"""
Initialize Demo Data for Testing
Run this script to populate the database with sample data
"""
from app import create_app
from models import db, User, Meal, Transaction, MealRate
from datetime import date, timedelta

def init_demo_data():
    """Initialize demo data"""
    app = create_app('development')
    
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        print("🔄 Clearing and recreating database...")
        
        # Create Manager
        manager = User(
            name='Manager User',
            email='manager@example.com',
            role='manager',
            is_active=True
        )
        manager.set_password('password')
        db.session.add(manager)
        print("✅ Manager created: manager@example.com")
        
        # Create Members
        member_data = [
            ('Mehedi Hasan', 'mehedi@example.com'),
            ('Arefin Ahmed', 'arefin@example.com'),
            ('Ali Hassan', 'ali@example.com'),
            ('Karim Khan', 'karim@example.com'),
        ]
        
        members = []
        for name, email in member_data:
            member = User(
                name=name,
                email=email,
                role='member',
                is_active=True
            )
            member.set_password('password')
            db.session.add(member)
            members.append(member)
            print(f"✅ Member created: {email}")
        
        db.session.commit()
        
        # Create meal rate
        meal_rate = MealRate(
            rate=50,
            effective_date=date.today(),
            description='Initial meal rate'
        )
        db.session.add(meal_rate)
        print("✅ Meal rate set: ৳50")
        
        # Create sample transactions for members AND manager
        all_users = [manager] + members
        for user in all_users:
            # Add initial deposit
            transaction = Transaction(
                user_id=user.id,
                amount=5000,
                type='deposit',
                description='Monthly deposit'
            )
            db.session.add(transaction)
        
        db.session.commit()
        print("✅ Initial deposits added: ৳5000 per user")
        
        # Create sample meal data for the past 5 days for ALL users
        for i in range(5):
            current_date = date.today() - timedelta(days=4-i)
            for user in all_users:
                meal_count = 2.5 if i % 2 == 0 else 2.0
                meal = Meal(
                    user_id=user.id,
                    date=current_date,
                    meal_count=meal_count
                )
                db.session.add(meal)
        
        db.session.commit()
        print("✅ Sample meal data added for past 5 days (including manager)")
        
        print("\n" + "="*50)
        print("✨ DEMO DATA INITIALIZED SUCCESSFULLY!")
        print("="*50)
        print("\n📝 TEST CREDENTIALS:\n")
        print("Manager Account:")
        print("  Email: manager@example.com")
        print("  Password: password")
        print("  Role: Manager (Full Access)")
        print("  NOTE: Manager is also included as a meal member!")
        print("\nMember Accounts:")
        for name, email in member_data:
            print(f"  • {name}")
            print(f"    Email: {email}")
            print(f"    Password: password")
        print("\n🚀 Run 'python app.py' to start the application!")
        print("📱 Visit http://localhost:5000 in your browser")
    # After creating meals, add sample expenses
    print("📊 Adding sample expenses...")
    sample_expenses = [
        (2000, "Rice - 50kg"),
        (1500, "Vegetables - Weekly supply"),
        (800, "Cooking oil"),
        (1200, "Chicken - 10kg"),
        (500, "Spices and condiments"),
    ]

    for amount, desc in sample_expenses:
        expense = Expense(
            amount=amount,
            description=desc
        )
        db.session.add(expense)

    db.session.commit()
    print(f"✅ {len(sample_expenses)} sample expenses added")

if __name__ == '__main__':
    init_demo_data()