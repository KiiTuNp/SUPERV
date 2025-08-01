#!/usr/bin/env python3
"""
Specific test for scrutator PDF generation to verify content
"""

import requests
import json
import time
import tempfile
import os

BASE_URL = "https://dffd1ffb-03ba-4c55-8b21-65220fce6f6a.preview.emergentagent.com/api"

def test_scrutator_pdf_content():
    """Test that PDF contains scrutator information"""
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    print("🔍 Testing Scrutator PDF Content Generation")
    print("=" * 50)
    
    # Step 1: Create meeting
    meeting_data = {
        "title": "Test PDF Scrutateurs",
        "organizer_name": "Alice Dupont"
    }
    
    response = session.post(f"{BASE_URL}/meetings", json=meeting_data)
    if response.status_code != 200:
        print("❌ Failed to create meeting")
        return False
    
    meeting = response.json()
    meeting_id = meeting['id']
    print(f"✅ Meeting created: {meeting['meeting_code']}")
    
    # Step 2: Add scrutators
    scrutator_data = {
        "names": ["Jean Dupont", "Marie Martin", "Pierre Durand"]
    }
    
    response = session.post(f"{BASE_URL}/meetings/{meeting_id}/scrutators", json=scrutator_data)
    if response.status_code != 200:
        print("❌ Failed to add scrutators")
        return False
    
    scrutator_info = response.json()
    print(f"✅ Scrutators added with code: {scrutator_info['scrutator_code']}")
    
    # Step 3: Add a participant and poll for complete data
    join_data = {
        "name": "Sophie Test",
        "meeting_code": meeting['meeting_code']
    }
    
    response = session.post(f"{BASE_URL}/participants/join", json=join_data)
    if response.status_code == 200:
        participant = response.json()
        
        # Approve participant
        approval_data = {
            "participant_id": participant['id'],
            "approved": True
        }
        session.post(f"{BASE_URL}/participants/{participant['id']}/approve", json=approval_data)
        print("✅ Participant added and approved")
    
    # Add a poll
    poll_data = {
        "question": "Test question?",
        "options": ["Oui", "Non"],
        "show_results_real_time": True
    }
    
    response = session.post(f"{BASE_URL}/meetings/{meeting_id}/polls", json=poll_data)
    if response.status_code == 200:
        poll = response.json()
        
        # Start poll and add vote
        session.post(f"{BASE_URL}/polls/{poll['id']}/start")
        vote_data = {
            "poll_id": poll['id'],
            "option_id": poll['options'][0]['id']
        }
        session.post(f"{BASE_URL}/votes", json=vote_data)
        session.post(f"{BASE_URL}/polls/{poll['id']}/close")
        print("✅ Poll created with vote")
    
    # Step 4: Generate PDF and examine content
    response = session.get(f"{BASE_URL}/meetings/{meeting_id}/report")
    if response.status_code != 200:
        print("❌ Failed to generate PDF")
        return False
    
    # Save PDF to examine
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_file.write(response.content)
        tmp_path = tmp_file.name
    
    file_size = os.path.getsize(tmp_path)
    print(f"✅ PDF generated: {file_size} bytes")
    
    # Try to extract text from PDF using different methods
    pdf_content = response.content
    
    # Method 1: Check raw bytes for text patterns
    try:
        # Convert to string with error handling
        content_str = pdf_content.decode('latin-1', errors='ignore')
        
        # Look for scrutator-related keywords
        scrutator_keywords = [
            'SCRUTATEURS',
            'Jean Dupont',
            'Marie Martin', 
            'Pierre Durand',
            'scrutateur',
            'Scrutateur'
        ]
        
        found_keywords = []
        for keyword in scrutator_keywords:
            if keyword in content_str:
                found_keywords.append(keyword)
        
        print(f"📄 PDF Content Analysis:")
        print(f"   - File size: {file_size} bytes")
        print(f"   - Content type: {response.headers.get('content-type', 'unknown')}")
        print(f"   - Found keywords: {found_keywords}")
        
        # Check if PDF has proper structure
        has_pdf_header = content_str.startswith('%PDF')
        has_scrutator_section = 'SCRUTATEURS' in content_str
        has_scrutator_names = any(name in content_str for name in ['Jean Dupont', 'Marie Martin', 'Pierre Durand'])
        
        print(f"   - Valid PDF header: {has_pdf_header}")
        print(f"   - Has SCRUTATEURS section: {has_scrutator_section}")
        print(f"   - Has scrutator names: {has_scrutator_names}")
        
        # Look for table structure indicators
        table_indicators = ['#', 'Nom du scrutateur', 'Ajouté le']
        has_table_structure = any(indicator in content_str for indicator in table_indicators)
        print(f"   - Has table structure: {has_table_structure}")
        
        if has_scrutator_section or has_scrutator_names or has_table_structure:
            print("✅ PDF contains scrutator information")
            success = True
        else:
            print("❌ PDF does not contain expected scrutator information")
            success = False
            
            # Debug: Show a sample of the content
            print("\n🔍 PDF Content Sample (first 1000 chars):")
            print(content_str[:1000])
            print("\n🔍 PDF Content Sample (last 1000 chars):")
            print(content_str[-1000:])
        
    except Exception as e:
        print(f"❌ Error analyzing PDF content: {str(e)}")
        success = False
    
    # Clean up
    os.unlink(tmp_path)
    
    return success

if __name__ == "__main__":
    success = test_scrutator_pdf_content()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: Scrutator PDF content test")
    exit(0 if success else 1)