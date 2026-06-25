# Testing Guide

## Quick Check

Run the current test suite:

```bash
python -m pytest tests
```

Compile-check the application:

```bash
python -m compileall app run.py config.py tests
```

## Current Coverage

- Guest users are redirected from protected pages.
- Logged-in users can access protected pages.
- Regular users are redirected away from admin pages.
- Admin users can access admin-protected pages.
- Sessions can be cleared cleanly.

## Manual Flow

1. Register a new user.
2. Log in with that user.
3. Create an order.
4. Update the order status.
5. Log out.
6. Log in as the admin user.
7. Review users and orders from the dashboard.

## Test Checklist

- [ ] Authentication flows
- [ ] Authorization for admin and user roles
- [ ] Order create, read, update, and delete paths
- [ ] Error pages
- [ ] Input validation
- [ ] Database setup and seed behavior
- [ ] JSON order endpoints
