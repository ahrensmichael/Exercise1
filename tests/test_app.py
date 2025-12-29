"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from src.app import activities
    initial_state = {
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
            "description": "Join the school soccer team for practice and matches",
            "schedule": "Practice: Tuesdays and Thursdays, 4:00 PM - 6:00 PM; Games on weekends",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Skill development and intramural basketball games",
            "schedule": "Wednesdays and Fridays, 4:30 PM - 6:00 PM",
            "max_participants": 18,
            "participants": ["noah@mergington.edu", "mia@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and mixed media projects",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, stagecraft, and production of school plays",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM; rehearsal weekends as needed",
            "max_participants": 25,
            "participants": ["charlotte@mergington.edu", "ethan@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments, science fairs, and guest lectures",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["amelia@mergington.edu", "jack@mergington.edu"]
        },
        "Debate Team": {
            "description": "Practice public speaking, research topics, and compete in debates",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM; tournaments on select weekends",
            "max_participants": 14,
            "participants": ["henry@mergington.edu", "zoe@mergington.edu"]
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(initial_state)
    yield
    # Reset after test
    activities.clear()
    activities.update(initial_state)


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""

    def test_get_activities(self, client, reset_activities):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities_data = response.json()
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data
        assert len(activities_data) == 9

    def test_activities_have_required_fields(self, client, reset_activities):
        """Test that activities have all required fields"""
        response = client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_data in activities_data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for the signup endpoint"""

    def test_successful_signup(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_increases_participant_count(self, client, reset_activities):
        """Test that signup increases the participant count"""
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        response = client.get("/activities")
        new_count = len(response.json()["Chess Club"]["participants"])
        assert new_count == initial_count + 1

    def test_signup_duplicate_email(self, client, reset_activities):
        """Test that duplicate emails are rejected"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUnregisterEndpoint:
    """Tests for the unregister endpoint"""

    def test_successful_unregister(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        response = client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_decreases_participant_count(self, client, reset_activities):
        """Test that unregister decreases the participant count"""
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        client.post("/activities/Chess Club/unregister?email=michael@mergington.edu")
        
        response = client.get("/activities")
        new_count = len(response.json()["Chess Club"]["participants"])
        assert new_count == initial_count - 1

    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregistering a student who is not registered"""
        response = client.post(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister from a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_removes_correct_participant(self, client, reset_activities):
        """Test that unregister removes only the correct participant"""
        response = client.get("/activities")
        participants_before = response.json()["Chess Club"]["participants"].copy()
        
        client.post("/activities/Chess Club/unregister?email=michael@mergington.edu")
        
        response = client.get("/activities")
        participants_after = response.json()["Chess Club"]["participants"]
        
        assert "michael@mergington.edu" not in participants_after
        assert "daniel@mergington.edu" in participants_after


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static page"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
