# Contributing Guidelines

## Code Style

- Follow PEP 8 conventions
- Use meaningful variable names
- Add docstrings for functions
- Keep functions focused and single-purpose

## Testing

Before submitting changes:
1. Test all authentication flows
2. Verify database operations
3. Check error handling
4. Test with different user roles

## Security Review Checklist

- [ ] No hardcoded secrets
- [ ] Input validation on all forms
- [ ] SQL injection protection (parametrized queries)
- [ ] Authentication checks on protected routes
- [ ] Error messages don't leak sensitive info
- [ ] Proper password hashing

## Commit Messages

Use clear, descriptive commit messages:
- `feat: Add user authentication`
- `fix: Correct order status update logic`
- `docs: Update README with setup instructions`
- `refactor: Simplify database connection logic`

## Pull Requests

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Commit with clear messages
4. Push to your fork
5. Create a Pull Request with description of changes
