#!/usr/bin/env python3
"""
TEST DE CHARGE RÉALISTE - 100 PARTICIPANTS SUR 15 MINUTES
Simulation complète d'une assemblée générale avec 100 participants
"""

import requests
import json
import time
import asyncio
import threading
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import concurrent.futures
from dataclasses import dataclass
import statistics

# Configuration
BASE_URL = "https://dffd1ffb-03ba-4c55-8b21-65220fce6f6a.preview.emergentagent.com/api"

@dataclass
class LoadTestMetrics:
    """Métriques de performance pour le test de charge"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: List[float] = None
    errors: List[str] = None
    start_time: datetime = None
    end_time: datetime = None
    
    def __post_init__(self):
        if self.response_times is None:
            self.response_times = []
        if self.errors is None:
            self.errors = []

class RealisticLoadTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.metrics = LoadTestMetrics()
        self.meeting_data = {}
        self.participants = []
        self.polls = []
        self.votes_submitted = []
        
        # Noms français réalistes pour 100 participants
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
        
        # Sujets réalistes d'assemblée générale
        self.realistic_polls = [
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
                "options": ["Priorité maximale", "Priorité élevée", "Priorité moyenne", "Priorité faible", "Pas de priorité"]
            },
            {
                "question": "Approuvez-vous la modification des statuts proposée par le conseil d'administration ?",
                "options": ["J'approuve entièrement", "J'approuve avec réserves", "Je n'approuve pas", "Je m'abstiens"]
            },
            {
                "question": "Quel mode de communication privilégier pour les futures assemblées ?",
                "options": ["Présentiel uniquement", "Hybride (présentiel + visio)", "Visioconférence uniquement", "Indifférent"]
            },
            {
                "question": "Êtes-vous satisfait de la gestion financière de l'organisation cette année ?",
                "options": ["Très satisfait", "Plutôt satisfait", "Plutôt insatisfait", "Très insatisfait", "Ne se prononce pas"]
            },
            {
                "question": "Faut-il renouveler le mandat du commissaire aux comptes actuel ?",
                "options": ["Oui, renouvellement", "Non, changement nécessaire", "Abstention"]
            }
        ]

    def log_metric(self, operation: str, success: bool, response_time: float, error_msg: str = None):
        """Enregistrer une métrique de performance"""
        self.metrics.total_requests += 1
        if success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
            if error_msg:
                self.metrics.errors.append(f"{operation}: {error_msg}")
        
        self.metrics.response_times.append(response_time)
        
        # Log en temps réel
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

    def add_participants_progressively(self):
        """Ajouter 100 participants de manière échelonnée sur 15 minutes"""
        print("\n👥 AJOUT PROGRESSIF DE 100 PARTICIPANTS (15 minutes)")
        print("=" * 50)
        
        if not self.meeting_data:
            print("❌ Pas de données d'assemblée disponibles")
            return False
        
        # Répartir les 100 participants sur 15 minutes (900 secondes)
        # Arrivée échelonnée : 10-15 participants par minute
        total_duration = 900  # 15 minutes en secondes
        participants_per_batch = 5  # 5 participants par lot
        batch_interval = 45  # 45 secondes entre chaque lot
        
        start_time = time.time()
        batch_count = 0
        
        for i in range(0, 100, participants_per_batch):
            batch_count += 1
            batch_participants = self.french_names[i:i+participants_per_batch]
            
            print(f"\n📥 Lot {batch_count}: Ajout de {len(batch_participants)} participants...")
            
            # Ajouter les participants du lot en parallèle
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for name in batch_participants:
                    future = executor.submit(self.add_single_participant, name)
                    futures.append(future)
                
                # Attendre que tous les participants du lot soient ajoutés
                for future in concurrent.futures.as_completed(futures):
                    try:
                        participant = future.result()
                        if participant:
                            self.participants.append(participant)
                    except Exception as e:
                        print(f"❌ Erreur lors de l'ajout d'un participant: {e}")
            
            # Attendre avant le prochain lot (sauf pour le dernier)
            if i + participants_per_batch < 100:
                elapsed = time.time() - start_time
                expected_time = batch_count * batch_interval
                
                if elapsed < expected_time:
                    wait_time = expected_time - elapsed
                    print(f"⏳ Attente de {wait_time:.1f}s avant le prochain lot...")
                    time.sleep(wait_time)
        
        total_time = time.time() - start_time
        print(f"\n✅ {len(self.participants)} participants ajoutés en {total_time:.1f}s")
        return len(self.participants) > 0

    def add_single_participant(self, name: str):
        """Ajouter un seul participant"""
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

    def approve_participants_batch(self):
        """Approuver tous les participants par lots"""
        print("\n✅ APPROBATION EN LOT DES PARTICIPANTS")
        print("=" * 50)
        
        if not self.participants:
            print("❌ Aucun participant à approuver")
            return False
        
        # Approuver par lots de 10
        batch_size = 10
        approved_count = 0
        
        for i in range(0, len(self.participants), batch_size):
            batch = self.participants[i:i+batch_size]
            print(f"📝 Approbation du lot {i//batch_size + 1}: {len(batch)} participants...")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for participant in batch:
                    future = executor.submit(self.approve_single_participant, participant)
                    futures.append(future)
                
                for future in concurrent.futures.as_completed(futures):
                    try:
                        if future.result():
                            approved_count += 1
                    except Exception as e:
                        print(f"❌ Erreur lors de l'approbation: {e}")
            
            # Petite pause entre les lots
            time.sleep(1)
        
        print(f"✅ {approved_count}/{len(self.participants)} participants approuvés")
        return approved_count > 0

    def approve_single_participant(self, participant):
        """Approuver un seul participant"""
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

    def create_realistic_polls(self):
        """Créer 6-7 sondages réalistes"""
        print("\n📊 CRÉATION DES SONDAGES")
        print("=" * 50)
        
        if not self.meeting_data:
            print("❌ Pas de données d'assemblée disponibles")
            return False
        
        # Sélectionner 6 sondages aléatoirement
        selected_polls = random.sample(self.realistic_polls, 6)
        
        for i, poll_data in enumerate(selected_polls, 1):
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
        
        print(f"✅ {len(self.polls)} sondages créés")
        return len(self.polls) > 0

    def simulate_realistic_voting(self):
        """Simuler des votes réalistes sur 15 minutes"""
        print("\n🗳️  SIMULATION DE VOTES RÉALISTES (15 minutes)")
        print("=" * 50)
        
        if not self.polls or not self.participants:
            print("❌ Pas de sondages ou participants disponibles")
            return False
        
        # Démarrer tous les sondages
        for i, poll in enumerate(self.polls, 1):
            try:
                start_time = time.time()
                response = self.session.post(f"{BASE_URL}/polls/{poll['id']}/start")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    self.log_metric(f"Démarrage sondage {i}", True, response_time)
                    print(f"▶️  Sondage {i} démarré")
                else:
                    self.log_metric(f"Démarrage sondage {i}", False, response_time, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_metric(f"Démarrage sondage {i}", False, 0, str(e))
        
        # Simulation de votes réalistes
        # Pas tous les participants votent sur tous les sondages (70-90% de participation)
        voting_duration = 900  # 15 minutes
        start_time = time.time()
        
        total_votes = 0
        
        for poll_index, poll in enumerate(self.polls):
            print(f"\n🗳️  Votes pour le sondage {poll_index + 1}...")
            
            # Participation variable (70-90%)
            participation_rate = random.uniform(0.70, 0.90)
            voting_participants = random.sample(self.participants, int(len(self.participants) * participation_rate))
            
            # Répartir les votes sur plusieurs vagues
            votes_per_wave = 15  # 15 votes simultanés maximum
            
            for i in range(0, len(voting_participants), votes_per_wave):
                wave_participants = voting_participants[i:i+votes_per_wave]
                
                # Votes simultanés pour cette vague
                with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
                    futures = []
                    for participant in wave_participants:
                        # Choix d'option réaliste (distribution non uniforme)
                        option_weights = self.get_realistic_option_weights(len(poll['options']))
                        chosen_option = random.choices(poll['options'], weights=option_weights)[0]
                        
                        future = executor.submit(self.submit_vote, poll['id'], chosen_option['id'], participant['name'])
                        futures.append(future)
                    
                    for future in concurrent.futures.as_completed(futures):
                        try:
                            if future.result():
                                total_votes += 1
                        except Exception as e:
                            print(f"❌ Erreur lors du vote: {e}")
                
                # Pause entre les vagues
                time.sleep(random.uniform(2, 5))
            
            # Pause entre les sondages
            time.sleep(random.uniform(5, 10))
        
        # Fermer tous les sondages
        for i, poll in enumerate(self.polls, 1):
            try:
                start_time = time.time()
                response = self.session.post(f"{BASE_URL}/polls/{poll['id']}/close")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    self.log_metric(f"Fermeture sondage {i}", True, response_time)
                    print(f"⏹️  Sondage {i} fermé")
                else:
                    self.log_metric(f"Fermeture sondage {i}", False, response_time, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_metric(f"Fermeture sondage {i}", False, 0, str(e))
        
        total_time = time.time() - start_time
        print(f"\n✅ {total_votes} votes soumis en {total_time:.1f}s")
        return total_votes > 0

    def get_realistic_option_weights(self, num_options):
        """Générer des poids réalistes pour les options (distribution non uniforme)"""
        if num_options == 2:
            return [0.6, 0.4]  # Légère préférence pour la première option
        elif num_options == 3:
            return [0.5, 0.3, 0.2]  # Distribution décroissante
        elif num_options == 4:
            return [0.4, 0.3, 0.2, 0.1]
        elif num_options == 5:
            return [0.3, 0.25, 0.2, 0.15, 0.1]
        else:
            # Distribution uniforme par défaut
            return [1.0/num_options] * num_options

    def submit_vote(self, poll_id: str, option_id: str, voter_name: str):
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
                self.log_metric(f"Vote {voter_name}", True, response_time)
                return True
            else:
                self.log_metric(f"Vote {voter_name}", False, response_time, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_metric(f"Vote {voter_name}", False, 0, str(e))
            return False

    def test_pdf_generation_with_large_dataset(self):
        """Tester la génération PDF avec un gros volume de données"""
        print("\n📄 GÉNÉRATION PDF AVEC GROS VOLUME DE DONNÉES")
        print("=" * 50)
        
        if not self.meeting_data:
            print("❌ Pas de données d'assemblée disponibles")
            return False
        
        try:
            print("🔄 Génération du rapport PDF en cours...")
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/meetings/{self.meeting_data['id']}/report")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'application/pdf' in content_type:
                    file_size = len(response.content)
                    self.log_metric("Génération PDF", True, response_time)
                    print(f"✅ PDF généré avec succès:")
                    print(f"   📊 Taille: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                    print(f"   ⏱️  Temps: {response_time:.3f}s")
                    print(f"   👥 Participants: {len(self.participants)}")
                    print(f"   📋 Sondages: {len(self.polls)}")
                    return True
                else:
                    self.log_metric("Génération PDF", False, response_time, f"Type de contenu incorrect: {content_type}")
                    return False
            else:
                self.log_metric("Génération PDF", False, response_time, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_metric("Génération PDF", False, 0, str(e))
            return False

    def verify_data_deletion(self):
        """Vérifier la suppression complète des données"""
        print("\n🗑️  VÉRIFICATION DE LA SUPPRESSION DES DONNÉES")
        print("=" * 50)
        
        if not self.meeting_data:
            print("❌ Pas de données d'assemblée disponibles")
            return False
        
        deletion_verified = True
        
        # Vérifier que l'assemblée est supprimée
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/meetings/{self.meeting_data['meeting_code']}")
            response_time = time.time() - start_time
            
            if response.status_code == 404:
                self.log_metric("Vérification suppression assemblée", True, response_time)
                print("✅ Assemblée correctement supprimée")
            else:
                self.log_metric("Vérification suppression assemblée", False, response_time, f"HTTP {response.status_code}")
                deletion_verified = False
        except Exception as e:
            self.log_metric("Vérification suppression assemblée", False, 0, str(e))
            deletion_verified = False
        
        # Vérifier que les participants sont supprimés (échantillon)
        sample_participants = random.sample(self.participants, min(10, len(self.participants)))
        for participant in sample_participants:
            try:
                start_time = time.time()
                response = self.session.get(f"{BASE_URL}/participants/{participant['id']}/status")
                response_time = time.time() - start_time
                
                if response.status_code == 404:
                    self.log_metric(f"Vérification suppression {participant['name']}", True, response_time)
                else:
                    self.log_metric(f"Vérification suppression {participant['name']}", False, response_time, f"HTTP {response.status_code}")
                    deletion_verified = False
            except Exception as e:
                self.log_metric(f"Vérification suppression {participant['name']}", False, 0, str(e))
                deletion_verified = False
        
        # Vérifier que les sondages sont supprimés (échantillon)
        sample_polls = random.sample(self.polls, min(3, len(self.polls)))
        for i, poll in enumerate(sample_polls, 1):
            try:
                start_time = time.time()
                response = self.session.get(f"{BASE_URL}/polls/{poll['id']}/results")
                response_time = time.time() - start_time
                
                if response.status_code == 404:
                    self.log_metric(f"Vérification suppression sondage {i}", True, response_time)
                else:
                    self.log_metric(f"Vérification suppression sondage {i}", False, response_time, f"HTTP {response.status_code}")
                    deletion_verified = False
            except Exception as e:
                self.log_metric(f"Vérification suppression sondage {i}", False, 0, str(e))
                deletion_verified = False
        
        if deletion_verified:
            print("✅ Suppression complète des données vérifiée")
        else:
            print("❌ Problèmes détectés lors de la suppression")
        
        return deletion_verified

    def generate_performance_report(self):
        """Générer un rapport détaillé des performances"""
        print("\n📈 RAPPORT DE PERFORMANCE DÉTAILLÉ")
        print("=" * 60)
        
        if not self.metrics.response_times:
            print("❌ Aucune donnée de performance disponible")
            return
        
        # Calculs statistiques
        response_times = self.metrics.response_times
        avg_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
        p99_time = sorted(response_times)[int(len(response_times) * 0.99)]
        
        total_duration = (self.metrics.end_time - self.metrics.start_time).total_seconds()
        requests_per_second = self.metrics.total_requests / total_duration if total_duration > 0 else 0
        
        success_rate = (self.metrics.successful_requests / self.metrics.total_requests * 100) if self.metrics.total_requests > 0 else 0
        
        print(f"🎯 MÉTRIQUES GLOBALES:")
        print(f"   📊 Total requêtes: {self.metrics.total_requests:,}")
        print(f"   ✅ Succès: {self.metrics.successful_requests:,} ({success_rate:.1f}%)")
        print(f"   ❌ Échecs: {self.metrics.failed_requests:,}")
        print(f"   ⏱️  Durée totale: {total_duration:.1f}s")
        print(f"   🚀 Requêtes/seconde: {requests_per_second:.2f}")
        
        print(f"\n⏱️  TEMPS DE RÉPONSE:")
        print(f"   📊 Moyenne: {avg_time:.3f}s")
        print(f"   📊 Médiane: {median_time:.3f}s")
        print(f"   📊 Minimum: {min_time:.3f}s")
        print(f"   📊 Maximum: {max_time:.3f}s")
        print(f"   📊 95e percentile: {p95_time:.3f}s")
        print(f"   📊 99e percentile: {p99_time:.3f}s")
        
        print(f"\n👥 DONNÉES DE CHARGE:")
        print(f"   👤 Participants ajoutés: {len(self.participants)}")
        print(f"   📋 Sondages créés: {len(self.polls)}")
        print(f"   🗳️  Votes estimés: {len([m for m in self.metrics.response_times if 'Vote' in str(m)])}")
        
        if self.metrics.errors:
            print(f"\n❌ ERREURS DÉTECTÉES ({len(self.metrics.errors)}):")
            for error in self.metrics.errors[:10]:  # Afficher les 10 premières erreurs
                print(f"   • {error}")
            if len(self.metrics.errors) > 10:
                print(f"   ... et {len(self.metrics.errors) - 10} autres erreurs")
        
        # Évaluation de la robustesse
        print(f"\n🏆 ÉVALUATION DE LA ROBUSTESSE:")
        if success_rate >= 95 and avg_time <= 1.0 and max_time <= 5.0:
            print("   ✅ EXCELLENT - Système très robuste")
        elif success_rate >= 90 and avg_time <= 2.0 and max_time <= 10.0:
            print("   ✅ BON - Système robuste")
        elif success_rate >= 80 and avg_time <= 5.0:
            print("   ⚠️  ACCEPTABLE - Quelques améliorations nécessaires")
        else:
            print("   ❌ PROBLÉMATIQUE - Optimisations requises")

    def run_complete_load_test(self):
        """Exécuter le test de charge complet"""
        print("🚀 DÉMARRAGE DU TEST DE CHARGE RÉALISTE")
        print("🎯 100 PARTICIPANTS - 15 MINUTES - ASSEMBLÉE GÉNÉRALE 2025")
        print("=" * 70)
        
        self.metrics.start_time = datetime.now()
        
        # Étapes du test
        steps = [
            ("Création de l'assemblée", self.create_meeting),
            ("Ajout progressif des participants", self.add_participants_progressively),
            ("Approbation en lot", self.approve_participants_batch),
            ("Création des sondages", self.create_realistic_polls),
            ("Simulation de votes réalistes", self.simulate_realistic_voting),
            ("Génération PDF avec gros volume", self.test_pdf_generation_with_large_dataset),
            ("Vérification suppression données", self.verify_data_deletion)
        ]
        
        results = {}
        
        for step_name, step_func in steps:
            print(f"\n🔄 {step_name.upper()}")
            print("-" * 50)
            
            try:
                step_start = time.time()
                result = step_func()
                step_duration = time.time() - step_start
                
                results[step_name] = {
                    'success': result,
                    'duration': step_duration
                }
                
                if result:
                    print(f"✅ {step_name} terminé avec succès ({step_duration:.1f}s)")
                else:
                    print(f"❌ {step_name} a échoué ({step_duration:.1f}s)")
                    
            except Exception as e:
                print(f"❌ Erreur critique dans {step_name}: {e}")
                results[step_name] = {
                    'success': False,
                    'duration': 0,
                    'error': str(e)
                }
        
        self.metrics.end_time = datetime.now()
        
        # Rapport final
        print("\n" + "=" * 70)
        print("🏁 RÉSULTATS DU TEST DE CHARGE")
        print("=" * 70)
        
        successful_steps = sum(1 for r in results.values() if r['success'])
        total_steps = len(results)
        
        print(f"📊 Étapes réussies: {successful_steps}/{total_steps}")
        
        for step_name, result in results.items():
            status = "✅" if result['success'] else "❌"
            print(f"{status} {step_name}: {result['duration']:.1f}s")
        
        # Rapport de performance détaillé
        self.generate_performance_report()
        
        # Conclusion
        if successful_steps == total_steps:
            print("\n🎉 TEST DE CHARGE RÉUSSI!")
            print("✅ Le système est robuste et peut gérer 100 participants")
        else:
            print(f"\n⚠️  TEST PARTIELLEMENT RÉUSSI ({successful_steps}/{total_steps})")
            print("🔧 Certaines optimisations peuvent être nécessaires")
        
        return successful_steps == total_steps

def main():
    """Fonction principale"""
    tester = RealisticLoadTester()
    success = tester.run_complete_load_test()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)