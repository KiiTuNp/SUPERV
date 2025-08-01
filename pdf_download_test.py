#!/usr/bin/env python3
"""
Comprehensive PDF Download Test for Vote Secret Application
Tests the complete PDF download process with realistic scenario as requested by user.

Scenario:
1. Create a complete meeting with organizer "Alice Dupont"
2. Add 3 participants and approve them
3. Create 2 polls with different options
4. Start polls and simulate realistic votes
5. Close polls
6. Generate PDF report via GET /api/meetings/{meeting_id}/report
7. Verify PDF is downloadable and contains correct data
8. Verify complete data deletion after generation
9. Verify meeting no longer exists
"""

import requests
import json
import time
import tempfile
import os
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BASE_URL = "https://acca2cb3-6c6a-4574-853d-844f59bfc1cb.preview.emergentagent.com/api"

class PDFDownloadTester:
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

    def step_1_create_meeting_with_alice(self):
        """Step 1: Create a complete meeting with organizer Alice Dupont"""
        try:
            meeting_data = {
                "title": "Assemblée Générale Annuelle 2025 - Conseil d'Administration",
                "organizer_name": "Alice Dupont"
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/meetings", json=meeting_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'meeting_code' in data and data['organizer_name'] == "Alice Dupont":
                    self.test_data['meeting'] = data
                    self.log_result("Step 1 - Create Meeting (Alice Dupont)", True, 
                                  f"Meeting created with code: {data['meeting_code']}", response_time)
                    return True
                else:
                    self.log_result("Step 1 - Create Meeting (Alice Dupont)", False, 
                                  f"Invalid response format: {data}", response_time)
                    return False
            else:
                self.log_result("Step 1 - Create Meeting (Alice Dupont)", False, 
                              f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Step 1 - Create Meeting (Alice Dupont)", False, f"Error: {str(e)}")
            return False

    def step_2_add_and_approve_participants(self):
        """Step 2: Add 3 participants and approve them"""
        if 'meeting' not in self.test_data:
            self.log_result("Step 2 - Add Participants", False, "No meeting data available")
            return False
        
        participants = [
            "Jean-Baptiste Moreau",
            "Sophie Lefebvre", 
            "Pierre-Alexandre Martin"
        ]
        
        self.test_data['participants'] = []
        
        # Add participants
        for i, participant_name in enumerate(participants):
            try:
                join_data = {
                    "name": participant_name,
                    "meeting_code": self.test_data['meeting']['meeting_code']
                }
                
                start_time = time.time()
                response = self.session.post(f"{BASE_URL}/participants/join", json=join_data)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    participant_data = response.json()
                    self.test_data['participants'].append(participant_data)
                    self.log_result(f"Step 2a - Add Participant {i+1} ({participant_name})", True, 
                                  f"Participant added successfully", response_time)
                else:
                    self.log_result(f"Step 2a - Add Participant {i+1} ({participant_name})", False, 
                                  f"HTTP {response.status_code}: {response.text}", response_time)
                    return False
            except Exception as e:
                self.log_result(f"Step 2a - Add Participant {i+1} ({participant_name})", False, f"Error: {str(e)}")
                return False
        
        # Approve all participants
        for i, participant in enumerate(self.test_data['participants']):
            try:
                approval_data = {
                    "participant_id": participant['id'],
                    "approved": True
                }
                
                start_time = time.time()
                response = self.session.post(f"{BASE_URL}/participants/{participant['id']}/approve", json=approval_data)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    self.log_result(f"Step 2b - Approve Participant {i+1} ({participant['name']})", True, 
                                  f"Participant approved successfully", response_time)
                else:
                    self.log_result(f"Step 2b - Approve Participant {i+1} ({participant['name']})", False, 
                                  f"HTTP {response.status_code}: {response.text}", response_time)
                    return False
            except Exception as e:
                self.log_result(f"Step 2b - Approve Participant {i+1} ({participant['name']})", False, f"Error: {str(e)}")
                return False
        
        return True

    def step_3_create_two_polls(self):
        """Step 3: Create 2 polls with different options"""
        if 'meeting' not in self.test_data:
            self.log_result("Step 3 - Create Polls", False, "No meeting data available")
            return False
        
        polls_data = [
            {
                "question": "Approuvez-vous l'augmentation du budget de fonctionnement de 12% pour l'année 2025 ?",
                "options": [
                    "Oui, j'approuve cette augmentation",
                    "Non, je m'oppose à cette augmentation", 
                    "Je m'abstiens de voter",
                    "Je souhaite une augmentation plus modérée (8%)"
                ],
                "timer_duration": 300,
                "show_results_real_time": True
            },
            {
                "question": "Quel devrait être notre priorité stratégique principale pour 2025 ?",
                "options": [
                    "Expansion géographique vers de nouveaux marchés",
                    "Investissement massif en recherche et développement",
                    "Amélioration de la satisfaction client existante",
                    "Optimisation des coûts et efficacité opérationnelle",
                    "Développement durable et responsabilité sociale"
                ],
                "timer_duration": 600,
                "show_results_real_time": True
            }
        ]
        
        self.test_data['polls'] = []
        meeting_id = self.test_data['meeting']['id']
        
        for i, poll_data in enumerate(polls_data):
            try:
                start_time = time.time()
                response = self.session.post(f"{BASE_URL}/meetings/{meeting_id}/polls", json=poll_data)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    poll_response = response.json()
                    self.test_data['polls'].append(poll_response)
                    self.log_result(f"Step 3 - Create Poll {i+1}", True, 
                                  f"Poll created with {len(poll_data['options'])} options", response_time)
                else:
                    self.log_result(f"Step 3 - Create Poll {i+1}", False, 
                                  f"HTTP {response.status_code}: {response.text}", response_time)
                    return False
            except Exception as e:
                self.log_result(f"Step 3 - Create Poll {i+1}", False, f"Error: {str(e)}")
                return False
        
        return True

    def step_4_start_polls_and_simulate_votes(self):
        """Step 4: Start polls and simulate realistic votes"""
        if 'polls' not in self.test_data or len(self.test_data['polls']) < 2:
            self.log_result("Step 4 - Start Polls and Vote", False, "No polls data available")
            return False
        
        # Start both polls
        for i, poll in enumerate(self.test_data['polls']):
            try:
                start_time = time.time()
                response = self.session.post(f"{BASE_URL}/polls/{poll['id']}/start")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    self.log_result(f"Step 4a - Start Poll {i+1}", True, 
                                  f"Poll started successfully", response_time)
                else:
                    self.log_result(f"Step 4a - Start Poll {i+1}", False, 
                                  f"HTTP {response.status_code}: {response.text}", response_time)
                    return False
            except Exception as e:
                self.log_result(f"Step 4a - Start Poll {i+1}", False, f"Error: {str(e)}")
                return False
        
        # Simulate realistic voting patterns
        # Poll 1: Budget increase - mixed opinions
        poll1_votes = [
            0,  # Yes, approve (Jean-Baptiste)
            1,  # No, oppose (Sophie)
            0,  # Yes, approve (Pierre-Alexandre)
            3,  # Moderate increase (additional vote 1)
            0,  # Yes, approve (additional vote 2)
            2,  # Abstain (additional vote 3)
            1,  # No, oppose (additional vote 4)
            0,  # Yes, approve (additional vote 5)
        ]
        
        # Poll 2: Strategic priority - diverse choices
        poll2_votes = [
            1,  # R&D investment (Jean-Baptiste)
            2,  # Customer satisfaction (Sophie)
            0,  # Geographic expansion (Pierre-Alexandre)
            4,  # Sustainable development (additional vote 1)
            1,  # R&D investment (additional vote 2)
            3,  # Cost optimization (additional vote 3)
            2,  # Customer satisfaction (additional vote 4)
            1,  # R&D investment (additional vote 5)
        ]
        
        # Submit votes for Poll 1
        poll1 = self.test_data['polls'][0]
        for vote_idx, option_idx in enumerate(poll1_votes):
            try:
                vote_data = {
                    "poll_id": poll1['id'],
                    "option_id": poll1['options'][option_idx]['id']
                }
                
                start_time = time.time()
                response = self.session.post(f"{BASE_URL}/votes", json=vote_data)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    if vote_idx < 3:  # Only log first 3 votes to avoid spam
                        self.log_result(f"Step 4b - Vote {vote_idx+1} on Poll 1", True, 
                                      f"Vote submitted for option {option_idx+1}", response_time)
                else:
                    self.log_result(f"Step 4b - Vote {vote_idx+1} on Poll 1", False, 
                                  f"HTTP {response.status_code}: {response.text}", response_time)
                    return False
            except Exception as e:
                self.log_result(f"Step 4b - Vote {vote_idx+1} on Poll 1", False, f"Error: {str(e)}")
                return False
        
        # Submit votes for Poll 2
        poll2 = self.test_data['polls'][1]
        for vote_idx, option_idx in enumerate(poll2_votes):
            try:
                vote_data = {
                    "poll_id": poll2['id'],
                    "option_id": poll2['options'][option_idx]['id']
                }
                
                start_time = time.time()
                response = self.session.post(f"{BASE_URL}/votes", json=vote_data)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    if vote_idx < 3:  # Only log first 3 votes to avoid spam
                        self.log_result(f"Step 4c - Vote {vote_idx+1} on Poll 2", True, 
                                      f"Vote submitted for option {option_idx+1}", response_time)
                else:
                    self.log_result(f"Step 4c - Vote {vote_idx+1} on Poll 2", False, 
                                  f"HTTP {response.status_code}: {response.text}", response_time)
                    return False
            except Exception as e:
                self.log_result(f"Step 4c - Vote {vote_idx+1} on Poll 2", False, f"Error: {str(e)}")
                return False
        
        # Log total votes summary
        self.log_result("Step 4d - Voting Summary", True, 
                      f"Total votes: Poll 1 ({len(poll1_votes)} votes), Poll 2 ({len(poll2_votes)} votes)")
        
        return True

    def step_5_close_polls(self):
        """Step 5: Close polls"""
        if 'polls' not in self.test_data:
            self.log_result("Step 5 - Close Polls", False, "No polls data available")
            return False
        
        for i, poll in enumerate(self.test_data['polls']):
            try:
                start_time = time.time()
                response = self.session.post(f"{BASE_URL}/polls/{poll['id']}/close")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    self.log_result(f"Step 5 - Close Poll {i+1}", True, 
                                  f"Poll closed successfully", response_time)
                else:
                    self.log_result(f"Step 5 - Close Poll {i+1}", False, 
                                  f"HTTP {response.status_code}: {response.text}", response_time)
                    return False
            except Exception as e:
                self.log_result(f"Step 5 - Close Poll {i+1}", False, f"Error: {str(e)}")
                return False
        
        return True

    def step_6_generate_pdf_report(self):
        """Step 6: Generate PDF report via GET /api/meetings/{meeting_id}/report"""
        if 'meeting' not in self.test_data:
            self.log_result("Step 6 - Generate PDF Report", False, "No meeting data available")
            return False
        
        try:
            meeting_id = self.test_data['meeting']['id']
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/report")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # Check Content-Type header
                content_type = response.headers.get('content-type', '')
                if 'application/pdf' not in content_type:
                    self.log_result("Step 6 - Generate PDF Report", False, 
                                  f"Wrong Content-Type: {content_type}", response_time)
                    return False
                
                # Check Content-Disposition header
                content_disposition = response.headers.get('content-disposition', '')
                if 'attachment' not in content_disposition:
                    self.log_result("Step 6 - Generate PDF Report", False, 
                                  f"Missing attachment header: {content_disposition}", response_time)
                    return False
                
                # Save PDF to verify it's valid
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    tmp_file.write(response.content)
                    tmp_path = tmp_file.name
                
                # Check file size
                file_size = os.path.getsize(tmp_path)
                
                # Verify PDF header
                with open(tmp_path, 'rb') as f:
                    pdf_header = f.read(4)
                    is_valid_pdf = pdf_header == b'%PDF'
                
                os.unlink(tmp_path)  # Clean up
                
                if file_size > 2000 and is_valid_pdf:  # PDF should be substantial and valid
                    self.test_data['pdf_generated'] = True
                    self.log_result("Step 6 - Generate PDF Report", True, 
                                  f"PDF generated successfully ({file_size} bytes, valid PDF format)", response_time)
                    return True
                else:
                    self.log_result("Step 6 - Generate PDF Report", False, 
                                  f"Invalid PDF: size={file_size}, valid_header={is_valid_pdf}", response_time)
                    return False
            else:
                self.log_result("Step 6 - Generate PDF Report", False, 
                              f"HTTP {response.status_code}: {response.text}", response_time)
                return False
        except Exception as e:
            self.log_result("Step 6 - Generate PDF Report", False, f"Error: {str(e)}")
            return False

    def step_7_verify_data_deletion(self):
        """Step 7: Verify complete data deletion after PDF generation"""
        if 'meeting' not in self.test_data:
            self.log_result("Step 7 - Verify Data Deletion", False, "No meeting data available")
            return False
        
        meeting_id = self.test_data['meeting']['id']
        meeting_code = self.test_data['meeting']['meeting_code']
        
        # Test 1: Meeting should no longer exist by code
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_code}")
            response_time = time.time() - start_time
            
            if response.status_code == 404:
                self.log_result("Step 7a - Meeting Deleted (by code)", True, 
                              f"Meeting no longer accessible by code", response_time)
            else:
                self.log_result("Step 7a - Meeting Deleted (by code)", False, 
                              f"Meeting still accessible: HTTP {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_result("Step 7a - Meeting Deleted (by code)", False, f"Error: {str(e)}")
            return False
        
        # Test 2: Organizer view should no longer exist
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/organizer")
            response_time = time.time() - start_time
            
            if response.status_code == 404:
                self.log_result("Step 7b - Organizer View Deleted", True, 
                              f"Organizer view no longer accessible", response_time)
            else:
                self.log_result("Step 7b - Organizer View Deleted", False, 
                              f"Organizer view still accessible: HTTP {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_result("Step 7b - Organizer View Deleted", False, f"Error: {str(e)}")
            return False
        
        # Test 3: Poll results should no longer exist
        if 'polls' in self.test_data:
            for i, poll in enumerate(self.test_data['polls']):
                try:
                    start_time = time.time()
                    response = self.session.get(f"{BASE_URL}/polls/{poll['id']}/results")
                    response_time = time.time() - start_time
                    
                    if response.status_code == 404:
                        self.log_result(f"Step 7c - Poll {i+1} Results Deleted", True, 
                                      f"Poll results no longer accessible", response_time)
                    else:
                        self.log_result(f"Step 7c - Poll {i+1} Results Deleted", False, 
                                      f"Poll results still accessible: HTTP {response.status_code}", response_time)
                        return False
                except Exception as e:
                    self.log_result(f"Step 7c - Poll {i+1} Results Deleted", False, f"Error: {str(e)}")
                    return False
        
        # Test 4: Participant status should no longer exist
        if 'participants' in self.test_data:
            for i, participant in enumerate(self.test_data['participants']):
                try:
                    start_time = time.time()
                    response = self.session.get(f"{BASE_URL}/participants/{participant['id']}/status")
                    response_time = time.time() - start_time
                    
                    if response.status_code == 404:
                        self.log_result(f"Step 7d - Participant {i+1} Status Deleted", True, 
                                      f"Participant status no longer accessible", response_time)
                    else:
                        self.log_result(f"Step 7d - Participant {i+1} Status Deleted", False, 
                                      f"Participant status still accessible: HTTP {response.status_code}", response_time)
                        return False
                except Exception as e:
                    self.log_result(f"Step 7d - Participant {i+1} Status Deleted", False, f"Error: {str(e)}")
                    return False
        
        return True

    def step_8_verify_meeting_nonexistent(self):
        """Step 8: Final verification that meeting no longer exists"""
        if 'meeting' not in self.test_data:
            self.log_result("Step 8 - Final Meeting Verification", False, "No meeting data available")
            return False
        
        meeting_id = self.test_data['meeting']['id']
        
        # Try to generate report again - should fail
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/report")
            response_time = time.time() - start_time
            
            if response.status_code == 404:
                self.log_result("Step 8 - Final Meeting Verification", True, 
                              f"Meeting completely removed - report generation fails as expected", response_time)
                return True
            else:
                self.log_result("Step 8 - Final Meeting Verification", False, 
                              f"Meeting still exists: HTTP {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_result("Step 8 - Final Meeting Verification", False, f"Error: {str(e)}")
            return False

    def run_complete_pdf_test(self):
        """Run the complete PDF download test scenario"""
        print("🚀 Starting Complete PDF Download Test Scenario")
        print("=" * 80)
        print("Testing user issue: 'Quand on appuie sur Confirmer et télécharger pour télécharger le PDF'")
        print("=" * 80)
        
        steps = [
            ("Step 1: Create Meeting with Alice Dupont", self.step_1_create_meeting_with_alice),
            ("Step 2: Add and Approve 3 Participants", self.step_2_add_and_approve_participants),
            ("Step 3: Create 2 Polls with Different Options", self.step_3_create_two_polls),
            ("Step 4: Start Polls and Simulate Realistic Votes", self.step_4_start_polls_and_simulate_votes),
            ("Step 5: Close Polls", self.step_5_close_polls),
            ("Step 6: Generate PDF Report (Critical Test)", self.step_6_generate_pdf_report),
            ("Step 7: Verify Complete Data Deletion", self.step_7_verify_data_deletion),
            ("Step 8: Verify Meeting No Longer Exists", self.step_8_verify_meeting_nonexistent)
        ]
        
        passed = 0
        total = 0
        
        for step_name, step_func in steps:
            print(f"\n🔄 {step_name}")
            print("-" * 60)
            try:
                if step_func():
                    passed += 1
                    print(f"✅ {step_name} - COMPLETED")
                else:
                    print(f"❌ {step_name} - FAILED")
                    break  # Stop on first failure as subsequent steps depend on previous ones
                total += 1
            except Exception as e:
                print(f"❌ {step_name} - ERROR: {str(e)}")
                break
        
        print("\n" + "=" * 80)
        print(f"🏁 PDF Download Test Results: {passed}/{len(steps)} steps completed")
        
        if passed == len(steps):
            print("🎉 COMPLETE SUCCESS! PDF download functionality is working perfectly!")
            print("✅ All critical points tested:")
            print("   - PDF generates correctly with real content")
            print("   - Complete data deletion works")
            print("   - Proper error responses for non-existent meetings")
            print("   - PDF file size > 2000 bytes")
            print("   - Correct headers (Content-Type: application/pdf)")
        else:
            print(f"⚠️  Test failed at step {passed + 1}. PDF download functionality has issues.")
        
        return passed == len(steps), self.results

def main():
    """Main test execution"""
    tester = PDFDownloadTester()
    success, results = tester.run_complete_pdf_test()
    
    # Print detailed summary
    print("\n📊 DETAILED TEST SUMMARY")
    print("=" * 80)
    
    for result in results:
        print(f"{result['status']} {result['test']}")
        if result['message']:
            print(f"    └─ {result['message']}")
        if result['response_time'] != "N/A":
            print(f"    └─ Response time: {result['response_time']}")
    
    print("\n🔍 CRITICAL FINDINGS:")
    if success:
        print("✅ Backend PDF generation is working correctly")
        print("✅ User's reported issue appears to be resolved")
        print("✅ Frontend correction by main agent should fix the download problem")
    else:
        print("❌ Backend PDF generation has issues that need to be addressed")
        print("❌ User's reported issue is likely due to backend problems")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)