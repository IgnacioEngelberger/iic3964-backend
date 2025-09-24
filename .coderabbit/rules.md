# CodeRabbit Rules for IIC3964 Backend

## Project Overview
This is a FastAPI backend for a university project (IIC3964) with the following characteristics:
- Python 3.12
- FastAPI framework
- Poetry for dependency management
- Docker containerization
- PostgreSQL/Supabase database
- Redis for caching
- Comprehensive testing with pytest
- CI/CD with GitHub Actions

## Code Review Guidelines

### Python Code Standards
1. **Type Hints**: All functions must have proper type hints
2. **Async/Await**: Use async/await patterns correctly for FastAPI endpoints
3. **Error Handling**: Implement proper exception handling
4. **Documentation**: Add docstrings to all functions and classes
5. **Imports**: Use absolute imports and organize them properly

### FastAPI Specific Rules
1. **Dependencies**: Use FastAPI's dependency injection system
2. **Response Models**: Define Pydantic models for all responses
3. **Status Codes**: Use appropriate HTTP status codes
4. **Validation**: Implement proper input validation
5. **Security**: Check for security vulnerabilities in endpoints

### Database Rules
1. **SQL Injection**: Never use string concatenation for SQL queries
2. **Transactions**: Use proper transaction management
3. **Connection Handling**: Ensure proper database connection handling
4. **Migrations**: Use Alembic for database migrations

### Testing Requirements
1. **Coverage**: Maintain high test coverage
2. **Test Quality**: Write meaningful tests, not just coverage
3. **Fixtures**: Use pytest fixtures appropriately
4. **Async Tests**: Test async functions properly

### Security Checklist
1. **Secrets**: Never commit secrets or API keys
2. **CORS**: Configure CORS properly
3. **Authentication**: Implement proper authentication
4. **Authorization**: Check user permissions
5. **Input Validation**: Validate all inputs

### Performance Considerations
1. **Database Queries**: Optimize database queries
2. **Caching**: Use Redis for caching when appropriate
3. **Async Operations**: Use async for I/O operations
4. **Memory Usage**: Be mindful of memory consumption

### Docker Best Practices
1. **Multi-stage Builds**: Use multi-stage builds for smaller images
2. **Security**: Run containers as non-root user
3. **Health Checks**: Implement proper health checks
4. **Environment Variables**: Use environment variables for configuration

### CI/CD Rules
1. **Workflow Syntax**: Ensure GitHub Actions workflows are correct
2. **Security**: Check for security issues in CI/CD
3. **Dependencies**: Keep dependencies updated
4. **Testing**: Run tests in CI/CD pipeline

## File-Specific Rules

### API Endpoints (`app/api/v1/endpoints/`)
- Must have proper type hints
- Must use FastAPI decorators correctly
- Must have proper error handling
- Must validate inputs with Pydantic models
- Must return appropriate response models

### Models (`app/models/`)
- Must inherit from SQLAlchemy Base
- Must have proper column definitions
- Must include proper relationships
- Must have proper constraints

### Schemas (`app/schemas/`)
- Must inherit from Pydantic BaseModel
- Must have proper field definitions
- Must include validation rules
- Must have proper serialization

### Configuration (`app/core/config.py`)
- Must use Pydantic Settings
- Must have proper environment variable handling
- Must include validation
- Must have secure defaults

### Tests (`tests/`)
- Must test both success and failure cases
- Must use proper fixtures
- Must test async functions correctly
- Must have meaningful assertions

## Common Issues to Flag

### Security Issues
- Hardcoded secrets or API keys
- SQL injection vulnerabilities
- Missing input validation
- Improper error handling that leaks information
- Missing authentication/authorization

### Performance Issues
- N+1 database queries
- Missing database indexes
- Inefficient algorithms
- Memory leaks
- Blocking I/O operations

### Code Quality Issues
- Missing type hints
- Poor error handling
- Code duplication
- Complex functions that should be split
- Missing documentation

### Best Practice Violations
- Not following FastAPI patterns
- Improper use of async/await
- Missing tests
- Poor naming conventions
- Inconsistent code style

## Review Priorities

### High Priority (Must Fix)
- Security vulnerabilities
- Breaking changes
- Performance issues
- Missing tests for critical functionality
- Incorrect type hints

### Medium Priority (Should Fix)
- Code quality issues
- Missing documentation
- Inconsistent patterns
- Minor performance improvements

### Low Priority (Nice to Have)
- Code style improvements
- Additional documentation
- Minor refactoring suggestions
- Optimization opportunities
