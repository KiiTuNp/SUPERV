#!/usr/bin/env python3
"""
Focused test for the NEW advanced scrutator workflow with approval and majority voting
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://dffd1ffb-03ba-4c55-8b21-65220fce6f6a.preview.emergentagent.com/api"

class AdvancedScrutatorTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def log_result(self, test_name: str, success: bool, message: str, response_time: float = 0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message} ({response_time:.3f}s)" if response_time > 0 else f"{status} {test_name}: {message}")
        return success

    def test_complete_advanced_scrutator_workflow(self):
        """Test the complete advanced scrutator workflow as requested"""
        print("\n🎯 TESTING COMPLETE ADVANCED SCRUTATOR WORKFLOW")
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
                all_passed &= self.log_result("1. Create Assembly", True, f"Assembly created: {scenario_data['meeting']['meeting_code']}", response_time)
            else:
                all_passed &= self.log_result("1. Create Assembly", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            all_passed &= self.log_result("1. Create Assembly", False, f"Error: {str(e)}")
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
                all_passed &= self.log_result("2. Add Scrutators", True, f"3 scrutators added with code: {data['scrutator_code']}", response_time)
            else:
                all_passed &= self.log_result("2. Add Scrutators", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            all_passed &= self.log_result("2. Add Scrutators", False, f"Error: {str(e)}")
            return False
        
        # Step 3: Test Jean Dupont connection - should get pending_approval
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
                    all_passed &= self.log_result("3. Jean Dupont Pending Status", True, f"Jean Dupont correctly receives pending_approval", response_time)
                else:
                    all_passed &= self.log_result("3. Jean Dupont Pending Status", False, f"Expected pending_approval, got: {data}", response_time)
            else:
                all_passed &= self.log_result("3. Jean Dupont Pending Status", False, f"HTTP {response.status_code}: {response.text}", response_time)
        except Exception as e:
            all_passed &= self.log_result("3. Jean Dupont Pending Status", False, f"Error: {str(e)}")
        
        # Step 4: Approve Jean Dupont
        try:
            meeting_id = scenario_data['meeting']['id']
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/scrutators")
            
            if response.status_code == 200:
                data = response.json()
                jean_scrutator = None
                for scrutator in data['scrutators']:
                    if scrutator['name'] == 'Jean Dupont':
                        jean_scrutator = scrutator
                        break
                
                if jean_scrutator:
                    approval_data = {
                        "scrutator_id": jean_scrutator['id'],
                        "approved": True
                    }
                    
                    start_time = time.time()
                    response = self.session.post(f"{BASE_URL}/scrutators/{jean_scrutator['id']}/approve", json=approval_data)
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        all_passed &= self.log_result("4. Approve Jean Dupont", True, f"Jean Dupont approved by organizer", response_time)
                    else:
                        all_passed &= self.log_result("4. Approve Jean Dupont", False, f"HTTP {response.status_code}: {response.text}", response_time)
                else:
                    all_passed &= self.log_result("4. Find Jean Dupont", False, "Jean Dupont not found in scrutators list")
        except Exception as e:
            all_passed &= self.log_result("4. Approve Jean Dupont", False, f"Error: {str(e)}")
        
        # Step 5: Test Jean Dupont can now access interface
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
                    all_passed &= self.log_result("5. Jean Dupont Access Interface", True, f"Jean Dupont can now access interface", response_time)
                else:
                    all_passed &= self.log_result("5. Jean Dupont Access Interface", False, f"Expected approved access, got: {data}", response_time)
            else:
                all_passed &= self.log_result("5. Jean Dupont Access Interface", False, f"HTTP {response.status_code}: {response.text}", response_time)
        except Exception as e:
            all_passed &= self.log_result("5. Jean Dupont Access Interface", False, f"Error: {str(e)}")
        
        # Step 6: Approve all scrutators for majority voting test
        try:
            meeting_id = scenario_data['meeting']['id']
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/scrutators")
            
            if response.status_code == 200:
                data = response.json()
                approved_count = 0
                
                for scrutator in data['scrutators']:
                    if scrutator['approval_status'] != 'approved':  # Only approve if not already approved
                        approval_data = {
                            "scrutator_id": scrutator['id'],
                            "approved": True
                        }
                        
                        response = self.session.post(f"{BASE_URL}/scrutators/{scrutator['id']}/approve", json=approval_data)
                        if response.status_code == 200:
                            approved_count += 1
                    else:
                        approved_count += 1  # Already approved
                
                if approved_count == 3:
                    all_passed &= self.log_result("6. Approve All Scrutators", True, f"All 3 scrutators approved for voting test")
                else:
                    all_passed &= self.log_result("6. Approve All Scrutators", False, f"Only {approved_count}/3 scrutators approved")
        except Exception as e:
            all_passed &= self.log_result("6. Approve All Scrutators", False, f"Error: {str(e)}")
        
        # Step 7: Add some participants and polls for PDF generation
        try:
            # Add participants
            participants = ["Sophie Participant", "Pierre Votant"]
            
            for participant_name in participants:
                join_data = {
                    "name": participant_name,
                    "meeting_code": scenario_data['meeting']['meeting_code']
                }
                
                response = self.session.post(f"{BASE_URL}/participants/join", json=join_data)
                if response.status_code == 200:
                    participant_data = response.json()
                    
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
            
            all_passed &= self.log_result("7. Setup Data for PDF", True, f"Added participants and polls for PDF generation test")
            
        except Exception as e:
            all_passed &= self.log_result("7. Setup Data for PDF", False, f"Error: {str(e)}")
        
        # Step 8: Test majority voting system for PDF generation
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
                print(f"    📊 Report request response: {data}")
                
                if data.get('scrutator_approval_required') and data.get('scrutator_count') == 3 and data.get('majority_needed') == 2:
                    all_passed &= self.log_result("8a. Request Report Generation", True, f"Report request sent, need {data['majority_needed']}/3 votes", response_time)
                    
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
                            print(f"    📊 Vote result: {vote_result}")
                            all_passed &= self.log_result(f"8b. {desc}", True, f"Vote recorded: {vote_result.get('message', 'Vote submitted')}", response_time)
                            
                            # Check if decision is made
                            if vote_result.get('decision') == 'approved':
                                all_passed &= self.log_result("8c. Majority Approval Reached", True, f"Majority approved: {vote_result['yes_votes']}/{vote_result['majority_needed']}")
                                scenario_data['generation_approved'] = True
                                break
                        else:
                            all_passed &= self.log_result(f"8b. {desc}", False, f"HTTP {response.status_code}: {response.text}", response_time)
                    
                else:
                    all_passed &= self.log_result("8a. Request Report Generation", False, f"Unexpected response: {data}", response_time)
            else:
                all_passed &= self.log_result("8a. Request Report Generation", False, f"HTTP {response.status_code}: {response.text}", response_time)
        except Exception as e:
            all_passed &= self.log_result("8. Test Majority Voting", False, f"Error: {str(e)}")
        
        # Step 9: Test actual PDF generation after approval
        try:
            if scenario_data.get('generation_approved'):
                meeting_id = scenario_data['meeting']['id']
                
                # First, let's check the meeting state after approval
                response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/organizer")
                if response.status_code == 200:
                    meeting_data = response.json()
                    print(f"    📊 Meeting state after approval: report_generation_pending={meeting_data['meeting'].get('report_generation_pending')}")
                
                start_time = time.time()
                response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/report")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'application/pdf' in content_type:
                        file_size = len(response.content)
                        all_passed &= self.log_result("9. Generate PDF After Approval", True, f"PDF generated successfully ({file_size} bytes)", response_time)
                    else:
                        all_passed &= self.log_result("9. Generate PDF After Approval", False, f"Wrong content type: {content_type}", response_time)
                elif response.status_code == 400:
                    # This might be the expected behavior - the flag was reset after approval
                    error_data = response.json()
                    if "nécessite l'approbation" in error_data.get('detail', ''):
                        all_passed &= self.log_result("9. Generate PDF After Approval", False, f"BACKEND BUG: Flag reset after approval - {error_data['detail']}", response_time)
                    else:
                        all_passed &= self.log_result("9. Generate PDF After Approval", False, f"HTTP 400: {error_data}", response_time)
                else:
                    all_passed &= self.log_result("9. Generate PDF After Approval", False, f"HTTP {response.status_code}: {response.text}", response_time)
            else:
                all_passed &= self.log_result("9. Generate PDF After Approval", False, "Cannot test PDF generation - approval not reached")
        except Exception as e:
            all_passed &= self.log_result("9. Generate PDF After Approval", False, f"Error: {str(e)}")
        
        # Step 10: Test majority rejection scenario
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
                            ("Bob Scrutateur", False, "Bob votes NO")  # Only need 2 NO votes for majority
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
                                    all_passed &= self.log_result("10a. Test Majority Rejection", True, f"Majority correctly rejected: {vote_result['no_votes']}/{vote_result['majority_needed']}")
                                    
                                    # Test that PDF generation is now blocked
                                    response = self.session.get(f"{BASE_URL}/meetings/{rejection_meeting['id']}/report")
                                    if response.status_code == 403:
                                        all_passed &= self.log_result("10b. PDF Generation Blocked", True, "PDF generation correctly blocked after rejection")
                                    elif response.status_code == 400:
                                        # Check if it's the right error message
                                        error_data = response.json()
                                        if "non approuvée" in error_data.get('detail', ''):
                                            all_passed &= self.log_result("10b. PDF Generation Blocked", True, "PDF generation correctly blocked (400 with proper message)")
                                        else:
                                            all_passed &= self.log_result("10b. PDF Generation Blocked", False, f"Wrong error message: {error_data}")
                                    else:
                                        all_passed &= self.log_result("10b. PDF Generation Blocked", False, f"Expected 403/400, got {response.status_code}")
                                    break
                    
                    # Clean up rejection test meeting
                    try:
                        # Force cleanup by trying to generate report (will fail but clean up)
                        self.session.get(f"{BASE_URL}/meetings/{rejection_meeting['id']}/report")
                    except:
                        pass
                        
        except Exception as e:
            all_passed &= self.log_result("10. Test Majority Rejection", False, f"Error: {str(e)}")
        
        # Summary
        print("\n" + "=" * 80)
        if all_passed:
            print("🎉 ADVANCED SCRUTATOR WORKFLOW VALIDATION COMPLETE - ALL TESTS PASSED!")
            print("✅ Scrutator approval workflow working (pending → approved)")
            print("✅ Majority voting system working (2/3 approval)")
            print("✅ PDF generation protected by scrutator approval")
            print("✅ Majority rejection system working")
            print("✅ All critical endpoints functioning correctly")
        else:
            print("❌ SOME ADVANCED SCRUTATOR WORKFLOW TESTS FAILED")
            print("Review the failed tests above for details")
        
        return all_passed

def main():
    """Main test execution"""
    tester = AdvancedScrutatorTester()
    success = tester.test_complete_advanced_scrutator_workflow()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)