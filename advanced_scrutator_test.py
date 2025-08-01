#!/usr/bin/env python3
"""
Advanced Scrutator Functionality Testing
Tests the advanced scrutator features including majority voting and PDF generation after approval
"""

import requests
import json
import time
import sys

# Configuration
BACKEND_URL = "https://8c46219a-4d23-4d71-859e-4aa3cf1d38ff.preview.emergentagent.com/api"

class AdvancedScrutatorTester:
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
        self.scrutator_ids = []
        
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
    
    def setup_meeting_with_scrutators(self):
        """Setup a meeting with scrutators for advanced testing"""
        try:
            # Create meeting
            meeting_data = {
                "title": "Test Scrutateurs Avancés - Approbation Majoritaire",
                "organizer_name": "Alice Dupont"
            }
            response = self.session.post(f"{BACKEND_URL}/meetings", json=meeting_data)
            
            if response.status_code == 200:
                data = response.json()
                self.meeting_id = data['id']
                self.meeting_code = data['meeting_code']
                
                # Add scrutators
                scrutator_data = {
                    "names": ["Jean Dupont", "Marie Martin", "Pierre Durand"]
                }
                scrutator_response = self.session.post(f"{BACKEND_URL}/meetings/{self.meeting_id}/scrutators", json=scrutator_data)
                
                if scrutator_response.status_code == 200:
                    scrutator_data = scrutator_response.json()
                    self.scrutator_code = scrutator_data['scrutator_code']
                    self.log_test("Setup Meeting with Scrutators", True, f"Meeting {self.meeting_code} with scrutator code {self.scrutator_code}")
                    return True
                else:
                    self.log_test("Setup Meeting with Scrutators", False, f"Failed to add scrutators: {scrutator_response.status_code}")
                    return False
            else:
                self.log_test("Setup Meeting with Scrutators", False, f"Failed to create meeting: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Setup Meeting with Scrutators", False, f"Exception: {str(e)}")
            return False
    
    def test_scrutator_approval_workflow(self):
        """Test the complete scrutator approval workflow"""
        if not self.scrutator_code:
            self.log_test("Scrutator Approval Workflow", False, "No scrutator code available")
            return False
        
        try:
            scrutator_names = ["Jean Dupont", "Marie Martin", "Pierre Durand"]
            
            # Step 1: All scrutators join (should be pending approval)
            for name in scrutator_names:
                start_time = time.time()
                response = self.session.post(f"{BACKEND_URL}/scrutators/join", json={
                    "name": name,
                    "scrutator_code": self.scrutator_code
                })
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'pending_approval':
                        self.log_test(f"Scrutator Join Pending ({name})", True, "Correctly requires approval", response_time)
                    else:
                        self.log_test(f"Scrutator Join Pending ({name})", False, f"Unexpected status: {data.get('status')}", response_time)
                        return False
                else:
                    self.log_test(f"Scrutator Join Pending ({name})", False, f"HTTP {response.status_code}: {response.text}", response_time)
                    return False
            
            # Step 2: Get scrutators list to get IDs for approval
            scrutators_response = self.session.get(f"{BACKEND_URL}/meetings/{self.meeting_id}/scrutators")
            if scrutators_response.status_code == 200:
                scrutators_data = scrutators_response.json()
                scrutators = scrutators_data.get('scrutators', [])
                
                # Step 3: Approve all scrutators
                for scrutator in scrutators:
                    start_time = time.time()
                    approval_response = self.session.post(f"{BACKEND_URL}/scrutators/{scrutator['id']}/approve", json={
                        "scrutator_id": scrutator['id'],
                        "approved": True
                    })
                    response_time = time.time() - start_time
                    
                    if approval_response.status_code == 200:
                        self.log_test(f"Scrutator Approval ({scrutator['name']})", True, "Scrutator approved successfully", response_time)
                    else:
                        self.log_test(f"Scrutator Approval ({scrutator['name']})", False, f"HTTP {approval_response.status_code}: {approval_response.text}", response_time)
                        return False
                
                # Step 4: Test that approved scrutators can now access
                start_time = time.time()
                access_response = self.session.post(f"{BACKEND_URL}/scrutators/join", json={
                    "name": "Jean Dupont",
                    "scrutator_code": self.scrutator_code
                })
                response_time = time.time() - start_time
                
                if access_response.status_code == 200:
                    access_data = access_response.json()
                    if access_data.get('status') == 'approved':
                        self.log_test("Approved Scrutator Access", True, "Approved scrutator can access interface", response_time)
                        return True
                    else:
                        self.log_test("Approved Scrutator Access", False, f"Unexpected status: {access_data.get('status')}", response_time)
                        return False
                else:
                    self.log_test("Approved Scrutator Access", False, f"HTTP {access_response.status_code}: {access_response.text}", response_time)
                    return False
            else:
                self.log_test("Get Scrutators List", False, f"HTTP {scrutators_response.status_code}: {scrutators_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Scrutator Approval Workflow", False, f"Exception: {str(e)}")
            return False
    
    def test_majority_voting_system(self):
        """Test the majority voting system for PDF generation"""
        if not self.meeting_id:
            self.log_test("Majority Voting System", False, "No meeting ID available")
            return False
        
        try:
            # Add some participants and polls first
            participants = ["Jean-Baptiste Moreau", "Sophie Lefebvre"]
            for participant_name in participants:
                self.session.post(f"{BACKEND_URL}/participants/join", json={
                    "name": participant_name,
                    "meeting_code": self.meeting_code
                })
            
            # Create a poll
            poll_data = {
                "question": "Test de vote pour rapport",
                "options": ["Option A", "Option B"]
            }
            self.session.post(f"{BACKEND_URL}/meetings/{self.meeting_id}/polls", json=poll_data)
            
            # Step 1: Request report generation
            start_time = time.time()
            request_response = self.session.post(f"{BACKEND_URL}/meetings/{self.meeting_id}/request-report", json={
                "meeting_id": self.meeting_id,
                "requested_by": "Alice Dupont"
            })
            response_time = time.time() - start_time
            
            if request_response.status_code == 200:
                request_data = request_response.json()
                if request_data.get('scrutator_approval_required'):
                    majority_needed = request_data.get('majority_needed', 0)
                    self.log_test("Report Generation Request", True, f"Scrutator approval required, majority needed: {majority_needed}", response_time)
                    
                    # Step 2: Scrutators vote (2 out of 3 approve - majority)
                    votes = [
                        ("Jean Dupont", True),   # YES
                        ("Marie Martin", True),  # YES  
                        ("Pierre Durand", False) # NO
                    ]
                    
                    for scrutator_name, vote in votes:
                        start_time = time.time()
                        vote_response = self.session.post(f"{BACKEND_URL}/meetings/{self.meeting_id}/scrutator-vote", json={
                            "meeting_id": self.meeting_id,
                            "scrutator_name": scrutator_name,
                            "approved": vote
                        })
                        response_time = time.time() - start_time
                        
                        if vote_response.status_code == 200:
                            vote_data = vote_response.json()
                            decision = vote_data.get('decision', 'pending')
                            vote_str = "YES" if vote else "NO"
                            self.log_test(f"Scrutator Vote ({scrutator_name})", True, f"Vote {vote_str}, Decision: {decision}", response_time)
                            
                            if decision == 'approved':
                                self.log_test("Majority Reached", True, f"Majority approval reached with {vote_data.get('yes_votes', 0)} YES votes", 0.001)
                                return True
                        else:
                            self.log_test(f"Scrutator Vote ({scrutator_name})", False, f"HTTP {vote_response.status_code}: {vote_response.text}", response_time)
                            return False
                    
                    self.log_test("Majority Voting System", False, "Majority should have been reached but wasn't detected")
                    return False
                else:
                    self.log_test("Report Generation Request", False, "Expected scrutator approval requirement", response_time)
                    return False
            else:
                self.log_test("Report Generation Request", False, f"HTTP {request_response.status_code}: {request_response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Majority Voting System", False, f"Exception: {str(e)}")
            return False
    
    def test_pdf_generation_after_approval(self):
        """Test PDF generation after majority approval"""
        if not self.meeting_id:
            self.log_test("PDF Generation After Approval", False, "No meeting ID available")
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
                    self.log_test("PDF Generation After Approval", True, f"PDF generated successfully after majority approval ({content_length} bytes)", response_time)
                    return True
                else:
                    self.log_test("PDF Generation After Approval", False, f"Invalid PDF response: {content_type}, {content_length} bytes", response_time)
                    return False
            else:
                self.log_test("PDF Generation After Approval", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_test("PDF Generation After Approval", False, f"Exception: {str(e)}")
            return False
    
    def test_direct_generation_without_scrutators(self):
        """Test direct PDF generation when no scrutators are present"""
        try:
            # Create a new meeting without scrutators
            meeting_data = {
                "title": "Test Direct Generation Sans Scrutateurs",
                "organizer_name": "Bob Martin"
            }
            response = self.session.post(f"{BACKEND_URL}/meetings", json=meeting_data)
            
            if response.status_code == 200:
                data = response.json()
                meeting_id = data['id']
                
                # Request report generation
                start_time = time.time()
                request_response = self.session.post(f"{BACKEND_URL}/meetings/{meeting_id}/request-report", json={
                    "meeting_id": meeting_id,
                    "requested_by": "Bob Martin"
                })
                response_time = time.time() - start_time
                
                if request_response.status_code == 200:
                    request_data = request_response.json()
                    if request_data.get('direct_generation'):
                        self.log_test("Direct Generation Without Scrutators", True, "Direct generation allowed when no scrutators", response_time)
                        
                        # Test actual PDF generation
                        pdf_response = self.session.get(f"{BACKEND_URL}/meetings/{meeting_id}/report")
                        if pdf_response.status_code == 200:
                            content_length = len(pdf_response.content)
                            self.log_test("Direct PDF Generation", True, f"PDF generated directly ({content_length} bytes)", 0.1)
                            return True
                        else:
                            self.log_test("Direct PDF Generation", False, f"PDF generation failed: {pdf_response.status_code}", 0.1)
                            return False
                    else:
                        self.log_test("Direct Generation Without Scrutators", False, "Expected direct generation flag", response_time)
                        return False
                else:
                    self.log_test("Direct Generation Without Scrutators", False, f"HTTP {request_response.status_code}: {request_response.text}", response_time)
                    return False
            else:
                self.log_test("Direct Generation Without Scrutators", False, f"Failed to create test meeting: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Direct Generation Without Scrutators", False, f"Exception: {str(e)}")
            return False
    
    def run_advanced_tests(self):
        """Run all advanced scrutator tests"""
        print("🔬 Starting Advanced Scrutator Functionality Testing")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Setup
        if not self.setup_meeting_with_scrutators():
            print("❌ CRITICAL: Could not setup test meeting with scrutators")
            return 0, 1
        
        # Advanced tests
        tests = [
            self.test_scrutator_approval_workflow,
            self.test_majority_voting_system,
            self.test_pdf_generation_after_approval,
            self.test_direct_generation_without_scrutators,
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
        print(f"🏁 ADVANCED SCRUTATOR TESTING COMPLETE")
        print(f"📊 RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("✅ ALL ADVANCED TESTS PASSED - Scrutator system fully operational!")
        elif passed >= total * 0.75:
            print("⚠️  MOSTLY WORKING - Minor issues in advanced features")
        else:
            print("❌ CRITICAL ISSUES - Advanced scrutator features need attention")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"  {result['status']} {result['test']} ({result['response_time']})")
            if result['details']:
                print(f"      {result['details']}")
        
        return passed, total

def main():
    """Main test execution"""
    tester = AdvancedScrutatorTester()
    passed, total = tester.run_advanced_tests()
    
    # Exit with appropriate code
    if passed == total:
        sys.exit(0)  # All tests passed
    else:
        sys.exit(1)  # Some tests failed

if __name__ == "__main__":
    main()