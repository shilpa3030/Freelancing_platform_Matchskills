# FreelanceHub - AI-Powered Freelancing Platform

A comprehensive freelancing platform built with Flask (Python) backend and vanilla JavaScript frontend, featuring AI-powered recommendations, real-time chat, and secure escrow payments.

**Quick start:** [docs/QUICKSTART.md](docs/QUICKSTART.md)

## Repository layout

| Path | Purpose |
|------|---------|
| `backend/` | Flask application (`run.py`, `app/` package, dependencies) |
| `frontend/` | Jinja templates and static files (CSS, JS, images); paths are wired in `backend/app/__init__.py` |
| `docs/` | Extra documentation (quick start guide) |

## 🚀 Features

### For Students/Freelancers
- ✅ User Registration & Authentication
- ✅ Profile Management with Skills
- ✅ Browse Projects
- ✅ AI-Powered Project Recommendations
- ✅ Submit Bids on Projects
- ✅ Real-time Chat with Clients
- ✅ Track Project Status
- ✅ Receive Ratings & Reviews
- ✅ Analytics Dashboard

### For Clients/Employers
- ✅ Post Projects
- ✅ View and Manage Bids
- ✅ AI-Powered Student Recommendations
- ✅ Accept/Reject Bids
- ✅ Escrow Payment System
- ✅ Rate Freelancers
- ✅ Real-time Communication
- ✅ Project Management Dashboard

### For Admins
- ✅ User Management
- ✅ Approve/Reject Students
- ✅ Deactivate Users
- ✅ Platform Analytics
- ✅ Monitor Projects

## 🛠️ Tech Stack

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **Flask-JWT-Extended** - Authentication
- **Flask-SocketIO** - Real-time communication
- **Scikit-learn** - ML recommendations
- **Pandas & NumPy** - Data processing

### Frontend
- **HTML5, CSS3, JavaScript**
- **Bootstrap 5** - UI framework
- **jQuery** - DOM manipulation
- **Chart.js** - Analytics visualization
- **Socket.IO** - Real-time chat

### Database
- **SQLite** (Development)
- **PostgreSQL/MySQL** (Production)

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser

### Step 1: Clone the Repository
```bash
cd freelance-platform
```

### Step 2: Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables (Optional)

Create a `.env` file in the `backend` directory:

```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///freelance.db
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret
```

### Step 4: Initialize Database

```bash
# From backend directory
python run.py
```

This will automatically create all database tables.

### Step 5: Run the Application

```bash
python run.py
```

The application will start on `http://localhost:5000`

## 🎯 Usage

### 1. Register as Student/Freelancer
- Go to `http://localhost:5000`
- Click "Register"
- Select "Student/Freelancer"
- Fill in your details
- Login with your credentials

### 2. Register as Client/Employer
- Click "Register"
- Select "Client/Employer"
- Fill in company details
- Login and start posting projects

### 3. Admin Access
To create an admin user, run this in Python shell:

```python
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    admin = User(email='admin@example.com', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
```

## 📱 Key Workflows

### Student Workflow
1. Register → Complete Profile → Add Skills
2. Browse Projects or View AI Recommendations
3. Submit Bids with Proposals
4. Chat with Clients
5. Complete Project → Receive Payment & Rating

### Client Workflow
1. Register → Complete Company Profile
2. Post New Project with Details
3. Review Bids from Students
4. Accept Bid → Create Escrow
5. Communicate via Chat
6. Mark Complete → Release Payment → Rate Student

### Admin Workflow
1. Login as Admin
2. View Platform Statistics
3. Manage Users (Approve/Deactivate)
4. Monitor Projects and Transactions

## 🔐 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- SQL injection protection (SQLAlchemy ORM)
- CORS configuration
- Secure escrow payment system

## 🤖 AI/ML Features

### Project Recommendation System
Uses TF-IDF and cosine similarity to match:
- Student skills with project requirements
- Project descriptions with student expertise
- Returns top 10 best matches

### Student Recommendation System
Helps clients find best freelancers by:
- Analyzing project requirements
- Matching with student skills and experience
- Considering ratings and past projects

### Analytics Dashboard
- Platform-wide statistics
- Trending skills analysis
- Category distribution
- Monthly trends
- Individual performance metrics

## 📊 Database Schema

### Main Tables
- **Users** - Authentication and role management
- **StudentProfile** - Freelancer details and skills
- **ClientProfile** - Company information
- **Projects** - Posted projects
- **Bids** - Student proposals
- **Messages** - Chat system
- **Reviews** - Ratings and feedback
- **EscrowAccount** - Payment management
- **Skills** - Available skills
- **StudentSkills** - Student-skill mapping

## 🔄 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Student
- `GET /api/student/profile` - Get profile
- `PUT /api/student/profile` - Update profile
- `POST /api/student/skills` - Add skill
- `GET /api/student/projects/browse` - Browse projects
- `POST /api/student/projects/:id/bid` - Submit bid
- `GET /api/student/recommendations` - AI recommendations

### Client
- `POST /api/client/projects` - Create project
- `GET /api/client/projects` - Get all projects
- `GET /api/client/projects/:id/bids` - View bids
- `POST /api/client/bids/:id/accept` - Accept bid
- `POST /api/client/reviews` - Submit review

### Admin
- `GET /api/admin/users` - Get all users
- `POST /api/admin/students/approve/:id` - Approve student
- `POST /api/admin/users/:id/deactivate` - Deactivate user
- `GET /api/admin/stats` - Platform statistics

### Payment
- `POST /api/payment/create-escrow` - Create escrow
- `POST /api/payment/release-escrow/:id` - Release payment
- `POST /api/payment/dispute/:id` - Raise dispute

## 🎨 Customization

### Change Color Scheme
Edit `frontend/static/css/style.css`:

```css
:root {
    --primary-color: #4a90e2;    /* Main brand color */
    --secondary-color: #f39c12;  /* Accent color */
    --success-color: #27ae60;    /* Success actions */
    --danger-color: #e74c3c;     /* Danger/delete actions */
}
```

### Modify Recommendation Algorithm
Edit `backend/app/ml_models/recommendation.py`:
- Adjust `max_features` parameter for TF-IDF
- Change similarity threshold
- Add additional factors (rating, experience, etc.)

## 📈 Future Enhancements

- [ ] Video interview integration
- [ ] Advanced filtering and search
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Blockchain-based escrow
- [ ] Skill assessment tests
- [ ] Milestone-based payments
- [ ] Dispute resolution system
- [ ] File sharing in chat
- [ ] Calendar integration

## 🐛 Troubleshooting

### Database Issues
```bash
# Reset database
rm backend/freelance.db
python run.py
```

### Port Already in Use
Change port in `backend/run.py`:
```python
socketio.run(app, host='0.0.0.0', port=5001)  # Change port
```

### CORS Errors
Check `backend/app/__init__.py` CORS configuration

### Socket.IO Connection Issues
Ensure both backend server and frontend are running
Check browser console for connection errors

## 📝 License

This project is open source and available for educational purposes.

## 👥 Contributors

Built as a student project for freelancing platform development.

## 📧 Support

For issues and questions, please create an issue in the repository.

## 🙏 Acknowledgments

- Flask documentation
- Bootstrap components
- Scikit-learn ML library
- Socket.IO for real-time features

---

**Note**: This is a demonstration project. For production use, implement additional security measures, comprehensive testing, and proper deployment configuration.
