"""Integration tests for task API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.api.v1.tasks import router
from src.main import app
from src.models.task import Task


@pytest.fixture(name="test_user_id")
def test_user_id_fixture():
    """Return test user ID."""
    return "test-user-123"


@pytest.fixture(name="test_session")
def test_session_fixture():
    """Create test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(test_session: Session, test_user_id: str):
    """Create test client with mocked authentication."""
    from src.core.database import get_session
    from src.core.dependencies import get_current_user_id

    def override_get_current_user_id():
        return test_user_id

    def override_get_session():
        yield test_session

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


class TestCreateTask:
    """Test POST /api/v1/tasks."""

    def test_create_task_success(self, client: TestClient):
        """Test creating a task successfully."""
        response = client.post(
            "/api/v1/tasks",
            json={"title": "New Task", "description": "Description"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert data["description"] == "Description"
        assert data["completed"] is False
        assert "id" in data
        assert "created_at" in data

    def test_create_task_minimal(self, client: TestClient):
        """Test creating task with only title."""
        response = client.post(
            "/api/v1/tasks",
            json={"title": "Minimal Task"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Minimal Task"
        assert data["description"] is None

    def test_create_task_validation_error(self, client: TestClient):
        """Test validation error for empty title."""
        response = client.post(
            "/api/v1/tasks",
            json={"title": ""},
        )
        assert response.status_code == 422  # Validation error


class TestListTasks:
    """Test GET /api/v1/tasks."""

    def test_list_tasks_empty(self, client: TestClient):
        """Test listing tasks when none exist."""
        response = client.get("/api/v1/tasks")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["tasks"] == []

    def test_list_tasks_with_data(self, client: TestClient, test_session: Session, test_user_id: str):
        """Test listing tasks with data."""
        # Create tasks directly
        task1 = Task(user_id=test_user_id, tags=[], title="Task 1")
        task2 = Task(user_id=test_user_id, tags=[], title="Task 2", completed=True)
        test_session.add(task1)
        test_session.add(task2)
        test_session.commit()

        response = client.get("/api/v1/tasks")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["tasks"]) == 2

    def test_list_tasks_filter_pending(self, client: TestClient, test_session: Session, test_user_id: str):
        """Test filtering by pending status."""
        task1 = Task(user_id=test_user_id, tags=[], title="Pending", completed=False)
        task2 = Task(user_id=test_user_id, tags=[], title="Completed", completed=True)
        test_session.add(task1)
        test_session.add(task2)
        test_session.commit()

        response = client.get("/api/v1/tasks?status=pending")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["tasks"][0]["title"] == "Pending"

    def test_list_tasks_filter_completed(self, client: TestClient, test_session: Session, test_user_id: str):
        """Test filtering by completed status."""
        task1 = Task(user_id=test_user_id, tags=[], title="Pending", completed=False)
        task2 = Task(user_id=test_user_id, tags=[], title="Completed", completed=True)
        test_session.add(task1)
        test_session.add(task2)
        test_session.commit()

        response = client.get("/api/v1/tasks?status=completed")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["tasks"][0]["title"] == "Completed"

    def test_list_tasks_sort_title(self, client: TestClient, test_session: Session, test_user_id: str):
        """Test sorting by title."""
        task1 = Task(user_id=test_user_id, tags=[], title="Zebra")
        task2 = Task(user_id=test_user_id, tags=[], title="Apple")
        test_session.add(task1)
        test_session.add(task2)
        test_session.commit()

        response = client.get("/api/v1/tasks?sort_by=title&order=asc")
        assert response.status_code == 200
        data = response.json()
        assert data["tasks"][0]["title"] == "Apple"
        assert data["tasks"][1]["title"] == "Zebra"


class TestGetTask:
    """Test GET /api/v1/tasks/{id}."""

    def test_get_task_success(self, client: TestClient, test_session: Session, test_user_id: str):
        """Test getting a task successfully."""
        task = Task(user_id=test_user_id, tags=[], title="Test Task")
        test_session.add(task)
        test_session.commit()
        test_session.refresh(task)

        response = client.get(f"/api/v1/tasks/{task.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Task"

    def test_get_task_not_found(self, client: TestClient):
        """Test getting non-existent task."""
        response = client.get("/api/v1/tasks/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestUpdateTask:
    """Test PUT /api/v1/tasks/{id}."""

    def test_update_task_success(self, client: TestClient, test_session: Session, test_user_id: str):
        """Test updating a task successfully."""
        task = Task(user_id=test_user_id, tags=[], title="Original")
        test_session.add(task)
        test_session.commit()
        test_session.refresh(task)

        response = client.put(
            f"/api/v1/tasks/{task.id}",
            json={"title": "Updated", "description": "New Description"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated"
        assert data["description"] == "New Description"

    def test_update_task_partial(self, client: TestClient, test_session: Session, test_user_id: str):
        """Test partial update."""
        task = Task(user_id=test_user_id, tags=[], title="Original", description="Original Desc")
        test_session.add(task)
        test_session.commit()
        test_session.refresh(task)

        response = client.put(
            f"/api/v1/tasks/{task.id}",
            json={"title": "Updated"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated"
        assert data["description"] == "Original Desc"  # Unchanged

    def test_update_task_not_found(self, client: TestClient):
        """Test updating non-existent task."""
        response = client.put(
            "/api/v1/tasks/99999",
            json={"title": "Updated"},
        )
        assert response.status_code == 404


class TestToggleComplete:
    """Test PATCH /api/v1/tasks/{id}/complete."""

    def test_toggle_complete_success(self, client: TestClient, test_session: Session, test_user_id: str):
        """Test toggling completion status."""
        task = Task(user_id=test_user_id, tags=[], title="Task", completed=False)
        test_session.add(task)
        test_session.commit()
        test_session.refresh(task)

        response = client.patch(
            f"/api/v1/tasks/{task.id}/complete",
            json={"completed": True},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True

    def test_toggle_complete_not_found(self, client: TestClient):
        """Test toggling non-existent task."""
        response = client.patch(
            "/api/v1/tasks/99999/complete",
            json={"completed": True},
        )
        assert response.status_code == 404


class TestDeleteTask:
    """Test DELETE /api/v1/tasks/{id}."""

    def test_delete_task_success(self, client: TestClient, test_session: Session, test_user_id: str):
        """Test deleting a task successfully."""
        task = Task(user_id=test_user_id, tags=[], title="To Delete")
        test_session.add(task)
        test_session.commit()
        test_session.refresh(task)

        response = client.delete(f"/api/v1/tasks/{task.id}")
        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(f"/api/v1/tasks/{task.id}")
        assert get_response.status_code == 404

    def test_delete_task_not_found(self, client: TestClient):
        """Test deleting non-existent task."""
        response = client.delete("/api/v1/tasks/99999")
        assert response.status_code == 404
