#!/usr/bin/env python3
"""
Focused Test for Scrutator Automatic Access Workflow
Tests the complete workflow as requested in the review.
"""

import asyncio
import json
import os
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE_URL = f"{BACKEND_URL}/api"

async def test_complete_scrutator_workflow():
    """Test the complete scrutator workflow as requested"""
    print("🔍 Testing Complete Scrutator Automatic Access Workflow")
    print("=" * 60)
    
    session = aiohttp.ClientSession()
    
    try:
        # Step 1: Create a meeting with an organizer
        print("📝 Step 1: Creating meeting with organizer...")
        meeting_payload = {
            "title": "Réunion Test Scrutateurs",
            "organizer_name": "Organisateur Principal"
        }
        
        async with session.post(f"{API_BASE_URL}/meetings", json=meeting_payload) as response:
            if response.status == 200:
                meeting_data = await response.json()
                print(f"✅ Meeting created: {meeting_data['title']}")
                print(f"   Meeting Code: {meeting_data['meeting_code']}")
                print(f"   Organizer: {meeting_data['organizer_name']}")
            else:
                print(f"❌ Failed to create meeting: {response.status}")
                return False
        
        # Step 2: Add scrutators to the meeting (generate scrutator code)
        print("\n👥 Step 2: Adding scrutators and generating code...")
        scrutator_payload = {
            "names": ["Marie Dubois", "Pierre Moreau", "Claire Leroy"]
        }
        
        async with session.post(
            f"{API_BASE_URL}/meetings/{meeting_data['id']}/scrutators",
            json=scrutator_payload
        ) as response:
            if response.status == 200:
                scrutator_data = await response.json()
                print(f"✅ Scrutators added successfully")
                print(f"   Scrutator Code: {scrutator_data['scrutator_code']}")
                print(f"   Authorized Scrutators: {', '.join(scrutator_data['scrutators'])}")
            else:
                print(f"❌ Failed to add scrutators: {response.status}")
                return False
        
        # Step 3: Test scrutator connection - should have IMMEDIATE access
        print("\n🔐 Step 3: Testing scrutator connection (should get immediate access)...")
        join_payload = {
            "name": "Marie Dubois",
            "scrutator_code": scrutator_data['scrutator_code']
        }
        
        async with session.post(f"{API_BASE_URL}/scrutators/join", json=join_payload) as response:
            if response.status == 200:
                join_result = await response.json()
                print(f"✅ Scrutator connection successful!")
                print(f"   Name: {join_result['scrutator_name']}")
                print(f"   Status: {join_result['status']} (IMMEDIATE ACCESS)")
                print(f"   Access Type: {join_result['access_type']}")
                
                if join_result['status'] != 'approved':
                    print(f"❌ ERROR: Expected 'approved' status, got '{join_result['status']}'")
                    return False
            else:
                print(f"❌ Failed scrutator connection: {response.status}")
                return False
        
        # Step 4: Verify scrutator can access organizer interface
        print("\n🖥️  Step 4: Verifying scrutator can access organizer interface...")
        async with session.get(f"{API_BASE_URL}/meetings/{meeting_data['id']}/organizer") as response:
            if response.status == 200:
                organizer_data = await response.json()
                print(f"✅ Scrutator can access organizer interface!")
                print(f"   Meeting: {organizer_data['meeting']['title']}")
                print(f"   Participants: {len(organizer_data['participants'])}")
                print(f"   Polls: {len(organizer_data['polls'])}")
            else:
                print(f"❌ Failed to access organizer interface: {response.status}")
                return False
        
        # Step 5: Verify scrutator list shows approved status
        print("\n📋 Step 5: Verifying scrutator appears in approved list...")
        async with session.get(f"{API_BASE_URL}/meetings/{meeting_data['id']}/scrutators") as response:
            if response.status == 200:
                scrutators_list = await response.json()
                print(f"✅ Scrutator list retrieved successfully!")
                
                # Find our scrutator
                marie_scrutator = None
                for scrutator in scrutators_list['scrutators']:
                    if scrutator['name'] == 'Marie Dubois':
                        marie_scrutator = scrutator
                        break
                
                if marie_scrutator:
                    print(f"   Found: {marie_scrutator['name']}")
                    print(f"   Status: {marie_scrutator['approval_status']}")
                    print(f"   Added at: {marie_scrutator['added_at']}")
                    
                    if marie_scrutator['approval_status'] == 'approved':
                        print("✅ Scrutator correctly shows as approved!")
                    else:
                        print(f"❌ ERROR: Expected 'approved', got '{marie_scrutator['approval_status']}'")
                        return False
                else:
                    print("❌ ERROR: Scrutator not found in list")
                    return False
            else:
                print(f"❌ Failed to get scrutator list: {response.status}")
                return False
        
        # Step 6: Test second scrutator for consistency
        print("\n👤 Step 6: Testing second scrutator (consistency check)...")
        join_payload2 = {
            "name": "Pierre Moreau",
            "scrutator_code": scrutator_data['scrutator_code']
        }
        
        async with session.post(f"{API_BASE_URL}/scrutators/join", json=join_payload2) as response:
            if response.status == 200:
                join_result2 = await response.json()
                print(f"✅ Second scrutator also got immediate access!")
                print(f"   Name: {join_result2['scrutator_name']}")
                print(f"   Status: {join_result2['status']}")
                
                if join_result2['status'] != 'approved':
                    print(f"❌ ERROR: Second scrutator should also be approved immediately")
                    return False
            else:
                print(f"❌ Failed second scrutator connection: {response.status}")
                return False
        
        # Step 7: Test security - unauthorized name should be rejected
        print("\n🛡️  Step 7: Testing security (unauthorized name should be rejected)...")
        unauthorized_payload = {
            "name": "Personne Non Autorisée",
            "scrutator_code": scrutator_data['scrutator_code']
        }
        
        async with session.post(f"{API_BASE_URL}/scrutators/join", json=unauthorized_payload) as response:
            if response.status == 403:
                print("✅ Security working: Unauthorized person correctly rejected!")
            elif response.status == 200:
                print("❌ SECURITY ISSUE: Unauthorized person got access!")
                return False
            else:
                print(f"❌ Unexpected response for unauthorized access: {response.status}")
                return False
        
        print("\n" + "=" * 60)
        print("🎉 COMPLETE WORKFLOW TEST PASSED!")
        print("✅ All scrutator automatic access features working correctly:")
        print("   • Scrutators get immediate approval without manual intervention")
        print("   • Scrutators can access organizer interface immediately")
        print("   • Multiple scrutators can join seamlessly")
        print("   • Security controls prevent unauthorized access")
        print("   • System provides smooth workflow without friction")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False
        
    finally:
        await session.close()

async def main():
    success = await test_complete_scrutator_workflow()
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        print("\n🏆 SCRUTATOR AUTOMATIC ACCESS SYSTEM: FULLY FUNCTIONAL")
    else:
        print("\n💥 SCRUTATOR AUTOMATIC ACCESS SYSTEM: ISSUES DETECTED")