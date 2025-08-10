#!/usr/bin/env python3
"""
Comprehensive Backend API Testing Suite
Tests all backend endpoints for the Vote Secret application
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://8c46219a-4d23-4d71-859e-4aa3cf1d38ff.preview.emergentagent.com/api"
TIMEOUT = 30

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        self.test_data = {}
        self.results = []
        
    def log_result(self, test_name: str, success: bool, message: str, details: Optional[Dict] = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_health_check(self):
        """Test the health check endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_result("Health Check", True, "API is healthy and responsive")
                    return True
                else:
                    self.log_result("Health Check", False, f"Unhealthy status: {data}")
                    return False
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Health Check", False, f"Network error: {str(e)}")
            return False
    
    def test_meeting_creation(self):
        """Test meeting creation"""
        try:
            meeting_data = {
                "title": "Test Meeting - Backend Verification",
                "organizer_name": "Test Organizer"
            }
            
            response = self.session.post(
                f"{BASE_URL}/meetings",
                json=meeting_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "meeting_code" in data:
                    self.test_data["meeting"] = data
                    self.log_result("Meeting Creation", True, f"Meeting created with code: {data['meeting_code']}")
                    return True
                else:
                    self.log_result("Meeting Creation", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_result("Meeting Creation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Meeting Creation", False, f"Network error: {str(e)}")
            return False
    
    def test_meeting_retrieval(self):
        """Test meeting retrieval by code"""
        if "meeting" not in self.test_data:
            self.log_result("Meeting Retrieval", False, "No meeting data available from creation test")
            return False
            
        try:
            meeting_code = self.test_data["meeting"]["meeting_code"]
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("meeting_code") == meeting_code:
                    self.log_result("Meeting Retrieval", True, f"Successfully retrieved meeting: {meeting_code}")
                    return True
                else:
                    self.log_result("Meeting Retrieval", False, f"Meeting code mismatch: {data}")
                    return False
            else:
                self.log_result("Meeting Retrieval", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Meeting Retrieval", False, f"Network error: {str(e)}")
            return False
    
    def test_participant_join(self):
        """Test participant joining"""
        if "meeting" not in self.test_data:
            self.log_result("Participant Join", False, "No meeting data available")
            return False
            
        try:
            participant_data = {
                "name": "Test Participant",
                "meeting_code": self.test_data["meeting"]["meeting_code"]
            }
            
            response = self.session.post(
                f"{BASE_URL}/participants/join",
                json=participant_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("name") == "Test Participant":
                    self.test_data["participant"] = data
                    self.log_result("Participant Join", True, f"Participant joined with ID: {data['id']}")
                    return True
                else:
                    self.log_result("Participant Join", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_result("Participant Join", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Participant Join", False, f"Network error: {str(e)}")
            return False
    
    def test_participant_approval(self):
        """Test participant approval"""
        if "participant" not in self.test_data:
            self.log_result("Participant Approval", False, "No participant data available")
            return False
            
        try:
            participant_id = self.test_data["participant"]["id"]
            approval_data = {
                "participant_id": participant_id,
                "approved": True
            }
            
            response = self.session.post(
                f"{BASE_URL}/participants/{participant_id}/approve",
                json=approval_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_result("Participant Approval", True, "Participant approved successfully")
                    return True
                else:
                    self.log_result("Participant Approval", False, f"Approval failed: {data}")
                    return False
            else:
                self.log_result("Participant Approval", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Participant Approval", False, f"Network error: {str(e)}")
            return False
    
    def test_poll_creation(self):
        """Test poll creation"""
        if "meeting" not in self.test_data:
            self.log_result("Poll Creation", False, "No meeting data available")
            return False
            
        try:
            meeting_id = self.test_data["meeting"]["id"]
            poll_data = {
                "question": "Test Poll Question - Do you approve this test?",
                "options": ["Yes", "No", "Abstain"],
                "timer_duration": 300
            }
            
            response = self.session.post(
                f"{BASE_URL}/meetings/{meeting_id}/polls",
                json=poll_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("question") == poll_data["question"]:
                    self.test_data["poll"] = data
                    self.log_result("Poll Creation", True, f"Poll created with ID: {data['id']}")
                    return True
                else:
                    self.log_result("Poll Creation", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_result("Poll Creation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Poll Creation", False, f"Network error: {str(e)}")
            return False
    
    def test_poll_start(self):
        """Test starting a poll"""
        if "poll" not in self.test_data:
            self.log_result("Poll Start", False, "No poll data available")
            return False
            
        try:
            poll_id = self.test_data["poll"]["id"]
            response = self.session.post(f"{BASE_URL}/polls/{poll_id}/start")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "started":
                    self.log_result("Poll Start", True, "Poll started successfully")
                    return True
                else:
                    self.log_result("Poll Start", False, f"Start failed: {data}")
                    return False
            else:
                self.log_result("Poll Start", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Poll Start", False, f"Network error: {str(e)}")
            return False
    
    def test_voting(self):
        """Test voting functionality"""
        if "poll" not in self.test_data:
            self.log_result("Voting", False, "No poll data available")
            return False
            
        try:
            poll_id = self.test_data["poll"]["id"]
            # Get the first option ID
            option_id = self.test_data["poll"]["options"][0]["id"]
            
            vote_data = {
                "poll_id": poll_id,
                "option_id": option_id
            }
            
            response = self.session.post(
                f"{BASE_URL}/votes",
                json=vote_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "vote_submitted":
                    self.log_result("Voting", True, "Vote submitted successfully")
                    return True
                else:
                    self.log_result("Voting", False, f"Vote submission failed: {data}")
                    return False
            else:
                self.log_result("Voting", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Voting", False, f"Network error: {str(e)}")
            return False
    
    def test_poll_results(self):
        """Test poll results retrieval"""
        if "poll" not in self.test_data:
            self.log_result("Poll Results", False, "No poll data available")
            return False
            
        try:
            poll_id = self.test_data["poll"]["id"]
            response = self.session.get(f"{BASE_URL}/polls/{poll_id}/results")
            
            if response.status_code == 200:
                data = response.json()
                if "results" in data and "total_votes" in data:
                    self.log_result("Poll Results", True, f"Results retrieved - Total votes: {data['total_votes']}")
                    return True
                else:
                    self.log_result("Poll Results", False, f"Invalid results format: {data}")
                    return False
            else:
                self.log_result("Poll Results", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Poll Results", False, f"Network error: {str(e)}")
            return False
    
    def test_organizer_view(self):
        """Test organizer view endpoint"""
        if "meeting" not in self.test_data:
            self.log_result("Organizer View", False, "No meeting data available")
            return False
            
        try:
            meeting_id = self.test_data["meeting"]["id"]
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/organizer")
            
            if response.status_code == 200:
                data = response.json()
                if "meeting" in data and "participants" in data and "polls" in data:
                    self.log_result("Organizer View", True, "Organizer view data retrieved successfully")
                    return True
                else:
                    self.log_result("Organizer View", False, f"Invalid organizer view format: {data}")
                    return False
            else:
                self.log_result("Organizer View", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Organizer View", False, f"Network error: {str(e)}")
            return False
    
    def test_pdf_report_request(self):
        """Test PDF report generation request"""
        if "meeting" not in self.test_data:
            self.log_result("PDF Report Request", False, "No meeting data available")
            return False
            
        try:
            meeting_id = self.test_data["meeting"]["id"]
            request_data = {
                "meeting_id": meeting_id,
                "requested_by": "Test Organizer"
            }
            
            response = self.session.post(
                f"{BASE_URL}/meetings/{meeting_id}/request-report",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "direct_generation" in data or "scrutator_approval_required" in data:
                    self.log_result("PDF Report Request", True, f"Report request processed: {data.get('message', 'Success')}")
                    return True
                else:
                    self.log_result("PDF Report Request", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_result("PDF Report Request", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("PDF Report Request", False, f"Network error: {str(e)}")
            return False
    
    def test_database_connectivity(self):
        """Test database connectivity through health endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                services = data.get("services", {})
                if services.get("database") == "connected":
                    self.log_result("Database Connectivity", True, "Database connection verified")
                    return True
                else:
                    self.log_result("Database Connectivity", False, f"Database not connected: {services}")
                    return False
            else:
                self.log_result("Database Connectivity", False, f"Health check failed: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Database Connectivity", False, f"Network error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print(f"🚀 Starting comprehensive backend testing...")
        print(f"📡 Backend URL: {BASE_URL}")
        print(f"⏰ Timeout: {TIMEOUT}s")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("Health Check", self.test_health_check),
            ("Database Connectivity", self.test_database_connectivity),
            ("Meeting Creation", self.test_meeting_creation),
            ("Meeting Retrieval", self.test_meeting_retrieval),
            ("Participant Join", self.test_participant_join),
            ("Participant Approval", self.test_participant_approval),
            ("Poll Creation", self.test_poll_creation),
            ("Poll Start", self.test_poll_start),
            ("Voting", self.test_voting),
            ("Poll Results", self.test_poll_results),
            ("Organizer View", self.test_organizer_view),
            ("PDF Report Request", self.test_pdf_report_request)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log_result(test_name, False, f"Test execution error: {str(e)}")
                failed += 1
            
            # Small delay between tests
            time.sleep(0.5)
        
        print("=" * 60)
        print(f"📊 TEST SUMMARY")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        if failed == 0:
            print("🎉 All tests passed! Backend is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
        
        return passed, failed, self.results

def main():
    """Main test execution"""
    tester = BackendTester()
    passed, failed, results = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            "summary": {
                "passed": passed,
                "failed": failed,
                "total": passed + failed,
                "success_rate": (passed/(passed+failed)*100) if (passed+failed) > 0 else 0
            },
            "results": results,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/backend_test_results.json")
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()