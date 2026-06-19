# Flask Order Management Application

A Flask web application for user authentication, role-based dashboards, and basic order management backed by MySQL.

## Features

- User registration and login with hashed passwords
- Admin and user roles
- Dashboard-based order creation and updates
- JSON order API for authenticated users
- MySQL schema initialization at startup
- Error pages for 403, 404, and 500 responses
- Environment-based configuration
- Console logging for key app events

## Requirements

- Python 3.8+
- MySQL Server
- pip

## Setup

1. Create and activate a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Create the database.

```sql
CREATE DATABASE blackeye;
```

4. Copy the environment template and update values.

```bash
copy .env.example .env
```

5. Run the application.

```bash
python run.py
```

The app runs at `http://localhost:5000`.

## Default Admin

- Email: `admin@blackeye.com`
- Password: `admin123`

Change the default password before using the app outside local development.

## Project Structure

```text
flaskapp/
|-- app/
|   |-- __init__.py
|   |-- auth.py
|   |-- database.py
|   |-- controllers/
|   |   |-- authcontroller.py
|   |   `-- ordercontroller.py
|   |-- routes/
|   |   |-- authroutes.py
|   |   `-- orderroutes.py
|   |-- static/
|   |   `-- css/style.css
|   `-- templates/
|       |-- base.html
|       |-- login.html
|       |-- register.html
|       |-- dashboard.html
|       |-- 403.html
|       |-- 404.html
|       `-- 500.html
|-- config.py
|-- run.py
|-- requirements.txt
|-- requirements-dev.txt
|-- setup_database.sql
`-- README.md
```

## Routes

- `GET /` redirects users to login or dashboard
- `GET, POST /login` handles login
- `GET, POST /register` handles registration
- `GET, POST /dashboard` shows and updates dashboard data
- `GET /logout` clears the session
- `GET /orders/` lists visible orders
- `GET /orders/<id>` shows one visible order
- `POST /orders/` creates an order
- `PUT /orders/<id>` updates an order
- `DELETE /orders/<id>` deletes an order

## Configuration

Settings are read from environment variables:

- `FLASK_ENV`
- `FLASK_DEBUG`
- `SECRET_KEY`
- `MYSQL_HOST`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`

## Development Checks

```bash
python -m compileall app run.py config.py
pytest
```

## Production Notes

- Use a strong `SECRET_KEY`
- Set `FLASK_DEBUG=False`
- Change the default admin password
- Use HTTPS behind a production web server
- Back up the MySQL database regularly
- Keep credentials in environment variables, not source files
