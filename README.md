# TaskMe

Modern commitment-based ToDo application with rewards, proof mechanisms, duels, teams, and global challenges.

## Features

- **Commitment-Based Tasks**: Stake points on task completion
- **Proof Mechanisms**: Photo, Video, Document, Peer Verification, Sensor Data
- **Rewards System**: Earn points, unlock badges and achievements
- **Duels**: One-on-one challenges with friends
- **Teams**: Collaborate with others on team challenges
- **Community**: Share achievements and participate in global challenges
- **Gamification**: Level system, leaderboards, and rewards

## Tech Stack

### Backend
- Django 5.0
- Django REST Framework
- PostgreSQL / SQLite
- JWT Authentication
- Security: OWASP compliance, Zero-Trust, CSP, CORS

### Frontend
- React
- Modern UI/UX (Apple-inspired design)
- Responsive design

## Security Features

- OWASP best practices implementation
- Zero-Trust architecture
- Least privilege access control
- Content Security Policy (CSP)
- CORS configuration
- Rate limiting
- Secure password validation
- JWT token-based authentication
- Input validation and sanitization

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL (optional, SQLite used by default)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm start
```

The app will be available at `http://localhost:3000/`

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI Schema: `http://localhost:8000/api/schema/`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login (JWT)
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile
- `POST /api/auth/profile/change-password/` - Change password
- `GET /api/auth/leaderboard/` - Get top users

### Tasks
- `GET /api/tasks/` - List user's tasks
- `POST /api/tasks/` - Create new task
- `GET /api/tasks/{id}/` - Get task details
- `PUT /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task
- `POST /api/tasks/{id}/complete/` - Mark task as completed
- `POST /api/tasks/{id}/submit_proof/` - Submit proof for task

### Task Proofs
- `GET /api/proofs/` - List user's proofs
- `GET /api/proofs/{id}/` - Get proof details
- `POST /api/proofs/{id}/approve/` - Approve proof (peer verification)
- `POST /api/proofs/{id}/reject/` - Reject proof

## Development

### Code Style
- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React code
- Write descriptive commit messages
- Add tests for new features

### Testing

Backend tests:
```bash
cd backend
python manage.py test
```

Frontend tests:
```bash
cd frontend
npm test
```

## Architecture Decisions

### Backend Architecture
- **Django REST Framework**: Chosen for robust API development
- **JWT Authentication**: Stateless authentication for better scalability
- **Custom User Model**: Email-based authentication with username
- **Modular App Structure**: Separate apps for accounts, tasks, rewards, challenges, teams

### Security Implementation
- **OWASP Top 10**: Addressed common vulnerabilities
- **Zero-Trust**: All requests require authentication (except registration/login)
- **Least Privilege**: Users can only access their own data
- **CSP**: Content Security Policy headers to prevent XSS
- **Rate Limiting**: API throttling to prevent abuse
- **Password Validation**: Strong password requirements

### Database Design
- **Indexed Fields**: Optimized queries with strategic indexes
- **Relationships**: Clear foreign key relationships
- **Timestamps**: Track creation and modification times
- **Soft Deletes**: Consider data preservation where needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.
