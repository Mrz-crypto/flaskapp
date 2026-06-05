# Testing Guide

## Unit Testing

Create test files in `tests/` directory:

```bash
mkdir tests
touch tests/__init__.py
touch tests/test_auth.py
touch tests/test_orders.py
```

### Example Test

`tests/test_auth.py`:
```python
import pytest
from app import create_app
from app.database import get_connection

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'login' in response.data.lower()

def test_register_page(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b'register' in response.data.lower()
```

## Running Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

## Integration Testing

Test the full flow:
1. Register new user
2. Login with credentials
3. Create order
4. View orders
5. Update order
6. Logout

## Performance Testing

Use `locust` for load testing:
```bash
pip install locust
locust -f locustfile.py
```

Example `locustfile.py`:
```python
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def login(self):
        self.client.post('/login', {
            'email': 'admin@admin.com',
            'password': 'admin123'
        })
```

## Test Checklist

- [ ] Authentication flows (login, register, logout)
- [ ] Authorization (admin vs user roles)
- [ ] Order CRUD operations
- [ ] Error handling
- [ ] Input validation
- [ ] Database operations
- [ ] API endpoints
- [ ] Security (SQL injection, XSS, CSRF)
