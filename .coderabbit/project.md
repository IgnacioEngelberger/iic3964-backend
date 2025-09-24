# IIC3964 Backend Project Configuration

## Project Information
- **Name**: IIC3964 Backend
- **Type**: University Project Backend API
- **Framework**: FastAPI
- **Language**: Python 3.12
- **Database**: PostgreSQL/Supabase
- **Cache**: Redis
- **Containerization**: Docker
- **CI/CD**: GitHub Actions

## Architecture Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Database      │
│   (React/Vue)   │◄──►│   Backend       │◄──►│   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │     Redis       │
                       │     Cache       │
                       └─────────────────┘
```

## Key Components

### API Layer (`app/api/`)
- RESTful API endpoints
- Versioned API (v1)
- Health check endpoints
- CRUD operations for resources

### Core Layer (`app/core/`)
- Configuration management
- Database connection
- Security settings
- Environment variables

### Models Layer (`app/models/`)
- SQLAlchemy models
- Database schema definitions
- Relationships between entities

### Schemas Layer (`app/schemas/`)
- Pydantic models
- Request/response validation
- Serialization/deserialization

### Testing (`tests/`)
- Unit tests with pytest
- Integration tests
- API endpoint tests
- Database tests

## Development Workflow

### Local Development
1. Use Poetry for dependency management
2. Run tests with `make test`
3. Use linting with `make lint`
4. Format code with `make format`
5. Run server with `make dev`

### Docker Development
1. Use `make docker-dev` for development
2. Use `make docker-test` for testing
3. Use `make docker-lint` for linting

### CI/CD Pipeline
1. GitHub Actions runs on every push/PR
2. Tests, linting, and type checking
3. Docker image building and testing
4. Deployment to production (when configured)

## Code Review Focus Areas

### Security
- Input validation
- SQL injection prevention
- Authentication/authorization
- CORS configuration
- Secret management

### Performance
- Database query optimization
- Async/await usage
- Caching strategies
- Memory usage
- API response times

### Code Quality
- Type hints
- Error handling
- Documentation
- Test coverage
- Code organization

### Best Practices
- FastAPI patterns
- Python conventions
- Docker best practices
- CI/CD practices
- Database design

## Common Patterns

### API Endpoints
```python
@router.get("/items/", response_model=List[Item])
async def get_items(db: Session = Depends(get_db)) -> List[Item]:
    # Implementation
```

### Database Models
```python
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
```

### Pydantic Schemas
```python
class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
```

### Tests
```python
def test_get_items(client: TestClient):
    response = client.get("/api/v1/items/")
    assert response.status_code == 200
```

## Review Checklist

### Before Review
- [ ] Code compiles without errors
- [ ] Tests pass
- [ ] Linting passes
- [ ] Type checking passes
- [ ] Documentation is updated

### During Review
- [ ] Security vulnerabilities checked
- [ ] Performance implications considered
- [ ] Code quality assessed
- [ ] Best practices followed
- [ ] Tests are adequate

### After Review
- [ ] All feedback addressed
- [ ] Tests still pass
- [ ] Documentation updated
- [ ] Ready for merge

## Integration Points

### External Services
- Supabase (Production Database)
- Redis (Caching)
- GitHub Actions (CI/CD)
- Docker Hub (Container Registry)

### Development Tools
- Poetry (Dependency Management)
- Pytest (Testing)
- Black (Code Formatting)
- isort (Import Sorting)
- Flake8 (Linting)
- MyPy (Type Checking)
- Pre-commit (Git Hooks)

## Deployment

### Development
- Local SQLite database
- Local Redis instance
- Hot reload enabled

### Production
- Supabase PostgreSQL
- Redis cloud service
- Docker containers
- Environment variables
- Health checks
- Monitoring
