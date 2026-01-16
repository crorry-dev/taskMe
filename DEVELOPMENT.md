# TaskMe Development Guide

## Quick Start for Developers

This guide helps you get TaskMe running on your local machine for development.

## Prerequisites

- Python 3.12+
- Node.js 18+
- Git
- Code editor (VS Code recommended)

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/crorry-dev/taskMe.git
cd taskMe
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

### 3. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm start
```

Frontend will be available at `http://localhost:3000`

## Development Workflow

### Backend Development

#### Running Tests

```bash
cd backend
source venv/bin/activate
python manage.py test
```

#### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

#### Accessing Admin Interface

Visit `http://localhost:8000/admin/` and log in with your superuser credentials.

#### API Documentation

Visit `http://localhost:8000/api/docs/` for interactive Swagger documentation.

#### Django Shell

```bash
python manage.py shell
```

### Frontend Development

#### Running Tests

```bash
cd frontend
npm test
```

#### Building for Production

```bash
npm run build
```

#### Code Formatting

```bash
npm run format  # (if configured)
```

## Code Structure

### Backend Structure

```
backend/
├── accounts/           # User authentication and profiles
├── tasks/             # Task management
├── rewards/           # Rewards and achievements
├── challenges/        # Duels and challenges
├── teams/             # Team and community features
├── taskme_project/    # Main project settings
├── manage.py          # Django management script
└── requirements.txt   # Python dependencies
```

### Frontend Structure

```
frontend/
├── public/            # Static files
├── src/
│   ├── components/    # Reusable React components
│   ├── contexts/      # React contexts (Auth, etc.)
│   ├── pages/         # Page components
│   ├── services/      # API services
│   ├── utils/         # Utility functions
│   └── App.js         # Main app component
└── package.json       # Node dependencies
```

## Common Tasks

### Adding a New API Endpoint

1. Create view in appropriate app's `views.py`
2. Add URL pattern to app's `urls.py`
3. Create/update serializer in `serializers.py`
4. Write tests in `tests.py`
5. Update API documentation

### Adding a New Frontend Page

1. Create component in `src/pages/`
2. Add route in `App.js`
3. Create necessary services in `src/services/`
4. Write tests

### Database Changes

1. Modify models in `models.py`
2. Create migrations: `python manage.py makemigrations`
3. Review migration file
4. Apply migration: `python manage.py migrate`
5. Update serializers if needed

## Debugging

### Backend Debugging

#### Using Django Debug Toolbar

Install debug toolbar:
```bash
pip install django-debug-toolbar
```

Add to settings (development only):
```python
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

#### Print Debugging

```python
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

#### Django Shell

```bash
python manage.py shell
>>> from accounts.models import User
>>> users = User.objects.all()
>>> print(users)
```

### Frontend Debugging

#### React DevTools

Install React DevTools browser extension for debugging React components.

#### Console Logging

```javascript
console.log('Debug:', data);
```

#### Network Inspection

Use browser DevTools Network tab to inspect API calls.

## Testing

### Backend Testing

#### Unit Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts

# Run specific test
python manage.py test accounts.tests.UserModelTest.test_user_creation

# With coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

#### API Testing

```bash
# Using curl
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "pass123"}'
```

### Frontend Testing

```bash
# Run tests
npm test

# With coverage
npm test -- --coverage

# E2E tests (if configured)
npm run test:e2e
```

## Code Style

### Python

Follow PEP 8:
```bash
# Install flake8
pip install flake8

# Check code
flake8 .

# Auto-format with black
pip install black
black .
```

### JavaScript

Follow project ESLint config:
```bash
# Check code
npm run lint

# Auto-fix
npm run lint:fix
```

## Git Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `refactor/description` - Code refactoring
- `docs/description` - Documentation updates

### Commit Messages

Use conventional commits:
```
feat: add user profile editing
fix: resolve login token refresh issue
docs: update API documentation
refactor: simplify task creation logic
test: add unit tests for rewards
```

### Making Changes

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push to remote
git push origin feature/new-feature

# Create pull request on GitHub
```

## Environment Variables

### Backend (.env)

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (.env)

```env
REACT_APP_API_URL=http://localhost:8000/api
```

## Troubleshooting

### Backend Issues

#### Database locked error
```bash
# Close all connections and restart server
```

#### Import errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

#### Port already in use
```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
python manage.py runserver 8001
```

### Frontend Issues

#### Module not found
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

#### Port already in use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

#### CORS errors
- Check backend CORS settings
- Ensure API URL is correct in .env
- Check browser console for details

## Useful Commands

### Backend

```bash
# Create new app
python manage.py startapp appname

# Shell with auto-imports
python manage.py shell_plus  # (requires django-extensions)

# Show all URLs
python manage.py show_urls  # (requires django-extensions)

# Reset database
python manage.py flush

# Dump/load data
python manage.py dumpdata > data.json
python manage.py loaddata data.json
```

### Frontend

```bash
# Check for outdated packages
npm outdated

# Update packages
npm update

# Audit security
npm audit
npm audit fix
```

## Best Practices

### Backend

1. Always use serializers for validation
2. Use permissions classes for access control
3. Write tests for new features
4. Use Django ORM, avoid raw SQL
5. Keep views thin, logic in models/services
6. Use environment variables for config

### Frontend

1. Use functional components with hooks
2. Keep components small and focused
3. Use Context for global state
4. Handle errors gracefully
5. Show loading states
6. Validate forms client-side
7. Keep API calls in services

## Getting Help

- Check documentation in `/docs`
- Read inline code comments
- Search GitHub issues
- Ask in project discussions
- Stack Overflow for general questions

## Contributing

See CONTRIBUTING.md for contribution guidelines (to be created).

## Resources

### Django
- [Django Documentation](https://docs.djangoproject.com/)
- [DRF Documentation](https://www.django-rest-framework.org/)
- [Django Best Practices](https://docs.djangoproject.com/en/stable/misc/design-philosophies/)

### React
- [React Documentation](https://react.dev/)
- [Material-UI Documentation](https://mui.com/)
- [React Router Documentation](https://reactrouter.com/)

### Security
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
