"""
Tests for the High School Management System API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
        "Basketball Team": {
            "description": "Join the school basketball team for training and competitions",
            "schedule": "Mondays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Practice soccer skills and play friendly matches",
            "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
            "max_participants": 18,
            "participants": []
        },
        "Drama Club": {
            "description": "Participate in theater productions and acting workshops",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": []
        },
        "Art Workshop": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": []
        },
        "Math Olympiad": {
            "description": "Prepare for math competitions and solve challenging problems",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": []
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific topics",
            "schedule": "Wednesdays, 4:00 PM - 5:00 PM",
            "max_participants": 14,
            "participants": []
        },
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
        }
    }
    
    # Reset activities to original state
    activities.clear()
    activities.update(original_activities)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 9
        assert "Basketball Team" in data
        assert "Soccer Club" in data
        assert "Drama Club" in data
        assert "Art Workshop" in data
        assert "Math Olympiad" in data
        assert "Science Club" in data
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_returns_correct_structure(self, client):
        """Test that each activity has the correct structure"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        basketball = data["Basketball Team"]
        assert "description" in basketball
        assert "schedule" in basketball
        assert "max_participants" in basketball
        assert "participants" in basketball
        assert isinstance(basketball["participants"], list)
    
    def test_get_activities_includes_existing_participants(self, client):
        """Test that activities with existing participants return them"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball Team/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Signed up test@mergington.edu for Basketball Team"
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "test@mergington.edu" in activities_data["Basketball Team"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_when_already_signed_up(self, client):
        """Test signup when student is already registered"""
        # First signup
        client.post("/activities/Basketball Team/signup?email=test@mergington.edu")
        
        # Try to signup again
        response = client.post(
            "/activities/Basketball Team/signup?email=test@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student already signed up"
    
    def test_signup_multiple_students_for_same_activity(self, client):
        """Test multiple students can sign up for the same activity"""
        # Sign up first student
        response1 = client.post(
            "/activities/Drama Club/signup?email=student1@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Sign up second student
        response2 = client.post(
            "/activities/Drama Club/signup?email=student2@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify both are registered
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = activities_data["Drama Club"]["participants"]
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants
        assert len(participants) == 2
    
    def test_signup_for_activity_with_special_characters_in_name(self, client):
        """Test signup for activities with spaces in their names"""
        response = client.post(
            "/activities/Art Workshop/signup?email=artist@mergington.edu"
        )
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_from_activity_success(self, client):
        """Test successful unregistration from an activity"""
        # First sign up
        client.post("/activities/Soccer Club/signup?email=test@mergington.edu")
        
        # Then unregister
        response = client.delete(
            "/activities/Soccer Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Unregistered test@mergington.edu from Soccer Club"
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "test@mergington.edu" not in activities_data["Soccer Club"]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistration from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_when_not_registered(self, client):
        """Test unregistration when student is not registered"""
        response = client.delete(
            "/activities/Science Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student is not registered for this activity"
    
    def test_unregister_existing_participant(self, client):
        """Test unregistration of a pre-existing participant"""
        # Chess Club already has michael@mergington.edu registered
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
        # daniel should still be there
        assert "daniel@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_and_unregister_workflow(self, client):
        """Test complete workflow of signing up and unregistering"""
        email = "workflow@mergington.edu"
        activity = "Math Olympiad"
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signed up
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregistered
        activities_response2 = client.get("/activities")
        activities_data2 = activities_response2.json()
        assert email not in activities_data2[activity]["participants"]
