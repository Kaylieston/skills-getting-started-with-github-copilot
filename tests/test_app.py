"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    original_activities = {
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
        "Basketball Team": {
            "description": "Competitive basketball team and practice",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis coaching and match play",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["isabella@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and visual arts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["grace@mergington.edu"]
        },
        "Music Band": {
            "description": "Learn instruments and perform in concerts",
            "schedule": "Mondays and Fridays, 4:00 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design, build, and program robots",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["ryan@mergington.edu"]
        },
        "Science Bowl": {
            "description": "Compete in science competitions and experiments",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["noah@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    yield
    
    # Cleanup
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_has_required_fields(self, client, reset_activities):
        """Test that activities have required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_chess_club_has_correct_participants(self, client, reset_activities):
        """Test that Chess Club has correct initial participants"""
        response = client.get("/activities")
        data = response.json()
        assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


class TestSignUpForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup actually adds participant to activity"""
        client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]
    
    def test_signup_duplicate_email_fails(self, client, reset_activities):
        """Test that signing up with duplicate email fails"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signing up for nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_multiple_students(self, client, reset_activities):
        """Test signing up multiple students to same activity"""
        client.post("/activities/Programming%20Class/signup?email=student1@mergington.edu")
        client.post("/activities/Programming%20Class/signup?email=student2@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        participants = data["Programming Class"]["participants"]
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants
        assert len(participants) == 4  # 2 original + 2 new


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregister from an activity"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes participant"""
        client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """Test that unregistering from nonexistent activity fails"""
        response = client.delete(
            "/activities/Nonexistent%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_not_signed_up_fails(self, client, reset_activities):
        """Test that unregistering non-participant fails"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=notstudent@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_multiple_participants(self, client, reset_activities):
        """Test unregistering multiple participants"""
        client.delete("/activities/Gym%20Class/unregister?email=john@mergington.edu")
        client.delete("/activities/Gym%20Class/unregister?email=olivia@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        assert len(data["Gym Class"]["participants"]) == 0


class TestSignupAndUnregister:
    """Integration tests for signup and unregister"""
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test signing up and then unregistering"""
        # Sign up
        response = client.post(
            "/activities/Tennis%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        assert "newstudent@mergington.edu" in response.json()["Tennis Club"]["participants"]
        
        # Unregister
        response = client.delete(
            "/activities/Tennis%20Club/unregister?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        assert "newstudent@mergington.edu" not in response.json()["Tennis Club"]["participants"]
    
    def test_signup_same_student_multiple_activities(self, client, reset_activities):
        """Test same student signing up for multiple activities"""
        email = "versatile@mergington.edu"
        
        # Sign up for multiple activities
        client.post(f"/activities/Art%20Studio/signup?email={email}")
        client.post(f"/activities/Music%20Band/signup?email={email}")
        client.post(f"/activities/Robotics%20Club/signup?email={email}")
        
        # Verify in all activities
        response = client.get("/activities")
        data = response.json()
        assert email in data["Art Studio"]["participants"]
        assert email in data["Music Band"]["participants"]
        assert email in data["Robotics Club"]["participants"]
