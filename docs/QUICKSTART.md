# Quick Start Guide

## Get Running in 5 Minutes!

### Step 1: Install Dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python run.py
```

### Step 3: Open Browser
Navigate to: `http://localhost:5000`

### Step 4: Create Accounts

#### Create Student Account
1. Click "Register"
2. Select "Student/Freelancer"
3. Fill: Email, Password, Name, College, Year
4. Click "Register"
5. Login with credentials

#### Create Client Account
1. Click "Register"
2. Select "Client/Employer"
3. Fill: Email, Password, Company Name, Description
4. Click "Register"
5. Login with credentials

#### Admin login (automatic)

When you run `python run.py`, if **no admin user exists yet**, the app creates one:

| | |
|--|--|
| **Email** | `admin@freelancehub.com` |
| **Password** | `admin123` |

Override with environment variables: `ADMIN_EMAIL`, `ADMIN_PASSWORD`.

Then open the site → **Sign in** with that email and password → **Admin console**.

**If login still fails:** you may already have a database from before this feature, or that email is taken by a client/freelancer. Delete `backend/instance/freelance.db` (dev only) and restart, or set `ADMIN_EMAIL` to a new address.

#### Create Admin manually (optional)

```python
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    admin = User(email='admin@freelancehub.com', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print("Admin created successfully!")
```

### Step 5: Test Features

**As Student:**
1. Login → Dashboard → Browse Projects
2. Click "Submit Bid" on any project
3. Fill bid amount and proposal
4. Check "My Bids" section

**As Client:**
1. Login → Dashboard → "Post New Project"
2. Fill project details (title, description, budget, skills)
3. Submit → View bids from students
4. Accept a bid → Project moves to "In Progress"

**As Admin:**
1. Login → Dashboard → View Statistics
2. Go to User Management
3. Approve students
4. Manage users

## Common Issues

### Port Already in Use
Edit `backend/run.py`, change line:
```python
socketio.run(app, host='0.0.0.0', port=5001)  # Use different port
```

### Database Errors
Delete the database and restart:
```bash
rm backend/freelance.db
python run.py
```

### Module Not Found
Make sure you activated the virtual environment:
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

## Sample Data

Create some test data:

```python
from app import create_app, db
from app.models import User, StudentProfile, ClientProfile, Project, Skill

app = create_app()
with app.app_context():
    # Create student
    student = User(email='john@student.com', role='student')
    student.set_password('password123')
    db.session.add(student)
    db.session.commit()
    
    profile = StudentProfile(
        user_id=student.id,
        name='John Doe',
        college='MIT',
        year='3rd Year',
        bio='Full-stack developer'
    )
    db.session.add(profile)
    
    # Create client
    client = User(email='company@client.com', role='client')
    client.set_password('password123')
    db.session.add(client)
    db.session.commit()
    
    client_profile = ClientProfile(
        user_id=client.id,
        company='Tech Corp',
        description='Leading tech company'
    )
    db.session.add(client_profile)
    
    # Create project
    project = Project(
        client_id=client.id,
        title='Build E-commerce Website',
        description='Need a full-featured online store',
        budget_min=50000,
        budget_max=100000,
        category='Web Development',
        required_skills='Python, Flask, React, PostgreSQL'
    )
    db.session.add(project)
    
    # Create skills
    skills = ['Python', 'Flask', 'React', 'JavaScript', 'PostgreSQL', 'Machine Learning']
    for skill_name in skills:
        skill = Skill(name=skill_name, category='Programming')
        db.session.add(skill)
    
    db.session.commit()
    print("Sample data created!")
```

## Video Tutorial

For a complete walkthrough, check our video guide [coming soon].

## Need Help?

- Check README.md for detailed documentation
- Look at code comments for implementation details
- Open an issue on GitHub

## Next Steps

1. Customize the UI colors in `frontend/static/css/style.css`
2. Add your own AI recommendation logic in `backend/app/ml_models/recommendation.py`
3. Integrate real payment gateway (Razorpay/Stripe)
4. Deploy to production (Heroku, Railway, AWS)

Happy Coding! 🚀
