#!/usr/bin/env python3
"""
TEST DE CHARGE CONDENSÉ - 100 PARTICIPANTS (VERSION RAPIDE)
Version accélérée du test de charge pour validation immédiate
"""

import requests
import json
import time
import random
from datetime import datetime
from typing import Dict, List
import concurrent.futures
import statistics

# Configuration
BASE_URL = "https://7ec35474-0815-47b0-a5a7-33937258cf82.preview.emergentagent.com/api"

class QuickLoadTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': [],
            'errors': []
        }
        self.meeting_data = {}
        self.participants = []
        self.polls = []
        
        # Noms français pour 100 participants
        self.french_names = [
            "Jean Dupont", "Marie Martin", "Pierre Durand", "Claire Moreau", "Antoine Bernard",
            "Sophie Lefebvre", "Michel Rousseau", "Isabelle Petit", "François Garnier", "Catherine Leroy",
            "Nicolas Roux", "Sylvie Fournier", "Alain Girard", "Monique Bonnet", "Philippe Mercier",
            "Nathalie Blanc", "Thierry Lambert", "Véronique Fabre", "Christophe Morel", "Brigitte Barbier",
            "Stéphane Leroux", "Martine Chevalier", "Olivier Joly", "Françoise Meunier", "Patrice Robin",
            "Corinne Gautier", "Didier Muller", "Chantal Bertrand", "Frédéric Lefevre", "Dominique Moreau",
            "Sébastien Roche", "Pascale Giraud", "Laurent Andre", "Valérie Prevost", "Hervé Marchand",
            "Sandrine Perrin", "Yves Morin", "Karine Clement", "Bruno Masson", "Céline Bourgeois",
            "Gérard Fontaine", "Jacqueline Roussel", "Daniel Leclerc", "Annie Legrand", "Claude Gauthier",
            "Michèle Dumont", "René Delaunay", "Josette Dufour", "Marcel Lemaire", "Odette Carpentier",
            "Roger Brun", "Simone Benoit", "Henri Caron", "Denise Guillot", "André Renard",
            "Paulette Picard", "Louis Blanchard", "Georgette Vidal", "Albert Fleury", "Jeannine Maillard",
            "Paul Lecomte", "Lucienne Gaillard", "Fernand Hubert", "Raymonde Berger", "Maurice Lacroix",
            "Yvette Collet", "Lucien Charpentier", "Suzanne Boucher", "Émile Vasseur", "Madeleine Menard",
            "Gaston Leblanc", "Berthe Rolland", "Armand Cousin", "Henriette Leconte", "Léon Bouchet",
            "Germaine Leclercq", "Eugène Mallet", "Marthe Gros", "Alphonse Benard", "Léonie Humbert",
            "Édouard Poulain", "Marguerite Lemoine", "Raoul Tessier", "Jeanne Chevallier", "Camille Perrot",
            "Blanche Reynaud", "Julien Guyot", "Augustine Barre", "Émilien Masse", "Célestine Bruneau",
            "Firmin Jamin", "Ernestine Pichon", "Désiré Marin", "Léontine Legros", "Aristide Salmon",
            "Philomène Bertin", "Honoré Lemaitre", "Victorine Pons", "Théophile Lejeune", "Alexandrine Roy"
        ]

    def log_metric(self, operation: str, success: bool, response_time: float, error_msg: str = None):
        """Enregistrer une métrique"""
        self.metrics['total_requests'] += 1
        if success:
            self.metrics['successful_requests'] += 1
        else:
            self.metrics['failed_requests'] += 1
            if error_msg:
                self.metrics['errors'].append(f"{operation}: {error_msg}")
        
        self.metrics['response_times'].append(response_time)
        
        status = "✅" if success else "❌"
        print(f"{status} {operation}: {response_time:.3f}s" + (f" - {error_msg}" if error_msg else ""))

    def create_meeting(self):
        """Créer l'assemblée générale"""
        print("🏛️  CRÉATION DE L'ASSEMBLÉE GÉNÉRALE")
        print("=" * 50)
        
        meeting_data = {
            "title": "Assemblée Générale Annuelle 2025",
            "organizer_name": "Alice Dupont"
        }
        
        try:
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/meetings", json=meeting_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.meeting_data = response.json()
                self.log_metric("Création assemblée", True, response_time)
                print(f"📋 Assemblée créée - Code: {self.meeting_data['meeting_code']}")
                return True
            else:
                self.log_metric("Création assemblée", False, response_time, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_metric("Création assemblée", False, 0, str(e))
            return False

    def add_100_participants_fast(self):
        """Ajouter 100 participants rapidement avec concurrence"""
        print("\n👥 AJOUT RAPIDE DE 100 PARTICIPANTS")
        print("=" * 50)
        
        if not self.meeting_data:
            print("❌ Pas de données d'assemblée disponibles")
            return False
        
        start_time = time.time()
        
        # Ajouter par lots de 20 participants en parallèle
        batch_size = 20
        for i in range(0, 100, batch_size):
            batch_names = self.french_names[i:i+batch_size]
            print(f"📥 Ajout du lot {i//batch_size + 1}: {len(batch_names)} participants...")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                futures = []
                for name in batch_names:
                    future = executor.submit(self.add_single_participant, name)
                    futures.append(future)
                
                for future in concurrent.futures.as_completed(futures):
                    try:
                        participant = future.result()
                        if participant:
                            self.participants.append(participant)
                    except Exception as e:
                        print(f"❌ Erreur: {e}")
        
        total_time = time.time() - start_time
        print(f"✅ {len(self.participants)} participants ajoutés en {total_time:.1f}s")
        return len(self.participants) >= 95  # Au moins 95% de succès

    def add_single_participant(self, name: str):
        """Ajouter un participant"""
        try:
            join_data = {
                "name": name,
                "meeting_code": self.meeting_data['meeting_code']
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/participants/join", json=join_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                participant = response.json()
                self.log_metric(f"Ajout {name}", True, response_time)
                return participant
            else:
                self.log_metric(f"Ajout {name}", False, response_time, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_metric(f"Ajout {name}", False, 0, str(e))
            return None

    def approve_all_participants_fast(self):
        """Approuver tous les participants rapidement"""
        print("\n✅ APPROBATION RAPIDE DE TOUS LES PARTICIPANTS")
        print("=" * 50)
        
        if not self.participants:
            return False
        
        start_time = time.time()
        approved_count = 0
        
        # Approuver par lots de 25
        batch_size = 25
        for i in range(0, len(self.participants), batch_size):
            batch = self.participants[i:i+batch_size]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
                futures = []
                for participant in batch:
                    future = executor.submit(self.approve_participant, participant)
                    futures.append(future)
                
                for future in concurrent.futures.as_completed(futures):
                    try:
                        if future.result():
                            approved_count += 1
                    except Exception as e:
                        print(f"❌ Erreur approbation: {e}")
        
        total_time = time.time() - start_time
        print(f"✅ {approved_count}/{len(self.participants)} participants approuvés en {total_time:.1f}s")
        return approved_count >= len(self.participants) * 0.95

    def approve_participant(self, participant):
        """Approuver un participant"""
        try:
            approval_data = {
                "participant_id": participant['id'],
                "approved": True
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/participants/{participant['id']}/approve", json=approval_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_metric(f"Approbation {participant['name']}", True, response_time)
                return True
            else:
                self.log_metric(f"Approbation {participant['name']}", False, response_time, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_metric(f"Approbation {participant['name']}", False, 0, str(e))
            return False

    def create_6_polls(self):
        """Créer 6 sondages réalistes"""
        print("\n📊 CRÉATION DE 6 SONDAGES")
        print("=" * 50)
        
        polls_data = [
            {
                "question": "Approuvez-vous l'augmentation du budget annuel de 15% pour l'année 2025 ?",
                "options": ["Oui, j'approuve", "Non, je m'oppose", "Je m'abstiens", "Je demande plus d'informations"]
            },
            {
                "question": "Êtes-vous favorable à la création d'un nouveau poste de directeur adjoint ?",
                "options": ["Très favorable", "Plutôt favorable", "Plutôt défavorable", "Très défavorable", "Sans opinion"]
            },
            {
                "question": "Quelle priorité donner aux investissements technologiques cette année ?",
                "options": ["Priorité maximale", "Priorité élevée", "Priorité moyenne", "Priorité faible"]
            },
            {
                "question": "Approuvez-vous la modification des statuts proposée ?",
                "options": ["J'approuve entièrement", "J'approuve avec réserves", "Je n'approuve pas", "Je m'abstiens"]
            },
            {
                "question": "Quel mode de communication privilégier pour les futures assemblées ?",
                "options": ["Présentiel uniquement", "Hybride (présentiel + visio)", "Visioconférence uniquement"]
            },
            {
                "question": "Êtes-vous satisfait de la gestion financière cette année ?",
                "options": ["Très satisfait", "Plutôt satisfait", "Plutôt insatisfait", "Très insatisfait"]
            }
        ]
        
        for i, poll_data in enumerate(polls_data, 1):
            try:
                start_time = time.time()
                response = self.session.post(f"{BASE_URL}/meetings/{self.meeting_data['id']}/polls", json=poll_data)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    poll = response.json()
                    self.polls.append(poll)
                    self.log_metric(f"Création sondage {i}", True, response_time)
                    print(f"📋 Sondage {i}: {poll_data['question'][:50]}...")
                else:
                    self.log_metric(f"Création sondage {i}", False, response_time, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_metric(f"Création sondage {i}", False, 0, str(e))
        
        return len(self.polls) >= 5

    def simulate_concurrent_voting(self):
        """Simuler des votes concurrents sur tous les sondages"""
        print("\n🗳️  SIMULATION DE VOTES CONCURRENTS")
        print("=" * 50)
        
        if not self.polls or not self.participants:
            return False
        
        # Démarrer tous les sondages
        for i, poll in enumerate(self.polls, 1):
            try:
                start_time = time.time()
                response = self.session.post(f"{BASE_URL}/polls/{poll['id']}/start")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    self.log_metric(f"Démarrage sondage {i}", True, response_time)
                else:
                    self.log_metric(f"Démarrage sondage {i}", False, response_time, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_metric(f"Démarrage sondage {i}", False, 0, str(e))
        
        # Simuler des votes concurrents
        total_votes = 0
        start_time = time.time()
        
        for poll_index, poll in enumerate(self.polls):
            print(f"🗳️  Votes pour le sondage {poll_index + 1}...")
            
            # 70-90% de participation par sondage
            participation_rate = random.uniform(0.70, 0.90)
            voting_participants = random.sample(self.participants, int(len(self.participants) * participation_rate))
            
            # Votes par vagues de 20 simultanés
            batch_size = 20
            for i in range(0, len(voting_participants), batch_size):
                batch = voting_participants[i:i+batch_size]
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                    futures = []
                    for participant in batch:
                        # Choix d'option aléatoire pondéré
                        option_weights = [0.4, 0.3, 0.2, 0.1][:len(poll['options'])]
                        chosen_option = random.choices(poll['options'], weights=option_weights)[0]
                        
                        future = executor.submit(self.submit_vote, poll['id'], chosen_option['id'])
                        futures.append(future)
                    
                    for future in concurrent.futures.as_completed(futures):
                        try:
                            if future.result():
                                total_votes += 1
                        except Exception as e:
                            pass
        
        # Fermer tous les sondages
        for i, poll in enumerate(self.polls, 1):
            try:
                start_time = time.time()
                response = self.session.post(f"{BASE_URL}/polls/{poll['id']}/close")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    self.log_metric(f"Fermeture sondage {i}", True, response_time)
                else:
                    self.log_metric(f"Fermeture sondage {i}", False, response_time, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_metric(f"Fermeture sondage {i}", False, 0, str(e))
        
        total_time = time.time() - start_time
        print(f"✅ {total_votes} votes soumis en {total_time:.1f}s")
        return total_votes > 0

    def submit_vote(self, poll_id: str, option_id: str):
        """Soumettre un vote"""
        try:
            vote_data = {
                "poll_id": poll_id,
                "option_id": option_id
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/votes", json=vote_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_metric("Vote", True, response_time)
                return True
            else:
                self.log_metric("Vote", False, response_time, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_metric("Vote", False, 0, str(e))
            return False

    def test_pdf_generation_large_data(self):
        """Tester génération PDF avec gros volume"""
        print("\n📄 GÉNÉRATION PDF AVEC 100 PARTICIPANTS")
        print("=" * 50)
        
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/meetings/{self.meeting_data['id']}/report")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'application/pdf' in content_type:
                    file_size = len(response.content)
                    self.log_metric("Génération PDF", True, response_time)
                    print(f"✅ PDF généré:")
                    print(f"   📊 Taille: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                    print(f"   ⏱️  Temps: {response_time:.3f}s")
                    print(f"   👥 Participants: {len(self.participants)}")
                    print(f"   📋 Sondages: {len(self.polls)}")
                    return True
                else:
                    self.log_metric("Génération PDF", False, response_time, f"Type incorrect: {content_type}")
                    return False
            else:
                self.log_metric("Génération PDF", False, response_time, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_metric("Génération PDF", False, 0, str(e))
            return False

    def verify_complete_deletion(self):
        """Vérifier suppression complète"""
        print("\n🗑️  VÉRIFICATION SUPPRESSION COMPLÈTE")
        print("=" * 50)
        
        deletion_ok = True
        
        # Vérifier assemblée supprimée
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/meetings/{self.meeting_data['meeting_code']}")
            response_time = time.time() - start_time
            
            if response.status_code == 404:
                self.log_metric("Vérification assemblée supprimée", True, response_time)
            else:
                self.log_metric("Vérification assemblée supprimée", False, response_time, f"HTTP {response.status_code}")
                deletion_ok = False
        except Exception as e:
            self.log_metric("Vérification assemblée supprimée", False, 0, str(e))
            deletion_ok = False
        
        # Vérifier échantillon de participants supprimés
        sample_size = min(10, len(self.participants))
        sample_participants = random.sample(self.participants, sample_size)
        
        for participant in sample_participants:
            try:
                start_time = time.time()
                response = self.session.get(f"{BASE_URL}/participants/{participant['id']}/status")
                response_time = time.time() - start_time
                
                if response.status_code == 404:
                    self.log_metric(f"Participant {participant['name']} supprimé", True, response_time)
                else:
                    self.log_metric(f"Participant {participant['name']} supprimé", False, response_time, f"HTTP {response.status_code}")
                    deletion_ok = False
            except Exception as e:
                self.log_metric(f"Participant {participant['name']} supprimé", False, 0, str(e))
                deletion_ok = False
        
        return deletion_ok

    def generate_performance_report(self):
        """Générer rapport de performance"""
        print("\n📈 RAPPORT DE PERFORMANCE")
        print("=" * 50)
        
        if not self.metrics['response_times']:
            print("❌ Pas de données")
            return
        
        times = self.metrics['response_times']
        avg_time = statistics.mean(times)
        max_time = max(times)
        min_time = min(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        
        success_rate = (self.metrics['successful_requests'] / self.metrics['total_requests'] * 100) if self.metrics['total_requests'] > 0 else 0
        
        print(f"📊 MÉTRIQUES:")
        print(f"   Total requêtes: {self.metrics['total_requests']:,}")
        print(f"   Succès: {self.metrics['successful_requests']:,} ({success_rate:.1f}%)")
        print(f"   Échecs: {self.metrics['failed_requests']:,}")
        print(f"   Temps moyen: {avg_time:.3f}s")
        print(f"   Temps max: {max_time:.3f}s")
        print(f"   95e percentile: {p95_time:.3f}s")
        
        print(f"\n👥 DONNÉES:")
        print(f"   Participants: {len(self.participants)}")
        print(f"   Sondages: {len(self.polls)}")
        
        if self.metrics['errors']:
            print(f"\n❌ ERREURS ({len(self.metrics['errors'])}):")
            for error in self.metrics['errors'][:5]:
                print(f"   • {error}")
        
        # Évaluation
        if success_rate >= 95 and avg_time <= 1.0 and max_time <= 5.0:
            print("\n🏆 ÉVALUATION: ✅ EXCELLENT - Système très robuste")
        elif success_rate >= 90 and avg_time <= 2.0:
            print("\n🏆 ÉVALUATION: ✅ BON - Système robuste")
        elif success_rate >= 80:
            print("\n🏆 ÉVALUATION: ⚠️  ACCEPTABLE - Améliorations possibles")
        else:
            print("\n🏆 ÉVALUATION: ❌ PROBLÉMATIQUE - Optimisations requises")

    def run_quick_load_test(self):
        """Exécuter le test de charge rapide"""
        print("🚀 TEST DE CHARGE RAPIDE - 100 PARTICIPANTS")
        print("🎯 ASSEMBLÉE GÉNÉRALE ANNUELLE 2025")
        print("=" * 60)
        
        start_time = time.time()
        
        steps = [
            ("Création assemblée", self.create_meeting),
            ("Ajout 100 participants", self.add_100_participants_fast),
            ("Approbation participants", self.approve_all_participants_fast),
            ("Création 6 sondages", self.create_6_polls),
            ("Votes concurrents", self.simulate_concurrent_voting),
            ("Génération PDF", self.test_pdf_generation_large_data),
            ("Vérification suppression", self.verify_complete_deletion)
        ]
        
        results = {}
        
        for step_name, step_func in steps:
            print(f"\n🔄 {step_name.upper()}")
            print("-" * 40)
            
            try:
                step_start = time.time()
                result = step_func()
                step_duration = time.time() - step_start
                
                results[step_name] = {
                    'success': result,
                    'duration': step_duration
                }
                
                status = "✅" if result else "❌"
                print(f"{status} {step_name} terminé ({step_duration:.1f}s)")
                
            except Exception as e:
                print(f"❌ Erreur dans {step_name}: {e}")
                results[step_name] = {'success': False, 'duration': 0}
        
        total_time = time.time() - start_time
        
        # Résultats finaux
        print("\n" + "=" * 60)
        print("🏁 RÉSULTATS DU TEST DE CHARGE")
        print("=" * 60)
        
        successful_steps = sum(1 for r in results.values() if r['success'])
        total_steps = len(results)
        
        print(f"📊 Étapes réussies: {successful_steps}/{total_steps}")
        print(f"⏱️  Durée totale: {total_time:.1f}s")
        
        for step_name, result in results.items():
            status = "✅" if result['success'] else "❌"
            print(f"{status} {step_name}: {result['duration']:.1f}s")
        
        self.generate_performance_report()
        
        if successful_steps == total_steps:
            print("\n🎉 TEST DE CHARGE RÉUSSI!")
            print("✅ Le système peut gérer 100 participants avec succès")
        else:
            print(f"\n⚠️  TEST PARTIELLEMENT RÉUSSI ({successful_steps}/{total_steps})")
        
        return successful_steps == total_steps

def main():
    tester = QuickLoadTester()
    success = tester.run_quick_load_test()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)