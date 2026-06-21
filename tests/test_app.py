import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Practice teamwork, strategy, and competitive soccer matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["alex@mergington.edu", "lisa@mergington.edu"]
        },
        "Swim Club": {
            "description": "Develop swimming skills, fitness, and relay techniques",
            "schedule": "Mondays and Wednesdays, 3:00 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu", "mia@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore drawing, painting, and mixed-media art projects",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["ava@mergington.edu", "lucas@mergington.edu"]
        },
        "Drama Club": {
            "description": "Practice acting, stagecraft, and prepare a school play",
            "schedule": "Thursdays, 4:30 PM - 6:00 PM",
            "max_participants": 20,
            "participants": ["sophia@mergington.edu", "ethan@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Prepare for science challenges in biology, physics, and engineering",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["emma@mergington.edu", "mason@mergington.edu"]
        },
        "Literature Circle": {
            "description": "Read and discuss novels, poetry, and literary themes",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["chloe@mergington.edu", "daniel@mergington.edu"]
        },
        "Math Club": {
            "description": "Solve puzzles, learn advanced math concepts, and compete in contests",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["olivia@mergington.edu", "liam@mergington.edu"]
        }
    }

    activities.clear()
    activities.update(initial_activities)
    yield
    activities.clear()
    activities.update(initial_activities)


@pytest.fixture
def client():
    return TestClient(app)


class TestRoot:
    def test_root_redirects_to_static_index(self, client):
        # Arrange
        expected_redirect_url = "/static/index.html"
        # Act
        response = client.get("/", follow_redirects=False)
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect_url


class TestGetActivities:
    def test_get_activities_returns_all_activities(self, client):
        # Arrange
        expected_num_activities = 10
        # Act
        response = client.get("/activities")
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == expected_num_activities

    def test_get_activities_contains_chess_club(self, client):
        # Arrange
        activity_name = "Chess Club"
        # Act
        response = client.get("/activities")
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert activity_name in data
        assert data[activity_name]["max_participants"] == 12


class TestSignupForActivity:
    def test_signup_for_activity_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_adds_participant_to_activity(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        # Act
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        # Assert
        assert len(activities[activity_name]["participants"]) == initial_count + 1
        assert email in activities[activity_name]["participants"]

    def test_signup_for_nonexistent_activity(self, client):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_student_fails(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


class TestRemoveParticipant:
    def test_remove_participant_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        # Act
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

    def test_remove_participant_from_activity(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        # Act
        client.delete(f"/activities/{activity_name}/participants", params={"email": email})
        # Assert
        assert len(activities[activity_name]["participants"]) == initial_count - 1
        assert email not in activities[activity_name]["participants"]

    def test_remove_from_nonexistent_activity(self, client):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        # Act
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_nonexistent_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        # Act
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
        # Assert
        assert response.status_code == 404
        assert "Student not found" in response.json()["detail"]
