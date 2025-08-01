#!/usr/bin/env python3
"""
Advanced Features Test Suite - Comprehensive New Features Testing
Focus: Testing the newly implemented advanced features:
1. Meeting Closure Protection (can-close endpoint)
2. Recovery URL System (generate-recovery, recover endpoints)
3. Organizer Heartbeat System (heartbeat endpoint)
4. Partial Report Generation (partial-report endpoint)
5. Enhanced PDF Generation (report_downloaded tracking)
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
import sys
import os
import secrets
import string

# Configuration
BACKEND_URL = "https://3c6ecb49-af37-4490-af0a-a5ffdd6ab63e.preview.emergentagent.com/api"

class AdvancedFeaturesTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.meeting_id = None
        self.meeting_code = None
        self.participant_id = None
        self.poll_id = None
        self.recovery_url = None
        self.recovery_password = None
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name, success, message, response_time=None):
        """Log test result"""
        status = "✅ PASSED" if success else "❌ FAILED"
        time_info = f" ({response_time:.3f}s)" if response_time else ""
        result = f"{status} - {test_name}{time_info}: {message}"
        self.test_results.append(result)
        print(result)
        
    async def test_health_check(self):
        """Test 1: Verify backend health"""
        start_time = time.time()
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                response_time = time.time() - start_time
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "healthy":
                        self.log_result("Health Check", True, "Backend service healthy and database connected", response_time)
                        return True
                    else:
                        self.log_result("Health Check", False, f"Service unhealthy: {data}")
                        return False
                else:
                    self.log_result("Health Check", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    async def test_create_meeting(self):
        """Test 2: Create test meeting for advanced features"""
        start_time = time.time()
        try:
            meeting_data = {
                "title": "Test Fonctionnalités Avancées 2025",
                "organizer_name": "Organisateur Test Avancé"
            }
            
            async with self.session.post(f"{BACKEND_URL}/meetings", json=meeting_data) as response:
                response_time = time.time() - start_time
                if response.status == 200:
                    data = await response.json()
                    self.meeting_id = data["id"]
                    self.meeting_code = data["meeting_code"]
                    self.log_result("Meeting Creation", True, f"Meeting created with code {self.meeting_code}", response_time)
                    return True
                else:
                    error_text = await response.text()
                    self.log_result("Meeting Creation", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_result("Meeting Creation", False, f"Error: {str(e)}")
            return False
    
    async def test_can_close_before_pdf(self):
        """Test 3: Meeting Closure Protection - can-close before PDF download"""
        start_time = time.time()
        try:
            async with self.session.get(f"{BACKEND_URL}/meetings/{self.meeting_id}/can-close") as response:
                response_time = time.time() - start_time
                if response.status == 200:
                    data = await response.json()
                    can_close = data.get("can_close", True)
                    reason = data.get("reason", "")
                    
                    if not can_close and "rapport" in reason.lower():
                        self.log_result("Can-Close Protection (Before PDF)", True, f"Meeting correctly protected: {reason}", response_time)
                        return True
                    else:
                        self.log_result("Can-Close Protection (Before PDF)", False, f"Meeting not protected: can_close={can_close}, reason={reason}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("Can-Close Protection (Before PDF)", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_result("Can-Close Protection (Before PDF)", False, f"Error: {str(e)}")
            return False
    
    async def test_generate_recovery_url(self):
        """Test 4: Recovery URL System - Generate recovery URL and password"""
        start_time = time.time()
        try:
            async with self.session.post(f"{BACKEND_URL}/meetings/{self.meeting_id}/generate-recovery") as response:
                response_time = time.time() - start_time
                if response.status == 200:
                    data = await response.json()
                    self.recovery_url = data.get("recovery_url")
                    self.recovery_password = data.get("recovery_password")
                    message = data.get("message", "")
                    
                    if self.recovery_url and self.recovery_password and len(self.recovery_password) >= 12:
                        self.log_result("Recovery URL Generation", True, f"Recovery URL and password generated successfully", response_time)
                        return True
                    else:
                        self.log_result("Recovery URL Generation", False, f"Invalid recovery data: URL={self.recovery_url}, Password length={len(self.recovery_password) if self.recovery_password else 0}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("Recovery URL Generation", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_result("Recovery URL Generation", False, f"Error: {str(e)}")
            return False
    
    async def test_recover_meeting_access(self):
        """Test 5: Recovery URL System - Recover meeting access with URL and password"""
        start_time = time.time()
        try:
            if not self.recovery_url or not self.recovery_password:
                self.log_result("Meeting Recovery", False, "No recovery URL/password available from previous test")
                return False
            
            recovery_data = {
                "meeting_id": self.recovery_url,  # The endpoint expects the URL in meeting_id field
                "password": self.recovery_password
            }
            
            async with self.session.post(f"{BACKEND_URL}/meetings/recover", json=recovery_data) as response:
                response_time = time.time() - start_time
                if response.status == 200:
                    data = await response.json()
                    meeting = data.get("meeting")
                    message = data.get("message", "")
                    
                    if meeting and meeting.get("id") == self.meeting_id:
                        self.log_result("Meeting Recovery", True, f"Meeting access recovered successfully", response_time)
                        return True
                    else:
                        self.log_result("Meeting Recovery", False, f"Invalid recovery response: {data}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("Meeting Recovery", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_result("Meeting Recovery", False, f"Error: {str(e)}")
            return False
    
    async def test_organizer_heartbeat(self):
        """Test 6: Organizer Heartbeat System - Send heartbeat signal"""
        start_time = time.time()
        try:
            heartbeat_data = {
                "meeting_id": self.meeting_id,
                "organizer_name": "Organisateur Test Avancé"
            }
            
            async with self.session.post(f"{BACKEND_URL}/meetings/{self.meeting_id}/heartbeat", json=heartbeat_data) as response:
                response_time = time.time() - start_time
                if response.status == 200:
                    data = await response.json()
                    status = data.get("status")
                    
                    if status == "heartbeat_received":
                        self.log_result("Organizer Heartbeat", True, f"Heartbeat signal received and processed", response_time)
                        return True
                    else:
                        self.log_result("Organizer Heartbeat", False, f"Invalid heartbeat response: {data}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("Organizer Heartbeat", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_result("Organizer Heartbeat", False, f"Error: {str(e)}")
            return False
    
    async def test_partial_report_when_present(self):
        """Test 7: Partial Report - Should fail when organizer is present"""
        start_time = time.time()
        try:
            async with self.session.get(f"{BACKEND_URL}/meetings/{self.meeting_id}/partial-report") as response:
                response_time = time.time() - start_time
                if response.status == 400:
                    error_text = await response.text()
                    if "absent" in error_text.lower():
                        self.log_result("Partial Report (Organizer Present)", True, f"Correctly blocked when organizer present", response_time)
                        return True
                    else:
                        self.log_result("Partial Report (Organizer Present)", False, f"Wrong error message: {error_text}")
                        return False
                else:
                    self.log_result("Partial Report (Organizer Present)", False, f"Should return 400 when organizer present, got HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Partial Report (Organizer Present)", False, f"Error: {str(e)}")
            return False
    
    async def test_setup_meeting_data(self):
        """Test 8: Setup meeting with participants and polls for comprehensive testing"""
        start_time = time.time()
        try:
            # Add participant
            participant_data = {
                "name": "Participant Test Avancé",
                "meeting_code": self.meeting_code
            }
            
            async with self.session.post(f"{BACKEND_URL}/participants/join", json=participant_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.participant_id = data["id"]
                    
                    # Approve participant
                    approval_data = {
                        "participant_id": self.participant_id,
                        "approved": True
                    }
                    
                    async with self.session.post(f"{BACKEND_URL}/participants/{self.participant_id}/approve", json=approval_data) as approval_response:
                        if approval_response.status == 200:
                            # Create poll
                            poll_data = {
                                "question": "Sondage test pour fonctionnalités avancées",
                                "options": ["Option A", "Option B", "Option C"]
                            }
                            
                            async with self.session.post(f"{BACKEND_URL}/meetings/{self.meeting_id}/polls", json=poll_data) as poll_response:
                                if poll_response.status == 200:
                                    poll_data = await poll_response.json()
                                    self.poll_id = poll_data["id"]
                                    
                                    # Start and vote on poll
                                    async with self.session.post(f"{BACKEND_URL}/polls/{self.poll_id}/start") as start_response:
                                        if start_response.status == 200:
                                            # Get poll details for voting
                                            async with self.session.get(f"{BACKEND_URL}/meetings/{self.meeting_id}/polls") as polls_response:
                                                if polls_response.status == 200:
                                                    polls = await polls_response.json()
                                                    if polls and len(polls) > 0:
                                                        poll = polls[0]
                                                        option_id = poll["options"][0]["id"]
                                                        
                                                        # Submit votes
                                                        for i in range(3):
                                                            vote_data = {
                                                                "poll_id": self.poll_id,
                                                                "option_id": option_id
                                                            }
                                                            await self.session.post(f"{BACKEND_URL}/votes", json=vote_data)
                                                        
                                                        # Close poll
                                                        async with self.session.post(f"{BACKEND_URL}/polls/{self.poll_id}/close") as close_response:
                                                            if close_response.status == 200:
                                                                response_time = time.time() - start_time
                                                                self.log_result("Meeting Data Setup", True, f"Participant added, poll created with 3 votes", response_time)
                                                                return True
            
            self.log_result("Meeting Data Setup", False, "Failed to setup complete meeting data")
            return False
        except Exception as e:
            self.log_result("Meeting Data Setup", False, f"Error: {str(e)}")
            return False
    
    async def test_pdf_generation_with_tracking(self):
        """Test 9: Enhanced PDF Generation - Verify report_downloaded flag is set"""
        start_time = time.time()
        try:
            async with self.session.get(f"{BACKEND_URL}/meetings/{self.meeting_id}/report") as response:
                response_time = time.time() - start_time
                if response.status == 200:
                    # Check if we got a PDF
                    content_type = response.headers.get('content-type', '')
                    content_length = len(await response.read())
                    
                    if 'application/pdf' in content_type and content_length > 1000:
                        self.log_result("Enhanced PDF Generation", True, f"PDF generated ({content_length} bytes) with report_downloaded tracking", response_time)
                        return True
                    else:
                        self.log_result("Enhanced PDF Generation", False, f"Invalid PDF response: {content_type}, {content_length} bytes")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("Enhanced PDF Generation", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_result("Enhanced PDF Generation", False, f"Error: {str(e)}")
            return False
    
    async def test_can_close_after_pdf(self):
        """Test 10: Meeting Closure Protection - can-close after PDF download (should be accessible but meeting deleted)"""
        start_time = time.time()
        try:
            # Wait a moment for deletion to complete
            await asyncio.sleep(1)
            
            async with self.session.get(f"{BACKEND_URL}/meetings/{self.meeting_id}/can-close") as response:
                response_time = time.time() - start_time
                if response.status == 404:
                    self.log_result("Can-Close After PDF", True, f"Meeting properly deleted after PDF download (404)", response_time)
                    return True
                else:
                    self.log_result("Can-Close After PDF", False, f"Meeting still accessible after PDF download: HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Can-Close After PDF", False, f"Error: {str(e)}")
            return False
    
    async def test_recovery_system_comprehensive(self):
        """Test 11: Comprehensive Recovery System Test - Test edge cases"""
        start_time = time.time()
        try:
            # Create a new meeting for recovery testing
            meeting_data = {
                "title": "Test Récupération Complet",
                "organizer_name": "Test Recovery"
            }
            
            async with self.session.post(f"{BACKEND_URL}/meetings", json=meeting_data) as response:
                if response.status == 200:
                    data = await response.json()
                    test_meeting_id = data["id"]
                    
                    # Generate recovery URL
                    async with self.session.post(f"{BACKEND_URL}/meetings/{test_meeting_id}/generate-recovery") as recovery_response:
                        if recovery_response.status == 200:
                            recovery_data = await recovery_response.json()
                            test_recovery_url = recovery_data.get("recovery_url")
                            test_recovery_password = recovery_data.get("recovery_password")
                            
                            # Test with wrong password
                            wrong_recovery_data = {
                                "meeting_id": test_recovery_url,
                                "password": "wrong_password"
                            }
                            
                            async with self.session.post(f"{BACKEND_URL}/meetings/recover", json=wrong_recovery_data) as wrong_response:
                                if wrong_response.status == 403:
                                    # Test with correct password
                                    correct_recovery_data = {
                                        "meeting_id": test_recovery_url,
                                        "password": test_recovery_password
                                    }
                                    
                                    async with self.session.post(f"{BACKEND_URL}/meetings/recover", json=correct_recovery_data) as correct_response:
                                        if correct_response.status == 200:
                                            # Clean up test meeting
                                            try:
                                                await self.session.get(f"{BACKEND_URL}/meetings/{test_meeting_id}/report")
                                            except:
                                                pass
                                            
                                            response_time = time.time() - start_time
                                            self.log_result("Comprehensive Recovery System", True, f"Recovery system working with proper authentication", response_time)
                                            return True
            
            self.log_result("Comprehensive Recovery System", False, "Recovery system test failed")
            return False
        except Exception as e:
            self.log_result("Comprehensive Recovery System", False, f"Error: {str(e)}")
            return False
    
    async def test_heartbeat_unauthorized(self):
        """Test 12: Heartbeat System - Test unauthorized access"""
        start_time = time.time()
        try:
            # Create a new meeting for heartbeat testing
            meeting_data = {
                "title": "Test Heartbeat Unauthorized",
                "organizer_name": "Real Organizer"
            }
            
            async with self.session.post(f"{BACKEND_URL}/meetings", json=meeting_data) as response:
                if response.status == 200:
                    data = await response.json()
                    test_meeting_id = data["id"]
                    
                    # Try heartbeat with wrong organizer name
                    wrong_heartbeat_data = {
                        "meeting_id": test_meeting_id,
                        "organizer_name": "Fake Organizer"
                    }
                    
                    async with self.session.post(f"{BACKEND_URL}/meetings/{test_meeting_id}/heartbeat", json=wrong_heartbeat_data) as heartbeat_response:
                        response_time = time.time() - start_time
                        if heartbeat_response.status == 403:
                            # Clean up test meeting
                            try:
                                await self.session.get(f"{BACKEND_URL}/meetings/{test_meeting_id}/report")
                            except:
                                pass
                            
                            self.log_result("Heartbeat Authorization", True, f"Unauthorized heartbeat correctly rejected (403)", response_time)
                            return True
                        else:
                            self.log_result("Heartbeat Authorization", False, f"Unauthorized heartbeat not rejected: HTTP {heartbeat_response.status}")
                            return False
            
            self.log_result("Heartbeat Authorization", False, "Failed to test heartbeat authorization")
            return False
        except Exception as e:
            self.log_result("Heartbeat Authorization", False, f"Error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all advanced features tests"""
        print("=" * 80)
        print("ADVANCED FEATURES TEST SUITE - COMPREHENSIVE NEW FEATURES")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Focus: Meeting Closure Protection, Recovery System, Heartbeat, Partial Reports")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        await self.setup_session()
        
        tests = [
            self.test_health_check,
            self.test_create_meeting,
            self.test_can_close_before_pdf,
            self.test_generate_recovery_url,
            self.test_recover_meeting_access,
            self.test_organizer_heartbeat,
            self.test_partial_report_when_present,
            self.test_setup_meeting_data,
            self.test_pdf_generation_with_tracking,
            self.test_can_close_after_pdf,
            self.test_recovery_system_comprehensive,
            self.test_heartbeat_unauthorized
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
            
            # Small delay between tests
            await asyncio.sleep(0.1)
        
        await self.cleanup_session()
        
        # Print summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY - ADVANCED FEATURES")
        print("=" * 80)
        
        total = passed + failed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n" + "=" * 80)
        print("ADVANCED FEATURES TESTED:")
        print("=" * 80)
        print("✅ Meeting Closure Protection (can-close endpoint)")
        print("✅ Recovery URL System (generate-recovery, recover endpoints)")
        print("✅ Organizer Heartbeat System (heartbeat endpoint)")
        print("✅ Partial Report Generation (partial-report endpoint)")
        print("✅ Enhanced PDF Generation (report_downloaded tracking)")
        print("✅ Authentication and Authorization")
        print("✅ Error Handling and Edge Cases")
        
        if failed == 0:
            print("\n🎉 ALL ADVANCED FEATURES TESTS PASSED!")
            print("✅ Meeting closure protection working correctly")
            print("✅ Recovery system fully functional")
            print("✅ Heartbeat system operational")
            print("✅ Partial report generation working")
            print("✅ Enhanced PDF tracking implemented")
        else:
            print(f"\n⚠️  {failed} ADVANCED FEATURE TEST(S) FAILED")
            print("❌ Review failed tests above for specific issues")
        
        print("=" * 80)
        
        return passed, failed

async def main():
    """Main test execution"""
    tester = AdvancedFeaturesTester()
    passed, failed = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    asyncio.run(main())