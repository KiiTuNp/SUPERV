#!/usr/bin/env python3
"""
Backend API Tests for Vote Secret Application
Tests the FastAPI backend endpoints for the anonymous voting platform.
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any

import aiohttp
import websockets
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE_URL = f"{BACKEND_URL}/api"

class VoteSecretAPITester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.meeting_data = {}
        self.participant_data = {}
        self.poll_data = {}
        
    async def setup_session(self):
        """Setup HTTP session for API calls"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        
    async def test_health_check(self):
        """Test 1: API Health Check"""
        try:
            async with self.session.get(f"{API_BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "healthy":
                        self.log_test("Health Check", True, "API is healthy", data)
                        return True
                    else:
                        self.log_test("Health Check", False, f"API unhealthy: {data}")
                        return False
                else:
                    self.log_test("Health Check", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False
            
    async def test_create_meeting(self):
        """Test 2: Create Meeting Session"""
        try:
            meeting_payload = {
                "title": "Test Meeting - Vote Secret API Test",
                "organizer_name": "API Test Organizer"
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/meetings",
                json=meeting_payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    required_fields = ["id", "title", "organizer_name", "meeting_code", "status"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test("Create Meeting", False, f"Missing fields: {missing_fields}")
                        return False
                        
                    # Store meeting data for subsequent tests
                    self.meeting_data = data
                    
                    self.log_test("Create Meeting", True, 
                                f"Meeting created with code: {data['meeting_code']}", data)
                    return True
                else:
                    error_data = await response.text()
                    self.log_test("Create Meeting", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Create Meeting", False, f"Error: {str(e)}")
            return False

    async def test_create_meeting_with_timezone(self):
        """Test 25: Create Meeting with Timezone Information"""
        try:
            meeting_payload = {
                "title": "Timezone Test Meeting - Paris",
                "organizer_name": "Paris Organizer",
                "organizer_timezone": "Europe/Paris"
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/meetings",
                json=meeting_payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure includes timezone
                    required_fields = ["id", "title", "organizer_name", "meeting_code", "status", "organizer_timezone"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test("Create Meeting with Timezone", False, f"Missing fields: {missing_fields}")
                        return False
                    
                    # Validate timezone is stored correctly
                    if data["organizer_timezone"] != "Europe/Paris":
                        self.log_test("Create Meeting with Timezone", False, 
                                    f"Expected timezone 'Europe/Paris', got: {data['organizer_timezone']}")
                        return False
                        
                    # Store timezone meeting data for subsequent tests
                    self.meeting_data["timezone_meeting"] = data
                    
                    self.log_test("Create Meeting with Timezone", True, 
                                f"Meeting created with timezone: {data['organizer_timezone']}")
                    return True
                else:
                    error_data = await response.text()
                    self.log_test("Create Meeting with Timezone", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Create Meeting with Timezone", False, f"Error: {str(e)}")
            return False

    async def test_create_meeting_different_timezone(self):
        """Test 26: Create Meeting with Different Timezone (New York)"""
        try:
            meeting_payload = {
                "title": "Timezone Test Meeting - New York",
                "organizer_name": "New York Organizer",
                "organizer_timezone": "America/New_York"
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/meetings",
                json=meeting_payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate timezone is stored correctly
                    if data["organizer_timezone"] != "America/New_York":
                        self.log_test("Create Meeting Different Timezone", False, 
                                    f"Expected timezone 'America/New_York', got: {data['organizer_timezone']}")
                        return False
                        
                    # Store NY timezone meeting data for subsequent tests
                    self.meeting_data["ny_timezone_meeting"] = data
                    
                    self.log_test("Create Meeting Different Timezone", True, 
                                f"Meeting created with timezone: {data['organizer_timezone']}")
                    return True
                else:
                    error_data = await response.text()
                    self.log_test("Create Meeting Different Timezone", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Create Meeting Different Timezone", False, f"Error: {str(e)}")
            return False

    async def test_backward_compatibility_no_timezone(self):
        """Test 27: Backward Compatibility - Meeting without Timezone"""
        try:
            meeting_payload = {
                "title": "No Timezone Test Meeting",
                "organizer_name": "No Timezone Organizer"
                # No organizer_timezone field
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/meetings",
                json=meeting_payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Should work without timezone (backward compatibility)
                    required_fields = ["id", "title", "organizer_name", "meeting_code", "status"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test("Backward Compatibility No Timezone", False, f"Missing fields: {missing_fields}")
                        return False
                    
                    # organizer_timezone should be null or not present
                    timezone_value = data.get("organizer_timezone")
                    if timezone_value is not None:
                        self.log_test("Backward Compatibility No Timezone", True, 
                                    f"Meeting created without timezone (timezone field: {timezone_value})")
                    else:
                        self.log_test("Backward Compatibility No Timezone", True, 
                                    "Meeting created without timezone field")
                        
                    # Store no-timezone meeting data
                    self.meeting_data["no_timezone_meeting"] = data
                    
                    return True
                else:
                    error_data = await response.text()
                    self.log_test("Backward Compatibility No Timezone", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Backward Compatibility No Timezone", False, f"Error: {str(e)}")
            return False
            
    async def test_get_meeting_by_code(self):
        """Test 3: Get Meeting by Code"""
        if not self.meeting_data:
            self.log_test("Get Meeting by Code", False, "No meeting data available")
            return False
            
        try:
            meeting_code = self.meeting_data["meeting_code"]
            
            async with self.session.get(
                f"{API_BASE_URL}/meetings/{meeting_code}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate that we get the same meeting
                    if data["id"] == self.meeting_data["id"]:
                        self.log_test("Get Meeting by Code", True, 
                                    f"Retrieved meeting: {data['title']}")
                        return True
                    else:
                        self.log_test("Get Meeting by Code", False, 
                                    "Retrieved different meeting")
                        return False
                else:
                    error_data = await response.text()
                    self.log_test("Get Meeting by Code", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Get Meeting by Code", False, f"Error: {str(e)}")
            return False
            
    async def test_participant_join(self):
        """Test 4: Participant Join Meeting"""
        if not self.meeting_data:
            self.log_test("Participant Join", False, "No meeting data available")
            return False
            
        try:
            join_payload = {
                "name": "Test Participant",
                "meeting_code": self.meeting_data["meeting_code"]
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/participants/join",
                json=join_payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    required_fields = ["id", "name", "meeting_id", "approval_status"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test("Participant Join", False, f"Missing fields: {missing_fields}")
                        return False
                        
                    # Store participant data
                    self.participant_data = data
                    
                    self.log_test("Participant Join", True, 
                                f"Participant joined: {data['name']} (Status: {data['approval_status']})")
                    return True
                else:
                    error_data = await response.text()
                    self.log_test("Participant Join", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Participant Join", False, f"Error: {str(e)}")
            return False
            
    async def test_approve_participant(self):
        """Test 5: Approve Participant"""
        if not self.participant_data:
            self.log_test("Approve Participant", False, "No participant data available")
            return False
            
        try:
            approval_payload = {
                "participant_id": self.participant_data["id"],
                "approved": True
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/participants/{self.participant_data['id']}/approve",
                json=approval_payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "success":
                        self.log_test("Approve Participant", True, "Participant approved successfully")
                        return True
                    else:
                        self.log_test("Approve Participant", False, f"Unexpected response: {data}")
                        return False
                else:
                    error_data = await response.text()
                    self.log_test("Approve Participant", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Approve Participant", False, f"Error: {str(e)}")
            return False
            
    async def test_create_poll(self):
        """Test 6: Create Poll"""
        if not self.meeting_data:
            self.log_test("Create Poll", False, "No meeting data available")
            return False
            
        try:
            poll_payload = {
                "question": "What is your preferred voting method?",
                "options": ["Secret ballot", "Open vote", "Anonymous online", "Paper ballot"],
                "timer_duration": 300  # 5 minutes
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/meetings/{self.meeting_data['id']}/polls",
                json=poll_payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    required_fields = ["id", "meeting_id", "question", "options", "status"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test("Create Poll", False, f"Missing fields: {missing_fields}")
                        return False
                        
                    # Validate options structure
                    if not data["options"] or len(data["options"]) != 4:
                        self.log_test("Create Poll", False, "Invalid options structure")
                        return False
                        
                    # Store poll data
                    self.poll_data = data
                    
                    self.log_test("Create Poll", True, 
                                f"Poll created: {data['question']} with {len(data['options'])} options")
                    return True
                else:
                    error_data = await response.text()
                    self.log_test("Create Poll", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Create Poll", False, f"Error: {str(e)}")
            return False
            
    async def test_start_poll(self):
        """Test 7: Start Poll"""
        if not self.poll_data:
            self.log_test("Start Poll", False, "No poll data available")
            return False
            
        try:
            async with self.session.post(
                f"{API_BASE_URL}/polls/{self.poll_data['id']}/start"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "started":
                        self.log_test("Start Poll", True, "Poll started successfully")
                        return True
                    else:
                        self.log_test("Start Poll", False, f"Unexpected response: {data}")
                        return False
                else:
                    error_data = await response.text()
                    self.log_test("Start Poll", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Start Poll", False, f"Error: {str(e)}")
            return False
            
    async def test_submit_vote(self):
        """Test 8: Submit Vote"""
        if not self.poll_data:
            self.log_test("Submit Vote", False, "No poll data available")
            return False
            
        try:
            # Get first option ID
            first_option = self.poll_data["options"][0]
            
            vote_payload = {
                "poll_id": self.poll_data["id"],
                "option_id": first_option["id"]
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/votes",
                json=vote_payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "vote_submitted":
                        self.log_test("Submit Vote", True, "Vote submitted successfully")
                        return True
                    else:
                        self.log_test("Submit Vote", False, f"Unexpected response: {data}")
                        return False
                else:
                    error_data = await response.text()
                    self.log_test("Submit Vote", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Submit Vote", False, f"Error: {str(e)}")
            return False
            
    async def test_get_poll_results(self):
        """Test 9: Get Poll Results"""
        if not self.poll_data:
            self.log_test("Get Poll Results", False, "No poll data available")
            return False
            
        try:
            async with self.session.get(
                f"{API_BASE_URL}/polls/{self.poll_data['id']}/results"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    required_fields = ["question", "results", "total_votes"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test("Get Poll Results", False, f"Missing fields: {missing_fields}")
                        return False
                        
                    # Check if we have at least one vote
                    if data["total_votes"] >= 1:
                        self.log_test("Get Poll Results", True, 
                                    f"Results retrieved: {data['total_votes']} total votes")
                        return True
                    else:
                        self.log_test("Get Poll Results", False, "No votes recorded")
                        return False
                else:
                    error_data = await response.text()
                    self.log_test("Get Poll Results", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Get Poll Results", False, f"Error: {str(e)}")
            return False
            
    async def test_websocket_connection(self):
        """Test 10: WebSocket Connection"""
        if not self.meeting_data:
            self.log_test("WebSocket Connection", False, "No meeting data available")
            return False
            
        try:
            # Convert HTTP URL to WebSocket URL
            ws_url = BACKEND_URL.replace('https://', 'wss://').replace('http://', 'ws://')
            websocket_url = f"{ws_url}/ws/meetings/{self.meeting_data['id']}"
            
            # Test WebSocket connection
            async with websockets.connect(websocket_url) as websocket:
                # Send a test message
                await websocket.send("test_connection")
                
                # Wait briefly for any response (optional)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    self.log_test("WebSocket Connection", True, 
                                f"Connected successfully, received: {response}")
                except asyncio.TimeoutError:
                    # No response is fine for this test
                    self.log_test("WebSocket Connection", True, "Connected successfully")
                
                return True
                
        except Exception as e:
            self.log_test("WebSocket Connection", False, f"Connection error: {str(e)}")
            return False
            
    async def test_mongodb_connectivity(self):
        """Test 11: MongoDB Connectivity (via API)"""
        try:
            # Test by creating and retrieving data
            test_payload = {
                "title": "MongoDB Test Meeting",
                "organizer_name": "DB Test Organizer"
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/meetings",
                json=test_payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    meeting_id = data["id"]
                    
                    # Try to retrieve the meeting
                    async with self.session.get(
                        f"{API_BASE_URL}/meetings/{data['meeting_code']}"
                    ) as get_response:
                        if get_response.status == 200:
                            retrieved_data = await get_response.json()
                            if retrieved_data["id"] == meeting_id:
                                self.log_test("MongoDB Connectivity", True, 
                                            "Database read/write operations successful")
                                return True
                            else:
                                self.log_test("MongoDB Connectivity", False, 
                                            "Data integrity issue")
                                return False
                        else:
                            self.log_test("MongoDB Connectivity", False, 
                                        "Failed to retrieve created data")
                            return False
                else:
                    self.log_test("MongoDB Connectivity", False, 
                                "Failed to create test data")
                    return False
                    
        except Exception as e:
            self.log_test("MongoDB Connectivity", False, f"Database error: {str(e)}")
            return False

    async def test_add_scrutators(self):
        """Test 12: Add Scrutators to Meeting"""
        if not self.meeting_data:
            self.log_test("Add Scrutators", False, "No meeting data available")
            return False
            
        try:
            scrutator_payload = {
                "names": ["Marie Dupont", "Jean Martin", "Sophie Bernard"]
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/meetings/{self.meeting_data['id']}/scrutators",
                json=scrutator_payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    required_fields = ["scrutator_code", "scrutators", "message"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test("Add Scrutators", False, f"Missing fields: {missing_fields}")
                        return False
                        
                    # Store scrutator data for subsequent tests
                    self.meeting_data["scrutator_code"] = data["scrutator_code"]
                    self.meeting_data["scrutators"] = data["scrutators"]
                    
                    self.log_test("Add Scrutators", True, 
                                f"Added {len(data['scrutators'])} scrutators with code: {data['scrutator_code']}")
                    return True
                else:
                    error_data = await response.text()
                    self.log_test("Add Scrutators", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Add Scrutators", False, f"Error: {str(e)}")
            return False

    async def test_scrutator_automatic_access(self):
        """Test 13: Scrutator Automatic Access (NEW FEATURE)"""
        if not self.meeting_data or "scrutator_code" not in self.meeting_data:
            self.log_test("Scrutator Automatic Access", False, "No scrutator code available")
            return False
            
        try:
            # Test joining as a scrutator with automatic approval
            join_payload = {
                "name": "Marie Dupont",  # First scrutator from the list
                "scrutator_code": self.meeting_data["scrutator_code"]
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/scrutators/join",
                json=join_payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    required_fields = ["meeting", "scrutator_name", "access_type", "status"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test("Scrutator Automatic Access", False, f"Missing fields: {missing_fields}")
                        return False
                    
                    # Check that scrutator gets IMMEDIATE access (approved status)
                    if data["status"] != "approved":
                        self.log_test("Scrutator Automatic Access", False, 
                                    f"Expected 'approved' status, got: {data['status']}")
                        return False
                    
                    # Check access type
                    if data["access_type"] != "scrutator":
                        self.log_test("Scrutator Automatic Access", False, 
                                    f"Expected 'scrutator' access_type, got: {data['access_type']}")
                        return False
                    
                    # Store scrutator data for subsequent tests
                    self.meeting_data["scrutator_data"] = data
                    
                    self.log_test("Scrutator Automatic Access", True, 
                                f"Scrutator '{data['scrutator_name']}' got immediate access with status: {data['status']}")
                    return True
                else:
                    error_data = await response.text()
                    self.log_test("Scrutator Automatic Access", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Scrutator Automatic Access", False, f"Error: {str(e)}")
            return False

    async def test_scrutator_organizer_interface_access(self):
        """Test 14: Scrutator Access to Organizer Interface"""
        if not self.meeting_data or "scrutator_data" not in self.meeting_data:
            self.log_test("Scrutator Organizer Interface Access", False, "No scrutator data available")
            return False
            
        try:
            # Test that scrutator can access organizer view
            meeting_id = self.meeting_data["id"]
            
            async with self.session.get(
                f"{API_BASE_URL}/meetings/{meeting_id}/organizer"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    required_fields = ["meeting", "participants", "polls"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test("Scrutator Organizer Interface Access", False, f"Missing fields: {missing_fields}")
                        return False
                    
                    # Verify meeting data is accessible
                    if data["meeting"]["id"] != meeting_id:
                        self.log_test("Scrutator Organizer Interface Access", False, "Wrong meeting data returned")
                        return False
                    
                    self.log_test("Scrutator Organizer Interface Access", True, 
                                "Scrutator can access organizer interface successfully")
                    return True
                else:
                    error_data = await response.text()
                    self.log_test("Scrutator Organizer Interface Access", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Scrutator Organizer Interface Access", False, f"Error: {str(e)}")
            return False

    async def test_get_meeting_scrutators(self):
        """Test 15: Get Meeting Scrutators List"""
        if not self.meeting_data:
            self.log_test("Get Meeting Scrutators", False, "No meeting data available")
            return False
            
        try:
            meeting_id = self.meeting_data["id"]
            
            async with self.session.get(
                f"{API_BASE_URL}/meetings/{meeting_id}/scrutators"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    required_fields = ["scrutator_code", "scrutators"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test("Get Meeting Scrutators", False, f"Missing fields: {missing_fields}")
                        return False
                    
                    # Check that we have at least one scrutator (the one that joined)
                    if not data["scrutators"] or len(data["scrutators"]) == 0:
                        self.log_test("Get Meeting Scrutators", False, "No scrutators found")
                        return False
                    
                    # Check that the joined scrutator is in the list with approved status
                    joined_scrutator = None
                    for scrutator in data["scrutators"]:
                        if scrutator["name"] == "Marie Dupont":
                            joined_scrutator = scrutator
                            break
                    
                    if not joined_scrutator:
                        self.log_test("Get Meeting Scrutators", False, "Joined scrutator not found in list")
                        return False
                    
                    if joined_scrutator["approval_status"] != "approved":
                        self.log_test("Get Meeting Scrutators", False, 
                                    f"Scrutator status should be 'approved', got: {joined_scrutator['approval_status']}")
                        return False
                    
                    self.log_test("Get Meeting Scrutators", True, 
                                f"Found {len(data['scrutators'])} scrutators, joined scrutator is approved")
                    return True
                else:
                    error_data = await response.text()
                    self.log_test("Get Meeting Scrutators", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Get Meeting Scrutators", False, f"Error: {str(e)}")
            return False

    async def test_second_scrutator_join(self):
        """Test 16: Second Scrutator Join (Test Automatic Approval)"""
        if not self.meeting_data or "scrutator_code" not in self.meeting_data:
            self.log_test("Second Scrutator Join", False, "No scrutator code available")
            return False
            
        try:
            # Test joining as a second scrutator
            join_payload = {
                "name": "Jean Martin",  # Second scrutator from the list
                "scrutator_code": self.meeting_data["scrutator_code"]
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/scrutators/join",
                json=join_payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check that second scrutator also gets immediate access
                    if data["status"] != "approved":
                        self.log_test("Second Scrutator Join", False, 
                                    f"Expected 'approved' status, got: {data['status']}")
                        return False
                    
                    if data["access_type"] != "scrutator":
                        self.log_test("Second Scrutator Join", False, 
                                    f"Expected 'scrutator' access_type, got: {data['access_type']}")
                        return False
                    
                    self.log_test("Second Scrutator Join", True, 
                                f"Second scrutator '{data['scrutator_name']}' got immediate access")
                    return True
                else:
                    error_data = await response.text()
                    self.log_test("Second Scrutator Join", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Second Scrutator Join", False, f"Error: {str(e)}")
            return False

    async def test_unauthorized_scrutator_join(self):
        """Test 17: Unauthorized Scrutator Join (Should Fail)"""
        if not self.meeting_data or "scrutator_code" not in self.meeting_data:
            self.log_test("Unauthorized Scrutator Join", False, "No scrutator code available")
            return False
            
        try:
            # Test joining with a name not in the authorized list
            join_payload = {
                "name": "Unauthorized Person",  # Not in the scrutator list
                "scrutator_code": self.meeting_data["scrutator_code"]
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/scrutators/join",
                json=join_payload
            ) as response:
                if response.status == 403:
                    # This is expected - unauthorized person should be rejected
                    self.log_test("Unauthorized Scrutator Join", True, 
                                "Unauthorized scrutator correctly rejected")
                    return True
                elif response.status == 200:
                    # This should not happen - unauthorized person got access
                    self.log_test("Unauthorized Scrutator Join", False, 
                                "Unauthorized scrutator incorrectly got access")
                    return False
                else:
                    error_data = await response.text()
                    self.log_test("Unauthorized Scrutator Join", False, 
                                f"Unexpected HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Unauthorized Scrutator Join", False, f"Error: {str(e)}")
            return False

    async def test_invalid_scrutator_code(self):
        """Test 18: Invalid Scrutator Code (Should Fail)"""
        try:
            # Test joining with invalid scrutator code
            join_payload = {
                "name": "Marie Dupont",
                "scrutator_code": "INVALID123"  # Invalid code
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/scrutators/join",
                json=join_payload
            ) as response:
                if response.status == 404:
                    # This is expected - invalid code should be rejected
                    self.log_test("Invalid Scrutator Code", True, 
                                "Invalid scrutator code correctly rejected")
                    return True
                elif response.status == 200:
                    # This should not happen - invalid code got access
                    self.log_test("Invalid Scrutator Code", False, 
                                "Invalid scrutator code incorrectly accepted")
                    return False
                else:
                    error_data = await response.text()
                    self.log_test("Invalid Scrutator Code", False, 
                                f"Unexpected HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Invalid Scrutator Code", False, f"Error: {str(e)}")
            return False

    async def test_close_poll_for_report(self):
        """Test 19: Close Poll to Have Data for Report"""
        if not self.poll_data:
            self.log_test("Close Poll for Report", False, "No poll data available")
            return False
            
        try:
            async with self.session.post(
                f"{API_BASE_URL}/polls/{self.poll_data['id']}/close"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "closed":
                        self.log_test("Close Poll for Report", True, "Poll closed successfully for report generation")
                        return True
                    else:
                        self.log_test("Close Poll for Report", False, f"Unexpected response: {data}")
                        return False
                else:
                    error_data = await response.text()
                    self.log_test("Close Poll for Report", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Close Poll for Report", False, f"Error: {str(e)}")
            return False

    async def test_request_report_generation(self):
        """Test 20: Request Report Generation (Scrutator Voting System)"""
        if not self.meeting_data:
            self.log_test("Request Report Generation", False, "No meeting data available")
            return False
            
        try:
            request_payload = {
                "meeting_id": self.meeting_data["id"],
                "requested_by": self.meeting_data["organizer_name"]
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/meetings/{self.meeting_data['id']}/request-report",
                json=request_payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Should require scrutator approval since we have scrutators
                    if data.get("scrutator_approval_required"):
                        # Store report request data
                        self.meeting_data["report_request"] = data
                        
                        self.log_test("Request Report Generation", True, 
                                    f"Report generation requested - requires approval from {data['scrutator_count']} scrutators (majority: {data['majority_needed']})")
                        return True
                    elif data.get("direct_generation"):
                        self.log_test("Request Report Generation", False, 
                                    "Expected scrutator approval but got direct generation")
                        return False
                    else:
                        self.log_test("Request Report Generation", False, f"Unexpected response: {data}")
                        return False
                else:
                    error_data = await response.text()
                    self.log_test("Request Report Generation", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Request Report Generation", False, f"Error: {str(e)}")
            return False

    async def test_scrutator_vote_approve(self):
        """Test 21: First Scrutator Vote (Approve)"""
        if not self.meeting_data or "report_request" not in self.meeting_data:
            self.log_test("First Scrutator Vote", False, "No report request data available")
            return False
            
        try:
            vote_payload = {
                "meeting_id": self.meeting_data["id"],
                "scrutator_name": "Marie Dupont",  # First scrutator who joined
                "approved": True  # Vote to approve
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/meetings/{self.meeting_data['id']}/scrutator-vote",
                json=vote_payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Should be pending since we need majority
                    if data.get("decision") == "pending":
                        self.log_test("First Scrutator Vote", True, 
                                    f"First vote recorded: {data['yes_votes']}/{data['total_scrutators']} yes votes, need {data['majority_needed']} for majority")
                        return True
                    elif data.get("decision") == "approved":
                        # If only one scrutator, might be approved immediately
                        if data.get("majority_needed") == 1:
                            self.log_test("First Scrutator Vote", True, 
                                        f"Report approved immediately (single scrutator): {data['yes_votes']}/{data['majority_needed']}")
                            return True
                        else:
                            self.log_test("First Scrutator Vote", False, 
                                        f"Unexpected immediate approval: {data}")
                            return False
                    else:
                        self.log_test("First Scrutator Vote", False, f"Unexpected response: {data}")
                        return False
                else:
                    error_data = await response.text()
                    self.log_test("First Scrutator Vote", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("First Scrutator Vote", False, f"Error: {str(e)}")
            return False

    async def test_scrutator_vote_majority(self):
        """Test 22: Second Scrutator Vote (Achieve Majority)"""
        if not self.meeting_data or "report_request" not in self.meeting_data:
            self.log_test("Second Scrutator Vote", False, "No report request data available")
            return False
            
        try:
            vote_payload = {
                "meeting_id": self.meeting_data["id"],
                "scrutator_name": "Jean Martin",  # Second scrutator who joined
                "approved": True  # Vote to approve
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/meetings/{self.meeting_data['id']}/scrutator-vote",
                json=vote_payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Should be approved now with majority
                    if data.get("decision") == "approved":
                        self.log_test("Second Scrutator Vote", True, 
                                    f"Majority achieved! Report generation approved: {data['yes_votes']}/{data['majority_needed']} votes")
                        return True
                    elif data.get("decision") == "pending":
                        self.log_test("Second Scrutator Vote", True, 
                                    f"Still pending: {data['yes_votes']}/{data['total_scrutators']} yes votes, need {data['majority_needed']} for majority")
                        return True
                    else:
                        self.log_test("Second Scrutator Vote", False, f"Unexpected response: {data}")
                        return False
                else:
                    error_data = await response.text()
                    self.log_test("Second Scrutator Vote", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Second Scrutator Vote", False, f"Error: {str(e)}")
            return False

    async def test_generate_report_after_approval(self):
        """Test 23: Generate Report After Scrutator Approval"""
        if not self.meeting_data:
            self.log_test("Generate Report After Approval", False, "No meeting data available")
            return False
            
        try:
            async with self.session.get(
                f"{API_BASE_URL}/meetings/{self.meeting_data['id']}/report"
            ) as response:
                if response.status == 200:
                    # Check if we get a PDF file
                    content_type = response.headers.get('content-type', '')
                    if 'application/pdf' in content_type:
                        # Read the PDF content to verify it's not empty
                        pdf_content = await response.read()
                        if len(pdf_content) > 1000:  # PDF should be at least 1KB
                            self.log_test("Generate Report After Approval", True, 
                                        f"PDF report generated successfully ({len(pdf_content)} bytes)")
                            return True
                        else:
                            self.log_test("Generate Report After Approval", False, 
                                        f"PDF too small ({len(pdf_content)} bytes)")
                            return False
                    else:
                        self.log_test("Generate Report After Approval", False, 
                                    f"Expected PDF, got content-type: {content_type}")
                        return False
                else:
                    error_data = await response.text()
                    self.log_test("Generate Report After Approval", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Generate Report After Approval", False, f"Error: {str(e)}")
            return False

    async def test_timezone_pdf_report_generation(self):
        """Test 28: PDF Report Generation with Timezone (Paris)"""
        if not self.meeting_data.get("timezone_meeting"):
            self.log_test("Timezone PDF Report Generation", False, "No timezone meeting data available")
            return False
            
        try:
            timezone_meeting = self.meeting_data["timezone_meeting"]
            
            # Create a poll for the timezone meeting to have data in the report
            poll_payload = {
                "question": "Timezone test poll - What time zone are you in?",
                "options": ["Europe/Paris", "America/New_York", "Asia/Tokyo", "UTC"],
                "timer_duration": 60
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/meetings/{timezone_meeting['id']}/polls",
                json=poll_payload
            ) as response:
                if response.status != 200:
                    self.log_test("Timezone PDF Report Generation", False, "Failed to create poll for timezone meeting")
                    return False
                
                poll_data = await response.json()
            
            # Start and close the poll
            await self.session.post(f"{API_BASE_URL}/polls/{poll_data['id']}/start")
            await asyncio.sleep(0.5)
            await self.session.post(f"{API_BASE_URL}/polls/{poll_data['id']}/close")
            
            # Generate PDF report
            async with self.session.get(
                f"{API_BASE_URL}/meetings/{timezone_meeting['id']}/report"
            ) as response:
                if response.status == 200:
                    # Check if we get a PDF file
                    content_type = response.headers.get('content-type', '')
                    if 'application/pdf' in content_type:
                        # Read the PDF content to verify it's not empty
                        pdf_content = await response.read()
                        if len(pdf_content) > 1000:  # PDF should be at least 1KB
                            self.log_test("Timezone PDF Report Generation", True, 
                                        f"PDF report with timezone generated successfully ({len(pdf_content)} bytes)")
                            return True
                        else:
                            self.log_test("Timezone PDF Report Generation", False, 
                                        f"PDF too small ({len(pdf_content)} bytes)")
                            return False
                    else:
                        self.log_test("Timezone PDF Report Generation", False, 
                                    f"Expected PDF, got content-type: {content_type}")
                        return False
                else:
                    error_data = await response.text()
                    self.log_test("Timezone PDF Report Generation", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Timezone PDF Report Generation", False, f"Error: {str(e)}")
            return False

    async def test_different_timezone_pdf_report(self):
        """Test 29: PDF Report Generation with Different Timezone (New York)"""
        if not self.meeting_data.get("ny_timezone_meeting"):
            self.log_test("Different Timezone PDF Report", False, "No NY timezone meeting data available")
            return False
            
        try:
            ny_meeting = self.meeting_data["ny_timezone_meeting"]
            
            # Create a poll for the NY timezone meeting
            poll_payload = {
                "question": "New York timezone test poll - Preferred meeting time?",
                "options": ["9 AM EST", "12 PM EST", "3 PM EST", "6 PM EST"],
                "timer_duration": 60
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/meetings/{ny_meeting['id']}/polls",
                json=poll_payload
            ) as response:
                if response.status != 200:
                    self.log_test("Different Timezone PDF Report", False, "Failed to create poll for NY timezone meeting")
                    return False
                
                poll_data = await response.json()
            
            # Start and close the poll
            await self.session.post(f"{API_BASE_URL}/polls/{poll_data['id']}/start")
            await asyncio.sleep(0.5)
            await self.session.post(f"{API_BASE_URL}/polls/{poll_data['id']}/close")
            
            # Generate PDF report
            async with self.session.get(
                f"{API_BASE_URL}/meetings/{ny_meeting['id']}/report"
            ) as response:
                if response.status == 200:
                    # Check if we get a PDF file
                    content_type = response.headers.get('content-type', '')
                    if 'application/pdf' in content_type:
                        # Read the PDF content to verify it's not empty
                        pdf_content = await response.read()
                        if len(pdf_content) > 1000:  # PDF should be at least 1KB
                            self.log_test("Different Timezone PDF Report", True, 
                                        f"PDF report with NY timezone generated successfully ({len(pdf_content)} bytes)")
                            return True
                        else:
                            self.log_test("Different Timezone PDF Report", False, 
                                        f"PDF too small ({len(pdf_content)} bytes)")
                            return False
                    else:
                        self.log_test("Different Timezone PDF Report", False, 
                                    f"Expected PDF, got content-type: {content_type}")
                        return False
                else:
                    error_data = await response.text()
                    self.log_test("Different Timezone PDF Report", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Different Timezone PDF Report", False, f"Error: {str(e)}")
            return False

    async def test_no_timezone_pdf_report(self):
        """Test 30: PDF Report Generation without Timezone (Backward Compatibility)"""
        if not self.meeting_data.get("no_timezone_meeting"):
            self.log_test("No Timezone PDF Report", False, "No no-timezone meeting data available")
            return False
            
        try:
            no_tz_meeting = self.meeting_data["no_timezone_meeting"]
            
            # Create a poll for the no-timezone meeting
            poll_payload = {
                "question": "No timezone test poll - Default time handling?",
                "options": ["Server time", "UTC time", "Local time", "No preference"],
                "timer_duration": 60
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/meetings/{no_tz_meeting['id']}/polls",
                json=poll_payload
            ) as response:
                if response.status != 200:
                    self.log_test("No Timezone PDF Report", False, "Failed to create poll for no-timezone meeting")
                    return False
                
                poll_data = await response.json()
            
            # Start and close the poll
            await self.session.post(f"{API_BASE_URL}/polls/{poll_data['id']}/start")
            await asyncio.sleep(0.5)
            await self.session.post(f"{API_BASE_URL}/polls/{poll_data['id']}/close")
            
            # Generate PDF report
            async with self.session.get(
                f"{API_BASE_URL}/meetings/{no_tz_meeting['id']}/report"
            ) as response:
                if response.status == 200:
                    # Check if we get a PDF file
                    content_type = response.headers.get('content-type', '')
                    if 'application/pdf' in content_type:
                        # Read the PDF content to verify it's not empty
                        pdf_content = await response.read()
                        if len(pdf_content) > 1000:  # PDF should be at least 1KB
                            self.log_test("No Timezone PDF Report", True, 
                                        f"PDF report without timezone generated successfully ({len(pdf_content)} bytes)")
                            return True
                        else:
                            self.log_test("No Timezone PDF Report", False, 
                                        f"PDF too small ({len(pdf_content)} bytes)")
                            return False
                    else:
                        self.log_test("No Timezone PDF Report", False, 
                                    f"Expected PDF, got content-type: {content_type}")
                        return False
                else:
                    error_data = await response.text()
                    self.log_test("No Timezone PDF Report", False, 
                                f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("No Timezone PDF Report", False, f"Error: {str(e)}")
            return False

    async def test_websocket_report_notifications(self):
        """Test 24: WebSocket Notifications for Report Generation"""
        if not self.meeting_data:
            self.log_test("WebSocket Report Notifications", False, "No meeting data available")
            return False
            
        try:
            # Convert HTTP URL to WebSocket URL
            ws_url = BACKEND_URL.replace('https://', 'wss://').replace('http://', 'ws://')
            websocket_url = f"{ws_url}/ws/meetings/{self.meeting_data['id']}"
            
            # Create a new meeting for this test to avoid conflicts
            meeting_payload = {
                "title": "WebSocket Test Meeting",
                "organizer_name": "WebSocket Test Organizer"
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/meetings",
                json=meeting_payload
            ) as response:
                if response.status != 200:
                    self.log_test("WebSocket Report Notifications", False, "Failed to create test meeting")
                    return False
                
                test_meeting = await response.json()
                
            # Add scrutators
            scrutator_payload = {
                "names": ["WebSocket Scrutator"]
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/meetings/{test_meeting['id']}/scrutators",
                json=scrutator_payload
            ) as response:
                if response.status != 200:
                    self.log_test("WebSocket Report Notifications", False, "Failed to add scrutators")
                    return False
                
                scrutator_data = await response.json()
            
            # Test WebSocket connection and notifications
            ws_test_url = f"{ws_url}/ws/meetings/{test_meeting['id']}"
            
            try:
                async with websockets.connect(ws_test_url, timeout=10) as websocket:
                    # Request report generation to trigger notification
                    request_payload = {
                        "meeting_id": test_meeting["id"],
                        "requested_by": test_meeting["organizer_name"]
                    }
                    
                    # Start listening for WebSocket messages
                    async def listen_for_messages():
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                            return json.loads(message)
                        except asyncio.TimeoutError:
                            return None
                    
                    # Make the request
                    async with self.session.post(
                        f"{API_BASE_URL}/meetings/{test_meeting['id']}/request-report",
                        json=request_payload
                    ) as response:
                        if response.status == 200:
                            # Listen for WebSocket notification
                            message = await listen_for_messages()
                            
                            if message and message.get("type") == "report_generation_requested":
                                self.log_test("WebSocket Report Notifications", True, 
                                            f"WebSocket notification received: {message['type']}")
                                return True
                            else:
                                self.log_test("WebSocket Report Notifications", False, 
                                            f"Expected 'report_generation_requested' notification, got: {message}")
                                return False
                        else:
                            self.log_test("WebSocket Report Notifications", False, 
                                        "Failed to request report generation")
                            return False
                            
            except websockets.exceptions.ConnectionClosed:
                self.log_test("WebSocket Report Notifications", False, "WebSocket connection closed unexpectedly")
                return False
            except Exception as ws_e:
                self.log_test("WebSocket Report Notifications", False, f"WebSocket error: {str(ws_e)}")
                return False
                
        except Exception as e:
            self.log_test("WebSocket Report Notifications", False, f"Error: {str(e)}")
            return False
            
    async def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Vote Secret Backend API Tests")
        print(f"📡 Testing API at: {API_BASE_URL}")
        print("🔍 Testing NEW FEATURE: Automatic Scrutator Access System")
        print("🌍 Testing NEW FEATURE: Timezone Support for PDF Reports")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Core API Tests + New Scrutator Tests + Timezone Tests
            tests = [
                self.test_health_check,
                self.test_mongodb_connectivity,
                self.test_create_meeting,
                # NEW TIMEZONE TESTS
                self.test_create_meeting_with_timezone,
                self.test_create_meeting_different_timezone,
                self.test_backward_compatibility_no_timezone,
                self.test_get_meeting_by_code,
                # NEW SCRUTATOR TESTS
                self.test_add_scrutators,
                self.test_scrutator_automatic_access,
                self.test_scrutator_organizer_interface_access,
                self.test_get_meeting_scrutators,
                self.test_second_scrutator_join,
                self.test_unauthorized_scrutator_join,
                self.test_invalid_scrutator_code,
                # EXISTING PARTICIPANT TESTS
                self.test_participant_join,
                self.test_approve_participant,
                # POLL TESTS
                self.test_create_poll,
                self.test_start_poll,
                self.test_submit_vote,
                self.test_get_poll_results,
                self.test_close_poll_for_report,
                # NEW SCRUTATOR VOTING SYSTEM TESTS
                self.test_request_report_generation,
                self.test_scrutator_vote_approve,
                self.test_scrutator_vote_majority,
                self.test_generate_report_after_approval,
                # NEW TIMEZONE PDF REPORT TESTS
                self.test_timezone_pdf_report_generation,
                self.test_different_timezone_pdf_report,
                self.test_no_timezone_pdf_report,
                self.test_websocket_report_notifications,
                # WEBSOCKET TEST
                self.test_websocket_connection,
            ]
            
            passed = 0
            failed = 0
            
            for test in tests:
                try:
                    result = await test()
                    if result:
                        passed += 1
                    else:
                        failed += 1
                except Exception as e:
                    print(f"❌ FAIL - {test.__name__}: Unexpected error: {str(e)}")
                    failed += 1
                    
                # Small delay between tests
                await asyncio.sleep(0.5)
                
        finally:
            await self.cleanup_session()
            
        # Print summary
        print("=" * 60)
        print(f"📊 TEST SUMMARY")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%" if (passed+failed) > 0 else "0%")
        
        if failed == 0:
            print("🎉 All tests passed! Backend API is working correctly.")
            return True
        else:
            print(f"⚠️  {failed} test(s) failed. Please check the issues above.")
            return False

async def main():
    """Main test runner"""
    tester = VoteSecretAPITester()
    success = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())