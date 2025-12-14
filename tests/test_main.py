"""Basic tests for the blog platform"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base
from app.db_utils import get_db

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestAuth:
    """Test authentication endpoints"""
    
    def test_register_user(self):
        """Test user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "password123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert "id" in data
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_login(self):
        """Test user login"""
        # Register user first
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "password123"
            }
        )
        
        # Login
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self):
        """Test login with wrong password"""
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "password123"
            }
        )
        
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401


class TestPosts:
    """Test post endpoints"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get authentication headers"""
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "password123"
            }
        )
        
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "password123"
            }
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_create_post(self, auth_headers):
        """Test creating a post"""
        response = client.post(
            "/api/v1/posts",
            json={
                "post_title": "Test Post",
                "post_content": "This is a test post content",
                "is_published": True
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["post_title"] == "Test Post"
        assert data["post_content"] == "This is a test post content"
    
    def test_get_posts(self):
        """Test getting all posts"""
        response = client.get("/api/v1/posts")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_post_unauthorized(self):
        """Test creating post without authentication"""
        response = client.post(
            "/api/v1/posts",
            json={
                "post_title": "Test Post",
                "post_content": "This is a test post content"
            }
        )
        assert response.status_code == 401
    
    def test_update_post(self, auth_headers):
        """Test updating a post"""
        # Create post
        create_response = client.post(
            "/api/v1/posts",
            json={
                "post_title": "Original Title",
                "post_content": "Original content",
                "is_published": True
            },
            headers=auth_headers
        )
        post_id = create_response.json()["id"]
        
        # Update post
        response = client.put(
            f"/api/v1/posts/{post_id}",
            json={
                "post_title": "Updated Title",
                "post_content": "Updated content"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["post_title"] == "Updated Title"
        assert data["post_content"] == "Updated content"
    
    def test_delete_post(self, auth_headers):
        """Test deleting a post"""
        # Create post
        create_response = client.post(
            "/api/v1/posts",
            json={
                "post_title": "Test Post",
                "post_content": "Test content",
                "is_published": True
            },
            headers=auth_headers
        )
        post_id = create_response.json()["id"]
        
        # Delete post
        response = client.delete(
            f"/api/v1/posts/{post_id}",
            headers=auth_headers
        )
        assert response.status_code == 204
        
        # Verify deleted
        get_response = client.get(f"/api/v1/posts/{post_id}")
        assert get_response.status_code == 404


class TestUsers:
    """Test user endpoints"""
    
    def test_get_users(self):
        """Test getting all users"""
        response = client.get("/api/v1/users")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_search_users(self):
        """Test searching users"""
        # Create user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "searchtest@example.com",
                "username": "searchuser",
                "password": "password123"
            }
        )
        
        # Search
        response = client.get("/api/v1/users?search=searchuser")
        assert response.status_code == 200
        users = response.json()
        assert len(users) > 0
        assert any(user["username"] == "searchuser" for user in users)


class TestComments:
    """Test comment functionality"""
    
    @pytest.fixture
    def setup_post(self):
        """Create a user and post for testing"""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "password123"
            }
        )
        
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create post
        post_response = client.post(
            "/api/v1/posts",
            json={
                "post_title": "Test Post",
                "post_content": "Test content",
                "is_published": True
            },
            headers=headers
        )
        post_id = post_response.json()["id"]
        
        return {"headers": headers, "post_id": post_id}
    
    def test_create_comment(self, setup_post):
        """Test creating a comment"""
        response = client.post(
            f"/api/v1/posts/{setup_post['post_id']}/comments",
            json={"comment_text": "Great post!"},
            headers=setup_post["headers"]
        )
        assert response.status_code == 201
        data = response.json()
        assert data["comment_text"] == "Great post!"
    
    def test_get_comments(self, setup_post):
        """Test getting post comments"""
        # Create comment
        client.post(
            f"/api/v1/posts/{setup_post['post_id']}/comments",
            json={"comment_text": "Test comment"},
            headers=setup_post["headers"]
        )
        
        # Get comments
        response = client.get(f"/api/v1/posts/{setup_post['post_id']}/comments")
        assert response.status_code == 200
        comments = response.json()
        assert len(comments) > 0
        assert comments[0]["comment_text"] == "Test comment"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
