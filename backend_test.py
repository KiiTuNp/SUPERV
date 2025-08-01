#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Vote Secret Application
Tests all endpoints, database connectivity, WebSocket functionality, and error handling
"""

import requests
import json
import time
import asyncio
import websockets
import tempfile
import os
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BASE_URL = "https://dffd1ffb-03ba-4c55-8b21-65220fce6f6a.preview.emergentagent.com/api"
WS_URL = "wss://0d9cde8c-733a-4be6-8f0b-33dc9641dcb8.preview.emergentagent.com/ws"

class VoteSecretTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_data = {}
        self.results = []
        
    def log_result(self, test_name: str, success: bool, message: str, response_time: float = 0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            'test': test_name,
            'status': status,
            'message': message,
            'response_time': f"{response_time:.3f}s" if response_time > 0 else "N/A"
        })
        print(f"{status} {test_name}: {message} ({response_time:.3f}s)" if response_time > 0 else f"{status} {test_name}: {message}")

    def test_health_check(self):
        """Test health check endpoint"""
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/health")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy' and 'services' in data:
                    self.log_result("Health Check", True, "Service is healthy", response_time)
                    return True
                else:
                    self.log_result("Health Check", False, f"Unhealthy response: {data}", response_time)
                    return False
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Health Check", False, f"Connection error: {str(e)}")
            return False

    def test_create_meeting(self):
        """Test meeting creation endpoint"""
        try:
            meeting_data = {
                "title": "Assemblée Générale Extraordinaire 2025",
                "organizer_name": "Marie Dubois"
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/meetings", json=meeting_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'meeting_code' in data and len(data['meeting_code']) == 8:
                    self.test_data['meeting'] = data
                    self.log_result("Create Meeting", True, f"Meeting created with code: {data['meeting_code']}", response_time)
                    return True
                else:
                    self.log_result("Create Meeting", False, f"Invalid response format: {data}", response_time)
                    return False
            else:
                self.log_result("Create Meeting", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Create Meeting", False, f"Error: {str(e)}")
            return False

    def test_meeting_validation(self):
        """Test meeting creation validation"""
        test_cases = [
            ({"title": "", "organizer_name": "Test"}, "Empty title validation"),
            ({"title": "Test", "organizer_name": ""}, "Empty organizer validation"),
            ({"title": "x" * 201, "organizer_name": "Test"}, "Title length validation"),
            ({"title": "Test", "organizer_name": "x" * 101}, "Organizer length validation")
        ]
        
        all_passed = True
        for invalid_data, test_desc in test_cases:
            try:
                start_time = time.time()
                response = self.session.post(f"{BASE_URL}/meetings", json=invalid_data)
                response_time = time.time() - start_time
                
                if response.status_code == 400:
                    self.log_result(f"Meeting Validation - {test_desc}", True, "Validation error returned correctly", response_time)
                else:
                    self.log_result(f"Meeting Validation - {test_desc}", False, f"Expected 400, got {response.status_code}", response_time)
                    all_passed = False
            except Exception as e:
                self.log_result(f"Meeting Validation - {test_desc}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_get_meeting_by_code(self):
        """Test getting meeting by code"""
        if 'meeting' not in self.test_data:
            self.log_result("Get Meeting by Code", False, "No meeting data available")
            return False
            
        try:
            meeting_code = self.test_data['meeting']['meeting_code']
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_code}")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data['id'] == self.test_data['meeting']['id']:
                    self.log_result("Get Meeting by Code", True, f"Meeting retrieved successfully", response_time)
                    return True
                else:
                    self.log_result("Get Meeting by Code", False, f"Meeting ID mismatch", response_time)
                    return False
            else:
                self.log_result("Get Meeting by Code", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Get Meeting by Code", False, f"Error: {str(e)}")
            return False

    def test_participant_join(self):
        """Test participant joining"""
        if 'meeting' not in self.test_data:
            self.log_result("Participant Join", False, "No meeting data available")
            return False
            
        try:
            join_data = {
                "name": "Pierre Martin",
                "meeting_code": self.test_data['meeting']['meeting_code']
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/participants/join", json=join_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and data['name'] == join_data['name']:
                    self.test_data['participant'] = data
                    self.log_result("Participant Join", True, f"Participant joined successfully", response_time)
                    return True
                else:
                    self.log_result("Participant Join", False, f"Invalid response format: {data}", response_time)
                    return False
            else:
                self.log_result("Participant Join", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Participant Join", False, f"Error: {str(e)}")
            return False

    def test_participant_validation(self):
        """Test participant join validation"""
        if 'meeting' not in self.test_data:
            self.log_result("Participant Validation", False, "No meeting data available")
            return False
            
        test_cases = [
            ({"name": "", "meeting_code": self.test_data['meeting']['meeting_code']}, "Empty name validation"),
            ({"name": "Test", "meeting_code": ""}, "Empty meeting code validation"),
            ({"name": "x" * 101, "meeting_code": self.test_data['meeting']['meeting_code']}, "Name length validation"),
            ({"name": "Test", "meeting_code": "INVALID"}, "Invalid meeting code validation"),
            ({"name": "Pierre Martin", "meeting_code": self.test_data['meeting']['meeting_code']}, "Duplicate name validation")
        ]
        
        all_passed = True
        for invalid_data, test_desc in test_cases:
            try:
                start_time = time.time()
                response = self.session.post(f"{BASE_URL}/participants/join", json=invalid_data)
                response_time = time.time() - start_time
                
                if response.status_code == 400 or response.status_code == 404:
                    self.log_result(f"Participant Validation - {test_desc}", True, "Validation error returned correctly", response_time)
                else:
                    self.log_result(f"Participant Validation - {test_desc}", False, f"Expected 400/404, got {response.status_code}", response_time)
                    all_passed = False
            except Exception as e:
                self.log_result(f"Participant Validation - {test_desc}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_participant_approval(self):
        """Test participant approval"""
        if 'participant' not in self.test_data:
            self.log_result("Participant Approval", False, "No participant data available")
            return False
            
        try:
            participant_id = self.test_data['participant']['id']
            approval_data = {
                "participant_id": participant_id,
                "approved": True
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/participants/{participant_id}/approve", json=approval_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.log_result("Participant Approval", True, "Participant approved successfully", response_time)
                    return True
                else:
                    self.log_result("Participant Approval", False, f"Unexpected response: {data}", response_time)
                    return False
            else:
                self.log_result("Participant Approval", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Participant Approval", False, f"Error: {str(e)}")
            return False

    def test_participant_status(self):
        """Test getting participant status"""
        if 'participant' not in self.test_data:
            self.log_result("Participant Status", False, "No participant data available")
            return False
            
        try:
            participant_id = self.test_data['participant']['id']
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/participants/{participant_id}/status")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if 'status' in data:
                    self.log_result("Participant Status", True, f"Status: {data['status']}", response_time)
                    return True
                else:
                    self.log_result("Participant Status", False, f"Invalid response format: {data}", response_time)
                    return False
            else:
                self.log_result("Participant Status", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Participant Status", False, f"Error: {str(e)}")
            return False

    def test_create_poll(self):
        """Test poll creation WITHOUT show_results_real_time field (NEW MODIFICATION)"""
        if 'meeting' not in self.test_data:
            self.log_result("Create Poll", False, "No meeting data available")
            return False
            
        try:
            poll_data = {
                "question": "Êtes-vous favorable à l'augmentation du budget de 15% ?",
                "options": ["Oui, je suis favorable", "Non, je m'oppose", "Je m'abstiens"],
                "timer_duration": 300
                # NOTE: show_results_real_time field removed as per new modifications
            }
            
            meeting_id = self.test_data['meeting']['id']
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/meetings/{meeting_id}/polls", json=poll_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and data['question'] == poll_data['question']:
                    self.test_data['poll'] = data
                    self.log_result("Create Poll", True, f"Poll created successfully", response_time)
                    return True
                else:
                    self.log_result("Create Poll", False, f"Invalid response format: {data}", response_time)
                    return False
            else:
                self.log_result("Create Poll", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Create Poll", False, f"Error: {str(e)}")
            return False

    def test_poll_validation(self):
        """Test poll creation validation"""
        if 'meeting' not in self.test_data:
            self.log_result("Poll Validation", False, "No meeting data available")
            return False
            
        meeting_id = self.test_data['meeting']['id']
        test_cases = [
            ({"question": "", "options": ["A", "B"]}, "Empty question validation"),
            ({"question": "Test?", "options": ["A"]}, "Insufficient options validation"),
            ({"question": "Test?", "options": ["A", ""]}, "Empty option validation"),
            ({"question": "Test?", "options": ["A", "A"]}, "Duplicate options validation")
        ]
        
        all_passed = True
        for invalid_data, test_desc in test_cases:
            try:
                start_time = time.time()
                response = self.session.post(f"{BASE_URL}/meetings/{meeting_id}/polls", json=invalid_data)
                response_time = time.time() - start_time
                
                if response.status_code == 400:
                    self.log_result(f"Poll Validation - {test_desc}", True, "Validation error returned correctly", response_time)
                else:
                    self.log_result(f"Poll Validation - {test_desc}", False, f"Expected 400, got {response.status_code}", response_time)
                    all_passed = False
            except Exception as e:
                self.log_result(f"Poll Validation - {test_desc}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_start_poll(self):
        """Test starting a poll"""
        if 'poll' not in self.test_data:
            self.log_result("Start Poll", False, "No poll data available")
            return False
            
        try:
            poll_id = self.test_data['poll']['id']
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/polls/{poll_id}/start")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'started':
                    self.log_result("Start Poll", True, "Poll started successfully", response_time)
                    return True
                else:
                    self.log_result("Start Poll", False, f"Unexpected response: {data}", response_time)
                    return False
            else:
                self.log_result("Start Poll", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Start Poll", False, f"Error: {str(e)}")
            return False

    def test_submit_vote(self):
        """Test vote submission"""
        if 'poll' not in self.test_data:
            self.log_result("Submit Vote", False, "No poll data available")
            return False
            
        try:
            poll = self.test_data['poll']
            option_id = poll['options'][0]['id']  # Vote for first option
            
            vote_data = {
                "poll_id": poll['id'],
                "option_id": option_id
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/votes", json=vote_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'vote_submitted':
                    self.log_result("Submit Vote", True, "Vote submitted successfully", response_time)
                    return True
                else:
                    self.log_result("Submit Vote", False, f"Unexpected response: {data}", response_time)
                    return False
            else:
                self.log_result("Submit Vote", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Submit Vote", False, f"Error: {str(e)}")
            return False

    def test_poll_results(self):
        """Test getting poll results"""
        if 'poll' not in self.test_data:
            self.log_result("Poll Results", False, "No poll data available")
            return False
            
        try:
            poll_id = self.test_data['poll']['id']
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/polls/{poll_id}/results")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if 'question' in data and 'results' in data and 'total_votes' in data:
                    self.log_result("Poll Results", True, f"Results retrieved, total votes: {data['total_votes']}", response_time)
                    return True
                else:
                    self.log_result("Poll Results", False, f"Invalid response format: {data}", response_time)
                    return False
            else:
                self.log_result("Poll Results", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Poll Results", False, f"Error: {str(e)}")
            return False

    def test_close_poll(self):
        """Test closing a poll"""
        if 'poll' not in self.test_data:
            self.log_result("Close Poll", False, "No poll data available")
            return False
            
        try:
            poll_id = self.test_data['poll']['id']
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/polls/{poll_id}/close")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'closed':
                    self.log_result("Close Poll", True, "Poll closed successfully", response_time)
                    return True
                else:
                    self.log_result("Close Poll", False, f"Unexpected response: {data}", response_time)
                    return False
            else:
                self.log_result("Close Poll", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Close Poll", False, f"Error: {str(e)}")
            return False

    def test_get_meeting_polls(self):
        """Test getting all polls for a meeting"""
        if 'meeting' not in self.test_data:
            self.log_result("Get Meeting Polls", False, "No meeting data available")
            return False
            
        try:
            meeting_id = self.test_data['meeting']['id']
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/polls")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_result("Get Meeting Polls", True, f"Retrieved {len(data)} polls", response_time)
                    return True
                else:
                    self.log_result("Get Meeting Polls", True, "No polls found (valid response)", response_time)
                    return True
            else:
                self.log_result("Get Meeting Polls", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Get Meeting Polls", False, f"Error: {str(e)}")
            return False

    def test_organizer_view(self):
        """Test organizer view endpoint"""
        if 'meeting' not in self.test_data:
            self.log_result("Organizer View", False, "No meeting data available")
            return False
            
        try:
            meeting_id = self.test_data['meeting']['id']
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/organizer")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if 'meeting' in data and 'participants' in data and 'polls' in data:
                    self.log_result("Organizer View", True, f"Organizer view retrieved successfully", response_time)
                    return True
                else:
                    self.log_result("Organizer View", False, f"Invalid response format: {data}", response_time)
                    return False
            else:
                self.log_result("Organizer View", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Organizer View", False, f"Error: {str(e)}")
            return False

    def test_pdf_report_generation(self):
        """Test PDF report generation"""
        if 'meeting' not in self.test_data:
            self.log_result("PDF Report Generation", False, "No meeting data available")
            return False
            
        try:
            meeting_id = self.test_data['meeting']['id']
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/report")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # Check if response is PDF
                content_type = response.headers.get('content-type', '')
                if 'application/pdf' in content_type:
                    # Save PDF to temporary file to verify it's valid
                    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                        tmp_file.write(response.content)
                        tmp_path = tmp_file.name
                    
                    # Check file size
                    file_size = os.path.getsize(tmp_path)
                    os.unlink(tmp_path)  # Clean up
                    
                    if file_size > 1000:  # PDF should be at least 1KB
                        self.log_result("PDF Report Generation", True, f"PDF generated successfully ({file_size} bytes)", response_time)
                        return True
                    else:
                        self.log_result("PDF Report Generation", False, f"PDF too small ({file_size} bytes)", response_time)
                        return False
                else:
                    self.log_result("PDF Report Generation", False, f"Wrong content type: {content_type}", response_time)
                    return False
            else:
                self.log_result("PDF Report Generation", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("PDF Report Generation", False, f"Error: {str(e)}")
            return False

    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        if 'meeting' not in self.test_data:
            self.log_result("WebSocket Connection", False, "No meeting data available")
            return False
            
        try:
            meeting_id = self.test_data['meeting']['id']
            ws_url = f"{WS_URL}/meetings/{meeting_id}"
            
            start_time = time.time()
            async with websockets.connect(ws_url) as websocket:
                # Send a test message
                await websocket.send("test message")
                
                # Try to receive (with timeout)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    response_time = time.time() - start_time
                    self.log_result("WebSocket Connection", True, "WebSocket connection successful", response_time)
                    return True
                except asyncio.TimeoutError:
                    response_time = time.time() - start_time
                    self.log_result("WebSocket Connection", True, "WebSocket connected (no immediate response)", response_time)
                    return True
                    
        except Exception as e:
            self.log_result("WebSocket Connection", False, f"WebSocket error: {str(e)}")
            return False

    def test_cors_headers(self):
        """Test CORS configuration"""
        try:
            start_time = time.time()
            response = self.session.options(f"{BASE_URL}/health", headers={
                'Origin': 'https://example.com',
                'Access-Control-Request-Method': 'GET'
            })
            response_time = time.time() - start_time
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            if any(cors_headers.values()):
                self.log_result("CORS Configuration", True, f"CORS headers present", response_time)
                return True
            else:
                self.log_result("CORS Configuration", False, "No CORS headers found", response_time)
                return False
                
        except Exception as e:
            self.log_result("CORS Configuration", False, f"Error: {str(e)}")
            return False

    def test_performance_load(self):
        """Test basic performance with multiple requests"""
        try:
            # Test multiple health check requests
            times = []
            for i in range(5):
                start_time = time.time()
                response = self.session.get(f"{BASE_URL}/health")
                response_time = time.time() - start_time
                times.append(response_time)
                
                if response.status_code != 200:
                    self.log_result("Performance Load Test", False, f"Request {i+1} failed with status {response.status_code}")
                    return False
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            
            if avg_time < 2.0 and max_time < 5.0:  # Reasonable thresholds
                self.log_result("Performance Load Test", True, f"Avg: {avg_time:.3f}s, Max: {max_time:.3f}s")
                return True
            else:
                self.log_result("Performance Load Test", False, f"Slow response - Avg: {avg_time:.3f}s, Max: {max_time:.3f}s")
                return False
                
        except Exception as e:
            self.log_result("Performance Load Test", False, f"Error: {str(e)}")
            return False

    def test_error_handling(self):
        """Test error handling for non-existent resources"""
        test_cases = [
            (f"{BASE_URL}/meetings/INVALID", "Invalid meeting code"),
            (f"{BASE_URL}/participants/invalid-id/status", "Invalid participant ID"),
            (f"{BASE_URL}/polls/invalid-id/results", "Invalid poll ID"),
            (f"{BASE_URL}/meetings/invalid-id/report", "Invalid meeting ID for report")
        ]
        
        all_passed = True
        for url, test_desc in test_cases:
            try:
                start_time = time.time()
                response = self.session.get(url)
                response_time = time.time() - start_time
                
                if response.status_code == 404:
                    self.log_result(f"Error Handling - {test_desc}", True, "404 returned correctly", response_time)
                else:
                    self.log_result(f"Error Handling - {test_desc}", False, f"Expected 404, got {response.status_code}", response_time)
                    all_passed = False
            except Exception as e:
                self.log_result(f"Error Handling - {test_desc}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_scrutator_functionality(self):
        """
        Test complete scrutator functionality as requested:
        1. Create meeting "Assemblée Test Scrutateurs"
        2. Add 3 scrutators: "Jean Dupont", "Marie Martin", "Pierre Durand"
        3. Verify scrutator code generation (format SCxxxxxx)
        4. Test scrutator connection with valid name and code
        5. Test rejection of unauthorized name
        6. Add participants and polls
        7. Generate PDF with scrutators
        8. Verify complete data deletion
        """
        print("\n🎯 TESTING COMPLETE SCRUTATOR FUNCTIONALITY")
        print("=" * 70)
        
        scenario_data = {}
        all_passed = True
        
        # Step 1: Create meeting "Assemblée Test Scrutateurs"
        try:
            meeting_data = {
                "title": "Assemblée Test Scrutateurs",
                "organizer_name": "Alice Dupont"
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/meetings", json=meeting_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                scenario_data['meeting'] = response.json()
                self.log_result("Step 1 - Create Meeting", True, f"Meeting created with code: {scenario_data['meeting']['meeting_code']}", response_time)
            else:
                self.log_result("Step 1 - Create Meeting", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Step 1 - Create Meeting", False, f"Error: {str(e)}")
            return False
        
        # Step 2: Add 3 scrutators
        try:
            scrutator_data = {
                "names": ["Jean Dupont", "Marie Martin", "Pierre Durand"]
            }
            
            meeting_id = scenario_data['meeting']['id']
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/meetings/{meeting_id}/scrutators", json=scrutator_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if 'scrutator_code' in data and data['scrutator_code'].startswith('SC') and len(data['scrutator_code']) == 8:
                    scenario_data['scrutator_code'] = data['scrutator_code']
                    scenario_data['scrutators'] = data['scrutators']
                    self.log_result("Step 2 - Add Scrutators", True, f"3 scrutators added with code: {data['scrutator_code']}", response_time)
                else:
                    self.log_result("Step 2 - Add Scrutators", False, f"Invalid scrutator code format: {data}", response_time)
                    return False
            else:
                self.log_result("Step 2 - Add Scrutators", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Step 2 - Add Scrutators", False, f"Error: {str(e)}")
            return False
        
        # Step 3: Get scrutators list
        try:
            meeting_id = scenario_data['meeting']['id']
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/scrutators")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if 'scrutator_code' in data and 'scrutators' in data and len(data['scrutators']) == 3:
                    self.log_result("Step 3 - Get Scrutators", True, f"Retrieved {len(data['scrutators'])} scrutators", response_time)
                else:
                    self.log_result("Step 3 - Get Scrutators", False, f"Invalid response format: {data}", response_time)
                    all_passed = False
            else:
                self.log_result("Step 3 - Get Scrutators", False, f"HTTP {response.status_code}: {response.text}", response_time)
                all_passed = False
        except Exception as e:
            self.log_result("Step 3 - Get Scrutators", False, f"Error: {str(e)}")
            all_passed = False
        
        # Step 4: Test scrutator connection with valid name
        try:
            join_data = {
                "name": "Jean Dupont",
                "scrutator_code": scenario_data['scrutator_code']
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/scrutators/join", json=join_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if 'meeting' in data and 'scrutator_name' in data and data['scrutator_name'] == "Jean Dupont":
                    self.log_result("Step 4 - Valid Scrutator Join", True, f"Jean Dupont connected successfully", response_time)
                else:
                    self.log_result("Step 4 - Valid Scrutator Join", False, f"Invalid response format: {data}", response_time)
                    all_passed = False
            else:
                self.log_result("Step 4 - Valid Scrutator Join", False, f"HTTP {response.status_code}: {response.text}", response_time)
                all_passed = False
        except Exception as e:
            self.log_result("Step 4 - Valid Scrutator Join", False, f"Error: {str(e)}")
            all_passed = False
        
        # Step 5: Test rejection of unauthorized name
        try:
            join_data = {
                "name": "Antoine Bernard",  # Not in authorized list
                "scrutator_code": scenario_data['scrutator_code']
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/scrutators/join", json=join_data)
            response_time = time.time() - start_time
            
            if response.status_code == 403:
                self.log_result("Step 5 - Unauthorized Scrutator Rejection", True, f"Antoine Bernard correctly rejected", response_time)
            else:
                self.log_result("Step 5 - Unauthorized Scrutator Rejection", False, f"Expected 403, got {response.status_code}", response_time)
                all_passed = False
        except Exception as e:
            self.log_result("Step 5 - Unauthorized Scrutator Rejection", False, f"Error: {str(e)}")
            all_passed = False
        
        # Step 6: Add participants and polls for complete scenario
        try:
            # Add participants
            participants = ["Sophie Lefebvre", "Pierre-Alexandre Martin"]
            scenario_data['participants'] = []
            
            for participant_name in participants:
                join_data = {
                    "name": participant_name,
                    "meeting_code": scenario_data['meeting']['meeting_code']
                }
                
                response = self.session.post(f"{BASE_URL}/participants/join", json=join_data)
                if response.status_code == 200:
                    participant_data = response.json()
                    scenario_data['participants'].append(participant_data)
                    
                    # Approve participant
                    approval_data = {
                        "participant_id": participant_data['id'],
                        "approved": True
                    }
                    self.session.post(f"{BASE_URL}/participants/{participant_data['id']}/approve", json=approval_data)
            
            # Create polls
            polls_data = [
                {
                    "question": "Approuvez-vous le budget 2025 ?",
                    "options": ["Oui", "Non", "Abstention"],
                    "show_results_real_time": True
                },
                {
                    "question": "Validez-vous les nouveaux statuts ?",
                    "options": ["Approuvé", "Rejeté", "Report"],
                    "show_results_real_time": True
                }
            ]
            
            scenario_data['polls'] = []
            meeting_id = scenario_data['meeting']['id']
            
            for poll_data in polls_data:
                response = self.session.post(f"{BASE_URL}/meetings/{meeting_id}/polls", json=poll_data)
                if response.status_code == 200:
                    poll = response.json()
                    scenario_data['polls'].append(poll)
                    
                    # Start poll and add some votes
                    self.session.post(f"{BASE_URL}/polls/{poll['id']}/start")
                    
                    # Add votes
                    for i in range(2):  # 2 votes per poll
                        vote_data = {
                            "poll_id": poll['id'],
                            "option_id": poll['options'][i % len(poll['options'])]['id']
                        }
                        self.session.post(f"{BASE_URL}/votes", json=vote_data)
                    
                    # Close poll
                    self.session.post(f"{BASE_URL}/polls/{poll['id']}/close")
            
            self.log_result("Step 6 - Add Participants and Polls", True, f"Added {len(scenario_data['participants'])} participants and {len(scenario_data['polls'])} polls")
            
        except Exception as e:
            self.log_result("Step 6 - Add Participants and Polls", False, f"Error: {str(e)}")
            all_passed = False
        
        # Step 7: Generate PDF with scrutators
        try:
            meeting_id = scenario_data['meeting']['id']
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/report")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'application/pdf' in content_type:
                    file_size = len(response.content)
                    # Check if PDF contains scrutator data (basic check)
                    pdf_content = response.content.decode('latin-1', errors='ignore')
                    has_scrutators = 'SCRUTATEURS' in pdf_content or 'Jean Dupont' in pdf_content
                    
                    if has_scrutators:
                        self.log_result("Step 7 - Generate PDF with Scrutators", True, f"PDF generated with scrutators ({file_size} bytes)", response_time)
                    else:
                        self.log_result("Step 7 - Generate PDF with Scrutators", False, f"PDF generated but scrutators not found in content", response_time)
                        all_passed = False
                else:
                    self.log_result("Step 7 - Generate PDF with Scrutators", False, f"Wrong content type: {content_type}", response_time)
                    all_passed = False
            else:
                self.log_result("Step 7 - Generate PDF with Scrutators", False, f"HTTP {response.status_code}: {response.text}", response_time)
                all_passed = False
        except Exception as e:
            self.log_result("Step 7 - Generate PDF with Scrutators", False, f"Error: {str(e)}")
            all_passed = False
        
        # Step 8: Verify complete data deletion
        try:
            meeting_id = scenario_data['meeting']['id']
            meeting_code = scenario_data['meeting']['meeting_code']
            
            # Test meeting deletion
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_code}")
            if response.status_code == 404:
                self.log_result("Step 8a - Meeting Deleted", True, "Meeting correctly deleted")
            else:
                self.log_result("Step 8a - Meeting Deleted", False, f"Expected 404, got {response.status_code}")
                all_passed = False
            
            # Test scrutators deletion
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/scrutators")
            if response.status_code == 404:
                self.log_result("Step 8b - Scrutators Deleted", True, "Scrutators correctly deleted")
            else:
                self.log_result("Step 8b - Scrutators Deleted", False, f"Expected 404, got {response.status_code}")
                all_passed = False
            
            # Test organizer view deletion
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/organizer")
            if response.status_code == 404:
                self.log_result("Step 8c - Organizer View Deleted", True, "Organizer view correctly deleted")
            else:
                self.log_result("Step 8c - Organizer View Deleted", False, f"Expected 404, got {response.status_code}")
                all_passed = False
                
        except Exception as e:
            self.log_result("Step 8 - Verify Data Deletion", False, f"Error: {str(e)}")
            all_passed = False
        
        # Summary
        if all_passed:
            self.log_result("SCRUTATOR FUNCTIONALITY", True, "✅ All scrutator tests passed - Functionality working correctly")
            print("\n🎉 SCRUTATOR VALIDATION COMPLETE:")
            print("✅ Scrutator code generation working (SCxxxxxx format)")
            print("✅ Scrutator validation and authorization working")
            print("✅ PDF generation includes scrutator data")
            print("✅ Complete data cleanup includes scrutators")
        else:
            self.log_result("SCRUTATOR FUNCTIONALITY", False, "❌ Some scrutator tests failed - Review issues above")
        
        return all_passed

    def test_scrutator_validation(self):
        """Test scrutator validation scenarios"""
        print("\n🔍 TESTING SCRUTATOR VALIDATION")
        print("=" * 50)
        
        # First create a meeting for testing
        meeting_data = {
            "title": "Test Validation Scrutateurs",
            "organizer_name": "Test Organizer"
        }
        
        response = self.session.post(f"{BASE_URL}/meetings", json=meeting_data)
        if response.status_code != 200:
            self.log_result("Scrutator Validation Setup", False, "Failed to create test meeting")
            return False
        
        meeting = response.json()
        meeting_id = meeting['id']
        all_passed = True
        
        # Test validation cases
        test_cases = [
            ({"names": []}, "Empty names list validation"),
            ({"names": [""]}, "Empty name validation"),
            ({"names": ["x" * 101]}, "Name length validation"),
            ({"names": ["Jean Dupont", "Jean Dupont"]}, "Duplicate names validation"),
            ({"names": ["Jean Dupont", "Marie Martin", ""]}, "Mixed valid/invalid names validation")
        ]
        
        for invalid_data, test_desc in test_cases:
            try:
                start_time = time.time()
                response = self.session.post(f"{BASE_URL}/meetings/{meeting_id}/scrutators", json=invalid_data)
                response_time = time.time() - start_time
                
                if response.status_code == 400:
                    self.log_result(f"Scrutator Validation - {test_desc}", True, "Validation error returned correctly", response_time)
                else:
                    self.log_result(f"Scrutator Validation - {test_desc}", False, f"Expected 400, got {response.status_code}", response_time)
                    all_passed = False
            except Exception as e:
                self.log_result(f"Scrutator Validation - {test_desc}", False, f"Error: {str(e)}")
                all_passed = False
        
        # Clean up test meeting
        try:
            self.session.get(f"{BASE_URL}/meetings/{meeting_id}/report")
        except:
            pass
        
        return all_passed

    def test_advanced_scrutator_workflow_with_approval_and_voting(self):
        """
        Test the NEW advanced scrutator workflow with approval and majority voting:
        1. Create assembly "Test Scrutateurs Approbation 2025"
        2. Add 3 scrutators: "Jean Dupont", "Marie Martin", "Pierre Durand"
        3. Test scrutator connection with approval required (pending_approval status)
        4. Organizer approves Jean Dupont
        5. Jean Dupont can now access interface
        6. Test majority voting system for PDF generation
        7. Test majority rejection scenario
        """
        print("\n🎯 TESTING ADVANCED SCRUTATOR WORKFLOW WITH APPROVAL AND MAJORITY VOTING")
        print("=" * 80)
        
        scenario_data = {}
        all_passed = True
        
        # Step 1: Create assembly "Test Scrutateurs Approbation 2025"
        try:
            meeting_data = {
                "title": "Test Scrutateurs Approbation 2025",
                "organizer_name": "Alice Organisateur"
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/meetings", json=meeting_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                scenario_data['meeting'] = response.json()
                self.log_result("Step 1 - Create Assembly", True, f"Assembly created: {scenario_data['meeting']['meeting_code']}", response_time)
            else:
                self.log_result("Step 1 - Create Assembly", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Step 1 - Create Assembly", False, f"Error: {str(e)}")
            return False
        
        # Step 2: Add 3 scrutators
        try:
            scrutator_data = {
                "names": ["Jean Dupont", "Marie Martin", "Pierre Durand"]
            }
            
            meeting_id = scenario_data['meeting']['id']
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/meetings/{meeting_id}/scrutators", json=scrutator_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                scenario_data['scrutator_code'] = data['scrutator_code']
                scenario_data['scrutators'] = data['scrutators']
                self.log_result("Step 2 - Add Scrutators", True, f"3 scrutators added with code: {data['scrutator_code']}", response_time)
            else:
                self.log_result("Step 2 - Add Scrutators", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Step 2 - Add Scrutators", False, f"Error: {str(e)}")
            return False
        
        # Step 3: Test Jean Dupont connection with approval required (should get pending_approval)
        try:
            join_data = {
                "name": "Jean Dupont",
                "scrutator_code": scenario_data['scrutator_code']
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/scrutators/join", json=join_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'pending_approval':
                    self.log_result("Step 3 - Jean Dupont Pending Approval", True, f"Jean Dupont correctly receives pending_approval status", response_time)
                    scenario_data['jean_pending'] = True
                else:
                    self.log_result("Step 3 - Jean Dupont Pending Approval", False, f"Expected pending_approval, got: {data}", response_time)
                    all_passed = False
            else:
                self.log_result("Step 3 - Jean Dupont Pending Approval", False, f"HTTP {response.status_code}: {response.text}", response_time)
                all_passed = False
        except Exception as e:
            self.log_result("Step 3 - Jean Dupont Pending Approval", False, f"Error: {str(e)}")
            all_passed = False
        
        # Step 4: Get all scrutators and approve them all
        try:
            meeting_id = scenario_data['meeting']['id']
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/scrutators")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                scrutators_list = data['scrutators']
                
                # Approve all scrutators
                approved_count = 0
                for scrutator in scrutators_list:
                    approval_data = {
                        "scrutator_id": scrutator['id'],
                        "approved": True
                    }
                    
                    response = self.session.post(f"{BASE_URL}/scrutators/{scrutator['id']}/approve", json=approval_data)
                    if response.status_code == 200:
                        approved_count += 1
                
                if approved_count == 3:
                    self.log_result("Step 4 - Approve All Scrutators", True, f"All 3 scrutators approved successfully", response_time)
                    scenario_data['all_approved'] = True
                else:
                    self.log_result("Step 4 - Approve All Scrutators", False, f"Only {approved_count}/3 scrutators approved")
                    all_passed = False
            else:
                self.log_result("Step 4 - Get Scrutators for Approval", False, f"HTTP {response.status_code}: {response.text}")
                all_passed = False
        except Exception as e:
            self.log_result("Step 4 - Approve All Scrutators", False, f"Error: {str(e)}")
            all_passed = False
        
        # Step 5: Test Jean Dupont can now access interface (should get approved status)
        try:
            join_data = {
                "name": "Jean Dupont",
                "scrutator_code": scenario_data['scrutator_code']
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/scrutators/join", json=join_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'approved' and 'meeting' in data:
                    self.log_result("Step 5 - Jean Dupont Access Interface", True, f"Jean Dupont can now access interface", response_time)
                else:
                    self.log_result("Step 5 - Jean Dupont Access Interface", False, f"Expected approved access, got: {data}", response_time)
                    all_passed = False
            else:
                self.log_result("Step 5 - Jean Dupont Access Interface", False, f"HTTP {response.status_code}: {response.text}", response_time)
                all_passed = False
        except Exception as e:
            self.log_result("Step 5 - Jean Dupont Access Interface", False, f"Error: {str(e)}")
            all_passed = False
        
        # Step 6: Add participants and polls for PDF generation test
        try:
            # Add participants
            participants = ["Sophie Participant", "Pierre Votant"]
            scenario_data['participants'] = []
            
            for participant_name in participants:
                join_data = {
                    "name": participant_name,
                    "meeting_code": scenario_data['meeting']['meeting_code']
                }
                
                response = self.session.post(f"{BASE_URL}/participants/join", json=join_data)
                if response.status_code == 200:
                    participant_data = response.json()
                    scenario_data['participants'].append(participant_data)
                    
                    # Approve participant
                    approval_data = {
                        "participant_id": participant_data['id'],
                        "approved": True
                    }
                    self.session.post(f"{BASE_URL}/participants/{participant_data['id']}/approve", json=approval_data)
            
            # Create polls
            poll_data = {
                "question": "Approuvez-vous le budget 2025 ?",
                "options": ["Oui", "Non", "Abstention"],
                "show_results_real_time": True
            }
            
            meeting_id = scenario_data['meeting']['id']
            response = self.session.post(f"{BASE_URL}/meetings/{meeting_id}/polls", json=poll_data)
            if response.status_code == 200:
                poll = response.json()
                scenario_data['poll'] = poll
                
                # Start poll and add votes
                self.session.post(f"{BASE_URL}/polls/{poll['id']}/start")
                
                # Add votes
                for i in range(3):
                    vote_data = {
                        "poll_id": poll['id'],
                        "option_id": poll['options'][i % len(poll['options'])]['id']
                    }
                    self.session.post(f"{BASE_URL}/votes", json=vote_data)
                
                # Close poll
                self.session.post(f"{BASE_URL}/polls/{poll['id']}/close")
            
            self.log_result("Step 6 - Setup Participants and Polls", True, f"Added {len(scenario_data['participants'])} participants and 1 poll")
            
        except Exception as e:
            self.log_result("Step 6 - Setup Participants and Polls", False, f"Error: {str(e)}")
            all_passed = False
        
        # Step 7: Test majority voting system for PDF generation
        try:
            meeting_id = scenario_data['meeting']['id']
            
            # Request report generation
            request_data = {
                "meeting_id": meeting_id,
                "requested_by": "Alice Organisateur"
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/meetings/{meeting_id}/request-report", json=request_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('scrutator_approval_required') and data.get('scrutator_count') == 3 and data.get('majority_needed') == 2:  # (3//2)+1 = 2
                    self.log_result("Step 7a - Request Report Generation", True, f"Report request sent to scrutators, majority needed: {data['majority_needed']}", response_time)
                    
                    # Simulate votes: Jean=YES, Marie=NO, Pierre=YES (2/3 majority)
                    votes = [
                        ("Jean Dupont", True, "Jean votes YES"),
                        ("Marie Martin", False, "Marie votes NO"),
                        ("Pierre Durand", True, "Pierre votes YES")
                    ]
                    
                    for scrutator_name, vote, desc in votes:
                        vote_data = {
                            "meeting_id": meeting_id,
                            "scrutator_name": scrutator_name,
                            "approved": vote
                        }
                        
                        start_time = time.time()
                        response = self.session.post(f"{BASE_URL}/meetings/{meeting_id}/scrutator-vote", json=vote_data)
                        response_time = time.time() - start_time
                        
                        if response.status_code == 200:
                            vote_result = response.json()
                            self.log_result(f"Step 7b - {desc}", True, f"Vote recorded: {vote_result.get('message', 'Vote submitted')}", response_time)
                            
                            # Check if decision is made
                            if vote_result.get('decision') == 'approved':
                                self.log_result("Step 7c - Majority Approval Reached", True, f"Majority approved generation: {vote_result['yes_votes']}/{vote_result['majority_needed']}")
                                scenario_data['generation_approved'] = True
                                break
                        else:
                            self.log_result(f"Step 7b - {desc}", False, f"HTTP {response.status_code}: {response.text}", response_time)
                            all_passed = False
                    
                else:
                    self.log_result("Step 7a - Request Report Generation", False, f"Unexpected response: {data}", response_time)
                    all_passed = False
            else:
                self.log_result("Step 7a - Request Report Generation", False, f"HTTP {response.status_code}: {response.text}", response_time)
                all_passed = False
        except Exception as e:
            self.log_result("Step 7 - Test Majority Voting", False, f"Error: {str(e)}")
            all_passed = False
        
        # Step 8: Test actual PDF generation after approval
        try:
            if scenario_data.get('generation_approved'):
                meeting_id = scenario_data['meeting']['id']
                start_time = time.time()
                response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/report")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'application/pdf' in content_type:
                        file_size = len(response.content)
                        self.log_result("Step 8 - Generate PDF After Approval", True, f"PDF generated successfully ({file_size} bytes)", response_time)
                    else:
                        self.log_result("Step 8 - Generate PDF After Approval", False, f"Wrong content type: {content_type}", response_time)
                        all_passed = False
                else:
                    self.log_result("Step 8 - Generate PDF After Approval", False, f"HTTP {response.status_code}: {response.text}", response_time)
                    all_passed = False
            else:
                self.log_result("Step 8 - Generate PDF After Approval", False, "Cannot test PDF generation - approval not reached")
                all_passed = False
        except Exception as e:
            self.log_result("Step 8 - Generate PDF After Approval", False, f"Error: {str(e)}")
            all_passed = False
        
        # Step 9: Test majority rejection scenario
        try:
            # Create new assembly for rejection test
            meeting_data = {
                "title": "Test Scrutateurs Rejet 2025",
                "organizer_name": "Bob Organisateur"
            }
            
            response = self.session.post(f"{BASE_URL}/meetings", json=meeting_data)
            if response.status_code == 200:
                rejection_meeting = response.json()
                
                # Add scrutators
                scrutator_data = {
                    "names": ["Alice Scrutateur", "Bob Scrutateur", "Charlie Scrutateur"]
                }
                
                response = self.session.post(f"{BASE_URL}/meetings/{rejection_meeting['id']}/scrutators", json=scrutator_data)
                if response.status_code == 200:
                    rejection_data = response.json()
                    
                    # Get and approve all scrutators
                    response = self.session.get(f"{BASE_URL}/meetings/{rejection_meeting['id']}/scrutators")
                    if response.status_code == 200:
                        scrutators_list = response.json()['scrutators']
                        for scrutator in scrutators_list:
                            approval_data = {
                                "scrutator_id": scrutator['id'],
                                "approved": True
                            }
                            self.session.post(f"{BASE_URL}/scrutators/{scrutator['id']}/approve", json=approval_data)
                    
                    # Request report generation
                    request_data = {
                        "meeting_id": rejection_meeting['id'],
                        "requested_by": "Bob Organisateur"
                    }
                    
                    response = self.session.post(f"{BASE_URL}/meetings/{rejection_meeting['id']}/request-report", json=request_data)
                    if response.status_code == 200:
                        # Simulate rejection votes: Alice=NO, Bob=NO, Charlie=YES (2/3 reject)
                        rejection_votes = [
                            ("Alice Scrutateur", False, "Alice votes NO"),
                            ("Bob Scrutateur", False, "Bob votes NO"),
                            ("Charlie Scrutateur", True, "Charlie votes YES")
                        ]
                        
                        for scrutator_name, vote, desc in rejection_votes:
                            vote_data = {
                                "meeting_id": rejection_meeting['id'],
                                "scrutator_name": scrutator_name,
                                "approved": vote
                            }
                            
                            response = self.session.post(f"{BASE_URL}/meetings/{rejection_meeting['id']}/scrutator-vote", json=vote_data)
                            if response.status_code == 200:
                                vote_result = response.json()
                                
                                if vote_result.get('decision') == 'rejected':
                                    self.log_result("Step 9 - Test Majority Rejection", True, f"Majority correctly rejected generation: {vote_result['no_votes']}/{vote_result['majority_needed']}")
                                    
                                    # Test that PDF generation is now blocked
                                    response = self.session.get(f"{BASE_URL}/meetings/{rejection_meeting['id']}/report")
                                    if response.status_code == 403:
                                        self.log_result("Step 9b - PDF Generation Blocked", True, "PDF generation correctly blocked after rejection")
                                    else:
                                        self.log_result("Step 9b - PDF Generation Blocked", False, f"Expected 403, got {response.status_code}")
                                        all_passed = False
                                    break
                    
                    # Clean up rejection test meeting
                    try:
                        self.session.get(f"{BASE_URL}/meetings/{rejection_meeting['id']}/report")
                    except:
                        pass
                        
        except Exception as e:
            self.log_result("Step 9 - Test Majority Rejection", False, f"Error: {str(e)}")
            all_passed = False
        
        # Summary
        if all_passed:
            self.log_result("ADVANCED SCRUTATOR WORKFLOW", True, "✅ All advanced scrutator workflow tests passed")
            print("\n🎉 ADVANCED SCRUTATOR WORKFLOW VALIDATION COMPLETE:")
            print("✅ Scrutator approval workflow working (pending → approved)")
            print("✅ Majority voting system working (2/3 approval)")
            print("✅ PDF generation protected by scrutator approval")
            print("✅ Majority rejection system working")
            print("✅ All critical endpoints functioning correctly")
        else:
            self.log_result("ADVANCED SCRUTATOR WORKFLOW", False, "❌ Some advanced scrutator workflow tests failed")
        
        return all_passed

    def test_complete_meeting_closure_notification_scenario(self):
        """
        Test complete scenario for participant notification when meeting is closed.
        This tests the exact scenario requested by the user:
        1. Create meeting with organizer "Marie Organisateur"
        2. Add and approve 2 participants: "Jean Participant" and "Sophie Votante"
        3. Create poll with 2 options: "Oui" and "Non"
        4. Start poll and simulate votes
        5. Close poll
        6. Generate PDF report (this deletes the meeting)
        7. Verify meeting is deleted (404 expected)
        8. Test that participants receive 404 when trying to access data
        """
        print("\n🎯 TESTING COMPLETE MEETING CLOSURE NOTIFICATION SCENARIO")
        print("=" * 70)
        
        scenario_data = {}
        all_passed = True
        
        # Step 1: Create meeting with organizer "Marie Organisateur"
        try:
            meeting_data = {
                "title": "Réunion de Test - Notification de Fermeture",
                "organizer_name": "Marie Organisateur"
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/meetings", json=meeting_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                scenario_data['meeting'] = response.json()
                self.log_result("Step 1 - Create Meeting", True, f"Meeting created with code: {scenario_data['meeting']['meeting_code']}", response_time)
            else:
                self.log_result("Step 1 - Create Meeting", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Step 1 - Create Meeting", False, f"Error: {str(e)}")
            return False
        
        # Step 2: Add and approve 2 participants
        participants = ["Jean Participant", "Sophie Votante"]
        scenario_data['participants'] = []
        
        for i, participant_name in enumerate(participants, 1):
            try:
                # Join meeting
                join_data = {
                    "name": participant_name,
                    "meeting_code": scenario_data['meeting']['meeting_code']
                }
                
                start_time = time.time()
                response = self.session.post(f"{BASE_URL}/participants/join", json=join_data)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    participant_data = response.json()
                    scenario_data['participants'].append(participant_data)
                    self.log_result(f"Step 2.{i}a - Add Participant {participant_name}", True, f"Participant joined successfully", response_time)
                    
                    # Approve participant
                    approval_data = {
                        "participant_id": participant_data['id'],
                        "approved": True
                    }
                    
                    start_time = time.time()
                    response = self.session.post(f"{BASE_URL}/participants/{participant_data['id']}/approve", json=approval_data)
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        self.log_result(f"Step 2.{i}b - Approve Participant {participant_name}", True, f"Participant approved successfully", response_time)
                    else:
                        self.log_result(f"Step 2.{i}b - Approve Participant {participant_name}", False, f"HTTP {response.status_code}: {response.text}", response_time)
                        all_passed = False
                else:
                    self.log_result(f"Step 2.{i}a - Add Participant {participant_name}", False, f"HTTP {response.status_code}: {response.text}", response_time)
                    all_passed = False
            except Exception as e:
                self.log_result(f"Step 2.{i} - Add/Approve Participant {participant_name}", False, f"Error: {str(e)}")
                all_passed = False
        
        if not all_passed:
            return False
        
        # Step 3: Create poll with 2 options: "Oui" and "Non"
        try:
            poll_data = {
                "question": "Êtes-vous d'accord avec la proposition ?",
                "options": ["Oui", "Non"],
                "show_results_real_time": True
            }
            
            meeting_id = scenario_data['meeting']['id']
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/meetings/{meeting_id}/polls", json=poll_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                scenario_data['poll'] = response.json()
                self.log_result("Step 3 - Create Poll", True, f"Poll created with 2 options", response_time)
            else:
                self.log_result("Step 3 - Create Poll", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Step 3 - Create Poll", False, f"Error: {str(e)}")
            return False
        
        # Step 4: Start poll and simulate votes
        try:
            poll_id = scenario_data['poll']['id']
            
            # Start poll
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/polls/{poll_id}/start")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result("Step 4a - Start Poll", True, f"Poll started successfully", response_time)
                
                # Simulate votes from both participants
                poll_options = scenario_data['poll']['options']
                votes = [
                    (poll_options[0]['id'], "Jean votes Oui"),  # Jean votes for first option (Oui)
                    (poll_options[1]['id'], "Sophie votes Non")  # Sophie votes for second option (Non)
                ]
                
                for option_id, vote_desc in votes:
                    vote_data = {
                        "poll_id": poll_id,
                        "option_id": option_id
                    }
                    
                    start_time = time.time()
                    response = self.session.post(f"{BASE_URL}/votes", json=vote_data)
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        self.log_result(f"Step 4b - Simulate Vote ({vote_desc})", True, f"Vote submitted successfully", response_time)
                    else:
                        self.log_result(f"Step 4b - Simulate Vote ({vote_desc})", False, f"HTTP {response.status_code}: {response.text}", response_time)
                        all_passed = False
            else:
                self.log_result("Step 4a - Start Poll", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Step 4 - Start Poll and Simulate Votes", False, f"Error: {str(e)}")
            return False
        
        if not all_passed:
            return False
        
        # Step 5: Close poll
        try:
            poll_id = scenario_data['poll']['id']
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/polls/{poll_id}/close")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result("Step 5 - Close Poll", True, f"Poll closed successfully", response_time)
            else:
                self.log_result("Step 5 - Close Poll", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Step 5 - Close Poll", False, f"Error: {str(e)}")
            return False
        
        # Step 6: Generate PDF report (this should delete the meeting)
        try:
            meeting_id = scenario_data['meeting']['id']
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/report")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'application/pdf' in content_type:
                    file_size = len(response.content)
                    self.log_result("Step 6 - Generate PDF Report", True, f"PDF generated successfully ({file_size} bytes) - Meeting should now be deleted", response_time)
                else:
                    self.log_result("Step 6 - Generate PDF Report", False, f"Wrong content type: {content_type}", response_time)
                    return False
            else:
                self.log_result("Step 6 - Generate PDF Report", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Step 6 - Generate PDF Report", False, f"Error: {str(e)}")
            return False
        
        # Step 7: Verify meeting is deleted (404 expected)
        try:
            meeting_code = scenario_data['meeting']['meeting_code']
            meeting_id = scenario_data['meeting']['id']
            
            # Test meeting by code
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_code}")
            response_time = time.time() - start_time
            
            if response.status_code == 404:
                self.log_result("Step 7a - Verify Meeting Deleted (by code)", True, f"Meeting correctly returns 404", response_time)
            else:
                self.log_result("Step 7a - Verify Meeting Deleted (by code)", False, f"Expected 404, got {response.status_code}", response_time)
                all_passed = False
            
            # Test organizer view
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/organizer")
            response_time = time.time() - start_time
            
            if response.status_code == 404:
                self.log_result("Step 7b - Verify Organizer View Deleted", True, f"Organizer view correctly returns 404", response_time)
            else:
                self.log_result("Step 7b - Verify Organizer View Deleted", False, f"Expected 404, got {response.status_code}", response_time)
                all_passed = False
                
        except Exception as e:
            self.log_result("Step 7 - Verify Meeting Deleted", False, f"Error: {str(e)}")
            all_passed = False
        
        # Step 8: Test that participants receive 404 when trying to access data
        try:
            for i, participant in enumerate(scenario_data['participants'], 1):
                participant_id = participant['id']
                participant_name = participant['name']
                
                # Test participant status
                start_time = time.time()
                response = self.session.get(f"{BASE_URL}/participants/{participant_id}/status")
                response_time = time.time() - start_time
                
                if response.status_code == 404:
                    self.log_result(f"Step 8.{i}a - Participant Status 404 ({participant_name})", True, f"Participant status correctly returns 404", response_time)
                else:
                    self.log_result(f"Step 8.{i}a - Participant Status 404 ({participant_name})", False, f"Expected 404, got {response.status_code}", response_time)
                    all_passed = False
            
            # Test poll results
            poll_id = scenario_data['poll']['id']
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/polls/{poll_id}/results")
            response_time = time.time() - start_time
            
            if response.status_code == 404:
                self.log_result("Step 8b - Poll Results 404", True, f"Poll results correctly returns 404", response_time)
            else:
                self.log_result("Step 8b - Poll Results 404", False, f"Expected 404, got {response.status_code}", response_time)
                all_passed = False
            
            # Test meeting polls
            meeting_id = scenario_data['meeting']['id']
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/polls")
            response_time = time.time() - start_time
            
            if response.status_code == 404:
                self.log_result("Step 8c - Meeting Polls 404", True, f"Meeting polls correctly returns 404", response_time)
            else:
                self.log_result("Step 8c - Meeting Polls 404", False, f"Expected 404, got {response.status_code}", response_time)
                all_passed = False
                
        except Exception as e:
            self.log_result("Step 8 - Test Participant 404 Responses", False, f"Error: {str(e)}")
            all_passed = False
        
        # Summary
        if all_passed:
            self.log_result("COMPLETE SCENARIO", True, "✅ All steps passed - Meeting closure notification mechanism working correctly")
            print("\n🎉 SCENARIO VALIDATION COMPLETE:")
            print("✅ Meeting completely deleted after PDF generation")
            print("✅ All participant endpoints return 404 after deletion")
            print("✅ All poll endpoints return 404 after deletion")
            print("✅ Frontend polling will detect these 404s and trigger notifications")
        else:
            self.log_result("COMPLETE SCENARIO", False, "❌ Some steps failed - Review issues above")
        
        return all_passed

    def test_bug_fix_scrutator_workflow_complete(self):
        """
        TEST DE CORRECTION DU BUG - WORKFLOW SCRUTATEURS COMPLET
        
        Test the complete workflow as requested by the user to validate the bug fix:
        1. Create assembly "Test Correction Bug Scrutateurs"
        2. Add 3 scrutators and generate access code
        3. Test scrutator connections and approval workflow
        4. Test complete majority voting workflow
        5. CRITICAL: Test PDF generation after majority approval (the bug fix)
        6. Test case without scrutators
        """
        print("\n🎯 TEST DE CORRECTION DU BUG - WORKFLOW SCRUTATEURS COMPLET")
        print("=" * 80)
        
        scenario_data = {}
        all_passed = True
        
        # 1. Créer une assemblée - "Test Correction Bug Scrutateurs"
        try:
            meeting_data = {
                "title": "Test Correction Bug Scrutateurs",
                "organizer_name": "Organisateur Principal"
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/meetings", json=meeting_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                scenario_data['meeting'] = response.json()
                self.log_result("1. Créer assemblée", True, f"Assemblée créée: {scenario_data['meeting']['meeting_code']}", response_time)
            else:
                self.log_result("1. Créer assemblée", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("1. Créer assemblée", False, f"Error: {str(e)}")
            return False
        
        # 2. Ajouter 3 scrutateurs et générer le code d'accès
        try:
            scrutator_data = {
                "names": ["Jean Dupont", "Marie Martin", "Pierre Durand"]
            }
            
            meeting_id = scenario_data['meeting']['id']
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/meetings/{meeting_id}/scrutators", json=scrutator_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                scenario_data['scrutator_code'] = data['scrutator_code']
                scenario_data['scrutators'] = data['scrutators']
                self.log_result("2. Ajouter 3 scrutateurs", True, f"Code généré: {data['scrutator_code']}", response_time)
            else:
                self.log_result("2. Ajouter 3 scrutateurs", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("2. Ajouter 3 scrutateurs", False, f"Error: {str(e)}")
            return False
        
        # 3. Connexion et approbation des scrutateurs
        scrutator_ids = {}
        
        # Jean Dupont se connecte (status pending)
        try:
            join_data = {
                "name": "Jean Dupont",
                "scrutator_code": scenario_data['scrutator_code']
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/scrutators/join", json=join_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'pending_approval':
                    self.log_result("3a. Jean Dupont connexion", True, "Status pending_approval correct", response_time)
                else:
                    self.log_result("3a. Jean Dupont connexion", False, f"Expected pending_approval, got: {data}", response_time)
                    all_passed = False
            else:
                self.log_result("3a. Jean Dupont connexion", False, f"HTTP {response.status_code}: {response.text}", response_time)
                all_passed = False
        except Exception as e:
            self.log_result("3a. Jean Dupont connexion", False, f"Error: {str(e)}")
            all_passed = False
        
        # Marie Martin se connecte (status pending)
        try:
            join_data = {
                "name": "Marie Martin",
                "scrutator_code": scenario_data['scrutator_code']
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/scrutators/join", json=join_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'pending_approval':
                    self.log_result("3b. Marie Martin connexion", True, "Status pending_approval correct", response_time)
                else:
                    self.log_result("3b. Marie Martin connexion", False, f"Expected pending_approval, got: {data}", response_time)
                    all_passed = False
            else:
                self.log_result("3b. Marie Martin connexion", False, f"HTTP {response.status_code}: {response.text}", response_time)
                all_passed = False
        except Exception as e:
            self.log_result("3b. Marie Martin connexion", False, f"Error: {str(e)}")
            all_passed = False
        
        # Pierre Durand se connecte (status pending)
        try:
            join_data = {
                "name": "Pierre Durand",
                "scrutator_code": scenario_data['scrutator_code']
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/scrutators/join", json=join_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'pending_approval':
                    self.log_result("3c. Pierre Durand connexion", True, "Status pending_approval correct", response_time)
                else:
                    self.log_result("3c. Pierre Durand connexion", False, f"Expected pending_approval, got: {data}", response_time)
                    all_passed = False
            else:
                self.log_result("3c. Pierre Durand connexion", False, f"HTTP {response.status_code}: {response.text}", response_time)
                all_passed = False
        except Exception as e:
            self.log_result("3c. Pierre Durand connexion", False, f"Error: {str(e)}")
            all_passed = False
        
        # Organisateur approuve tous les scrutateurs
        try:
            meeting_id = scenario_data['meeting']['id']
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/scrutators")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                scrutators_list = data['scrutators']
                
                approved_count = 0
                for scrutator in scrutators_list:
                    approval_data = {
                        "scrutator_id": scrutator['id'],
                        "approved": True
                    }
                    
                    response = self.session.post(f"{BASE_URL}/scrutators/{scrutator['id']}/approve", json=approval_data)
                    if response.status_code == 200:
                        approved_count += 1
                        scrutator_ids[scrutator['name']] = scrutator['id']
                
                if approved_count == 3:
                    self.log_result("3d. Organisateur approuve tous", True, f"Tous les 3 scrutateurs approuvés", response_time)
                else:
                    self.log_result("3d. Organisateur approuve tous", False, f"Seulement {approved_count}/3 approuvés")
                    all_passed = False
            else:
                self.log_result("3d. Organisateur approuve tous", False, f"HTTP {response.status_code}: {response.text}")
                all_passed = False
        except Exception as e:
            self.log_result("3d. Organisateur approuve tous", False, f"Error: {str(e)}")
            all_passed = False
        
        # 4. Vérifier accès après approbation - Jean Dupont peut maintenant accéder
        try:
            join_data = {
                "name": "Jean Dupont",
                "scrutator_code": scenario_data['scrutator_code']
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/scrutators/join", json=join_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'approved' and 'meeting' in data:
                    self.log_result("4. Jean Dupont accès après approbation", True, "Accès interface autorisé", response_time)
                else:
                    self.log_result("4. Jean Dupont accès après approbation", False, f"Expected approved access, got: {data}", response_time)
                    all_passed = False
            else:
                self.log_result("4. Jean Dupont accès après approbation", False, f"HTTP {response.status_code}: {response.text}", response_time)
                all_passed = False
        except Exception as e:
            self.log_result("4. Jean Dupont accès après approbation", False, f"Error: {str(e)}")
            all_passed = False
        
        # 5. Test complet du workflow de vote majoritaire
        # Ajouter des participants et sondages
        try:
            # Add participants
            participants = ["Participant Un", "Participant Deux"]
            scenario_data['participants'] = []
            
            for participant_name in participants:
                join_data = {
                    "name": participant_name,
                    "meeting_code": scenario_data['meeting']['meeting_code']
                }
                
                response = self.session.post(f"{BASE_URL}/participants/join", json=join_data)
                if response.status_code == 200:
                    participant_data = response.json()
                    scenario_data['participants'].append(participant_data)
                    
                    # Approve participant
                    approval_data = {
                        "participant_id": participant_data['id'],
                        "approved": True
                    }
                    self.session.post(f"{BASE_URL}/participants/{participant_data['id']}/approve", json=approval_data)
            
            # Create poll
            poll_data = {
                "question": "Approuvez-vous le budget 2025 ?",
                "options": ["Oui", "Non", "Abstention"],
                "show_results_real_time": True
            }
            
            meeting_id = scenario_data['meeting']['id']
            response = self.session.post(f"{BASE_URL}/meetings/{meeting_id}/polls", json=poll_data)
            if response.status_code == 200:
                poll = response.json()
                scenario_data['poll'] = poll
                
                # Start poll and add votes
                self.session.post(f"{BASE_URL}/polls/{poll['id']}/start")
                
                # Add votes
                for i in range(3):
                    vote_data = {
                        "poll_id": poll['id'],
                        "option_id": poll['options'][i % len(poll['options'])]['id']
                    }
                    self.session.post(f"{BASE_URL}/votes", json=vote_data)
                
                # Close poll
                self.session.post(f"{BASE_URL}/polls/{poll['id']}/close")
            
            self.log_result("5a. Ajouter participants et sondages", True, f"Ajouté {len(scenario_data['participants'])} participants et 1 sondage")
            
        except Exception as e:
            self.log_result("5a. Ajouter participants et sondages", False, f"Error: {str(e)}")
            all_passed = False
        
        # Organisateur demande la génération via /request-report
        try:
            meeting_id = scenario_data['meeting']['id']
            request_data = {
                "meeting_id": meeting_id,
                "requested_by": "Organisateur Principal"
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/meetings/{meeting_id}/request-report", json=request_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('scrutator_approval_required') and data.get('majority_needed') == 2:  # (3//2)+1 = 2
                    self.log_result("5b. Organisateur demande génération", True, f"Demande envoyée, majorité requise: {data['majority_needed']}", response_time)
                else:
                    self.log_result("5b. Organisateur demande génération", False, f"Unexpected response: {data}", response_time)
                    all_passed = False
            else:
                self.log_result("5b. Organisateur demande génération", False, f"HTTP {response.status_code}: {response.text}", response_time)
                all_passed = False
        except Exception as e:
            self.log_result("5b. Organisateur demande génération", False, f"Error: {str(e)}")
            all_passed = False
        
        # Jean Dupont vote OUI
        try:
            vote_data = {
                "meeting_id": meeting_id,
                "scrutator_name": "Jean Dupont",
                "approved": True
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/meetings/{meeting_id}/scrutator-vote", json=vote_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.log_result("5c. Jean Dupont vote OUI", True, f"Vote enregistré: {result.get('message', 'Vote submitted')}", response_time)
            else:
                self.log_result("5c. Jean Dupont vote OUI", False, f"HTTP {response.status_code}: {response.text}", response_time)
                all_passed = False
        except Exception as e:
            self.log_result("5c. Jean Dupont vote OUI", False, f"Error: {str(e)}")
            all_passed = False
        
        # Marie Martin vote OUI
        try:
            vote_data = {
                "meeting_id": meeting_id,
                "scrutator_name": "Marie Martin",
                "approved": True
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/meetings/{meeting_id}/scrutator-vote", json=vote_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.log_result("5d. Marie Martin vote OUI", True, f"Vote enregistré: {result.get('message', 'Vote submitted')}", response_time)
            else:
                self.log_result("5d. Marie Martin vote OUI", False, f"HTTP {response.status_code}: {response.text}", response_time)
                all_passed = False
        except Exception as e:
            self.log_result("5d. Marie Martin vote OUI", False, f"Error: {str(e)}")
            all_passed = False
        
        # Pierre Durand vote NON
        try:
            vote_data = {
                "meeting_id": meeting_id,
                "scrutator_name": "Pierre Durand",
                "approved": False
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/meetings/{meeting_id}/scrutator-vote", json=vote_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                if result.get('decision') == 'approved':
                    self.log_result("5e. Pierre Durand vote NON", True, f"Majorité atteinte (2/3): {result.get('message', 'Approved')}", response_time)
                    scenario_data['generation_approved'] = True
                else:
                    self.log_result("5e. Pierre Durand vote NON", True, f"Vote enregistré: {result.get('message', 'Vote submitted')}", response_time)
            else:
                self.log_result("5e. Pierre Durand vote NON", False, f"HTTP {response.status_code}: {response.text}", response_time)
                all_passed = False
        except Exception as e:
            self.log_result("5e. Pierre Durand vote NON", False, f"Error: {str(e)}")
            all_passed = False
        
        # POINT CRITIQUE: Tester la génération PDF via GET /report
        try:
            meeting_id = scenario_data['meeting']['id']
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/report")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'application/pdf' in content_type:
                    file_size = len(response.content)
                    self.log_result("5f. CRITIQUE: Génération PDF après approbation", True, f"✅ BUG CORRIGÉ! PDF généré ({file_size} bytes)", response_time)
                    scenario_data['pdf_generated'] = True
                else:
                    self.log_result("5f. CRITIQUE: Génération PDF après approbation", False, f"❌ BUG PERSISTE! Wrong content type: {content_type}", response_time)
                    all_passed = False
            else:
                self.log_result("5f. CRITIQUE: Génération PDF après approbation", False, f"❌ BUG PERSISTE! HTTP {response.status_code}: {response.text}", response_time)
                all_passed = False
        except Exception as e:
            self.log_result("5f. CRITIQUE: Génération PDF après approbation", False, f"❌ BUG PERSISTE! Error: {str(e)}")
            all_passed = False
        
        # Vérifier que toutes les données sont supprimées
        if scenario_data.get('pdf_generated'):
            try:
                meeting_id = scenario_data['meeting']['id']
                meeting_code = scenario_data['meeting']['meeting_code']
                
                # Test meeting deletion
                response = self.session.get(f"{BASE_URL}/meetings/{meeting_code}")
                if response.status_code == 404:
                    self.log_result("5g. Vérification suppression données", True, "Toutes les données supprimées après PDF")
                else:
                    self.log_result("5g. Vérification suppression données", False, f"Données non supprimées: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_result("5g. Vérification suppression données", False, f"Error: {str(e)}")
                all_passed = False
        
        # 6. Test du cas sans scrutateurs
        try:
            meeting_data = {
                "title": "Assemblée Sans Scrutateurs",
                "organizer_name": "Organisateur Simple"
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/meetings", json=meeting_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                no_scrutator_meeting = response.json()
                
                # Add a participant and poll
                join_data = {
                    "name": "Participant Simple",
                    "meeting_code": no_scrutator_meeting['meeting_code']
                }
                
                response = self.session.post(f"{BASE_URL}/participants/join", json=join_data)
                if response.status_code == 200:
                    participant = response.json()
                    
                    # Approve participant
                    approval_data = {
                        "participant_id": participant['id'],
                        "approved": True
                    }
                    self.session.post(f"{BASE_URL}/participants/{participant['id']}/approve", json=approval_data)
                
                # Create and complete a poll
                poll_data = {
                    "question": "Test sans scrutateurs ?",
                    "options": ["Oui", "Non"],
                    "show_results_real_time": True
                }
                
                response = self.session.post(f"{BASE_URL}/meetings/{no_scrutator_meeting['id']}/polls", json=poll_data)
                if response.status_code == 200:
                    poll = response.json()
                    
                    # Start, vote, close
                    self.session.post(f"{BASE_URL}/polls/{poll['id']}/start")
                    vote_data = {
                        "poll_id": poll['id'],
                        "option_id": poll['options'][0]['id']
                    }
                    self.session.post(f"{BASE_URL}/votes", json=vote_data)
                    self.session.post(f"{BASE_URL}/polls/{poll['id']}/close")
                
                # Test direct PDF generation
                start_time = time.time()
                response = self.session.get(f"{BASE_URL}/meetings/{no_scrutator_meeting['id']}/report")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'application/pdf' in content_type:
                        file_size = len(response.content)
                        self.log_result("6. Test sans scrutateurs", True, f"PDF généré directement ({file_size} bytes)", response_time)
                    else:
                        self.log_result("6. Test sans scrutateurs", False, f"Wrong content type: {content_type}", response_time)
                        all_passed = False
                else:
                    self.log_result("6. Test sans scrutateurs", False, f"HTTP {response.status_code}: {response.text}", response_time)
                    all_passed = False
            else:
                self.log_result("6. Test sans scrutateurs", False, f"Failed to create meeting: {response.status_code}")
                all_passed = False
        except Exception as e:
            self.log_result("6. Test sans scrutateurs", False, f"Error: {str(e)}")
            all_passed = False
        
        # Summary
        if all_passed:
            self.log_result("RÉSULTAT FINAL", True, "✅ TOUS LES TESTS PASSENT - BUG CORRIGÉ AVEC SUCCÈS!")
            print("\n🎉 VALIDATION COMPLÈTE DU BUG FIX:")
            print("✅ Workflow scrutateurs avec approbation fonctionne")
            print("✅ Système de vote majoritaire fonctionne (2/3)")
            print("✅ CRITIQUE: Génération PDF après approbation majoritaire fonctionne")
            print("✅ Suppression complète des données après génération")
            print("✅ Génération directe sans scrutateurs fonctionne")
            print("\n🚀 LE BUG EST CORRIGÉ - PRÊT POUR PRODUCTION!")
        else:
            self.log_result("RÉSULTAT FINAL", False, "❌ CERTAINS TESTS ÉCHOUENT - BUG PEUT PERSISTER")
            print("\n⚠️  ATTENTION: Certains tests ont échoué")
            print("Vérifiez les détails ci-dessus pour identifier les problèmes restants")
        
        return all_passed

    def run_all_tests(self):
        """Run all backend tests with priority on bug fix validation"""
        print("🚀 STARTING COMPREHENSIVE BACKEND API TESTING")
        print("=" * 70)
        print(f"Backend URL: {BASE_URL}")
        print(f"WebSocket URL: {WS_URL}")
        print("=" * 70)
        
        # PRIORITY: Test the bug fix first
        bug_fix_tests = [
            ("🎯 BUG FIX TEST - Workflow Scrutateurs Complet", self.test_bug_fix_scrutator_workflow_complete),
        ]
        
        # Core functionality tests
        core_tests = [
            ("Health Check", self.test_health_check),
            ("Create Meeting", self.test_create_meeting),
            ("Meeting Validation", self.test_meeting_validation),
            ("Get Meeting by Code", self.test_get_meeting_by_code),
            ("Participant Join", self.test_participant_join),
            ("Participant Validation", self.test_participant_validation),
            ("Participant Approval", self.test_participant_approval),
            ("Participant Status", self.test_participant_status),
            ("Create Poll", self.test_create_poll),
            ("Poll Validation", self.test_poll_validation),
            ("Start Poll", self.test_start_poll),
            ("Submit Vote", self.test_submit_vote),
            ("Poll Results", self.test_poll_results),
            ("Close Poll", self.test_close_poll),
            ("Get Meeting Polls", self.test_get_meeting_polls),
            ("Organizer View", self.test_organizer_view),
            ("PDF Report Generation", self.test_pdf_report_generation),
            ("CORS Configuration", self.test_cors_headers),
            ("Performance Load Test", self.test_performance_load),
            ("Error Handling", self.test_error_handling),
        ]
        
        # Advanced functionality tests
        advanced_tests = [
            ("Scrutator Functionality", self.test_scrutator_functionality),
            ("Scrutator Validation", self.test_scrutator_validation),
            ("Advanced Scrutator Workflow", self.test_advanced_scrutator_workflow_with_approval_and_voting)
        ]
        
        passed = 0
        total = 0
        
        # Run bug fix test FIRST - This is the most critical
        print("\n🔥 PRIORITY: TESTING BUG FIX")
        print("=" * 50)
        for test_name, test_func in bug_fix_tests:
            total += 1
            try:
                if test_func():
                    passed += 1
                time.sleep(0.1)  # Small delay between tests
            except Exception as e:
                self.log_result(test_name, False, f"Test exception: {str(e)}")
        
        # Run core tests
        print("\n📋 CORE FUNCTIONALITY TESTS")
        print("=" * 40)
        for test_name, test_func in core_tests:
            total += 1
            try:
                if test_func():
                    passed += 1
                time.sleep(0.1)  # Small delay between tests
            except Exception as e:
                self.log_result(test_name, False, f"Test exception: {str(e)}")
        
        # Run advanced tests
        print("\n🔬 ADVANCED FUNCTIONALITY TESTS")
        print("=" * 40)
        for test_name, test_func in advanced_tests:
            total += 1
            try:
                if test_func():
                    passed += 1
                time.sleep(0.1)
            except Exception as e:
                self.log_result(test_name, False, f"Test exception: {str(e)}")
        
        # WebSocket test (async)
        print("\n🌐 WEBSOCKET TEST")
        print("=" * 25)
        try:
            ws_result = asyncio.run(self.test_websocket_connection())
            if ws_result:
                passed += 1
            total += 1
        except Exception as e:
            self.log_result("WebSocket Connection", False, f"WebSocket test error: {str(e)}")
            total += 1
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        for result in self.results:
            print(f"{result['status']} {result['test']}: {result['message']} ({result['response_time']})")
        
        print(f"\n🎯 OVERALL RESULTS: {passed}/{total} tests passed ({success_rate:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Backend is fully functional.")
        elif success_rate >= 90:
            print("✅ EXCELLENT: Backend is production-ready with minor issues.")
        elif success_rate >= 75:
            print("⚠️  GOOD: Backend is mostly functional with some issues to address.")
        else:
            print("❌ CRITICAL: Backend has significant issues that need immediate attention.")
        
        return passed, total, self.results

def main():
    """Main test execution"""
    tester = VoteSecretTester()
    passed, total, results = tester.run_all_tests()
    
    # Print summary
    print("\n📊 DETAILED TEST SUMMARY")
    print("=" * 60)
    
    for result in results:
        print(f"{result['status']} {result['test']}")
        if result['message']:
            print(f"    └─ {result['message']}")
        if result['response_time'] != "N/A":
            print(f"    └─ Response time: {result['response_time']}")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)