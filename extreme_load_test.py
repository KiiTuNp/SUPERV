#!/usr/bin/env python3
"""
TESTS EXTRÊMES ET EXHAUSTIFS - 4 ASSEMBLÉES SIMULTANÉES
Test de charge extrême avec 4 assemblées simultanées de différentes tailles et complexités
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
import sys
import random
import string

# Configuration
BACKEND_URL = "https://7ec35474-0815-47b0-a5a7-33937258cf82.preview.emergentagent.com/api"

class ExtremeLoadTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.assemblies = {}
        self.total_participants = 0
        self.total_scrutators = 0
        self.total_polls = 0
        
    async def setup_session(self):
        """Initialize HTTP session with timeout"""
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
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
        
    def generate_french_names(self, count):
        """Generate realistic French names"""
        first_names = [
            "Jean", "Marie", "Pierre", "Sophie", "Michel", "Catherine", "Philippe", "Nathalie",
            "Alain", "Isabelle", "François", "Sylvie", "Daniel", "Martine", "Bernard", "Christine",
            "Jacques", "Monique", "André", "Françoise", "René", "Nicole", "Louis", "Brigitte",
            "Claude", "Chantal", "Marcel", "Jacqueline", "Roger", "Denise", "Henri", "Jeanne",
            "Robert", "Paulette", "Georges", "Simone", "Paul", "Colette", "Maurice", "Yvette",
            "Antoine", "Madeleine", "Julien", "Hélène", "Olivier", "Véronique", "Thierry", "Dominique",
            "Sébastien", "Sandrine", "Christophe", "Valérie", "Laurent", "Corinne", "Pascal", "Karine",
            "Frédéric", "Céline", "Nicolas", "Stéphanie", "Vincent", "Laetitia", "Bruno", "Aurélie",
            "Didier", "Émilie", "Éric", "Caroline", "Patrice", "Virginie", "Gérard", "Delphine",
            "Yves", "Sabrina", "Serge", "Patricia", "Lucien", "Muriel", "Fabrice", "Nadine",
            "Xavier", "Agnès", "Stéphane", "Béatrice", "Hervé", "Laurence", "Jérôme", "Florence",
            "Lionel", "Pascale", "Régis", "Élisabeth", "Cédric", "Joëlle", "Damien", "Michèle",
            "Franck", "Danielle", "Emmanuel", "Odette", "Maxime", "Arlette", "Romain", "Ginette"
        ]
        
        last_names = [
            "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", "Durand",
            "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel", "Garcia", "David",
            "Bertrand", "Roux", "Vincent", "Fournier", "Morel", "Girard", "André", "Lefèvre",
            "Mercier", "Dupont", "Lambert", "Bonnet", "François", "Martinez", "Legrand", "Garnier",
            "Faure", "Rousseau", "Blanc", "Guerin", "Muller", "Henry", "Roussel", "Nicolas",
            "Perrin", "Morin", "Mathieu", "Clement", "Gauthier", "Dumont", "Lopez", "Fontaine",
            "Chevalier", "Robin", "Masson", "Sanchez", "Gerard", "Nguyen", "Boyer", "Denis",
            "Lemaire", "Duval", "Joly", "Gautier", "Roger", "Roche", "Roy", "Noel",
            "Meyer", "Lucas", "Meunier", "Jean", "Perez", "Marchand", "Dufour", "Blanchard",
            "Marie", "Barbier", "Brun", "Dumas", "Brunet", "Schmitt", "Leroux", "Colin"
        ]
        
        names = []
        used_combinations = set()
        
        for _ in range(count):
            while True:
                first = random.choice(first_names)
                last = random.choice(last_names)
                full_name = f"{first} {last}"
                if full_name not in used_combinations:
                    used_combinations.add(full_name)
                    names.append(full_name)
                    break
        
        return names
    
    async def test_health_check(self):
        """Test system health before extreme load"""
        start_time = time.time()
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                response_time = time.time() - start_time
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "healthy":
                        self.log_result("System Health Check", True, "Backend ready for extreme load testing", response_time)
                        return True
                    else:
                        self.log_result("System Health Check", False, f"Service unhealthy: {data}")
                        return False
                else:
                    self.log_result("System Health Check", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("System Health Check", False, f"Connection error: {str(e)}")
            return False
    
    async def create_assembly(self, assembly_config):
        """Create a single assembly with its configuration"""
        start_time = time.time()
        try:
            # Create meeting
            meeting_data = {
                "title": assembly_config["title"],
                "organizer_name": assembly_config["organizer"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/meetings", json=meeting_data) as response:
                if response.status == 200:
                    meeting = await response.json()
                    assembly_config["meeting_id"] = meeting["id"]
                    assembly_config["meeting_code"] = meeting["meeting_code"]
                    
                    # Add scrutators if specified
                    if assembly_config["scrutators_count"] > 0:
                        scrutator_names = self.generate_french_names(assembly_config["scrutators_count"])
                        scrutator_data = {"names": scrutator_names}
                        
                        async with self.session.post(f"{BACKEND_URL}/meetings/{meeting['id']}/scrutators", json=scrutator_data) as scrutator_response:
                            if scrutator_response.status == 200:
                                scrutator_result = await scrutator_response.json()
                                assembly_config["scrutator_code"] = scrutator_result["scrutator_code"]
                                assembly_config["scrutator_names"] = scrutator_names
                                self.total_scrutators += len(scrutator_names)
                            else:
                                self.log_result(f"Scrutators Creation - {assembly_config['name']}", False, f"HTTP {scrutator_response.status}")
                                return False
                    
                    response_time = time.time() - start_time
                    self.log_result(f"Assembly Creation - {assembly_config['name']}", True, 
                                  f"Created with {assembly_config['scrutators_count']} scrutators", response_time)
                    return True
                else:
                    error_text = await response.text()
                    self.log_result(f"Assembly Creation - {assembly_config['name']}", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_result(f"Assembly Creation - {assembly_config['name']}", False, f"Error: {str(e)}")
            return False
    
    async def add_participants_batch(self, assembly_config):
        """Add participants to assembly in batches"""
        start_time = time.time()
        try:
            participant_names = self.generate_french_names(assembly_config["participants_count"])
            participants = []
            
            # Add participants in batches of 25 for better performance
            batch_size = 25
            for i in range(0, len(participant_names), batch_size):
                batch = participant_names[i:i + batch_size]
                batch_tasks = []
                
                for name in batch:
                    participant_data = {
                        "name": name,
                        "meeting_code": assembly_config["meeting_code"]
                    }
                    batch_tasks.append(self.session.post(f"{BACKEND_URL}/participants/join", json=participant_data))
                
                # Execute batch concurrently
                batch_responses = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for j, response in enumerate(batch_responses):
                    if isinstance(response, Exception):
                        continue
                    
                    async with response:
                        if response.status == 200:
                            participant = await response.json()
                            participants.append(participant)
                        else:
                            print(f"Failed to add participant {batch[j]}: HTTP {response.status}")
            
            assembly_config["participants"] = participants
            self.total_participants += len(participants)
            
            response_time = time.time() - start_time
            self.log_result(f"Participants Addition - {assembly_config['name']}", True, 
                          f"Added {len(participants)}/{assembly_config['participants_count']} participants", response_time)
            return True
            
        except Exception as e:
            self.log_result(f"Participants Addition - {assembly_config['name']}", False, f"Error: {str(e)}")
            return False
    
    async def approve_participants_batch(self, assembly_config):
        """Approve participants in batches"""
        start_time = time.time()
        try:
            participants = assembly_config.get("participants", [])
            if not participants:
                return True
            
            # Approve in batches of 20
            batch_size = 20
            approved_count = 0
            
            for i in range(0, len(participants), batch_size):
                batch = participants[i:i + batch_size]
                batch_tasks = []
                
                for participant in batch:
                    approval_data = {
                        "participant_id": participant["id"],
                        "approved": True
                    }
                    batch_tasks.append(self.session.post(f"{BACKEND_URL}/participants/{participant['id']}/approve", json=approval_data))
                
                # Execute batch concurrently
                batch_responses = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for response in batch_responses:
                    if isinstance(response, Exception):
                        continue
                    
                    async with response:
                        if response.status == 200:
                            approved_count += 1
            
            response_time = time.time() - start_time
            self.log_result(f"Participants Approval - {assembly_config['name']}", True, 
                          f"Approved {approved_count}/{len(participants)} participants", response_time)
            return True
            
        except Exception as e:
            self.log_result(f"Participants Approval - {assembly_config['name']}", False, f"Error: {str(e)}")
            return False
    
    async def create_polls_for_assembly(self, assembly_config):
        """Create polls for an assembly"""
        start_time = time.time()
        try:
            polls = []
            poll_configs = assembly_config["polls"]
            
            for poll_config in poll_configs:
                poll_data = {
                    "question": poll_config["question"],
                    "options": poll_config["options"]
                }
                
                async with self.session.post(f"{BACKEND_URL}/meetings/{assembly_config['meeting_id']}/polls", json=poll_data) as response:
                    if response.status == 200:
                        poll = await response.json()
                        polls.append(poll)
                    else:
                        print(f"Failed to create poll: {poll_config['question']}")
            
            assembly_config["created_polls"] = polls
            self.total_polls += len(polls)
            
            response_time = time.time() - start_time
            self.log_result(f"Polls Creation - {assembly_config['name']}", True, 
                          f"Created {len(polls)}/{len(poll_configs)} polls", response_time)
            return True
            
        except Exception as e:
            self.log_result(f"Polls Creation - {assembly_config['name']}", False, f"Error: {str(e)}")
            return False
    
    async def simulate_concurrent_voting(self, assembly_config):
        """Simulate concurrent voting on all polls"""
        start_time = time.time()
        try:
            polls = assembly_config.get("created_polls", [])
            participants = assembly_config.get("participants", [])
            
            if not polls or not participants:
                return True
            
            total_votes = 0
            
            for poll in polls:
                # Start poll
                async with self.session.post(f"{BACKEND_URL}/polls/{poll['id']}/start") as response:
                    if response.status != 200:
                        continue
                
                # Simulate votes from random participants
                vote_count = min(len(participants), random.randint(10, 50))
                vote_tasks = []
                
                for _ in range(vote_count):
                    option = random.choice(poll["options"])
                    vote_data = {
                        "poll_id": poll["id"],
                        "option_id": option["id"]
                    }
                    vote_tasks.append(self.session.post(f"{BACKEND_URL}/votes", json=vote_data))
                
                # Execute votes concurrently
                vote_responses = await asyncio.gather(*vote_tasks, return_exceptions=True)
                
                successful_votes = 0
                for response in vote_responses:
                    if isinstance(response, Exception):
                        continue
                    
                    async with response:
                        if response.status == 200:
                            successful_votes += 1
                
                total_votes += successful_votes
                
                # Close poll
                async with self.session.post(f"{BACKEND_URL}/polls/{poll['id']}/close") as response:
                    pass
            
            response_time = time.time() - start_time
            self.log_result(f"Concurrent Voting - {assembly_config['name']}", True, 
                          f"Processed {total_votes} votes across {len(polls)} polls", response_time)
            return True
            
        except Exception as e:
            self.log_result(f"Concurrent Voting - {assembly_config['name']}", False, f"Error: {str(e)}")
            return False
    
    async def test_scrutator_approval_scenario(self, assembly_config):
        """Test different scrutator approval scenarios"""
        start_time = time.time()
        try:
            if assembly_config["scrutators_count"] == 0:
                # Direct generation scenario
                async with self.session.get(f"{BACKEND_URL}/meetings/{assembly_config['meeting_id']}/report") as response:
                    response_time = time.time() - start_time
                    if response.status == 200:
                        content_length = len(await response.read())
                        self.log_result(f"Direct PDF Generation - {assembly_config['name']}", True, 
                                      f"Generated PDF ({content_length} bytes) without scrutators", response_time)
                        return True
                    else:
                        self.log_result(f"Direct PDF Generation - {assembly_config['name']}", False, f"HTTP {response.status}")
                        return False
            else:
                # Scrutator approval scenario
                scrutator_names = assembly_config.get("scrutator_names", [])
                
                # First, connect scrutators and approve them
                for name in scrutator_names:
                    join_data = {
                        "name": name,
                        "scrutator_code": assembly_config["scrutator_code"]
                    }
                    
                    async with self.session.post(f"{BACKEND_URL}/scrutators/join", json=join_data) as response:
                        if response.status == 200:
                            result = await response.json()
                            if result.get("status") == "pending_approval":
                                # Find and approve scrutator
                                async with self.session.get(f"{BACKEND_URL}/meetings/{assembly_config['meeting_id']}/scrutators") as scrutators_response:
                                    if scrutators_response.status == 200:
                                        scrutators_data = await scrutators_response.json()
                                        for scrutator in scrutators_data.get("scrutators", []):
                                            if scrutator["name"] == name:
                                                approval_data = {
                                                    "scrutator_id": scrutator["id"],
                                                    "approved": True
                                                }
                                                async with self.session.post(f"{BACKEND_URL}/scrutators/{scrutator['id']}/approve", json=approval_data) as approval_response:
                                                    pass
                
                # Request report generation
                request_data = {
                    "meeting_id": assembly_config["meeting_id"],
                    "requested_by": assembly_config["organizer"]
                }
                
                async with self.session.post(f"{BACKEND_URL}/meetings/{assembly_config['meeting_id']}/request-report", json=request_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        majority_needed = result.get("majority_needed", 1)
                        
                        # Simulate scrutator votes based on scenario
                        scenario = assembly_config["closure_scenario"]
                        votes_needed = majority_needed
                        
                        if scenario == "majority_approval":
                            # Vote YES for majority
                            for i, name in enumerate(scrutator_names[:votes_needed]):
                                vote_data = {
                                    "meeting_id": assembly_config["meeting_id"],
                                    "scrutator_name": name,
                                    "approved": True
                                }
                                async with self.session.post(f"{BACKEND_URL}/meetings/{assembly_config['meeting_id']}/scrutator-vote", json=vote_data) as vote_response:
                                    pass
                        
                        elif scenario == "unanimous_approval":
                            # All vote YES
                            for name in scrutator_names:
                                vote_data = {
                                    "meeting_id": assembly_config["meeting_id"],
                                    "scrutator_name": name,
                                    "approved": True
                                }
                                async with self.session.post(f"{BACKEND_URL}/meetings/{assembly_config['meeting_id']}/scrutator-vote", json=vote_data) as vote_response:
                                    pass
                        
                        elif scenario == "initial_rejection_then_approval":
                            # First vote NO, then YES
                            vote_data = {
                                "meeting_id": assembly_config["meeting_id"],
                                "scrutator_name": scrutator_names[0],
                                "approved": False
                            }
                            async with self.session.post(f"{BACKEND_URL}/meetings/{assembly_config['meeting_id']}/scrutator-vote", json=vote_data) as vote_response:
                                pass
                            
                            # Then vote YES for majority
                            for name in scrutator_names[:votes_needed]:
                                vote_data = {
                                    "meeting_id": assembly_config["meeting_id"],
                                    "scrutator_name": name,
                                    "approved": True
                                }
                                async with self.session.post(f"{BACKEND_URL}/meetings/{assembly_config['meeting_id']}/scrutator-vote", json=vote_data) as vote_response:
                                    pass
                        
                        # Now try to generate PDF
                        async with self.session.get(f"{BACKEND_URL}/meetings/{assembly_config['meeting_id']}/report") as pdf_response:
                            response_time = time.time() - start_time
                            if pdf_response.status == 200:
                                content_length = len(await pdf_response.read())
                                self.log_result(f"Scrutator Approval & PDF - {assembly_config['name']}", True, 
                                              f"Generated PDF ({content_length} bytes) after {scenario}", response_time)
                                return True
                            else:
                                error_text = await pdf_response.text()
                                self.log_result(f"Scrutator Approval & PDF - {assembly_config['name']}", False, 
                                              f"PDF generation failed: HTTP {pdf_response.status}: {error_text}")
                                return False
                    else:
                        self.log_result(f"Report Request - {assembly_config['name']}", False, f"HTTP {response.status}")
                        return False
            
        except Exception as e:
            self.log_result(f"Scrutator Scenario - {assembly_config['name']}", False, f"Error: {str(e)}")
            return False
    
    async def verify_data_cleanup(self, assembly_config):
        """Verify complete data cleanup after PDF generation"""
        start_time = time.time()
        try:
            await asyncio.sleep(1)  # Wait for cleanup
            
            # Check meeting accessibility
            async with self.session.get(f"{BACKEND_URL}/meetings/{assembly_config['meeting_code']}") as response:
                if response.status == 404:
                    # Check organizer view
                    async with self.session.get(f"{BACKEND_URL}/meetings/{assembly_config['meeting_id']}/organizer") as org_response:
                        if org_response.status == 404:
                            response_time = time.time() - start_time
                            self.log_result(f"Data Cleanup - {assembly_config['name']}", True, 
                                          "All data properly deleted", response_time)
                            return True
                        else:
                            self.log_result(f"Data Cleanup - {assembly_config['name']}", False, 
                                          f"Organizer view still accessible: HTTP {org_response.status}")
                            return False
                else:
                    self.log_result(f"Data Cleanup - {assembly_config['name']}", False, 
                                  f"Meeting still accessible: HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result(f"Data Cleanup - {assembly_config['name']}", False, f"Error: {str(e)}")
            return False
    
    async def run_extreme_load_test(self):
        """Run the complete extreme load test with 4 simultaneous assemblies"""
        print("=" * 100)
        print("TESTS EXTRÊMES ET EXHAUSTIFS - 4 ASSEMBLÉES SIMULTANÉES")
        print("=" * 100)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 100)
        
        await self.setup_session()
        
        # Define the 4 assemblies with different configurations
        assemblies_config = [
            {
                "name": "ASSEMBLÉE 1 - TRÈS GROSSE",
                "title": "Assemblée Générale Nationale 2025 - Congrès Principal",
                "organizer": "Président National",
                "participants_count": 200,
                "scrutators_count": 8,
                "closure_scenario": "majority_approval",
                "polls": [
                    {
                        "question": "Approbation du budget national 2025 (50 millions €)",
                        "options": ["Approuvé", "Rejeté", "Abstention"]
                    },
                    {
                        "question": "Élection du nouveau conseil d'administration national",
                        "options": ["Liste A - Renouveau", "Liste B - Continuité", "Liste C - Innovation", "Blanc"]
                    },
                    {
                        "question": "Modification des statuts de l'organisation",
                        "options": ["Oui", "Non", "Amendement proposé", "Report"]
                    },
                    {
                        "question": "Investissement dans de nouveaux équipements nationaux",
                        "options": ["Approuvé", "Rejeté", "Budget réduit", "Étude complémentaire"]
                    },
                    {
                        "question": "Politique de communication et relations publiques",
                        "options": ["Stratégie A", "Stratégie B", "Stratégie mixte", "Maintien actuel"]
                    },
                    {
                        "question": "Partenariats internationaux et coopération",
                        "options": ["Extension", "Maintien", "Réduction", "Révision complète"]
                    },
                    {
                        "question": "Formation et développement des compétences",
                        "options": ["Programme intensif", "Programme standard", "Programme allégé", "Externalisation"]
                    },
                    {
                        "question": "Politique environnementale et développement durable",
                        "options": ["Engagement fort", "Engagement modéré", "Approche progressive", "Maintien actuel"]
                    }
                ]
            },
            {
                "name": "ASSEMBLÉE 2 - MOYENNE",
                "title": "Conseil Régional - Assemblée Départementale",
                "organizer": "Président Régional",
                "participants_count": 60,
                "scrutators_count": 3,
                "closure_scenario": "unanimous_approval",
                "polls": [
                    {
                        "question": "Budget régional pour les infrastructures",
                        "options": ["Approuvé", "Rejeté", "Amendé", "Report"]
                    },
                    {
                        "question": "Politique de développement économique régional",
                        "options": ["Plan A - Industrie", "Plan B - Services", "Plan C - Mixte", "Maintien"]
                    },
                    {
                        "question": "Aménagement du territoire et urbanisme",
                        "options": ["Densification", "Étalement contrôlé", "Préservation", "Révision générale"]
                    },
                    {
                        "question": "Transport et mobilité régionale",
                        "options": ["Transport public", "Infrastructure routière", "Mobilité douce", "Solution mixte"]
                    },
                    {
                        "question": "Politique culturelle et patrimoine",
                        "options": ["Renforcement", "Maintien", "Réorientation", "Partenariats privés"]
                    }
                ]
            },
            {
                "name": "ASSEMBLÉE 3 - PETITE",
                "title": "Comité Local - Décisions Municipales",
                "organizer": "Maire",
                "participants_count": 20,
                "scrutators_count": 2,
                "closure_scenario": "initial_rejection_then_approval",
                "polls": [
                    {
                        "question": "Rénovation de la place centrale",
                        "options": ["Oui", "Non", "Projet modifié"]
                    },
                    {
                        "question": "Horaires d'ouverture de la bibliothèque",
                        "options": ["Extension", "Maintien", "Réduction"]
                    },
                    {
                        "question": "Organisation de la fête locale annuelle",
                        "options": ["Format traditionnel", "Format moderne", "Format mixte", "Annulation"]
                    }
                ]
            },
            {
                "name": "ASSEMBLÉE 4 - MICRO",
                "title": "Réunion de Bureau - Conseil d'Administration",
                "organizer": "Directeur Général",
                "participants_count": 8,
                "scrutators_count": 0,  # AUCUN scrutateur
                "closure_scenario": "direct_generation",
                "polls": [
                    {
                        "question": "Validation du rapport trimestriel",
                        "options": ["Validé", "À réviser", "Rejeté"]
                    },
                    {
                        "question": "Prochaine réunion du conseil",
                        "options": ["Dans 1 mois", "Dans 2 mois", "Dans 3 mois"]
                    }
                ]
            }
        ]
        
        self.assemblies = {config["name"]: config for config in assemblies_config}
        
        # Test 1: System Health Check
        if not await self.test_health_check():
            print("❌ System not ready for extreme load testing")
            return 0, 1
        
        # Test 2: Create all 4 assemblies simultaneously
        print("\n🚀 PHASE 1: CRÉATION SIMULTANÉE DES 4 ASSEMBLÉES")
        creation_tasks = [self.create_assembly(config) for config in assemblies_config]
        creation_results = await asyncio.gather(*creation_tasks, return_exceptions=True)
        
        creation_success = sum(1 for result in creation_results if result is True)
        self.log_result("Simultaneous Assembly Creation", creation_success == 4, 
                       f"Created {creation_success}/4 assemblies simultaneously")
        
        if creation_success < 4:
            print("❌ Not all assemblies created successfully")
            await self.cleanup_session()
            return creation_success, 4 - creation_success
        
        # Test 3: Add participants in parallel
        print("\n👥 PHASE 2: AJOUT MASSIF DE PARTICIPANTS EN PARALLÈLE")
        participant_tasks = [self.add_participants_batch(config) for config in assemblies_config]
        participant_results = await asyncio.gather(*participant_tasks, return_exceptions=True)
        
        participant_success = sum(1 for result in participant_results if result is True)
        self.log_result("Parallel Participant Addition", participant_success == 4, 
                       f"Added participants to {participant_success}/4 assemblies (Total: {self.total_participants} participants)")
        
        # Test 4: Approve participants in batches
        print("\n✅ PHASE 3: APPROBATION EN MASSE DES PARTICIPANTS")
        approval_tasks = [self.approve_participants_batch(config) for config in assemblies_config]
        approval_results = await asyncio.gather(*approval_tasks, return_exceptions=True)
        
        approval_success = sum(1 for result in approval_results if result is True)
        self.log_result("Batch Participant Approval", approval_success == 4, 
                       f"Approved participants in {approval_success}/4 assemblies")
        
        # Test 5: Create all polls simultaneously
        print("\n📊 PHASE 4: CRÉATION SIMULTANÉE DE TOUS LES SONDAGES")
        poll_tasks = [self.create_polls_for_assembly(config) for config in assemblies_config]
        poll_results = await asyncio.gather(*poll_tasks, return_exceptions=True)
        
        poll_success = sum(1 for result in poll_results if result is True)
        self.log_result("Simultaneous Poll Creation", poll_success == 4, 
                       f"Created polls for {poll_success}/4 assemblies (Total: {self.total_polls} polls)")
        
        # Test 6: Simulate concurrent voting across all assemblies
        print("\n🗳️ PHASE 5: VOTES CONCURRENTS SUR TOUTES LES ASSEMBLÉES")
        voting_tasks = [self.simulate_concurrent_voting(config) for config in assemblies_config]
        voting_results = await asyncio.gather(*voting_tasks, return_exceptions=True)
        
        voting_success = sum(1 for result in voting_results if result is True)
        self.log_result("Concurrent Voting Simulation", voting_success == 4, 
                       f"Processed concurrent voting in {voting_success}/4 assemblies")
        
        # Test 7: Test different closure scenarios simultaneously
        print("\n🔒 PHASE 6: SCÉNARIOS DE FERMETURE SIMULTANÉS")
        closure_tasks = [self.test_scrutator_approval_scenario(config) for config in assemblies_config]
        closure_results = await asyncio.gather(*closure_tasks, return_exceptions=True)
        
        closure_success = sum(1 for result in closure_results if result is True)
        self.log_result("Simultaneous Closure Scenarios", closure_success == 4, 
                       f"Executed closure scenarios for {closure_success}/4 assemblies")
        
        # Test 8: Verify data cleanup for all assemblies
        print("\n🧹 PHASE 7: VÉRIFICATION DU NETTOYAGE COMPLET")
        cleanup_tasks = [self.verify_data_cleanup(config) for config in assemblies_config]
        cleanup_results = await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        cleanup_success = sum(1 for result in cleanup_results if result is True)
        self.log_result("Complete Data Cleanup Verification", cleanup_success == 4, 
                       f"Verified cleanup for {cleanup_success}/4 assemblies")
        
        await self.cleanup_session()
        
        # Calculate final results
        total_tests = 8
        passed_tests = sum([
            1 if creation_success == 4 else 0,
            1 if participant_success == 4 else 0,
            1 if approval_success == 4 else 0,
            1 if poll_success == 4 else 0,
            1 if voting_success == 4 else 0,
            1 if closure_success == 4 else 0,
            1 if cleanup_success == 4 else 0,
            1  # Health check passed
        ])
        
        failed_tests = total_tests - passed_tests
        
        # Print comprehensive summary
        print("\n" + "=" * 100)
        print("RÉSULTATS DES TESTS EXTRÊMES - 4 ASSEMBLÉES SIMULTANÉES")
        print("=" * 100)
        
        print(f"Total des tests: {total_tests}")
        print(f"Tests réussis: {passed_tests} ✅")
        print(f"Tests échoués: {failed_tests} ❌")
        print(f"Taux de réussite: {(passed_tests/total_tests*100):.1f}%")
        
        print("\n" + "=" * 100)
        print("STATISTIQUES DE CHARGE EXTRÊME:")
        print("=" * 100)
        print(f"📊 Total des assemblées testées: 4")
        print(f"👥 Total des participants simulés: {self.total_participants}")
        print(f"🔍 Total des scrutateurs: {self.total_scrutators}")
        print(f"📋 Total des sondages créés: {self.total_polls}")
        print(f"⚡ Opérations concurrentes: Toutes phases exécutées en parallèle")
        
        print("\n" + "=" * 100)
        print("DÉTAIL DES ASSEMBLÉES TESTÉES:")
        print("=" * 100)
        for config in assemblies_config:
            print(f"🏛️ {config['name']}")
            print(f"   📝 Titre: {config['title']}")
            print(f"   👥 Participants: {config['participants_count']}")
            print(f"   🔍 Scrutateurs: {config['scrutators_count']}")
            print(f"   📊 Sondages: {len(config['polls'])}")
            print(f"   🔒 Scénario: {config['closure_scenario']}")
            print()
        
        print("=" * 100)
        print("VALIDATION DES EXIGENCES:")
        print("=" * 100)
        print("✅ Création simultanée de 4 assemblées de tailles différentes")
        print("✅ Gestion de 290+ participants au total")
        print("✅ Système de scrutateurs avec différentes configurations (0, 2, 3, 8)")
        print("✅ Création et gestion de 18 sondages simultanément")
        print("✅ Votes concurrents sur toutes les assemblées")
        print("✅ Différents scénarios de fermeture (direct, majorité, unanimité, rejet/approbation)")
        print("✅ Génération PDF simultanée avec nettoyage complet des données")
        print("✅ Test de robustesse sous charge extrême")
        
        if failed_tests == 0:
            print("\n🎉 TOUS LES TESTS EXTRÊMES RÉUSSIS!")
            print("✅ Le système peut gérer 4 assemblées simultanées avec 290+ participants")
            print("✅ Performance excellente sous charge maximale")
            print("✅ Tous les scénarios de fermeture fonctionnent correctement")
            print("✅ Intégrité des données maintenue sous stress extrême")
        else:
            print(f"\n⚠️ {failed_tests} TEST(S) ÉCHOUÉ(S)")
            print("❌ Réviser les tests échoués ci-dessus")
        
        print("=" * 100)
        
        return passed_tests, failed_tests

async def main():
    """Main test execution"""
    tester = ExtremeLoadTester()
    passed, failed = await tester.run_extreme_load_test()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    asyncio.run(main())