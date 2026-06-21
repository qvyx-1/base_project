---
name: api-routes
description: 'Scaffold FastAPI/HTTP API routes for base_project. Use for creating routers, request/response schemas, middleware, authentication, or any HTTP API layer.'
argument-hint: 'API endpoint names and methods'
---

# API Routes

Scaffold HTTP API routes for `base_project` using FastAPI with proper structure, validation, and documentation.

## When to Use

- Adding REST API endpoints
- Creating request/response schemas
- Setting up authentication middleware
- Configuring CORS, rate limiting, or other middleware
- Adding OpenAPI/Swagger customization

## Procedure

### 1. Add Dependencies

```toml
# In pyproject.toml [project.dependencies]:
"fastapi>=0.115"
"uvicorn>=0.30"
"httpx>=0.27"          # for test client
```

```bash
uv sync
```

### 2. Create API Package Structure

```bash
mkdir -p src/base_project/api/schemas
touch src/base_project/api/__init__.py
touch src/base_project/api/schemas/__init__.py
```

### 3. Create Request/Response Schemas

`src/base_project/api/schemas/user.py`:

```python
"""User API schemas."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Schema for creating a user."""

    username: str
    email: EmailStr


class UserResponse(BaseModel):
    """Schema for user response."""

    id: int
    username: str
    email: str

    model_config = {"from_attributes": True}
```

`src/base_project/api/schemas/__init__.py`:

```python
"""API schemas package."""

from base_project.api.schemas.user import UserCreate, UserResponse

__all__ = ["UserCreate", "UserResponse"]
```

### 4. Create Router

`src/base_project/api/users.py`:

```python
"""Users API router."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from base_project.api.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate) -> UserResponse:
    """Create a new user.

    Args:
        user: User creation request body.

    Returns:
        Created user response.
    """
    # TODO: Implement actual user creation logic
    return UserResponse(
        id=1,
        username=user.username,
        email=user.email,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int) -> UserResponse:
    """Get a user by ID.

    Args:
        user_id: User identifier.

    Returns:
        User response.

    Raises:
        HTTPException: If user not found.
    """
    # TODO: Implement actual user lookup logic
    raise HTTPException(status_code=404, detail="User not found")
```

### 5. Create App Factory

`src/base_project/api/app.py`:

```python"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI

from base_project.api.users import router as users_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI app instance.
    """
    app = FastAPI(
        title="Base Project API",
        version="0.1.0",
        description="API for base_project",
    )

    app.include_router(users_router)

    return app
```

### 6. Update main.py to Support Server Mode

Extend `main.py`:

```python
def run_server(config: AppConfig) -> None:
    """Start the FastAPI server.

    Args:
        config: Application configuration.
    """
    import uvicorn

    app = create_app()
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        log_level="info" if not config.debug else "debug",
    )
```

### 7. Write Tests

`tests/test_api.py`:

```python
"""Tests for API endpoints."""

import pytest

from fastapi.testclient import TestClient

from base_project.api.app import create_app


@pytest.fixture
def client() -> TestClient:
    """Create test client fixture.

    Returns:
        TestClient instance.
    """
    app = create_app()
    return TestClient(app)


class TestUsersAPI:
    """Test cases for users API."""

    def test_create_user(self, client: TestClient) -> None:
        """Test user creation endpoint."""
        response = client.post(
            "/users/",
            json={"username": "testuser", "email": "test@example.com"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"

    def test_get_user_not_found(self, client: TestClient) -> None:
        """Test getting non-existent user returns 404."""
        response = client.get("/users/999")
        assert response.status_code == 404
```

### 8. Validate

```bash
uv run ruff check .
uv run mypy src/
uv run pytest
```

## API Structure Reference

```
src/base_project/api/
├── __init__.py
├── app.py              # App factory
├── users.py            # Router for /users
├── <resource>.py       # Additional routers
└── schemas/
    ├── __init__.py
    └── <resource>.py   # Pydantic schemas
```

## Common Patterns

### Pagination

```python
from typing import Generic, TypeVar
from fastapi import Query

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    items: list[T]
    total: int
    page: int
    size: int

@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[UserResponse]:
    ...
```

### Authentication Middleware

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Extract and validate the bearer token.

    Args:
        credentials: Bearer token credentials.

    Returns:
        Decoded user identifier.

    Raises:
        HTTPException: If token is invalid.
    """
    # TODO: Implement token validation
    return credentials.credentials
```

## Anti-Patterns

- **Don't** put business logic in routers — delegate to services
- **Don't** skip request/response schemas — always validate input
- **Don't** use `Any` types — be specific with Pydantic models
- **Don't** forget to add tags for OpenAPI grouping
- **Don't** expose internal model fields in responses
