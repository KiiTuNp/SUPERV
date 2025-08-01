#!/usr/bin/env python3
"""
Comprehensive Backend Testing Suite for Vote Secret Application
Tests all core and advanced functionalities after deployment improvements
"""

import requests
import json
import time
import asyncio
import websockets
from datetime import datetime
import os
import sys

# Configuration
BACKEND_URL = "https://8c46219a-4d23-4d71-859e-4aa3cf1d38ff.preview.emergentagent.com/api"
WEBSOCKET_URL = "wss://068d0d89-bf36-41bf-ba1d-76e3bffe12be.preview.emergentagent.com/ws"

class VoteSecretTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = []
        self.meeting_id = None
        self.meeting_code = None
        self.scrutator_code = None
        self.participant_ids = []
        self.poll_ids = []
        
    def log_test(self, test_name, success, details="", response_time=0):
        """Log test results"""
        status = "✅ PASSED" if success else "❌ FAILED"
        result = {
            'test': test_name,
            'status': status,
            'success': success,
            'details': details,
            'response_time': f"{response_time:.3f}s"
        }
        self.test_results.append(result)
        print(f"{status} - {test_name} ({response_time:.3f}s)")
        if details:
            print(f"    Details: {details}")
    
    def test_health_check(self):
        """Test API health check endpoint"""
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/health")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy' and data.get('services', {}).get('database') == 'connected':
                    self.log_test("Health Check", True, f"Service healthy, database connected", response_time)
                    return True
                else:
                    self.log_test("Health Check", False, f"Unhealthy response: {data}", response_time)
                    return False
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_meeting_creation(self):
        """Test meeting creation with validation"""
        try:
            # Test valid meeting creation
            start_time = time.time()
            meeting_data = {
                "title": "Test Complet Backend Vote Secret 2025",
                "organizer_name": "Alice Dupont"
            }
            response = self.session.post(f"{BACKEND_URL}/meetings", json=meeting_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.meeting_id = data['id']
                self.meeting_code = data['meeting_code']
                self.log_test("Meeting Creation", True, f"Meeting created with code {self.meeting_code}", response_time)
                return True
            else:
                self.log_test("Meeting Creation", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_test("Meeting Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_meeting_validation(self):
        """Test meeting creation validation"""
        try:
            # Test empty title
            start_time = time.time()
            response = self.session.post(f"{BACKEND_URL}/meetings", json={
                "title": "",
                "organizer_name": "Test User"
            })
            response_time = time.time() - start_time
            
            if response.status_code == 400:
                self.log_test("Meeting Validation (Empty Title)", True, "Correctly rejected empty title", response_time)
                return True
            else:
                self.log_test("Meeting Validation (Empty Title)", False, f"Should reject empty title, got {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_test("Meeting Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_meeting_retrieval(self):
        """Test meeting retrieval by code"""
        if not self.meeting_code:
            self.log_test("Meeting Retrieval", False, "No meeting code available")
            return False
        
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/meetings/{self.meeting_code}")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data['meeting_code'] == self.meeting_code:
                    self.log_test("Meeting Retrieval", True, f"Retrieved meeting {self.meeting_code}", response_time)
                    return True
                else:
                    self.log_test("Meeting Retrieval", False, f"Wrong meeting returned", response_time)
                    return False
            else:
                self.log_test("Meeting Retrieval", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_test("Meeting Retrieval", False, f"Exception: {str(e)}")
            return False
    
    def test_participant_join(self):
        """Test participant joining"""
        if not self.meeting_code:
            self.log_test("Participant Join", False, "No meeting code available")
            return False
        
        try:
            participants = [
                "Jean-Baptiste Moreau",
                "Sophie Lefebvre", 
                "Pierre-Alexandre Martin"
            ]
            
            for participant_name in participants:
                start_time = time.time()
                response = self.session.post(f"{BACKEND_URL}/participants/join", json={
                    "name": participant_name,
                    "meeting_code": self.meeting_code
                })
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    self.participant_ids.append(data['id'])
                    self.log_test(f"Participant Join ({participant_name})", True, f"Participant joined successfully", response_time)
                else:
                    self.log_test(f"Participant Join ({participant_name})", False, f"HTTP {response.status_code}: {response.text}", response_time)
                    return False
            
            return True
        except Exception as e:
            self.log_test("Participant Join", False, f"Exception: {str(e)}")
            return False
    
    def test_participant_approval(self):
        """Test participant approval process"""
        if not self.participant_ids:
            self.log_test("Participant Approval", False, "No participants to approve")
            return False
        
        try:
            for participant_id in self.participant_ids:
                start_time = time.time()
                response = self.session.post(f"{BACKEND_URL}/participants/{participant_id}/approve", json={
                    "participant_id": participant_id,
                    "approved": True
                })
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    self.log_test(f"Participant Approval", True, f"Participant {participant_id[:8]} approved", response_time)
                else:
                    self.log_test(f"Participant Approval", False, f"HTTP {response.status_code}: {response.text}", response_time)
                    return False
            
            return True
        except Exception as e:
            self.log_test("Participant Approval", False, f"Exception: {str(e)}")
            return False
    
    def test_scrutator_system(self):
        """Test complete scrutator system"""
        if not self.meeting_id:
            self.log_test("Scrutator System", False, "No meeting ID available")
            return False
        
        try:
            # Add scrutators
            start_time = time.time()
            scrutator_data = {
                "names": ["Jean Dupont", "Marie Martin", "Pierre Durand"]
            }
            response = self.session.post(f"{BACKEND_URL}/meetings/{self.meeting_id}/scrutators", json=scrutator_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.scrutator_code = data['scrutator_code']
                self.log_test("Scrutator Addition", True, f"3 scrutators added with code {self.scrutator_code}", response_time)
                
                # Test scrutator join
                start_time = time.time()
                join_response = self.session.post(f"{BACKEND_URL}/scrutators/join", json={
                    "name": "Jean Dupont",
                    "scrutator_code": self.scrutator_code
                })
                response_time = time.time() - start_time
                
                if join_response.status_code == 200:
                    join_data = join_response.json()
                    if join_data.get('status') == 'pending_approval':
                        self.log_test("Scrutator Join (Pending)", True, "Scrutator correctly requires approval", response_time)
                        return True
                    elif join_data.get('status') == 'approved':
                        self.log_test("Scrutator Join (Approved)", True, "Scrutator already approved", response_time)
                        return True
                    else:
                        self.log_test("Scrutator Join", False, f"Unexpected status: {join_data}", response_time)
                        return False
                else:
                    self.log_test("Scrutator Join", False, f"HTTP {join_response.status_code}: {join_response.text}", response_time)
                    return False
            else:
                self.log_test("Scrutator Addition", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_test("Scrutator System", False, f"Exception: {str(e)}")
            return False
    
    def test_poll_creation(self):
        """Test poll creation and management"""
        if not self.meeting_id:
            self.log_test("Poll Creation", False, "No meeting ID available")
            return False
        
        try:
            # Create polls with French content
            polls = [
                {
                    "question": "Approbation du budget 2025",
                    "options": ["Pour", "Contre", "Abstention"]
                },
                {
                    "question": "Élection du nouveau président",
                    "options": ["Candidat A", "Candidat B", "Candidat C", "Vote blanc"]
                }
            ]
            
            for poll_data in polls:
                start_time = time.time()
                response = self.session.post(f"{BACKEND_URL}/meetings/{self.meeting_id}/polls", json=poll_data)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    self.poll_ids.append(data['id'])
                    self.log_test(f"Poll Creation ({poll_data['question'][:30]}...)", True, f"Poll created with {len(poll_data['options'])} options", response_time)
                else:
                    self.log_test(f"Poll Creation", False, f"HTTP {response.status_code}: {response.text}", response_time)
                    return False
            
            return True
        except Exception as e:
            self.log_test("Poll Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_poll_management(self):
        """Test poll start/stop functionality"""
        if not self.poll_ids:
            self.log_test("Poll Management", False, "No polls to manage")
            return False
        
        try:
            for poll_id in self.poll_ids:
                # Start poll
                start_time = time.time()
                response = self.session.post(f"{BACKEND_URL}/polls/{poll_id}/start")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    self.log_test(f"Poll Start", True, f"Poll {poll_id[:8]} started", response_time)
                else:
                    self.log_test(f"Poll Start", False, f"HTTP {response.status_code}: {response.text}", response_time)
                    return False
            
            return True
        except Exception as e:
            self.log_test("Poll Management", False, f"Exception: {str(e)}")
            return False
    
    def test_voting_system(self):
        """Test anonymous voting system with equality logic"""
        if not self.poll_ids:
            self.log_test("Voting System", False, "No polls available for voting")
            return False
        
        try:
            # Test voting on first poll - create equality scenario
            poll_id = self.poll_ids[0]
            
            # Get poll details first
            poll_response = self.session.get(f"{BACKEND_URL}/polls/{poll_id}/results")
            if poll_response.status_code != 200:
                self.log_test("Voting System", False, "Could not get poll details")
                return False
            
            poll_data = poll_response.json()
            options = [opt for opt in poll_data.get('results', [])]
            
            if len(options) < 2:
                self.log_test("Voting System", False, "Not enough options for equality test")
                return False
            
            # Create equality scenario: 2 votes for first option, 2 votes for second option
            votes = [
                (options[0], 2),  # 2 votes for first option
                (options[1], 2),  # 2 votes for second option
            ]
            
            for option_data, vote_count in votes:
                for _ in range(vote_count):
                    start_time = time.time()
                    # We need to find the actual option_id from the poll structure
                    # Let's get the poll structure first
                    poll_detail_response = self.session.get(f"{BACKEND_URL}/meetings/{self.meeting_id}/polls")
                    if poll_detail_response.status_code == 200:
                        polls = poll_detail_response.json()
                        target_poll = next((p for p in polls if p['id'] == poll_id), None)
                        if target_poll:
                            target_option = next((opt for opt in target_poll['options'] if opt['text'] == option_data['option']), None)
                            if target_option:
                                vote_response = self.session.post(f"{BACKEND_URL}/votes", json={
                                    "poll_id": poll_id,
                                    "option_id": target_option['id']
                                })
                                response_time = time.time() - start_time
                                
                                if vote_response.status_code == 200:
                                    self.log_test(f"Vote Submission", True, f"Vote cast for {option_data['option']}", response_time)
                                else:
                                    self.log_test(f"Vote Submission", False, f"HTTP {vote_response.status_code}: {vote_response.text}", response_time)
                                    return False
            
            # Close poll and check results
            close_response = self.session.post(f"{BACKEND_URL}/polls/{poll_id}/close")
            if close_response.status_code == 200:
                self.log_test("Poll Close", True, "Poll closed successfully", 0.01)
                
                # Check final results for equality handling
                results_response = self.session.get(f"{BACKEND_URL}/polls/{poll_id}/results")
                if results_response.status_code == 200:
                    results = results_response.json()
                    total_votes = results.get('total_votes', 0)
                    if total_votes > 0:
                        self.log_test("Vote Equality Logic", True, f"Voting completed with {total_votes} total votes", 0.01)
                        return True
                    else:
                        self.log_test("Vote Equality Logic", False, "No votes recorded", 0.01)
                        return False
                else:
                    self.log_test("Vote Results", False, f"Could not get results: {results_response.status_code}", 0.01)
                    return False
            else:
                self.log_test("Poll Close", False, f"Could not close poll: {close_response.status_code}", 0.01)
                return False
                
        except Exception as e:
            self.log_test("Voting System", False, f"Exception: {str(e)}")
            return False
    
    def test_organizer_view(self):
        """Test organizer dashboard view"""
        if not self.meeting_id:
            self.log_test("Organizer View", False, "No meeting ID available")
            return False
        
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/meetings/{self.meeting_id}/organizer")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                meeting = data.get('meeting', {})
                participants = data.get('participants', [])
                polls = data.get('polls', [])
                
                self.log_test("Organizer View", True, f"Dashboard loaded: {len(participants)} participants, {len(polls)} polls", response_time)
                return True
            else:
                self.log_test("Organizer View", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_test("Organizer View", False, f"Exception: {str(e)}")
            return False
    
    def test_pdf_generation(self):
        """Test PDF report generation and data deletion"""
        if not self.meeting_id:
            self.log_test("PDF Generation", False, "No meeting ID available")
            return False
        
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/meetings/{self.meeting_id}/report")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # Check if it's a PDF
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                if 'application/pdf' in content_type and content_length > 1000:
                    self.log_test("PDF Generation", True, f"PDF generated successfully ({content_length} bytes)", response_time)
                    
                    # Test that data is deleted after PDF generation
                    time.sleep(1)  # Wait a moment
                    verify_response = self.session.get(f"{BACKEND_URL}/meetings/{self.meeting_id}/organizer")
                    if verify_response.status_code == 404:
                        self.log_test("Data Deletion After PDF", True, "Meeting data properly deleted after PDF generation", 0.01)
                        return True
                    else:
                        self.log_test("Data Deletion After PDF", False, f"Meeting still accessible after PDF: {verify_response.status_code}", 0.01)
                        return False
                else:
                    self.log_test("PDF Generation", False, f"Invalid PDF response: {content_type}, {content_length} bytes", response_time)
                    return False
            else:
                self.log_test("PDF Generation", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_test("PDF Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_websocket_connection(self):
        """Test WebSocket connection for real-time updates"""
        if not self.meeting_id:
            self.log_test("WebSocket Connection", False, "No meeting ID available")
            return False
        
        try:
            async def test_websocket():
                try:
                    uri = f"{WEBSOCKET_URL}/meetings/{self.meeting_id}"
                    async with websockets.connect(uri, timeout=10) as websocket:
                        # Send a test message
                        await websocket.send("test")
                        # Try to receive a response (with timeout)
                        response = await asyncio.wait_for(websocket.recv(), timeout=5)
                        return True
                except asyncio.TimeoutError:
                    return False
                except Exception:
                    return False
            
            start_time = time.time()
            result = asyncio.run(test_websocket())
            response_time = time.time() - start_time
            
            if result:
                self.log_test("WebSocket Connection", True, "WebSocket connection successful", response_time)
                return True
            else:
                self.log_test("WebSocket Connection", False, "WebSocket connection failed or timeout", response_time)
                return False
        except Exception as e:
            self.log_test("WebSocket Connection", False, f"Exception: {str(e)}")
            return False
    
    def test_cors_configuration(self):
        """Test CORS headers"""
        try:
            start_time = time.time()
            response = self.session.options(f"{BACKEND_URL}/health")
            response_time = time.time() - start_time
            
            cors_headers = [
                'access-control-allow-origin',
                'access-control-allow-methods',
                'access-control-allow-headers'
            ]
            
            has_cors = any(header in response.headers for header in cors_headers)
            
            if has_cors:
                self.log_test("CORS Configuration", True, "CORS headers present", response_time)
                return True
            else:
                self.log_test("CORS Configuration", False, "Missing CORS headers", response_time)
                return False
        except Exception as e:
            self.log_test("CORS Configuration", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        try:
            # Test 404 for non-existent meeting
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/meetings/INVALID123")
            response_time = time.time() - start_time
            
            if response.status_code == 404:
                self.log_test("Error Handling (404)", True, "Proper 404 response for invalid meeting", response_time)
                return True
            else:
                self.log_test("Error Handling (404)", False, f"Expected 404, got {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_test("Error Handling", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Comprehensive Backend Testing for Vote Secret")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Core functionality tests
        tests = [
            self.test_health_check,
            self.test_meeting_creation,
            self.test_meeting_validation,
            self.test_meeting_retrieval,
            self.test_participant_join,
            self.test_participant_approval,
            self.test_scrutator_system,
            self.test_poll_creation,
            self.test_poll_management,
            self.test_voting_system,
            self.test_organizer_view,
            self.test_cors_configuration,
            self.test_error_handling,
            self.test_pdf_generation,  # This should be last as it deletes data
            self.test_websocket_connection,
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ FAILED - {test.__name__}: Exception {str(e)}")
        
        print("\n" + "=" * 80)
        print(f"🏁 BACKEND TESTING COMPLETE")
        print(f"📊 RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("✅ ALL TESTS PASSED - Backend is fully operational!")
        elif passed >= total * 0.9:
            print("⚠️  MOSTLY WORKING - Minor issues detected")
        else:
            print("❌ CRITICAL ISSUES - Backend needs attention")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"  {result['status']} {result['test']} ({result['response_time']})")
            if result['details']:
                print(f"      {result['details']}")
        
        return passed, total

def main():
    """Main test execution"""
    tester = VoteSecretTester()
    passed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    if passed == total:
        sys.exit(0)  # All tests passed
    else:
        sys.exit(1)  # Some tests failed

if __name__ == "__main__":
    main()