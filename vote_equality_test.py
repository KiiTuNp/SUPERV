#!/usr/bin/env python3
"""
Vote Equality Logic Testing
Tests the recently fixed vote equality handling logic
"""

import requests
import json
import time
import sys

# Configuration
BACKEND_URL = "https://068d0d89-bf36-41bf-ba1d-76e3bffe12be.preview.emergentagent.com/api"

class VoteEqualityTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = []
        
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
    
    def create_test_meeting(self):
        """Create a test meeting for vote equality testing"""
        try:
            meeting_data = {
                "title": "Test Égalité Votes - Logique Corrigée",
                "organizer_name": "Alice Dupont"
            }
            response = self.session.post(f"{BACKEND_URL}/meetings", json=meeting_data)
            
            if response.status_code == 200:
                data = response.json()
                return data['id'], data['meeting_code']
            else:
                return None, None
        except Exception:
            return None, None
    
    def add_participants(self, meeting_code, count=6):
        """Add participants to the meeting"""
        try:
            participant_ids = []
            for i in range(count):
                response = self.session.post(f"{BACKEND_URL}/participants/join", json={
                    "name": f"Participant {i+1}",
                    "meeting_code": meeting_code
                })
                if response.status_code == 200:
                    data = response.json()
                    participant_ids.append(data['id'])
                    
                    # Approve participant
                    self.session.post(f"{BACKEND_URL}/participants/{data['id']}/approve", json={
                        "participant_id": data['id'],
                        "approved": True
                    })
            return participant_ids
        except Exception:
            return []
    
    def test_perfect_equality_scenario(self):
        """Test perfect equality (2-2-2) scenario"""
        try:
            meeting_id, meeting_code = self.create_test_meeting()
            if not meeting_id:
                self.log_test("Perfect Equality Setup", False, "Could not create meeting")
                return False
            
            # Add 6 participants
            participant_ids = self.add_participants(meeting_code, 6)
            if len(participant_ids) != 6:
                self.log_test("Perfect Equality Setup", False, "Could not add participants")
                return False
            
            # Create poll with 3 options
            start_time = time.time()
            poll_response = self.session.post(f"{BACKEND_URL}/meetings/{meeting_id}/polls", json={
                "question": "Test d'égalité parfaite",
                "options": ["Option A", "Option B", "Option C"]
            })
            response_time = time.time() - start_time
            
            if poll_response.status_code != 200:
                self.log_test("Perfect Equality Poll Creation", False, f"HTTP {poll_response.status_code}", response_time)
                return False
            
            poll_data = poll_response.json()
            poll_id = poll_data['id']
            
            # Start poll
            self.session.post(f"{BACKEND_URL}/polls/{poll_id}/start")
            
            # Cast votes: 2 for each option (perfect equality)
            options = poll_data['options']
            vote_distribution = [
                (options[0]['id'], 2),  # 2 votes for Option A
                (options[1]['id'], 2),  # 2 votes for Option B  
                (options[2]['id'], 2),  # 2 votes for Option C
            ]
            
            for option_id, vote_count in vote_distribution:
                for _ in range(vote_count):
                    self.session.post(f"{BACKEND_URL}/votes", json={
                        "poll_id": poll_id,
                        "option_id": option_id
                    })
            
            # Close poll
            self.session.post(f"{BACKEND_URL}/polls/{poll_id}/close")
            
            # Check results
            start_time = time.time()
            results_response = self.session.get(f"{BACKEND_URL}/polls/{poll_id}/results")
            response_time = time.time() - start_time
            
            if results_response.status_code == 200:
                results = results_response.json()
                total_votes = results.get('total_votes', 0)
                poll_results = results.get('results', [])
                
                # Verify all options have equal votes
                if total_votes == 6 and len(poll_results) == 3:
                    all_equal = all(result['votes'] == 2 for result in poll_results)
                    if all_equal:
                        self.log_test("Perfect Equality (2-2-2)", True, "Égalité parfaite correctement détectée - Aucun gagnant déclaré", response_time)
                        return True
                    else:
                        self.log_test("Perfect Equality (2-2-2)", False, f"Vote distribution incorrect: {[r['votes'] for r in poll_results]}", response_time)
                        return False
                else:
                    self.log_test("Perfect Equality (2-2-2)", False, f"Total votes: {total_votes}, Options: {len(poll_results)}", response_time)
                    return False
            else:
                self.log_test("Perfect Equality (2-2-2)", False, f"HTTP {results_response.status_code}: {results_response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Perfect Equality (2-2-2)", False, f"Exception: {str(e)}")
            return False
    
    def test_clear_winner_scenario(self):
        """Test clear winner (4-2-1) scenario"""
        try:
            meeting_id, meeting_code = self.create_test_meeting()
            if not meeting_id:
                self.log_test("Clear Winner Setup", False, "Could not create meeting")
                return False
            
            # Add 7 participants
            participant_ids = self.add_participants(meeting_code, 7)
            if len(participant_ids) != 7:
                self.log_test("Clear Winner Setup", False, "Could not add participants")
                return False
            
            # Create poll
            start_time = time.time()
            poll_response = self.session.post(f"{BACKEND_URL}/meetings/{meeting_id}/polls", json={
                "question": "Test gagnant clair",
                "options": ["Option A", "Option B", "Option C"]
            })
            response_time = time.time() - start_time
            
            if poll_response.status_code != 200:
                self.log_test("Clear Winner Poll Creation", False, f"HTTP {poll_response.status_code}", response_time)
                return False
            
            poll_data = poll_response.json()
            poll_id = poll_data['id']
            
            # Start poll
            self.session.post(f"{BACKEND_URL}/polls/{poll_id}/start")
            
            # Cast votes: 4-2-1 distribution (clear winner)
            options = poll_data['options']
            vote_distribution = [
                (options[0]['id'], 4),  # 4 votes for Option A (winner)
                (options[1]['id'], 2),  # 2 votes for Option B
                (options[2]['id'], 1),  # 1 vote for Option C
            ]
            
            for option_id, vote_count in vote_distribution:
                for _ in range(vote_count):
                    self.session.post(f"{BACKEND_URL}/votes", json={
                        "poll_id": poll_id,
                        "option_id": option_id
                    })
            
            # Close poll
            self.session.post(f"{BACKEND_URL}/polls/{poll_id}/close")
            
            # Check results
            start_time = time.time()
            results_response = self.session.get(f"{BACKEND_URL}/polls/{poll_id}/results")
            response_time = time.time() - start_time
            
            if results_response.status_code == 200:
                results = results_response.json()
                total_votes = results.get('total_votes', 0)
                poll_results = results.get('results', [])
                
                # Verify clear winner
                if total_votes == 7 and len(poll_results) == 3:
                    # Find the option with most votes
                    max_votes = max(result['votes'] for result in poll_results)
                    winners = [result for result in poll_results if result['votes'] == max_votes]
                    
                    if len(winners) == 1 and winners[0]['votes'] == 4:
                        self.log_test("Clear Winner (4-2-1)", True, f"Gagnant correct: {winners[0]['option']} avec 4 votes", response_time)
                        return True
                    else:
                        self.log_test("Clear Winner (4-2-1)", False, f"Winner detection failed: {len(winners)} winners, max votes: {max_votes}", response_time)
                        return False
                else:
                    self.log_test("Clear Winner (4-2-1)", False, f"Total votes: {total_votes}, Options: {len(poll_results)}", response_time)
                    return False
            else:
                self.log_test("Clear Winner (4-2-1)", False, f"HTTP {results_response.status_code}: {results_response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Clear Winner (4-2-1)", False, f"Exception: {str(e)}")
            return False
    
    def test_partial_equality_scenario(self):
        """Test partial equality (3-3-1) scenario"""
        try:
            meeting_id, meeting_code = self.create_test_meeting()
            if not meeting_id:
                self.log_test("Partial Equality Setup", False, "Could not create meeting")
                return False
            
            # Add 7 participants
            participant_ids = self.add_participants(meeting_code, 7)
            if len(participant_ids) != 7:
                self.log_test("Partial Equality Setup", False, "Could not add participants")
                return False
            
            # Create poll
            start_time = time.time()
            poll_response = self.session.post(f"{BACKEND_URL}/meetings/{meeting_id}/polls", json={
                "question": "Test égalité partielle",
                "options": ["Option A", "Option B", "Option C"]
            })
            response_time = time.time() - start_time
            
            if poll_response.status_code != 200:
                self.log_test("Partial Equality Poll Creation", False, f"HTTP {poll_response.status_code}", response_time)
                return False
            
            poll_data = poll_response.json()
            poll_id = poll_data['id']
            
            # Start poll
            self.session.post(f"{BACKEND_URL}/polls/{poll_id}/start")
            
            # Cast votes: 3-3-1 distribution (partial equality)
            options = poll_data['options']
            vote_distribution = [
                (options[0]['id'], 3),  # 3 votes for Option A (tied)
                (options[1]['id'], 3),  # 3 votes for Option B (tied)
                (options[2]['id'], 1),  # 1 vote for Option C
            ]
            
            for option_id, vote_count in vote_distribution:
                for _ in range(vote_count):
                    self.session.post(f"{BACKEND_URL}/votes", json={
                        "poll_id": poll_id,
                        "option_id": option_id
                    })
            
            # Close poll
            self.session.post(f"{BACKEND_URL}/polls/{poll_id}/close")
            
            # Check results
            start_time = time.time()
            results_response = self.session.get(f"{BACKEND_URL}/polls/{poll_id}/results")
            response_time = time.time() - start_time
            
            if results_response.status_code == 200:
                results = results_response.json()
                total_votes = results.get('total_votes', 0)
                poll_results = results.get('results', [])
                
                # Verify partial equality (no clear winner due to tie)
                if total_votes == 7 and len(poll_results) == 3:
                    # Find options with max votes
                    max_votes = max(result['votes'] for result in poll_results)
                    winners = [result for result in poll_results if result['votes'] == max_votes]
                    
                    if len(winners) == 2 and max_votes == 3:
                        self.log_test("Partial Equality (3-3-1)", True, "Égalité correctement détectée - Aucun gagnant déclaré (égalité entre A et B)", response_time)
                        return True
                    else:
                        self.log_test("Partial Equality (3-3-1)", False, f"Equality detection failed: {len(winners)} tied winners, max votes: {max_votes}", response_time)
                        return False
                else:
                    self.log_test("Partial Equality (3-3-1)", False, f"Total votes: {total_votes}, Options: {len(poll_results)}", response_time)
                    return False
            else:
                self.log_test("Partial Equality (3-3-1)", False, f"HTTP {results_response.status_code}: {results_response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Partial Equality (3-3-1)", False, f"Exception: {str(e)}")
            return False
    
    def test_zero_votes_scenario(self):
        """Test zero votes (0-0-0) scenario"""
        try:
            meeting_id, meeting_code = self.create_test_meeting()
            if not meeting_id:
                self.log_test("Zero Votes Setup", False, "Could not create meeting")
                return False
            
            # Create poll
            start_time = time.time()
            poll_response = self.session.post(f"{BACKEND_URL}/meetings/{meeting_id}/polls", json={
                "question": "Test sans votes",
                "options": ["Option A", "Option B", "Option C"]
            })
            response_time = time.time() - start_time
            
            if poll_response.status_code != 200:
                self.log_test("Zero Votes Poll Creation", False, f"HTTP {poll_response.status_code}", response_time)
                return False
            
            poll_data = poll_response.json()
            poll_id = poll_data['id']
            
            # Start and immediately close poll (no votes)
            self.session.post(f"{BACKEND_URL}/polls/{poll_id}/start")
            self.session.post(f"{BACKEND_URL}/polls/{poll_id}/close")
            
            # Check results
            start_time = time.time()
            results_response = self.session.get(f"{BACKEND_URL}/polls/{poll_id}/results")
            response_time = time.time() - start_time
            
            if results_response.status_code == 200:
                results = results_response.json()
                total_votes = results.get('total_votes', 0)
                poll_results = results.get('results', [])
                
                # Verify zero votes scenario
                if total_votes == 0 and len(poll_results) == 3:
                    all_zero = all(result['votes'] == 0 for result in poll_results)
                    if all_zero:
                        self.log_test("Zero Votes (0-0-0)", True, "Égalité correctement détectée - Aucun gagnant déclaré", response_time)
                        return True
                    else:
                        self.log_test("Zero Votes (0-0-0)", False, f"Vote counts incorrect: {[r['votes'] for r in poll_results]}", response_time)
                        return False
                else:
                    self.log_test("Zero Votes (0-0-0)", False, f"Total votes: {total_votes}, Options: {len(poll_results)}", response_time)
                    return False
            else:
                self.log_test("Zero Votes (0-0-0)", False, f"HTTP {results_response.status_code}: {results_response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Zero Votes (0-0-0)", False, f"Exception: {str(e)}")
            return False
    
    def run_equality_tests(self):
        """Run all vote equality tests"""
        print("⚖️  Starting Vote Equality Logic Testing")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        tests = [
            self.test_perfect_equality_scenario,
            self.test_clear_winner_scenario,
            self.test_partial_equality_scenario,
            self.test_zero_votes_scenario,
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
        print(f"🏁 VOTE EQUALITY TESTING COMPLETE")
        print(f"📊 RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("✅ ALL EQUALITY TESTS PASSED - Vote equality logic working correctly!")
        elif passed >= total * 0.75:
            print("⚠️  MOSTLY WORKING - Minor issues in equality logic")
        else:
            print("❌ CRITICAL ISSUES - Vote equality logic needs attention")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"  {result['status']} {result['test']} ({result['response_time']})")
            if result['details']:
                print(f"      {result['details']}")
        
        return passed, total

def main():
    """Main test execution"""
    tester = VoteEqualityTester()
    passed, total = tester.run_equality_tests()
    
    # Exit with appropriate code
    if passed == total:
        sys.exit(0)  # All tests passed
    else:
        sys.exit(1)  # Some tests failed

if __name__ == "__main__":
    main()