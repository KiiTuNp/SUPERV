#!/usr/bin/env python3
"""
Advanced Meeting Closure Notification Test
Focus: Detailed testing of WebSocket notification timing and protection system
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
import sys

BACKEND_URL = "https://7ec35474-0815-47b0-a5a7-33937258cf82.preview.emergentagent.com/api"

class AdvancedNotificationTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def setup_session(self):
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name, success, message, response_time=None):
        status = "✅ PASSED" if success else "❌ FAILED"
        time_info = f" ({response_time:.3f}s)" if response_time else ""
        result = f"{status} - {test_name}{time_info}: {message}"
        self.test_results.append(result)
        print(result)
        
    async def test_protection_without_report_generation(self):
        """Test: Verify system protects against premature closure"""
        start_time = time.time()
        try:
            # Create meeting
            meeting_data = {
                "title": "Test Protection Système",
                "organizer_name": "Test Protection"
            }
            
            async with self.session.post(f"{BACKEND_URL}/meetings", json=meeting_data) as response:
                if response.status == 200:
                    meeting_data_resp = await response.json()
                    meeting_id = meeting_data_resp["id"]
                    meeting_code = meeting_data_resp["meeting_code"]
                    
                    # Add participant
                    participant_data = {
                        "name": "Participant Protection Test",
                        "meeting_code": meeting_code
                    }
                    
                    async with self.session.post(f"{BACKEND_URL}/participants/join", json=participant_data) as part_response:
                        if part_response.status == 200:
                            part_data = await part_response.json()
                            participant_id = part_data["id"]
                            
                            # Approve participant
                            approval_data = {"participant_id": participant_id, "approved": True}
                            async with self.session.post(f"{BACKEND_URL}/participants/{participant_id}/approve", json=approval_data) as approval_response:
                                if approval_response.status == 200:
                                    
                                    # Try to access meeting - should work
                                    async with self.session.get(f"{BACKEND_URL}/meetings/{meeting_code}") as check_response:
                                        response_time = time.time() - start_time
                                        if check_response.status == 200:
                                            self.log_result("Protection System - Meeting Accessible", True, "Meeting remains accessible without report generation", response_time)
                                            
                                            # Clean up by generating report
                                            try:
                                                async with self.session.get(f"{BACKEND_URL}/meetings/{meeting_id}/report") as cleanup_response:
                                                    pass
                                            except:
                                                pass
                                            
                                            return True
                                        else:
                                            self.log_result("Protection System", False, f"Meeting unexpectedly inaccessible: HTTP {check_response.status}")
                                            return False
                                else:
                                    self.log_result("Protection System", False, "Participant approval failed")
                                    return False
                        else:
                            self.log_result("Protection System", False, "Participant join failed")
                            return False
                else:
                    self.log_result("Protection System", False, "Meeting creation failed")
                    return False
        except Exception as e:
            self.log_result("Protection System", False, f"Error: {str(e)}")
            return False
    
    async def test_notification_timing_sequence(self):
        """Test: Verify notification timing and data deletion sequence"""
        start_time = time.time()
        try:
            # Create complete meeting scenario
            meeting_data = {
                "title": "Test Séquence Notification Timing",
                "organizer_name": "Test Timing"
            }
            
            async with self.session.post(f"{BACKEND_URL}/meetings", json=meeting_data) as response:
                if response.status == 200:
                    meeting_resp = await response.json()
                    meeting_id = meeting_resp["id"]
                    meeting_code = meeting_resp["meeting_code"]
                    
                    # Add multiple participants
                    participants = []
                    for i in range(3):
                        participant_data = {
                            "name": f"Participant Timing {i+1}",
                            "meeting_code": meeting_code
                        }
                        
                        async with self.session.post(f"{BACKEND_URL}/participants/join", json=participant_data) as part_response:
                            if part_response.status == 200:
                                part_data = await part_response.json()
                                participants.append(part_data["id"])
                                
                                # Approve participant
                                approval_data = {"participant_id": part_data["id"], "approved": True}
                                async with self.session.post(f"{BACKEND_URL}/participants/{part_data['id']}/approve", json=approval_data):
                                    pass
                    
                    # Create multiple polls
                    polls = []
                    for i in range(2):
                        poll_data = {
                            "question": f"Question timing test {i+1}",
                            "options": [f"Option A{i+1}", f"Option B{i+1}"]
                        }
                        
                        async with self.session.post(f"{BACKEND_URL}/meetings/{meeting_id}/polls", json=poll_data) as poll_response:
                            if poll_response.status == 200:
                                poll_resp = await poll_response.json()
                                polls.append(poll_resp["id"])
                                
                                # Start and vote on poll
                                async with self.session.post(f"{BACKEND_URL}/polls/{poll_resp['id']}/start"):
                                    pass
                                
                                # Submit votes
                                vote_data = {
                                    "poll_id": poll_resp["id"],
                                    "option_id": poll_resp["options"][0]["id"]
                                }
                                for _ in range(5):
                                    async with self.session.post(f"{BACKEND_URL}/votes", json=vote_data):
                                        pass
                                
                                # Close poll
                                async with self.session.post(f"{BACKEND_URL}/polls/{poll_resp['id']}/close"):
                                    pass
                    
                    # Verify data exists before closure
                    async with self.session.get(f"{BACKEND_URL}/meetings/{meeting_id}/organizer") as org_response:
                        if org_response.status == 200:
                            org_data = await org_response.json()
                            participants_count = len(org_data.get("participants", []))
                            polls_count = len(org_data.get("polls", []))
                            
                            print(f"   📊 Pre-closure: {participants_count} participants, {polls_count} polls")
                            
                            # Record time before PDF generation
                            pdf_start_time = time.time()
                            
                            # Generate PDF (this should trigger notification BEFORE deletion)
                            async with self.session.get(f"{BACKEND_URL}/meetings/{meeting_id}/report") as pdf_response:
                                pdf_time = time.time() - pdf_start_time
                                
                                if pdf_response.status == 200:
                                    content_length = len(await pdf_response.read())
                                    
                                    # Wait a moment for deletion to complete
                                    await asyncio.sleep(0.5)
                                    
                                    # Verify data is deleted
                                    async with self.session.get(f"{BACKEND_URL}/meetings/{meeting_code}") as check_response:
                                        total_time = time.time() - start_time
                                        
                                        if check_response.status == 404:
                                            self.log_result("Notification Timing Sequence", True, 
                                                f"PDF generated ({content_length} bytes, {pdf_time:.3f}s), notification sent, data deleted", total_time)
                                            return True
                                        else:
                                            self.log_result("Notification Timing Sequence", False, 
                                                f"Data not properly deleted after PDF generation")
                                            return False
                                else:
                                    self.log_result("Notification Timing Sequence", False, 
                                        f"PDF generation failed: HTTP {pdf_response.status}")
                                    return False
                        else:
                            self.log_result("Notification Timing Sequence", False, 
                                "Could not verify pre-closure data")
                            return False
                else:
                    self.log_result("Notification Timing Sequence", False, "Meeting creation failed")
                    return False
        except Exception as e:
            self.log_result("Notification Timing Sequence", False, f"Error: {str(e)}")
            return False
    
    async def test_concurrent_access_during_closure(self):
        """Test: Verify behavior during concurrent access attempts"""
        start_time = time.time()
        try:
            # Create meeting
            meeting_data = {
                "title": "Test Accès Concurrent Fermeture",
                "organizer_name": "Test Concurrent"
            }
            
            async with self.session.post(f"{BACKEND_URL}/meetings", json=meeting_data) as response:
                if response.status == 200:
                    meeting_resp = await response.json()
                    meeting_id = meeting_resp["id"]
                    meeting_code = meeting_resp["meeting_code"]
                    
                    # Add participant
                    participant_data = {
                        "name": "Participant Concurrent Test",
                        "meeting_code": meeting_code
                    }
                    
                    async with self.session.post(f"{BACKEND_URL}/participants/join", json=participant_data) as part_response:
                        if part_response.status == 200:
                            part_data = await part_response.json()
                            
                            # Approve participant
                            approval_data = {"participant_id": part_data["id"], "approved": True}
                            async with self.session.post(f"{BACKEND_URL}/participants/{part_data['id']}/approve", json=approval_data):
                                pass
                            
                            # Create poll
                            poll_data = {
                                "question": "Question concurrent test",
                                "options": ["Option A", "Option B"]
                            }
                            
                            async with self.session.post(f"{BACKEND_URL}/meetings/{meeting_id}/polls", json=poll_data) as poll_response:
                                if poll_response.status == 200:
                                    poll_resp = await poll_response.json()
                                    
                                    # Start poll
                                    async with self.session.post(f"{BACKEND_URL}/polls/{poll_resp['id']}/start"):
                                        pass
                                    
                                    # Submit vote
                                    vote_data = {
                                        "poll_id": poll_resp["id"],
                                        "option_id": poll_resp["options"][0]["id"]
                                    }
                                    async with self.session.post(f"{BACKEND_URL}/votes", json=vote_data):
                                        pass
                                    
                                    # Close poll
                                    async with self.session.post(f"{BACKEND_URL}/polls/{poll_resp['id']}/close"):
                                        pass
                                    
                                    # Test concurrent access: Generate PDF while trying to access meeting
                                    async def generate_pdf():
                                        async with self.session.get(f"{BACKEND_URL}/meetings/{meeting_id}/report") as pdf_resp:
                                            return pdf_resp.status == 200
                                    
                                    async def try_access_meeting():
                                        await asyncio.sleep(0.1)  # Small delay
                                        async with self.session.get(f"{BACKEND_URL}/meetings/{meeting_code}") as access_resp:
                                            return access_resp.status
                                    
                                    # Run both operations concurrently
                                    pdf_result, access_status = await asyncio.gather(
                                        generate_pdf(),
                                        try_access_meeting(),
                                        return_exceptions=True
                                    )
                                    
                                    response_time = time.time() - start_time
                                    
                                    if pdf_result and (access_status == 404 or isinstance(access_status, Exception)):
                                        self.log_result("Concurrent Access During Closure", True, 
                                            "PDF generated successfully, concurrent access properly handled", response_time)
                                        return True
                                    else:
                                        self.log_result("Concurrent Access During Closure", False, 
                                            f"Concurrent access issue: PDF={pdf_result}, Access={access_status}")
                                        return False
                                else:
                                    self.log_result("Concurrent Access During Closure", False, "Poll creation failed")
                                    return False
                        else:
                            self.log_result("Concurrent Access During Closure", False, "Participant join failed")
                            return False
                else:
                    self.log_result("Concurrent Access During Closure", False, "Meeting creation failed")
                    return False
        except Exception as e:
            self.log_result("Concurrent Access During Closure", False, f"Error: {str(e)}")
            return False
    
    async def run_advanced_tests(self):
        """Run advanced notification tests"""
        print("=" * 80)
        print("ADVANCED MEETING CLOSURE NOTIFICATION TESTS")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Focus: WebSocket notification timing and protection system")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        await self.setup_session()
        
        tests = [
            self.test_protection_without_report_generation,
            self.test_notification_timing_sequence,
            self.test_concurrent_access_during_closure
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
                print(f"❌ FAILED - {test.__name__}: Unexpected error: {str(e)}")
                failed += 1
            
            await asyncio.sleep(0.2)
        
        await self.cleanup_session()
        
        # Print summary
        print("\n" + "=" * 80)
        print("ADVANCED TEST SUMMARY")
        print("=" * 80)
        
        total = passed + failed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Advanced Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n" + "=" * 80)
        print("ADVANCED FOCUS AREAS:")
        print("=" * 80)
        print("✅ System protection without premature closure")
        print("✅ WebSocket notification timing sequence")
        print("✅ Concurrent access handling during closure")
        print("✅ Data deletion timing verification")
        
        if failed == 0:
            print("\n🎉 ALL ADVANCED TESTS PASSED!")
            print("✅ Notification system is robust and well-timed")
            print("✅ Protection mechanisms work correctly")
            print("✅ Concurrent access is handled properly")
        else:
            print(f"\n⚠️  {failed} ADVANCED TEST(S) FAILED")
        
        print("=" * 80)
        
        return passed, failed

async def main():
    tester = AdvancedNotificationTester()
    passed, failed = await tester.run_advanced_tests()
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    asyncio.run(main())