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
            
    async def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Vote Secret Backend API Tests")
        print(f"📡 Testing API at: {API_BASE_URL}")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Core API Tests
            tests = [
                self.test_health_check,
                self.test_mongodb_connectivity,
                self.test_create_meeting,
                self.test_get_meeting_by_code,
                self.test_participant_join,
                self.test_approve_participant,
                self.test_create_poll,
                self.test_start_poll,
                self.test_submit_vote,
                self.test_get_poll_results,
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