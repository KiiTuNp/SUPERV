#!/usr/bin/env python3
"""
Focused PDF Report Generation Test for Vote Secret Application
Tests the specific functionality reported as not working by the user
"""

import requests
import json
import time
import tempfile
import os
from datetime import datetime

# Configuration
BASE_URL = "https://acca2cb3-6c6a-4574-853d-844f59bfc1cb.preview.emergentagent.com/api"

class PDFReportTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_data = {}
        
    def log_result(self, test_name: str, success: bool, message: str, response_time: float = 0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}" + (f" ({response_time:.3f}s)" if response_time > 0 else ""))
        return success

    def setup_test_meeting(self):
        """Create a test meeting for PDF generation"""
        print("🔧 Setting up test meeting...")
        
        # 1. Create meeting
        meeting_data = {
            "title": "Assemblée Générale Test PDF 2025",
            "organizer_name": "Sophie Dubois"
        }
        
        start_time = time.time()
        response = self.session.post(f"{BASE_URL}/meetings", json=meeting_data)
        response_time = time.time() - start_time
        
        if response.status_code != 200:
            return self.log_result("Setup - Create Meeting", False, f"HTTP {response.status_code}: {response.text}", response_time)
        
        meeting = response.json()
        self.test_data['meeting'] = meeting
        self.log_result("Setup - Create Meeting", True, f"Meeting created with code: {meeting['meeting_code']}", response_time)
        
        return True

    def add_test_participants(self):
        """Add and approve test participants"""
        print("👥 Adding test participants...")
        
        participants = [
            "Jean Dupont",
            "Marie Martin", 
            "Pierre Durand",
            "Claire Moreau",
            "Antoine Bernard"
        ]
        
        meeting_code = self.test_data['meeting']['meeting_code']
        approved_participants = []
        
        for name in participants:
            # Join participant
            join_data = {
                "name": name,
                "meeting_code": meeting_code
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/participants/join", json=join_data)
            response_time = time.time() - start_time
            
            if response.status_code != 200:
                self.log_result(f"Setup - Join {name}", False, f"HTTP {response.status_code}: {response.text}", response_time)
                continue
                
            participant = response.json()
            self.log_result(f"Setup - Join {name}", True, "Participant joined", response_time)
            
            # Approve participant
            approval_data = {
                "participant_id": participant['id'],
                "approved": True
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/participants/{participant['id']}/approve", json=approval_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                approved_participants.append(participant)
                self.log_result(f"Setup - Approve {name}", True, "Participant approved", response_time)
            else:
                self.log_result(f"Setup - Approve {name}", False, f"HTTP {response.status_code}: {response.text}", response_time)
        
        self.test_data['participants'] = approved_participants
        return len(approved_participants) > 0

    def create_test_polls(self):
        """Create test polls with multiple options"""
        print("📊 Creating test polls...")
        
        polls_data = [
            {
                "question": "Êtes-vous favorable à l'augmentation du budget de 15% pour 2025?",
                "options": ["Oui, je suis favorable", "Non, je m'oppose", "Je m'abstiens", "J'ai besoin de plus d'informations"],
                "timer_duration": 300,
                "show_results_real_time": True
            },
            {
                "question": "Quelle priorité devrait avoir notre organisation cette année?",
                "options": ["Développement technologique", "Formation du personnel", "Expansion géographique", "Amélioration des processus", "Réduction des coûts"],
                "timer_duration": None,
                "show_results_real_time": True
            },
            {
                "question": "Approuvez-vous la nouvelle politique de télétravail?",
                "options": ["Totalement d'accord", "Plutôt d'accord", "Plutôt en désaccord", "Totalement en désaccord"],
                "timer_duration": 180,
                "show_results_real_time": False
            }
        ]
        
        meeting_id = self.test_data['meeting']['id']
        created_polls = []
        
        for i, poll_data in enumerate(polls_data, 1):
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/meetings/{meeting_id}/polls", json=poll_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                poll = response.json()
                created_polls.append(poll)
                self.log_result(f"Setup - Create Poll {i}", True, f"Poll created: {poll_data['question'][:50]}...", response_time)
            else:
                self.log_result(f"Setup - Create Poll {i}", False, f"HTTP {response.status_code}: {response.text}", response_time)
        
        self.test_data['polls'] = created_polls
        return len(created_polls) > 0

    def simulate_votes(self):
        """Simulate votes on the created polls"""
        print("🗳️  Simulating votes...")
        
        if not self.test_data.get('polls'):
            return self.log_result("Setup - Simulate Votes", False, "No polls available")
        
        votes_cast = 0
        
        for poll in self.test_data['polls']:
            # Start the poll first
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/polls/{poll['id']}/start")
            response_time = time.time() - start_time
            
            if response.status_code != 200:
                self.log_result(f"Setup - Start Poll", False, f"HTTP {response.status_code}: {response.text}", response_time)
                continue
            
            self.log_result(f"Setup - Start Poll", True, f"Poll started", response_time)
            
            # Cast multiple votes (simulating different participants)
            options = poll['options']
            vote_distribution = [3, 2, 1, 1]  # Different vote counts per option
            
            for i, option in enumerate(options):
                votes_for_option = vote_distribution[i] if i < len(vote_distribution) else 1
                
                for vote_num in range(votes_for_option):
                    vote_data = {
                        "poll_id": poll['id'],
                        "option_id": option['id']
                    }
                    
                    start_time = time.time()
                    response = self.session.post(f"{BASE_URL}/votes", json=vote_data)
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        votes_cast += 1
                    else:
                        self.log_result(f"Setup - Cast Vote", False, f"HTTP {response.status_code}: {response.text}", response_time)
            
            # Close the poll
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/polls/{poll['id']}/close")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result(f"Setup - Close Poll", True, f"Poll closed", response_time)
            else:
                self.log_result(f"Setup - Close Poll", False, f"HTTP {response.status_code}: {response.text}", response_time)
        
        self.log_result("Setup - Simulate Votes", True, f"Cast {votes_cast} votes across all polls")
        return votes_cast > 0

    def test_pdf_generation(self):
        """Test the PDF report generation endpoint"""
        print("📄 Testing PDF report generation...")
        
        if 'meeting' not in self.test_data:
            return self.log_result("PDF Generation", False, "No meeting data available")
        
        meeting_id = self.test_data['meeting']['id']
        
        # Test the GET endpoint for PDF generation
        start_time = time.time()
        response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/report")
        response_time = time.time() - start_time
        
        # Check response status
        if response.status_code != 200:
            return self.log_result("PDF Generation", False, f"HTTP {response.status_code}: {response.text}", response_time)
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        if 'application/pdf' not in content_type:
            return self.log_result("PDF Generation", False, f"Wrong content type: {content_type}", response_time)
        
        # Check content disposition header
        content_disposition = response.headers.get('content-disposition', '')
        if 'attachment' not in content_disposition or 'filename' not in content_disposition:
            return self.log_result("PDF Generation", False, f"Missing or invalid Content-Disposition header: {content_disposition}", response_time)
        
        # Save and validate PDF content
        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(response.content)
                tmp_path = tmp_file.name
            
            # Check file size
            file_size = os.path.getsize(tmp_path)
            
            # Basic PDF validation - check for PDF header
            with open(tmp_path, 'rb') as f:
                header = f.read(4)
                is_pdf = header == b'%PDF'
            
            os.unlink(tmp_path)  # Clean up
            
            if not is_pdf:
                return self.log_result("PDF Generation", False, f"Invalid PDF format (header check failed)", response_time)
            
            if file_size < 1000:  # PDF should be at least 1KB
                return self.log_result("PDF Generation", False, f"PDF too small ({file_size} bytes)", response_time)
            
            self.log_result("PDF Generation", True, f"Valid PDF generated ({file_size} bytes)", response_time)
            return True
            
        except Exception as e:
            return self.log_result("PDF Generation", False, f"Error validating PDF: {str(e)}", response_time)

    def test_data_deletion(self):
        """Test that data is deleted after PDF generation"""
        print("🗑️  Testing data deletion after PDF generation...")
        
        if 'meeting' not in self.test_data:
            return self.log_result("Data Deletion", False, "No meeting data available")
        
        meeting_id = self.test_data['meeting']['id']
        meeting_code = self.test_data['meeting']['meeting_code']
        
        # Try to access the meeting after PDF generation
        start_time = time.time()
        response = self.session.get(f"{BASE_URL}/meetings/{meeting_code}")
        response_time = time.time() - start_time
        
        if response.status_code == 404:
            self.log_result("Data Deletion - Meeting", True, "Meeting deleted successfully", response_time)
        else:
            self.log_result("Data Deletion - Meeting", False, f"Meeting still exists: HTTP {response.status_code}", response_time)
            return False
        
        # Try to access organizer view
        start_time = time.time()
        response = self.session.get(f"{BASE_URL}/meetings/{meeting_id}/organizer")
        response_time = time.time() - start_time
        
        if response.status_code == 404:
            self.log_result("Data Deletion - Organizer View", True, "Organizer view inaccessible (data deleted)", response_time)
        else:
            self.log_result("Data Deletion - Organizer View", False, f"Organizer view still accessible: HTTP {response.status_code}", response_time)
            return False
        
        # Try to access polls
        if self.test_data.get('polls'):
            poll_id = self.test_data['polls'][0]['id']
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/polls/{poll_id}/results")
            response_time = time.time() - start_time
            
            if response.status_code == 404:
                self.log_result("Data Deletion - Poll Results", True, "Poll data deleted successfully", response_time)
            else:
                self.log_result("Data Deletion - Poll Results", False, f"Poll data still exists: HTTP {response.status_code}", response_time)
                return False
        
        return True

    def test_error_handling(self):
        """Test error handling for non-existent meetings"""
        print("⚠️  Testing error handling...")
        
        # Test with invalid meeting ID
        invalid_meeting_id = "invalid-meeting-id-12345"
        
        start_time = time.time()
        response = self.session.get(f"{BASE_URL}/meetings/{invalid_meeting_id}/report")
        response_time = time.time() - start_time
        
        if response.status_code == 404:
            self.log_result("Error Handling - Invalid Meeting", True, "404 returned for invalid meeting ID", response_time)
            return True
        else:
            self.log_result("Error Handling - Invalid Meeting", False, f"Expected 404, got HTTP {response.status_code}", response_time)
            return False

    def run_pdf_report_test(self):
        """Run the complete PDF report generation test"""
        print("🚀 Starting PDF Report Generation Test")
        print("=" * 60)
        
        # Setup phase
        if not self.setup_test_meeting():
            print("❌ Failed to create test meeting. Aborting test.")
            return False
        
        if not self.add_test_participants():
            print("❌ Failed to add test participants. Aborting test.")
            return False
        
        if not self.create_test_polls():
            print("❌ Failed to create test polls. Aborting test.")
            return False
        
        if not self.simulate_votes():
            print("❌ Failed to simulate votes. Aborting test.")
            return False
        
        print("\n" + "=" * 60)
        print("🎯 Running PDF Report Tests")
        print("=" * 60)
        
        # Main tests
        tests_passed = 0
        total_tests = 3
        
        if self.test_pdf_generation():
            tests_passed += 1
        
        if self.test_data_deletion():
            tests_passed += 1
        
        if self.test_error_handling():
            tests_passed += 1
        
        print("\n" + "=" * 60)
        print(f"🏁 PDF Report Test Results: {tests_passed}/{total_tests} tests passed")
        
        if tests_passed == total_tests:
            print("🎉 All PDF report tests passed! Functionality is working correctly.")
            return True
        else:
            print(f"⚠️  {total_tests - tests_passed} tests failed. PDF report functionality has issues.")
            return False

def main():
    """Main test execution"""
    tester = PDFReportTester()
    success = tester.run_pdf_report_test()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)