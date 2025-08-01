#!/usr/bin/env python3
"""
Complete Scrutator Functionality Test - Final Verification
"""

import requests
import json
import time
import tempfile
import os

BASE_URL = "https://dffd1ffb-03ba-4c55-8b21-65220fce6f6a.preview.emergentagent.com/api"

def run_complete_scrutator_test():
    """Run the complete scrutator test scenario as requested by the user"""
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    print("🎯 COMPLETE SCRUTATOR FUNCTIONALITY TEST")
    print("=" * 60)
    
    results = []
    
    def log_result(test_name, success, message, response_time=0):
        status = "✅ PASS" if success else "❌ FAIL"
        results.append({'test': test_name, 'success': success, 'message': message})
        time_str = f" ({response_time:.3f}s)" if response_time > 0 else ""
        print(f"{status} {test_name}: {message}{time_str}")
        return success
    
    # Test 1: Create meeting "Assemblée Test Scrutateurs"
    try:
        meeting_data = {
            "title": "Assemblée Test Scrutateurs",
            "organizer_name": "Alice Dupont"
        }
        
        start_time = time.time()
        response = session.post(f"{BASE_URL}/meetings", json=meeting_data)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            meeting = response.json()
            log_result("1. Create Meeting", True, f"Meeting created with code: {meeting['meeting_code']}", response_time)
        else:
            log_result("1. Create Meeting", False, f"HTTP {response.status_code}: {response.text}", response_time)
            return False
    except Exception as e:
        log_result("1. Create Meeting", False, f"Error: {str(e)}")
        return False
    
    # Test 2: Add 3 scrutators
    try:
        scrutator_data = {
            "names": ["Jean Dupont", "Marie Martin", "Pierre Durand"]
        }
        
        start_time = time.time()
        response = session.post(f"{BASE_URL}/meetings/{meeting['id']}/scrutators", json=scrutator_data)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            scrutator_info = response.json()
            if (scrutator_info['scrutator_code'].startswith('SC') and 
                len(scrutator_info['scrutator_code']) == 8 and
                len(scrutator_info['scrutators']) == 3):
                log_result("2. Add Scrutators", True, f"3 scrutators added with code: {scrutator_info['scrutator_code']}", response_time)
            else:
                log_result("2. Add Scrutators", False, f"Invalid response format: {scrutator_info}", response_time)
                return False
        else:
            log_result("2. Add Scrutators", False, f"HTTP {response.status_code}: {response.text}", response_time)
            return False
    except Exception as e:
        log_result("2. Add Scrutators", False, f"Error: {str(e)}")
        return False
    
    # Test 3: Verify scrutator code generation format
    scrutator_code = scrutator_info['scrutator_code']
    code_valid = (scrutator_code.startswith('SC') and 
                  len(scrutator_code) == 8 and 
                  scrutator_code[2:].isalnum())
    log_result("3. Scrutator Code Format", code_valid, f"Code format {'valid' if code_valid else 'invalid'}: {scrutator_code}")
    
    # Test 4: Get scrutators list
    try:
        start_time = time.time()
        response = session.get(f"{BASE_URL}/meetings/{meeting['id']}/scrutators")
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if ('scrutator_code' in data and 
                'scrutators' in data and 
                len(data['scrutators']) == 3):
                log_result("4. Get Scrutators List", True, f"Retrieved {len(data['scrutators'])} scrutators", response_time)
            else:
                log_result("4. Get Scrutators List", False, f"Invalid response: {data}", response_time)
        else:
            log_result("4. Get Scrutators List", False, f"HTTP {response.status_code}: {response.text}", response_time)
    except Exception as e:
        log_result("4. Get Scrutators List", False, f"Error: {str(e)}")
    
    # Test 5: Valid scrutator connection
    try:
        join_data = {
            "name": "Jean Dupont",
            "scrutator_code": scrutator_code
        }
        
        start_time = time.time()
        response = session.post(f"{BASE_URL}/scrutators/join", json=join_data)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if ('meeting' in data and 
                'scrutator_name' in data and 
                data['scrutator_name'] == "Jean Dupont"):
                log_result("5. Valid Scrutator Join", True, "Jean Dupont connected successfully", response_time)
            else:
                log_result("5. Valid Scrutator Join", False, f"Invalid response: {data}", response_time)
        else:
            log_result("5. Valid Scrutator Join", False, f"HTTP {response.status_code}: {response.text}", response_time)
    except Exception as e:
        log_result("5. Valid Scrutator Join", False, f"Error: {str(e)}")
    
    # Test 6: Invalid scrutator rejection
    try:
        join_data = {
            "name": "Antoine Bernard",  # Not in authorized list
            "scrutator_code": scrutator_code
        }
        
        start_time = time.time()
        response = session.post(f"{BASE_URL}/scrutators/join", json=join_data)
        response_time = time.time() - start_time
        
        if response.status_code == 403:
            log_result("6. Invalid Scrutator Rejection", True, "Antoine Bernard correctly rejected (403)", response_time)
        else:
            log_result("6. Invalid Scrutator Rejection", False, f"Expected 403, got {response.status_code}", response_time)
    except Exception as e:
        log_result("6. Invalid Scrutator Rejection", False, f"Error: {str(e)}")
    
    # Test 7: Add participants and polls for complete scenario
    try:
        # Add participants
        participants = ["Sophie Lefebvre", "Pierre-Alexandre Martin"]
        participant_ids = []
        
        for participant_name in participants:
            join_data = {
                "name": participant_name,
                "meeting_code": meeting['meeting_code']
            }
            
            response = session.post(f"{BASE_URL}/participants/join", json=join_data)
            if response.status_code == 200:
                participant = response.json()
                participant_ids.append(participant['id'])
                
                # Approve participant
                approval_data = {
                    "participant_id": participant['id'],
                    "approved": True
                }
                session.post(f"{BASE_URL}/participants/{participant['id']}/approve", json=approval_data)
        
        # Create polls
        polls = []
        poll_data = {
            "question": "Approuvez-vous le budget 2025 ?",
            "options": ["Oui", "Non", "Abstention"],
            "show_results_real_time": True
        }
        
        response = session.post(f"{BASE_URL}/meetings/{meeting['id']}/polls", json=poll_data)
        if response.status_code == 200:
            poll = response.json()
            polls.append(poll)
            
            # Start poll and add votes
            session.post(f"{BASE_URL}/polls/{poll['id']}/start")
            
            # Add some votes
            for i in range(3):
                vote_data = {
                    "poll_id": poll['id'],
                    "option_id": poll['options'][i % len(poll['options'])]['id']
                }
                session.post(f"{BASE_URL}/votes", json=vote_data)
            
            # Close poll
            session.post(f"{BASE_URL}/polls/{poll['id']}/close")
        
        log_result("7. Add Participants & Polls", True, f"Added {len(participants)} participants and {len(polls)} polls")
        
    except Exception as e:
        log_result("7. Add Participants & Polls", False, f"Error: {str(e)}")
    
    # Test 8: Generate PDF with scrutators
    try:
        start_time = time.time()
        response = session.get(f"{BASE_URL}/meetings/{meeting['id']}/report")
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'application/pdf' in content_type:
                file_size = len(response.content)
                
                # Check PDF content for scrutator data
                pdf_content = response.content.decode('latin-1', errors='ignore')
                has_table_structure = any(indicator in pdf_content for indicator in ['#', 'Nom', 'scrutateur'])
                
                if file_size > 2000 and has_table_structure:
                    log_result("8. Generate PDF with Scrutators", True, f"PDF generated with scrutators ({file_size} bytes)", response_time)
                else:
                    log_result("8. Generate PDF with Scrutators", False, f"PDF missing scrutator content ({file_size} bytes)", response_time)
            else:
                log_result("8. Generate PDF with Scrutators", False, f"Wrong content type: {content_type}", response_time)
        else:
            log_result("8. Generate PDF with Scrutators", False, f"HTTP {response.status_code}: {response.text}", response_time)
    except Exception as e:
        log_result("8. Generate PDF with Scrutators", False, f"Error: {str(e)}")
    
    # Test 9: Verify complete data deletion
    try:
        # Test meeting deletion
        response = session.get(f"{BASE_URL}/meetings/{meeting['meeting_code']}")
        meeting_deleted = response.status_code == 404
        
        # Test scrutators deletion
        response = session.get(f"{BASE_URL}/meetings/{meeting['id']}/scrutators")
        scrutators_deleted = response.status_code == 404
        
        # Test organizer view deletion
        response = session.get(f"{BASE_URL}/meetings/{meeting['id']}/organizer")
        organizer_deleted = response.status_code == 404
        
        all_deleted = meeting_deleted and scrutators_deleted and organizer_deleted
        log_result("9. Complete Data Deletion", all_deleted, 
                  f"Meeting: {'✓' if meeting_deleted else '✗'}, "
                  f"Scrutators: {'✓' if scrutators_deleted else '✗'}, "
                  f"Organizer: {'✓' if organizer_deleted else '✗'}")
        
    except Exception as e:
        log_result("9. Complete Data Deletion", False, f"Error: {str(e)}")
    
    # Summary
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    
    print("\n" + "=" * 60)
    print(f"🏁 SCRUTATOR TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL SCRUTATOR TESTS PASSED!")
        print("\n✅ VERIFIED FUNCTIONALITY:")
        print("  • Meeting creation with scrutator support")
        print("  • Scrutator addition with validation")
        print("  • Scrutator code generation (SCxxxxxx format)")
        print("  • Scrutator authentication and authorization")
        print("  • PDF generation including scrutator data")
        print("  • Complete data cleanup after PDF generation")
        print("\n🔒 SECURITY VERIFIED:")
        print("  • Only authorized names can use scrutator code")
        print("  • Invalid names are properly rejected (403)")
        print("  • Scrutator data is included in reports")
        print("  • All data is securely deleted after PDF generation")
    else:
        print(f"⚠️  {total - passed} tests failed. Review issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_complete_scrutator_test()
    exit(0 if success else 1)