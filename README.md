# Flask Order Management Application

A Flask-based web application for managing users, orders, and authentication with role-based access control (Admin/User).

## Features

- **User Authentication**: Secure login and registration with password hashing
- **Role-Based Access**: Admin and regular user roles
- **Order Management**: Create, read, update, and delete orders
- **Database Integration**: MySQL database with proper schema
- **Error Handling**: Comprehensive error pages (403, 404, 500)
- **Logging**: Activity and error logging

## Prerequisites

- Python 3.8+
- MySQL Server
- pip (Python package manager)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd flaskapp
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and update the values:
```bash
cp .env.example .env
```

Edit `.env` with your database credentials:
```
FLASK_ENV=development
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here-change-in-production
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=blackeye
```

### 5. Create Database
```sql
CREATE DATABASE blackeye;
```

### 6. Run the Application
```bash
python run.py
```

The app will be available at `http://localhost:5000`

## Default Credentials

- **Email**: admin@admin.com
- **Password**: admin123

⚠️ **Change these credentials immediately in production!**

## Project Structure

```
flaskapp/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── database.py           # Database connection & initialization
│   ├── controllers/
│   │   ├── auth.py           # Authentication decorators
│   │   ├── authcontroller.py # Auth logic (login, register, dashboard)
│   │   └── ordercontroller.py # Order management logic
│   ├── routes/
│   │   ├── authroutes.py     # Auth endpoints
│   │   └── orderroutes.py    # Order API endpoints
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── style2.js
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── 403.html
│       ├── 404.html
│       └── 500.html
├── config.py                 # Configuration (uses environment variables)
├── run.py                    # Entry point
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## API Endpoints

### Authentication
- `GET /` - Home (redirects to login/dashboard)
- `GET/POST /login` - User login
- `GET/POST /register` - User registration
- `GET /logout` - User logout
- `GET/POST /dashboard` - User dashboard

### Orders (with authentication)
- `GET /orders/` - List all orders
- `GET /orders/<id>` - Get specific order
- `POST /orders/` - Create order
- `PUT /orders/<id>` - Update order
- `DELETE /orders/<id>` - Delete order

## Configuration

All sensitive settings are managed via environment variables in `.env`:

- `FLASK_ENV`: Application environment (development/production)
- `FLASK_DEBUG`: Debug mode (True/False)
- `SECRET_KEY`: Session encryption key (change in production!)
- `MYSQL_HOST`: Database host
- `MYSQL_USER`: Database user
- `MYSQL_PASSWORD`: Database password
- `MYSQL_DATABASE`: Database name

## Security Notes

🔒 **Important for Production**:
1. Change `SECRET_KEY` to a secure random value
2. Use strong database passwords
3. Set `FLASK_DEBUG=False` in production
4. Use HTTPS only
5. Implement CSRF protection
6. Set secure session cookies
7. Validate and sanitize all user inputs
8. Use environment variables for all secrets
9. Implement rate limiting
10. Add CORS headers if needed

## Logging

Application logs are displayed in the console and include:
- Database connection status
- User login/logout events
- Failed authentication attempts
- Database errors
- Server errors

## Error Handling

The application includes error handlers for:
- **403 Forbidden** - Access denied
- **404 Not Found** - Page not found
- **500 Internal Server Error** - Server error

## Development

### Running in Debug Mode
```bash
FLASK_DEBUG=True python run.py
```

### Database Initialization
Tables are automatically created on application startup:
- `users` - User accounts
- `orders` - User orders

## Troubleshooting

### Database Connection Failed
- Ensure MySQL is running
- Verify credentials in `.env`
- Check database exists

### Port Already in Use
- Change port in `run.py` or use: `python run.py -p 5001`

### Module Import Errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

## License

[Your License Here]

## Support

For issues or questions, please contact [Your Contact Info].
