#!/usr/bin/env python3
"""
Performance and Production Readiness Testing
Tests API response times, WebSocket connectivity, and system robustness
"""

import requests
import json
import time
import asyncio
import websockets
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import statistics

BASE_URL = "https://1699400a-9fcd-4176-98dd-a6c9c5120b3e.preview.emergentagent.com/api"
WS_URL = "wss://1699400a-9fcd-4176-98dd-a6c9c5120b3e.preview.emergentagent.com/ws"

class PerformanceTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 10
        self.results = []
        
    def log_result(self, test_name: str, success: bool, message: str, details=None):
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
    
    def test_api_response_times(self):
        """Test API response times for production readiness"""
        print("\n🚀 Testing API Response Times...")
        
        endpoints = [
            ("/health", "GET", None),
            ("/meetings", "POST", {"title": "Performance Test", "organizer_name": "Perf Tester"}),
        ]
        
        response_times = []
        
        for endpoint, method, data in endpoints:
            times = []
            for i in range(5):  # Test each endpoint 5 times
                start_time = time.time()
                try:
                    if method == "GET":
                        response = self.session.get(f"{BASE_URL}{endpoint}")
                    else:
                        response = self.session.post(f"{BASE_URL}{endpoint}", json=data)
                    
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # Convert to ms
                    
                    if response.status_code in [200, 201]:
                        times.append(response_time)
                    
                except Exception as e:
                    print(f"   Error testing {endpoint}: {str(e)}")
            
            if times:
                avg_time = statistics.mean(times)
                max_time = max(times)
                min_time = min(times)
                
                response_times.extend(times)
                
                # Production readiness: API should respond within 200ms average
                if avg_time <= 200:
                    self.log_result(f"Response Time - {endpoint}", True, 
                                  f"Avg: {avg_time:.1f}ms, Min: {min_time:.1f}ms, Max: {max_time:.1f}ms")
                else:
                    self.log_result(f"Response Time - {endpoint}", False, 
                                  f"Too slow - Avg: {avg_time:.1f}ms (>200ms threshold)")
        
        if response_times:
            overall_avg = statistics.mean(response_times)
            if overall_avg <= 200:
                self.log_result("Overall API Performance", True, f"Average response time: {overall_avg:.1f}ms")
                return True
            else:
                self.log_result("Overall API Performance", False, f"Average response time too high: {overall_avg:.1f}ms")
                return False
        
        return False
    
    def test_concurrent_requests(self):
        """Test system under concurrent load"""
        print("\n🔄 Testing Concurrent Request Handling...")
        
        def make_health_request():
            try:
                start_time = time.time()
                response = requests.get(f"{BASE_URL}/health", timeout=10)
                end_time = time.time()
                return {
                    "success": response.status_code == 200,
                    "response_time": (end_time - start_time) * 1000,
                    "status_code": response.status_code
                }
            except Exception as e:
                return {"success": False, "error": str(e), "response_time": None}
        
        # Test with 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_health_request) for _ in range(10)]
            results = [future.result() for future in futures]
        
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        if successful >= 8:  # At least 80% success rate
            avg_time = statistics.mean([r["response_time"] for r in results if r["response_time"]])
            self.log_result("Concurrent Requests", True, 
                          f"Success: {successful}/10, Avg time: {avg_time:.1f}ms")
            return True
        else:
            self.log_result("Concurrent Requests", False, 
                          f"Too many failures: {failed}/10 failed")
            return False
    
    async def test_websocket_connectivity(self):
        """Test WebSocket connectivity"""
        print("\n🔌 Testing WebSocket Connectivity...")
        
        try:
            # First create a meeting to get a valid meeting ID
            meeting_response = self.session.post(f"{BASE_URL}/meetings", json={
                "title": "WebSocket Test Meeting",
                "organizer_name": "WS Tester"
            })
            
            if meeting_response.status_code != 200:
                self.log_result("WebSocket Test", False, "Failed to create test meeting")
                return False
            
            meeting_data = meeting_response.json()
            meeting_id = meeting_data["id"]
            
            # Test WebSocket connection
            ws_url = f"{WS_URL}/meetings/{meeting_id}"
            
            async with websockets.connect(ws_url) as websocket:
                # Send a test message
                await websocket.send(json.dumps({"type": "test", "message": "ping"}))
                
                # Wait for potential response (with timeout)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    self.log_result("WebSocket Connectivity", True, "WebSocket connection established and responsive")
                    return True
                except asyncio.TimeoutError:
                    # No response is actually expected for our test message, so this is OK
                    self.log_result("WebSocket Connectivity", True, "WebSocket connection established successfully")
                    return True
                    
        except Exception as e:
            self.log_result("WebSocket Connectivity", False, f"WebSocket connection failed: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test API error handling robustness"""
        print("\n🛡️ Testing Error Handling Robustness...")
        
        error_tests = [
            # Invalid meeting code
            ("Invalid Meeting Code", "GET", "/meetings/INVALID", 404, None),
            # Empty meeting creation
            ("Empty Meeting Data", "POST", "/meetings", 400, {}),
            # Invalid participant join
            ("Invalid Participant Join", "POST", "/participants/join", 400, {"name": "", "meeting_code": ""}),
            # Non-existent poll
            ("Non-existent Poll", "GET", "/polls/invalid-id/results", 404, None),
        ]
        
        passed = 0
        total = len(error_tests)
        
        for test_name, method, endpoint, expected_status, data in error_tests:
            try:
                if method == "GET":
                    response = self.session.get(f"{BASE_URL}{endpoint}")
                else:
                    response = self.session.post(f"{BASE_URL}{endpoint}", json=data)
                
                if response.status_code == expected_status:
                    self.log_result(f"Error Handling - {test_name}", True, 
                                  f"Correctly returned HTTP {response.status_code}")
                    passed += 1
                else:
                    self.log_result(f"Error Handling - {test_name}", False, 
                                  f"Expected {expected_status}, got {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Error Handling - {test_name}", False, f"Request failed: {str(e)}")
        
        success_rate = (passed / total) * 100
        if success_rate >= 75:  # At least 75% of error handling tests should pass
            self.log_result("Overall Error Handling", True, f"Success rate: {success_rate:.1f}%")
            return True
        else:
            self.log_result("Overall Error Handling", False, f"Success rate too low: {success_rate:.1f}%")
            return False
    
    def test_pdf_generation_performance(self):
        """Test PDF generation functionality and performance"""
        print("\n📄 Testing PDF Generation Performance...")
        
        try:
            # Create a meeting with data for PDF generation
            meeting_response = self.session.post(f"{BASE_URL}/meetings", json={
                "title": "PDF Test Meeting - Production Readiness",
                "organizer_name": "PDF Tester"
            })
            
            if meeting_response.status_code != 200:
                self.log_result("PDF Generation", False, "Failed to create test meeting")
                return False
            
            meeting_data = meeting_response.json()
            meeting_id = meeting_data["id"]
            
            # Add a participant
            participant_response = self.session.post(f"{BASE_URL}/participants/join", json={
                "name": "PDF Test Participant",
                "meeting_code": meeting_data["meeting_code"]
            })
            
            if participant_response.status_code == 200:
                participant_data = participant_response.json()
                # Approve participant
                self.session.post(f"{BASE_URL}/participants/{participant_data['id']}/approve", json={
                    "participant_id": participant_data["id"],
                    "approved": True
                })
            
            # Create and start a poll
            poll_response = self.session.post(f"{BASE_URL}/meetings/{meeting_id}/polls", json={
                "question": "PDF Test Question - Is the system ready for production?",
                "options": ["Yes", "No", "Needs improvement"]
            })
            
            if poll_response.status_code == 200:
                poll_data = poll_response.json()
                # Start the poll
                self.session.post(f"{BASE_URL}/polls/{poll_data['id']}/start")
                # Submit a vote
                self.session.post(f"{BASE_URL}/votes", json={
                    "poll_id": poll_data["id"],
                    "option_id": poll_data["options"][0]["id"]
                })
            
            # Test PDF report request (should be direct generation since no scrutators)
            start_time = time.time()
            report_response = self.session.post(f"{BASE_URL}/meetings/{meeting_id}/request-report", json={
                "meeting_id": meeting_id,
                "requested_by": "PDF Tester"
            })
            end_time = time.time()
            
            if report_response.status_code == 200:
                response_time = (end_time - start_time) * 1000
                data = report_response.json()
                
                if data.get("direct_generation"):
                    self.log_result("PDF Generation", True, 
                                  f"PDF generation request processed in {response_time:.1f}ms")
                    return True
                else:
                    self.log_result("PDF Generation", True, 
                                  f"PDF generation workflow functional (scrutator approval required)")
                    return True
            else:
                self.log_result("PDF Generation", False, 
                              f"PDF generation failed: HTTP {report_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("PDF Generation", False, f"PDF generation test failed: {str(e)}")
            return False
    
    def run_performance_tests(self):
        """Run all performance tests"""
        print("🎯 PRODUCTION READINESS TESTING")
        print("=" * 60)
        
        tests = [
            ("API Response Times", self.test_api_response_times),
            ("Concurrent Request Handling", self.test_concurrent_requests),
            ("Error Handling Robustness", self.test_error_handling),
            ("PDF Generation Performance", self.test_pdf_generation_performance),
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
            
            time.sleep(1)  # Brief pause between test suites
        
        # Run WebSocket test separately (async)
        print("\n🔌 Testing WebSocket Connectivity...")
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            ws_result = loop.run_until_complete(self.test_websocket_connectivity())
            loop.close()
            
            if ws_result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            self.log_result("WebSocket Connectivity", False, f"WebSocket test failed: {str(e)}")
            failed += 1
        
        print("\n" + "=" * 60)
        print("📊 PRODUCTION READINESS SUMMARY")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        if failed == 0:
            print("🚀 SYSTEM IS PRODUCTION READY!")
            print("   All performance and robustness tests passed.")
        else:
            print("⚠️  PRODUCTION READINESS ISSUES DETECTED")
            print("   Review failed tests before deployment.")
        
        return passed, failed, self.results

def main():
    """Main performance test execution"""
    tester = PerformanceTester()
    passed, failed, results = tester.run_performance_tests()
    
    # Save results
    with open('/app/performance_test_results.json', 'w') as f:
        json.dump({
            "summary": {
                "passed": passed,
                "failed": failed,
                "total": passed + failed,
                "success_rate": (passed/(passed+failed)*100) if (passed+failed) > 0 else 0,
                "production_ready": failed == 0
            },
            "results": results,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n📄 Performance test results saved to: /app/performance_test_results.json")
    
    return failed == 0

if __name__ == "__main__":
    main()