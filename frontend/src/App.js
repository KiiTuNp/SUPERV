import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Badge } from "./components/ui/badge";
import { Progress } from "./components/ui/progress";
import { Separator } from "./components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Switch } from "./components/ui/switch";
import { CheckCircle, Clock, Users, Vote, AlertCircle, Play, Square, Download, FileText, Settings, UserPlus, Sparkles, Shield, BarChart3, Timer } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

console.log("🔍 Environment loaded:", { BACKEND_URL, API });

function App() {
  const [currentView, setCurrentView] = useState("home");
  const [meeting, setMeeting] = useState(null);
  const [participant, setParticipant] = useState(null);
  const [ws, setWs] = useState(null);
  const [meetingClosed, setMeetingClosed] = useState(false);
  const [closedMeetingInfo, setClosedMeetingInfo] = useState(null);
  const [redirectCountdown, setRedirectCountdown] = useState(10);
  const [isScrutator, setIsScrutator] = useState(false);  // Indique si l'utilisateur connecté est un scrutateur
  const [scrutatorName, setScrutatorName] = useState('');  // Nom du scrutateur connecté

  // Report generation voting states
  const [showReportVoteModal, setShowReportVoteModal] = useState(false);
  const [reportVoteData, setReportVoteData] = useState(null);
  const [reportGenerationInProgress, setReportGenerationInProgress] = useState(false);

  // Particle background effect
  useEffect(() => {
    const createParticle = () => {
      const particle = document.createElement('div');
      particle.className = 'particle';
      particle.style.left = Math.random() * 100 + 'vw';
      particle.style.width = Math.random() * 4 + 2 + 'px';
      particle.style.height = particle.style.width;
      particle.style.animationDuration = Math.random() * 3 + 3 + 's';
      particle.style.animationDelay = Math.random() * 2 + 's';
      
      document.body.appendChild(particle);
      
      setTimeout(() => {
        if (particle.parentNode) {
          particle.parentNode.removeChild(particle);
        }
      }, 6000);
    };

    const particleInterval = setInterval(createParticle, 300);
    return () => clearInterval(particleInterval);
  }, []);

  // Home Component - Modern Design
  const Home = () => {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 bg-pattern-dots flex items-center justify-center p-4">
        <div className="w-full max-w-6xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <div className="hero-animate inline-block mb-6">
              <div className="w-24 h-24 mx-auto bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl flex items-center justify-center shadow-lg">
                <Vote className="w-12 h-12 text-white" />
              </div>
            </div>
            <h1 className="text-5xl md:text-7xl font-black text-modern-heading gradient-text mb-4">
              Vote Secret
            </h1>
            <p className="text-xl md:text-2xl text-modern-body max-w-3xl mx-auto mb-12">
              Système de vote anonyme moderne pour assemblées avec suppression automatique des données
            </p>
          </div>

          {/* Main Actions */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Participant Action - Prominent */}
            <div className="order-1 lg:order-1">
              <Card className="glass-card-strong border-0 shadow-2xl overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-blue-600 to-blue-700 text-white pb-8">
                  <div className="flex items-center justify-center mb-4">
                    <UserPlus className="w-12 h-12" />
                  </div>
                  <CardTitle className="text-2xl md:text-3xl font-bold text-center">
                    Rejoindre une Réunion
                  </CardTitle>
                  <CardDescription className="text-blue-100 text-center text-lg">
                    Participez à un vote avec votre code de réunion
                  </CardDescription>
                </CardHeader>
                <CardContent className="p-8">
                  <div className="space-y-4 mb-6">
                    <div className="flex items-center gap-3 text-slate-600">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-blue-600 font-bold text-sm">1</span>
                      </div>
                      <span>Entrez votre nom et le code de réunion</span>
                    </div>
                    <div className="flex items-center gap-3 text-slate-600">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-blue-600 font-bold text-sm">2</span>
                      </div>
                      <span>Attendez l'approbation de l'organisateur</span>
                    </div>
                    <div className="flex items-center gap-3 text-slate-600">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-blue-600 font-bold text-sm">3</span>
                      </div>
                      <span>Votez en toute confidentialité</span>
                    </div>
                  </div>
                  <Button 
                    onClick={() => setCurrentView("join")} 
                    className="w-full h-14 text-lg font-bold btn-gradient-primary"
                  >
                    <UserPlus className="w-6 h-6 mr-2" />
                    Rejoindre Maintenant
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Organizer Action - Elegant and Discrete */}
            <div className="order-2 lg:order-2">
              <Card className="glass-card border-0 shadow-xl hover:shadow-2xl transition-all duration-300 overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-slate-500 to-slate-600 text-white relative">
                  <div className="absolute inset-0 bg-white bg-opacity-10"></div>
                  <div className="relative z-10">
                    <div className="flex items-center justify-center mb-3">
                      <div className="w-10 h-10 bg-white bg-opacity-20 rounded-xl flex items-center justify-center">
                        <Settings className="w-6 h-6" />
                      </div>
                    </div>
                    <CardTitle className="text-xl font-bold text-center">
                      Interface Organisateur
                    </CardTitle>
                    <CardDescription className="text-slate-200 text-center">
                      Créez et gérez votre réunion de vote
                    </CardDescription>
                  </div>
                </CardHeader>
                <CardContent className="p-6 bg-gradient-to-br from-white to-slate-50">
                  <div className="space-y-3 mb-6 text-sm">
                    <div className="flex items-center gap-3 text-slate-700 p-2 rounded-lg bg-gradient-to-r from-blue-50 to-blue-100">
                      <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center">
                        <Vote className="w-3 h-3 text-white" />
                      </div>
                      <span className="font-medium">Créer des sondages</span>
                    </div>
                    <div className="flex items-center gap-3 text-slate-700 p-2 rounded-lg bg-gradient-to-r from-blue-50 to-blue-100">
                      <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center">
                        <Users className="w-3 h-3 text-white" />
                      </div>
                      <span className="font-medium">Gérer les participants</span>
                    </div>
                    <div className="flex items-center gap-3 text-slate-700 p-2 rounded-lg bg-gradient-to-r from-blue-50 to-blue-100">
                      <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center">
                        <FileText className="w-3 h-3 text-white" />
                      </div>
                      <span className="font-medium">Générer le rapport</span>
                    </div>
                  </div>
                  <Button 
                    onClick={() => setCurrentView("create")} 
                    variant="outline" 
                    className="w-full h-12 border-2 border-blue-200 hover:bg-gradient-to-r hover:from-blue-500 hover:to-blue-600 hover:text-white hover:border-transparent transition-all duration-300"
                  >
                    <Settings className="w-5 h-5 mr-2" />
                    Accès Organisateur
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Footer */}
          <div className="text-center mt-12 text-slate-500">
            <p className="flex items-center justify-center gap-2">
              <Sparkles className="w-4 h-4" />
              Vote Secret v2.0 - Technologie 2025
              <Sparkles className="w-4 h-4" />
            </p>
          </div>
        </div>
      </div>
    );
  };

  // Create Meeting Component - Enhanced
  const CreateMeeting = () => {
    const [title, setTitle] = useState("");
    const [organizerName, setOrganizerName] = useState("");
    const [loading, setLoading] = useState(false);

    const handleCreate = async (e) => {
      e.preventDefault();
      console.log("🔍 handleCreate called with:", { title, organizerName });
      
      if (!title || !organizerName) {
        alert("Veuillez remplir tous les champs");
        return;
      }
      
      setLoading(true);
      try {
        console.log("🚀 Making API call to create meeting...");
        const response = await axios.post(`${API}/meetings`, {
          title,
          organizer_name: organizerName
        });
        console.log("✅ Meeting created successfully:", response.data);
        setMeeting(response.data);
        setCurrentView("organizer");
        connectWebSocket(response.data.id);
      } catch (error) {
        console.error("❌ Error creating meeting:", error);
        alert("Erreur lors de la création de la réunion: " + (error.response?.data?.detail || error.message));
      } finally {
        setLoading(false);
      }
    };

    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 bg-pattern-grid flex items-center justify-center p-4">
        <Card className="glass-card-strong w-full max-w-md border-0 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-t-xl">
            <div className="w-16 h-16 bg-white bg-opacity-20 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Settings className="w-8 h-8" />
            </div>
            <CardTitle className="text-2xl font-bold text-center">Créer une Réunion</CardTitle>
            <CardDescription className="text-blue-100 text-center">
              Configurez votre session de vote anonyme
            </CardDescription>
          </CardHeader>
          <CardContent className="p-8">
            <form onSubmit={handleCreate} className="space-y-6">
              <div>
                <label className="block text-sm font-semibold mb-3 text-slate-700">
                  Titre de la réunion
                </label>
                <Input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="ex: Assemblée générale 2025"
                  required
                  className="h-12 input-modern border-blue-200 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold mb-3 text-slate-700">
                  Votre nom (organisateur)
                </label>
                <Input
                  type="text"
                  value={organizerName}
                  onChange={(e) => setOrganizerName(e.target.value)}
                  placeholder="ex: Jean Dupont"
                  required
                  className="h-12 input-modern border-blue-200 focus:border-blue-500"
                />
              </div>
              <div className="flex space-x-3 pt-4">
                <Button 
                  type="button"
                  onClick={() => setCurrentView("home")} 
                  variant="outline" 
                  className="flex-1 h-12 border-slate-300 hover:bg-slate-50"
                >
                  Retour
                </Button>
                <Button 
                  type="submit"
                  disabled={!title || !organizerName || loading}
                  className="flex-1 h-12 btn-gradient-primary"
                >
                  {loading ? (
                    <>
                      <div className="spinner-modern mr-2" />
                      Création...
                    </>
                  ) : (
                    <>
                      <Settings className="w-5 h-5 mr-2" />
                      Créer
                    </>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  };

  // Join Meeting Component - Enhanced
  const JoinMeeting = () => {
    const [name, setName] = useState("");
    const [meetingCode, setMeetingCode] = useState("");
    const [loading, setLoading] = useState(false);

    const handleJoin = async (e) => {
      e.preventDefault();
      console.log("🔍 handleJoin called with:", { name, meetingCode });
      
      if (!name || !meetingCode) {
        alert("Veuillez remplir tous les champs");
        return;
      }
      
      setLoading(true);
      try {
        console.log("🚀 Making API call to join meeting...");
        
        // Détecter si c'est un code de scrutateur (commence par "SC")
        const isScrutatorCode = meetingCode.toUpperCase().startsWith('SC');
        
        if (isScrutatorCode) {
          // Tentative de connexion en tant que scrutateur
          console.log("🔍 Tentative de connexion en tant que scrutateur...");
          
          try {
            const response = await axios.post(`${API}/scrutators/join`, {
              name,
              scrutator_code: meetingCode.toUpperCase()
            });
            
            console.log("✅ Successfully joined as scrutator:", response.data);
            
            if (response.data.status === "approved") {
              // Scrutateur approuvé - accès à l'interface organisateur
              setMeeting(response.data.meeting);
              setIsScrutator(true);
              setScrutatorName(name);
              setCurrentView("organizer");
              connectWebSocket(response.data.meeting.id);
              
              alert(`✅ Connexion réussie en tant que scrutateur !\n\nBonjour ${name}, vous avez maintenant accès à l'interface organisateur pour surveiller la réunion "${response.data.meeting.title}".`);
            } else if (response.data.status === "pending_approval") {
              // En attente d'approbation
              alert(`⏳ Demande d'accès envoyée !\n\n${response.data.message}\n\nVeuillez attendre que l'organisateur approuve votre accès.`);
              setCurrentView("home");
            }
            
            return;
          } catch (scrutatorError) {
            console.error("❌ Error joining as scrutator:", scrutatorError);
            // Si l'erreur est due à un nom non autorisé, afficher un message spécifique
            if (scrutatorError.response?.status === 403) {
              alert("❌ Accès refusé !\n\nVotre nom n'est pas autorisé pour ce code de scrutateur. Vérifiez que vous utilisez exactement le nom qui a été ajouté par l'organisateur.");
            } else {
              alert("❌ Code de scrutateur invalide ou réunion inactive.\n\nVérifiez le code et réessayez.");
            }
            setLoading(false);
            return;
          }
        } else {
          // Code de réunion normal - rejoindre en tant que participant
          const response = await axios.post(`${API}/participants/join`, {
            name,
            meeting_code: meetingCode.toUpperCase()
          });
          console.log("✅ Successfully joined meeting:", response.data);
          setParticipant(response.data);
          
          // Get meeting details
          const meetingResponse = await axios.get(`${API}/meetings/${meetingCode.toUpperCase()}`);
          setMeeting(meetingResponse.data);
          
          setCurrentView("participant");
          connectWebSocket(meetingResponse.data.id);
        }
      } catch (error) {
        console.error("❌ Error joining meeting:", error);
        alert("Erreur: " + (error.response?.data?.detail || "Impossible de rejoindre la réunion"));
      } finally {
        setLoading(false);
      }
    };

    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 bg-pattern-dots flex items-center justify-center p-4">
        <Card className="glass-card-strong w-full max-w-md border-0 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-t-xl">
            <div className="w-16 h-16 bg-white bg-opacity-20 rounded-xl flex items-center justify-center mx-auto mb-4">
              <UserPlus className="w-8 h-8" />
            </div>
            <CardTitle className="text-2xl font-bold text-center">Rejoindre une Réunion</CardTitle>
            <CardDescription className="text-blue-100 text-center">
              Entrez vos informations pour participer au vote
            </CardDescription>
          </CardHeader>
          <CardContent className="p-8">
            <form onSubmit={handleJoin} className="space-y-6">
              <div>
                <label className="block text-sm font-semibold mb-3 text-slate-700">
                  Votre nom complet
                </label>
                <Input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="ex: Marie Martin"
                  required
                  className="h-12 input-modern border-blue-200 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold mb-3 text-slate-700">
                  Code de réunion
                </label>
                <Input
                  type="text"
                  value={meetingCode}
                  onChange={(e) => setMeetingCode(e.target.value.toUpperCase())}
                  placeholder="ex: ABC12345 ou SC123ABC"
                  className="h-12 input-modern border-blue-200 focus:border-blue-500 font-mono text-lg tracking-wider text-center"
                  required
                />
                <div className="mt-2 space-y-1">
                  <p className="text-xs text-slate-500">
                    • <strong>Code participant</strong> (ex: ABC12345) : Pour participer au vote
                  </p>
                  <p className="text-xs text-slate-500">
                    • <strong>Code scrutateur</strong> (ex: SC123ABC) : Pour superviser la réunion
                  </p>
                </div>
              </div>
              <div className="flex space-x-3 pt-4">
                <Button 
                  type="button"
                  onClick={() => setCurrentView("home")} 
                  variant="outline" 
                  className="flex-1 h-12 border-slate-300 hover:bg-slate-50"
                >
                  Retour
                </Button>
                <Button 
                  type="submit"
                  disabled={!name || !meetingCode || loading}
                  className="flex-1 h-12 btn-gradient-primary"
                >
                  {loading ? (
                    <>
                      <div className="spinner-modern mr-2" />
                      Connexion...
                    </>
                  ) : (
                    <>
                      <UserPlus className="w-5 h-5 mr-2" />
                      Rejoindre
                    </>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  };

  // Organizer Dashboard Component - Enhanced
  const OrganizerDashboard = () => {
    const [participants, setParticipants] = useState([]);
    const [polls, setPolls] = useState([]);
    const [newPollQuestion, setNewPollQuestion] = useState("");
    const [newPollOptions, setNewPollOptions] = useState(["", ""]);
    const [timerDuration, setTimerDuration] = useState("");
    const [showResultsRealTime, setShowResultsRealTime] = useState(true);
    const [showCreatePollModal, setShowCreatePollModal] = useState(false);
    const [showReportModal, setShowReportModal] = useState(false);
    const [showScrutatorModal, setShowScrutatorModal] = useState(false);
    const [showParticipantsModal, setShowParticipantsModal] = useState(false);
    const [downloadingReport, setDownloadingReport] = useState(false);
    
    // Scrutator states
    const [scrutatorNames, setScrutatorNames] = useState(['']);
    const [scrutatorCode, setScrutatorCode] = useState('');
    const [scrutators, setScrutators] = useState([]);
    const [scrutatorCodeGenerated, setScrutatorCodeGenerated] = useState(false);
    const [isScrutator, setIsScrutator] = useState(false);  // Indique si l'utilisateur connecté est un scrutateur
    const [scrutatorName, setScrutatorName] = useState('');  // Nom du scrutateur connecté

    // Report generation voting states
    const [showReportVoteModal, setShowReportVoteModal] = useState(false);
    const [reportVoteData, setReportVoteData] = useState(null);
    const [reportGenerationInProgress, setReportGenerationInProgress] = useState(false);

    useEffect(() => {
      if (meeting) {
        loadOrganizerData();
        loadScrutators();
        
        // Set up polling
        const interval = setInterval(() => {
          loadOrganizerData();
          loadScrutators();
        }, 5000);
        
        return () => clearInterval(interval);
      }
    }, [meeting]);

    const loadOrganizerData = async () => {
      try {
        const response = await axios.get(`${API}/meetings/${meeting.id}/organizer`);
        setParticipants(response.data.participants);
        setPolls(response.data.polls);
      } catch (error) {
        console.error("Error loading organizer data:", error);
      }
    };

    const approveParticipant = async (participantId, approved) => {
      try {
        await axios.post(`${API}/participants/${participantId}/approve`, {
          participant_id: participantId,
          approved
        });
        loadOrganizerData();
      } catch (error) {
        console.error("Error approving participant:", error);
      }
    };

    const createPoll = async () => {
      if (!newPollQuestion || newPollOptions.some(opt => !opt.trim())) return;
      
      try {
        await axios.post(`${API}/meetings/${meeting.id}/polls`, {
          question: newPollQuestion,
          options: newPollOptions.filter(opt => opt.trim()),
          timer_duration: timerDuration ? parseInt(timerDuration) : null,
          show_results_real_time: showResultsRealTime
        });
        
        setNewPollQuestion("");
        setNewPollOptions(["", ""]);
        setTimerDuration("");
        setShowResultsRealTime(true);
        setShowCreatePollModal(false);
        loadOrganizerData();
      } catch (error) {
        console.error("Error creating poll:", error);
      }
    };

    const startPoll = async (pollId) => {
      try {
        await axios.post(`${API}/polls/${pollId}/start`);
        loadOrganizerData();
      } catch (error) {
        console.error("Error starting poll:", error);
      }
    };

    const closePoll = async (pollId) => {
      try {
        await axios.post(`${API}/polls/${pollId}/close`);
        loadOrganizerData();
      } catch (error) {
        console.error("Error closing poll:", error);
      }
    };

    const addPollOption = () => {
      setNewPollOptions([...newPollOptions, ""]);
    };

    const addScrutatorName = () => {
      setScrutatorNames([...scrutatorNames, '']);
    };

    const removeScrutatorName = (index) => {
      if (scrutatorNames.length > 1) {
        const newNames = scrutatorNames.filter((_, i) => i !== index);
        setScrutatorNames(newNames);
      }
    };

    const updateScrutatorName = (index, value) => {
      const newNames = [...scrutatorNames];
      newNames[index] = value;
      setScrutatorNames(newNames);
    };

    const addScrutators = async () => {
      try {
        // Filtrer les noms vides
        const validNames = scrutatorNames.filter(name => name.trim() !== '');
        
        if (validNames.length === 0) {
          alert("Veuillez entrer au moins un nom de scrutateur");
          return;
        }

        const response = await axios.post(`${API}/meetings/${meeting.id}/scrutators`, {
          names: validNames
        });

        setScrutatorCode(response.data.scrutator_code);
        setScrutators(response.data.scrutators);
        setScrutatorCodeGenerated(true);
        
        alert(`Code de scrutateur généré avec succès : ${response.data.scrutator_code}`);
      } catch (error) {
        console.error("Erreur lors de l'ajout des scrutateurs:", error);
        alert("Erreur lors de l'ajout des scrutateurs: " + (error.response?.data?.detail || "Erreur inconnue"));
      }
    };

    const loadScrutators = async () => {
      try {
        const response = await axios.get(`${API}/meetings/${meeting.id}/scrutators`);
        setScrutators(response.data.scrutators);
        setScrutatorCode(response.data.scrutator_code || '');
        setScrutatorCodeGenerated(!!response.data.scrutator_code);
      } catch (error) {
        console.error("Erreur lors du chargement des scrutateurs:", error);
      }
    };

    const approveScrutator = async (scrutatorId, approved) => {
      try {
        await axios.post(`${API}/scrutators/${scrutatorId}/approve`, {
          scrutator_id: scrutatorId,
          approved: approved
        });
        
        // Recharger la liste des scrutateurs
        loadScrutators();
        
        alert(approved ? "Scrutateur approuvé avec succès" : "Scrutateur rejeté");
      } catch (error) {
        console.error("Erreur lors de l'approbation du scrutateur:", error);
        alert("Erreur lors de l'approbation: " + (error.response?.data?.detail || "Erreur inconnue"));
      }
    };

    const requestReportGeneration = async () => {
      try {
        const response = await axios.post(`${API}/meetings/${meeting.id}/request-report`, {
          meeting_id: meeting.id,
          requested_by: meeting.organizer_name
        });

        if (response.data.direct_generation) {
          // Pas de scrutateurs - génération directe
          downloadReport();
        } else {
          // Scrutateurs présents - attendre leur approbation
          setReportGenerationInProgress(true);
          alert(`Demande envoyée aux ${response.data.scrutator_count} scrutateurs. Majorité requise: ${response.data.majority_needed} votes positifs.`);
        }
      } catch (error) {
        console.error("Erreur lors de la demande de génération:", error);
        alert("Erreur: " + (error.response?.data?.detail || "Erreur inconnue"));
      }
    };

    const submitScrutatorVote = async (approved) => {
      try {
        const response = await axios.post(`${API}/meetings/${meeting.id}/scrutator-vote`, {
          meeting_id: meeting.id,
          scrutator_name: scrutatorName,
          approved: approved
        });

        setShowReportVoteModal(false);
        
        if (response.data.decision === "approved") {
          alert(`✅ Génération du rapport approuvée !\n\n${response.data.yes_votes} votes positifs sur ${response.data.majority_needed} requis.`);
        } else if (response.data.decision === "rejected") {
          alert(`❌ Génération du rapport rejetée.\n\n${response.data.no_votes} votes négatifs sur ${response.data.majority_needed} requis.`);
        } else {
          alert(`🗳️ Vote enregistré !\n\n${response.data.message}`);
        }
      } catch (error) {
        console.error("Erreur lors du vote:", error);
        alert("Erreur lors du vote: " + (error.response?.data?.detail || "Erreur inconnue"));
      }
    };

    const updatePollOption = (index, value) => {
      const updated = [...newPollOptions];
      updated[index] = value;
      setNewPollOptions(updated);
    };

    const removePollOption = (index) => {
      if (newPollOptions.length > 2) {
        setNewPollOptions(newPollOptions.filter((_, i) => i !== index));
      }
    };

    const downloadReport = async () => {
      if (!meeting?.id) return;
      
      setDownloadingReport(true);
      
      try {
        console.log("🔄 Début de la génération du rapport PDF...");
        
        // Make API call to generate and download PDF
        const response = await fetch(`${API}/meetings/${meeting.id}/report`, {
          method: 'GET',
          headers: {
            'Accept': 'application/pdf',
          },
        });
        
        console.log("📡 Réponse API reçue:", response.status);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error("❌ Erreur API:", errorText);
          throw new Error(`Erreur ${response.status}: ${errorText}`);
        }
        
        // Get the PDF blob
        const blob = await response.blob();
        console.log("📄 PDF blob reçu, taille:", blob.size, "bytes");
        
        // Create download link
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `Rapport_${meeting.title.replace(/[^a-zA-Z0-9]/g, '_')}_${meeting.meeting_code}.pdf`;
        
        // Force download
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Clean up the blob URL
        window.URL.revokeObjectURL(downloadUrl);
        
        console.log("✅ Téléchargement PDF réussi");
        
        // Close modal and show success message
        setShowReportModal(false);
        setDownloadingReport(false);
        
        // Store meeting info for notifications before clearing
        const meetingInfo = {
          title: meeting.title,
          organizerName: meeting.organizer_name || "Organisateur",
          meetingCode: meeting.meeting_code
        };
        
        // Show success message and redirect after a brief delay
        setTimeout(() => {
          alert("✅ Rapport téléchargé avec succès!\n\n📝 Toutes les données de la réunion ont été supprimées.\n\n🏠 Retour à l'accueil...");
          
          // Clear all local state and return to home
          setCurrentView("home");
          setMeeting(null);
          setParticipants([]);
          setPolls([]);
          setParticipant(null);
        }, 500);
        
      } catch (error) {
        console.error("❌ Erreur lors du téléchargement:", error);
        setDownloadingReport(false);
        
        alert("❌ Erreur lors du téléchargement du rapport:\n\n" + 
              error.message + 
              "\n\nVeuillez réessayer ou contacter le support technique.");
      }
    };

    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
        <div className="w-full">
          {/* Header pleine largeur */}
          <Card className="glass-card border-0 shadow-lg mb-8 rounded-none">
            <CardHeader className="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
              <div className="max-w-6xl mx-auto flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 p-4">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-white bg-opacity-20 rounded-xl flex items-center justify-center">
                    <Vote className="w-6 h-6" />
                  </div>
                  <div>
                    <CardTitle className="text-2xl font-bold">{meeting?.title}</CardTitle>
                    
                    {/* Bouton Ajouter des scrutateurs */}
                    <div className="mt-2 mb-2">
                      <Button
                        onClick={() => setShowScrutatorModal(true)}
                        size="sm"
                        variant="outline"
                        className="border-white border-opacity-60 text-white hover:bg-white hover:text-blue-600 transition-all duration-300 text-xs"
                      >
                        <UserPlus className="w-3 h-3 mr-1" />
                        Ajouter des scrutateurs
                      </Button>
                      {scrutators.length > 0 && (
                        <span className="ml-2 text-blue-200 text-xs">
                          ({scrutators.length} scrutateur{scrutators.length > 1 ? 's' : ''})
                        </span>
                      )}
                    </div>
                    
                    <CardDescription className="text-blue-100">
                      Par {meeting?.organizer_name || "Organisateur"} à {meeting?.created_at ? new Date(meeting.created_at).toLocaleTimeString('fr-FR', {hour: '2-digit', minute: '2-digit'}) : "00:00"} le {meeting?.created_at ? new Date(meeting.created_at).toLocaleDateString('fr-FR') : new Date().toLocaleDateString('fr-FR')}
                    </CardDescription>
                  </div>
                </div>
                
                {/* Code de réunion mis en évidence */}
                <div className="bg-gradient-to-r from-orange-400 to-purple-500 rounded-xl p-4 shadow-lg border-2 border-red-500">
                  <p className="text-white text-sm font-medium mb-2">Code de réunion</p>
                  <div className="flex items-center gap-3">
                    <div className="meeting-code text-white text-2xl font-mono font-bold tracking-widest bg-black bg-opacity-20 px-3 py-1 rounded-lg">
                      {meeting?.meeting_code}
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      className="border-white border-opacity-50 text-white hover:bg-white hover:text-purple-600 transition-all"
                      onClick={() => navigator.clipboard.writeText(meeting?.meeting_code)}
                    >
                      Copier
                    </Button>
                  </div>
                </div>

                {/* Participants avec statistiques détaillées */}
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-blue-100 text-sm font-medium">Participants</p>
                    <div className="text-white">
                      <span className="text-xl font-bold">{participants.filter(p => p.approval_status === 'approved').length}</span>
                      <span className="text-blue-200 text-sm"> approuvés</span>
                      {participants.filter(p => p.approval_status === 'pending').length > 0 && (
                        <>
                          <br />
                          <span className="text-lg font-semibold text-yellow-300">{participants.filter(p => p.approval_status === 'pending').length}</span>
                          <span className="text-yellow-200 text-sm"> en attente</span>
                        </>
                      )}
                    </div>
                  </div>
                  <Button
                    onClick={() => setShowParticipantsModal(true)}
                    className="bg-white bg-opacity-20 hover:bg-white hover:text-blue-600 border border-white border-opacity-30"
                  >
                    <Users className="w-4 h-4 mr-2" />
                    Gérer les participants
                  </Button>
                </div>
              </div>
            </CardHeader>
          </Card>
        </div>

        <div className="max-w-6xl mx-auto p-4">
          {/* Section principale - Interface Organisateur */}
          <div className="space-y-6">
            {/* En-tête des sondages avec bouton créer */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <h2 className="text-2xl font-bold text-slate-800">Sondages de la réunion</h2>
              <Button
                onClick={() => setShowCreatePollModal(true)}
                className="btn-gradient-primary"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Créer un sondage
              </Button>
            </div>

            {/* Liste des sondages */}
            {polls.length > 0 ? (
              <div className="space-y-6">
                {polls.map((poll) => {
                  const totalVotes = poll.options.reduce((sum, opt) => sum + opt.votes, 0);
                  const winnerOption = poll.status === "closed" ? 
                    poll.options.reduce((prev, current) => (prev.votes > current.votes) ? prev : current) : null;
                  
                  return (
                    <div key={poll.id} className="glass-card border-0 shadow-lg bg-white rounded-2xl overflow-hidden">
                      <div className={`poll-card-header p-4 ${
                        poll.status === "closed" ? "poll-card-closed" : 
                        poll.status === "draft" ? "poll-card-draft" : ""
                      }`}>
                        <div className="flex flex-col gap-3">
                          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                            <h3 className="text-lg font-semibold text-white">{poll.question}</h3>
                            <div className="flex items-center gap-2">
                              {poll.status === "draft" && (
                                <Button 
                                  size="sm" 
                                  onClick={() => startPoll(poll.id)}
                                  className="bg-white bg-opacity-20 hover:bg-white hover:text-blue-600 transition-all"
                                >
                                  <Play className="w-4 h-4 mr-1" />
                                  Lancer
                                </Button>
                              )}
                              {poll.status === "active" && (
                                <>
                                  <Badge className="bg-green-500 text-white shadow-sm">
                                    <Clock className="w-3 h-3 mr-1" />
                                    En cours
                                  </Badge>
                                  <Button 
                                    size="sm" 
                                    onClick={() => closePoll(poll.id)}
                                    className="bg-white bg-opacity-20 hover:bg-white hover:text-blue-600 transition-all"
                                  >
                                    <Square className="w-4 h-4 mr-1" />
                                    Fermer
                                  </Button>
                                </>
                              )}
                              {poll.status === "closed" && (
                                <Badge className="bg-slate-500 text-white shadow-sm">
                                  <CheckCircle className="w-3 h-3 mr-1" />
                                  Fermé
                                </Badge>
                              )}
                            </div>
                          </div>
                          
                          {/* Informations supplémentaires dans l'en-tête */}
                          <div className="flex flex-wrap items-center gap-4 text-sm text-white opacity-90">
                            <div className="flex items-center gap-1">
                              <Users className="w-4 h-4" />
                              <span>{totalVotes} vote{totalVotes !== 1 ? 's' : ''}</span>
                            </div>
                            
                            {poll.timer_duration && (
                              <div className="flex items-center gap-1">
                                <Timer className="w-4 h-4" />
                                <span>Minuteur: {poll.timer_duration}s</span>
                              </div>
                            )}
                            
                            {poll.status === "closed" && winnerOption && (
                              <div className="flex items-center gap-1 bg-white bg-opacity-20 px-2 py-1 rounded-full">
                                <span className="text-yellow-300">🏆</span>
                                <span className="font-medium">Gagnant: {winnerOption.text}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      <div className="p-6 bg-white">
                        <div className="space-y-4">
                          {poll.options.map((option) => {
                            const percentage = totalVotes > 0 ? (option.votes / totalVotes) * 100 : 0;
                            const isWinner = poll.status === "closed" && winnerOption && option.id === winnerOption.id;
                            
                            return (
                              <div key={option.id} className={`space-y-2 ${isWinner ? 'vote-option-winner' : 'bg-slate-50 border border-slate-200'} p-3 rounded-lg transition-all`}>
                                <div className="flex justify-between items-center text-sm">
                                  <span className={`font-medium ${isWinner ? 'text-green-700 font-semibold' : 'text-slate-700'}`}>
                                    {isWinner && <span className="mr-2">🏆</span>}
                                    {option.text}
                                  </span>
                                  <span className={`font-bold ${isWinner ? 'text-green-600' : 'text-slate-600'}`}>
                                    {option.votes} votes ({percentage.toFixed(1)}%)
                                  </span>
                                </div>
                                <div className="relative">
                                  <Progress 
                                    value={percentage} 
                                    className={`h-3 ${isWinner ? 'progress-winner' : ''}`}
                                  />
                                  {isWinner && (
                                    <div className="absolute inset-0 bg-gradient-to-r from-green-400 to-green-500 rounded-full opacity-70"></div>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="border-0 shadow-lg bg-white rounded-2xl overflow-hidden" style={{background: 'white'}}>
                <div className="text-center py-16 p-6">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Vote className="w-8 h-8 text-blue-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-slate-800 mb-2">Aucun sondage créé</h3>
                  <p className="text-slate-500 mb-6">Créez votre premier sondage pour commencer les votes</p>
                  <Button
                    onClick={() => setShowCreatePollModal(true)}
                    className="btn-gradient-primary"
                  >
                    <Sparkles className="w-4 h-4 mr-2" />
                    Créer un sondage
                  </Button>
                </div>
              </div>
            )}
          </div>

          {/* Bouton rapport en bas */}
          <div className="mt-12 flex justify-center">
            <div className="border-0 shadow-lg bg-white rounded-2xl overflow-hidden" style={{background: 'white'}}>
              <div className="p-6 text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <FileText className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="text-lg font-semibold text-slate-800 mb-2">Générer le rapport final</h3>
                <p className="text-slate-500 mb-4 text-sm">
                  Télécharger le rapport PDF et supprimer définitivement toutes les données
                </p>
                <Button
                  onClick={() => setShowReportModal(true)}
                  className="bg-red-600 hover:bg-red-700 text-white"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Voir le résumé du rapport
                </Button>
              </div>
            </div>
          </div>
        </div>
        {/* Modal de gestion des participants */}
        {showParticipantsModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <Card className="w-full max-w-4xl max-h-[80vh] overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Users className="w-5 h-5" />
                    Gestion des Participants ({participants.length})
                  </CardTitle>
                  <Button
                    onClick={() => setShowParticipantsModal(false)}
                    variant="outline"
                    size="sm"
                    className="border-white text-white hover:bg-white hover:text-blue-600"
                  >
                    ×
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="p-6 overflow-y-auto max-h-96">
                <div className="space-y-4">
                  {participants.map((participant) => (
                    <div key={participant.id} className="flex items-center justify-between p-4 border border-blue-200 rounded-lg bg-white shadow-sm hover:shadow-md transition-shadow">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold shadow-sm">
                          {participant.name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <p className="font-semibold text-slate-800">{participant.name}</p>
                          <p className="text-sm text-slate-500">
                            Rejoint le {new Date(participant.joined_at).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {participant.approval_status === "pending" && (
                          <>
                            <Button 
                              size="sm" 
                              onClick={() => approveParticipant(participant.id, true)}
                              className="btn-gradient-success"
                            >
                              <CheckCircle className="w-4 h-4 mr-1" />
                              Approuver
                            </Button>
                            <Button 
                              size="sm" 
                              variant="outline" 
                              onClick={() => approveParticipant(participant.id, false)}
                              className="border-blue-300 hover:bg-blue-50"
                            >
                              Rejeter
                            </Button>
                          </>
                        )}
                        {participant.approval_status === "approved" && (
                          <Badge className="status-approved">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            Approuvé
                          </Badge>
                        )}
                        {participant.approval_status === "rejected" && (
                          <Badge className="status-rejected">Rejeté</Badge>
                        )}
                      </div>
                    </div>
                  ))}
                  {participants.length === 0 && (
                    <div className="text-center py-8">
                      <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <UserPlus className="w-8 h-8 text-blue-600" />
                      </div>
                      <p className="text-slate-500 text-lg">Aucun participant pour le moment</p>
                      <p className="text-slate-400 text-sm mt-2">Partagez le code : <span className="font-mono font-bold text-blue-600">{meeting?.meeting_code}</span></p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Modal de création de sondage */}
        {showCreatePollModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <Card className="w-full max-w-2xl">
              <CardHeader className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5" />
                    Créer un Nouveau Sondage
                  </CardTitle>
                  <Button
                    onClick={() => setShowCreatePollModal(false)}
                    variant="outline"
                    size="sm"
                    className="border-white text-white hover:bg-white hover:text-blue-600"
                  >
                    ×
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="p-6 space-y-6">
                <div>
                  <label className="block text-sm font-semibold mb-3 text-slate-700">Question du sondage</label>
                  <Input
                    value={newPollQuestion}
                    onChange={(e) => setNewPollQuestion(e.target.value)}
                    placeholder="ex: Approuvez-vous cette proposition ?"
                    className="h-12 input-modern"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-semibold mb-3 text-slate-700">Options de réponse</label>
                  <div className="space-y-3">
                    {newPollOptions.map((option, index) => (
                      <div key={index} className="flex gap-2">
                        <Input
                          value={option}
                          onChange={(e) => updatePollOption(index, e.target.value)}
                          placeholder={`Option ${index + 1}`}
                          className="input-modern"
                        />
                        {newPollOptions.length > 2 && (
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => removePollOption(index)}
                            className="w-10 h-10 flex-shrink-0"
                          >
                            ×
                          </Button>
                        )}
                      </div>
                    ))}
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={addPollOption}
                      className="border-blue-300 hover:bg-blue-50"
                    >
                      + Ajouter une option
                    </Button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold mb-3 text-slate-700">
                      Minuteur (optionnel)
                    </label>
                    <Input
                      type="number"
                      value={timerDuration}
                      onChange={(e) => setTimerDuration(e.target.value)}
                      placeholder="Durée en secondes"
                      className="input-modern"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold mb-3 text-slate-700">
                      Résultats en temps réel
                    </label>
                    <div className="flex items-center space-x-2 mt-2">
                      <Switch
                        checked={showResultsRealTime}
                        onCheckedChange={setShowResultsRealTime}
                      />
                      <label className="text-sm text-slate-600">
                        {showResultsRealTime ? "Activé" : "Désactivé"}
                      </label>
                    </div>
                  </div>
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <Button 
                    variant="outline" 
                    onClick={() => setShowCreatePollModal(false)}
                  >
                    Annuler
                  </Button>
                  <Button 
                    onClick={createPoll}
                    disabled={!newPollQuestion || newPollOptions.some(opt => !opt.trim())}
                    className="btn-gradient-primary"
                  >
                    <Sparkles className="w-4 h-4 mr-2" />
                    Créer le sondage
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Modal de gestion des scrutateurs */}
        {showScrutatorModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <Card className="w-full max-w-3xl max-h-[90vh] overflow-hidden bg-white">
              <CardHeader className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <UserPlus className="w-5 h-5" />
                    Gestion des Scrutateurs
                  </CardTitle>
                  <Button
                    onClick={() => setShowScrutatorModal(false)}
                    variant="outline"
                    size="sm"
                    className="border-white text-white hover:bg-white hover:text-purple-600"
                  >
                    ×
                  </Button>
                </div>
                <CardDescription className="text-purple-100 text-sm">
                  🔐 Fonction sécurisée - Les scrutateurs auront accès à l'interface organisateur
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6 overflow-y-auto max-h-[70vh]">
                <div className="space-y-6">
                  
                  {/* Explication et mise en garde */}
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-amber-800 mb-3 flex items-center gap-2">
                      <Shield className="w-5 h-5 text-amber-600" />
                      Information importante sur les scrutateurs
                    </h3>
                    
                    <div className="text-sm text-amber-700 space-y-2">
                      <p><strong>Qu'est-ce qu'un scrutateur ?</strong></p>
                      <p>Un scrutateur est une personne autorisée qui peut accéder à l'interface organisateur pour surveiller le déroulement du vote en temps réel.</p>
                      
                      <p className="mt-3"><strong>Privilèges des scrutateurs :</strong></p>
                      <ul className="list-disc list-inside space-y-1 ml-2">
                        <li>Accès complet à l'interface organisateur</li>
                        <li>Visualisation en temps réel des participants et votes</li>
                        <li>Consultation des résultats des sondages</li>
                        <li>Surveillance du processus de vote</li>
                      </ul>
                      
                      <div className="bg-red-50 border border-red-200 rounded-lg p-3 mt-4">
                        <p className="text-red-800 font-semibold">⚠️ Mesures de sécurité importantes :</p>
                        <ul className="list-disc list-inside space-y-1 ml-2 text-red-700">
                          <li>Ne partagez le code scrutateur qu'avec des personnes de confiance</li>
                          <li>Les scrutateurs peuvent voir toutes les données de la réunion</li>
                          <li>Seuls les noms que vous ajoutez peuvent utiliser le code</li>
                          <li>Le code scrutateur est différent du code de réunion</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Liste des scrutateurs (si déjà ajoutés) */}
                  {scrutators.length > 0 && (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <h3 className="text-lg font-semibold text-green-800 mb-3 flex items-center gap-2">
                        <CheckCircle className="w-5 h-5 text-green-600" />
                        Scrutateurs autorisés ({scrutators.length})
                      </h3>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-4">
                        {scrutators.map((scrutator, index) => (
                          <div key={index} className="bg-white rounded-lg p-3 border border-green-100">
                            <div className="flex items-center gap-2">
                              <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center text-green-600 font-bold text-xs">
                                {index + 1}
                              </div>
                              <span className="text-slate-700 font-medium">{scrutator.name || scrutator}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                      
                      {scrutatorCode && (
                        <div className="bg-white rounded-lg p-4 border border-green-100">
                          <h4 className="font-semibold text-green-800 mb-2">Code scrutateur généré :</h4>
                          <div className="flex items-center gap-3">
                            <div className="font-mono text-lg font-bold text-green-600 bg-green-100 px-3 py-1 rounded-lg">
                              {scrutatorCode}
                            </div>
                            <Button
                              size="sm"
                              variant="outline"
                              className="border-green-300 text-green-600 hover:bg-green-100"
                              onClick={() => navigator.clipboard.writeText(scrutatorCode)}
                            >
                              Copier
                            </Button>
                          </div>
                          <p className="text-green-600 text-sm mt-2">
                            ⚠️ Partagez ce code uniquement avec les personnes listées ci-dessus
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Ajouter des scrutateurs */}
                  {!scrutatorCodeGenerated && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <h3 className="text-lg font-semibold text-blue-800 mb-3 flex items-center gap-2">
                        <UserPlus className="w-5 h-5 text-blue-600" />
                        Ajouter des scrutateurs
                      </h3>
                      
                      <div className="space-y-3">
                        {scrutatorNames.map((name, index) => (
                          <div key={index} className="flex gap-2">
                            <Input
                              value={name}
                              onChange={(e) => updateScrutatorName(index, e.target.value)}
                              placeholder={`Nom du scrutateur ${index + 1}`}
                              className="input-modern"
                            />
                            {scrutatorNames.length > 1 && (
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={() => removeScrutatorName(index)}
                                className="w-10 h-10 flex-shrink-0 border-red-300 text-red-600 hover:bg-red-50"
                              >
                                ×
                              </Button>
                            )}
                          </div>
                        ))}
                        
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={addScrutatorName}
                          className="border-blue-300 hover:bg-blue-50 text-blue-600"
                        >
                          + Ajouter un autre scrutateur
                        </Button>
                      </div>
                    </div>
                  )}
                </div>

                {/* Boutons d'action */}
                <div className="flex justify-end space-x-3 pt-6 border-t border-slate-200">
                  <Button 
                    variant="outline" 
                    onClick={() => setShowScrutatorModal(false)}
                    className="border-slate-300 hover:bg-slate-50"
                  >
                    {scrutatorCodeGenerated ? "Fermer" : "Annuler"}
                  </Button>
                  {!scrutatorCodeGenerated && (
                    <Button 
                      onClick={addScrutators}
                      disabled={scrutatorNames.every(name => !name.trim())}
                      className="bg-purple-600 hover:bg-purple-700 text-white disabled:opacity-50"
                    >
                      <UserPlus className="w-4 h-4 mr-2" />
                      Générer le code scrutateur
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Modal de génération de rapport avec résumé détaillé */}
        {showReportModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <Card className="w-full max-w-3xl max-h-[90vh] overflow-hidden bg-white">
              <CardHeader className="bg-gradient-to-r from-red-500 to-red-600 text-white">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Résumé du Rapport Final
                  </CardTitle>
                  <Button
                    onClick={() => setShowReportModal(false)}
                    variant="outline"
                    size="sm"
                    className="border-white text-white hover:bg-white hover:text-red-600"
                  >
                    ×
                  </Button>
                </div>
                <CardDescription className="text-red-100 text-sm">
                  ⚠️ Action irréversible - Toutes les données seront supprimées après téléchargement
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6 overflow-y-auto max-h-[70vh]">
                {/* Résumé des données qui seront dans le rapport */}
                <div className="space-y-6">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-slate-800 mb-3 flex items-center gap-2">
                      <BarChart3 className="w-5 h-5 text-blue-600" />
                      Contenu du rapport PDF
                    </h3>
                    
                    {/* Informations de la réunion */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div className="bg-white rounded-lg p-3 border border-blue-100">
                        <h4 className="font-semibold text-slate-700 mb-2">Informations générales</h4>
                        <ul className="text-sm text-slate-600 space-y-1">
                          <li>• Titre: <strong>{meeting?.title}</strong></li>
                          <li>• Code: <strong>{meeting?.meeting_code}</strong></li>
                          <li>• Date: <strong>{new Date().toLocaleDateString('fr-FR')}</strong></li>
                          <li>• Heure: <strong>{new Date().toLocaleTimeString('fr-FR')}</strong></li>
                        </ul>
                      </div>
                      
                      <div className="bg-white rounded-lg p-3 border border-blue-100">
                        <h4 className="font-semibold text-slate-700 mb-2">Statistiques</h4>
                        <ul className="text-sm text-slate-600 space-y-1">
                          <li>• Participants: <strong>{participants.filter(p => p.approval_status === 'approved').length} approuvés</strong></li>
                          <li>• Sondages: <strong>{polls.length} total</strong></li>
                          <li>• Votes: <strong>{polls.reduce((sum, poll) => sum + poll.options.reduce((voteSum, opt) => voteSum + opt.votes, 0), 0)} total</strong></li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Liste des participants approuvés */}
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-slate-800 mb-3 flex items-center gap-2">
                      <Users className="w-5 h-5 text-green-600" />
                      Participants approuvés ({participants.filter(p => p.approval_status === 'approved').length})
                    </h3>
                    
                    {participants.filter(p => p.approval_status === 'approved').length > 0 ? (
                      <div className="bg-white rounded-lg p-3 border border-green-100">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                          {participants.filter(p => p.approval_status === 'approved').map((participant, index) => (
                            <div key={participant.id} className="text-sm text-slate-600 flex items-center gap-2">
                              <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center text-green-600 font-bold text-xs">
                                {index + 1}
                              </div>
                              <span>{participant.name}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <p className="text-sm text-slate-500 italic">Aucun participant approuvé</p>
                    )}
                  </div>

                  {/* Liste des sondages */}
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-slate-800 mb-3 flex items-center gap-2">
                      <Vote className="w-5 h-5 text-purple-600" />
                      Sondages et résultats ({polls.length})
                    </h3>
                    
                    {polls.length > 0 ? (
                      <div className="space-y-3">
                        {polls.map((poll, index) => (
                          <div key={poll.id} className="bg-white rounded-lg p-3 border border-purple-100">
                            <div className="flex items-start gap-3">
                              <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center text-purple-600 font-bold text-xs flex-shrink-0">
                                {index + 1}
                              </div>
                              <div className="flex-1">
                                <h4 className="font-semibold text-slate-700 mb-2">{poll.question}</h4>
                                <div className="text-sm text-slate-600">
                                  <p className="mb-1">Statut: <span className={`font-medium ${
                                    poll.status === 'active' ? 'text-green-600' : 
                                    poll.status === 'closed' ? 'text-blue-600' : 'text-slate-600'
                                  }`}>{
                                    poll.status === 'active' ? 'En cours' :
                                    poll.status === 'closed' ? 'Fermé' : 'Brouillon'
                                  }</span></p>
                                  <div className="mt-2">
                                    <p className="font-medium mb-1">Options et votes:</p>
                                    {poll.options.map((option) => (
                                      <div key={option.id} className="ml-2 text-xs text-slate-500">
                                        • {option.text}: {option.votes} votes
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-slate-500 italic">Aucun sondage créé</p>
                    )}
                  </div>

                  {/* Avertissement sur la suppression */}
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-red-800 mb-3 flex items-center gap-2">
                      <AlertCircle className="w-5 h-5 text-red-600" />
                      Que se passe-t-il après le téléchargement ?
                    </h3>
                    
                    <div className="bg-white rounded-lg p-3 border border-red-100">
                      <ul className="text-sm text-red-700 space-y-2">
                        <li className="flex items-start gap-2">
                          <span className="text-red-500 font-bold">1.</span>
                          <span>Le rapport PDF sera automatiquement téléchargé sur votre appareil</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-red-500 font-bold">2.</span>
                          <span>Toutes les données de cette réunion seront <strong>définitivement supprimées</strong> de nos serveurs</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-red-500 font-bold">3.</span>
                          <span>Les participants ne pourront plus accéder aux résultats</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-red-500 font-bold">4.</span>
                          <span>Le code de réunion <strong>{meeting?.meeting_code}</strong> deviendra invalide</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-red-500 font-bold">5.</span>
                          <span>Cette action est <strong>irréversible</strong> - aucune récupération possible</span>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Boutons d'action */}
                <div className="flex justify-end space-x-3 pt-6 border-t border-slate-200">
                  <Button 
                    variant="outline" 
                    onClick={() => setShowReportModal(false)}
                    className="border-slate-300 hover:bg-slate-50"
                  >
                    Annuler
                  </Button>
                  <Button 
                    onClick={downloadReport}
                    disabled={downloadingReport}
                    className="bg-red-600 hover:bg-red-700 text-white disabled:opacity-50"
                  >
                    {downloadingReport ? (
                      <>
                        <div className="w-4 h-4 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        Génération en cours...
                      </>
                    ) : (
                      <>
                        <Download className="w-4 h-4 mr-2" />
                        Confirmer et télécharger
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    );
  };

  // Participant Dashboard Component - Enhanced with ALL polls display
  const ParticipantDashboard = () => {
    const [status, setStatus] = useState("pending");
    const [polls, setPolls] = useState([]);
    const [votedPolls, setVotedPolls] = useState(new Set());

    useEffect(() => {
      if (participant) {
        checkParticipantStatus();
        loadPolls();
        
        // Set up polling for participant status and polls
        const interval = setInterval(() => {
          checkParticipantStatus();
          loadPolls();
        }, 3000);
        
        return () => clearInterval(interval);
      }
    }, [participant]);

    // Handle meeting closed countdown
    useEffect(() => {
      if (meetingClosed && redirectCountdown > 0) {
        const timer = setTimeout(() => {
          setRedirectCountdown(redirectCountdown - 1);
        }, 1000);
        
        return () => clearTimeout(timer);
      } else if (meetingClosed && redirectCountdown === 0) {
        // Redirect to home
        setCurrentView("home");
        setMeeting(null);
        setParticipant(null);
        setMeetingClosed(false);
        setClosedMeetingInfo(null);
        setRedirectCountdown(10);
      }
    }, [meetingClosed, redirectCountdown, setCurrentView, setMeeting, setParticipant, setMeetingClosed, setClosedMeetingInfo, setRedirectCountdown]);

    const checkParticipantStatus = async () => {
      try {
        const response = await axios.get(`${API}/participants/${participant.id}/status`);
        setStatus(response.data.status);
      } catch (error) {
        console.error("Error checking status:", error);
        
        // If we get a 404, the meeting might have been deleted
        if (error.response?.status === 404) {
          handleMeetingClosed();
        }
      }
    };

    const loadPolls = async () => {
      if (!meeting) return;
      try {
        const response = await axios.get(`${API}/meetings/${meeting.id}/polls`);
        // Show ALL polls (active, closed, draft) to participants
        setPolls(response.data);
      } catch (error) {
        console.error("Error loading polls:", error);
        
        // If we get a 404, the meeting has been deleted
        if (error.response?.status === 404) {
          handleMeetingClosed();
        }
      }
    };

    const handleMeetingClosed = () => {
      if (!meetingClosed) {
        setClosedMeetingInfo({
          title: meeting?.title || "Réunion",
          organizerName: meeting?.organizer_name || "Organisateur",
          meetingCode: meeting?.meeting_code || "N/A"
        });
        setMeetingClosed(true);
        setRedirectCountdown(10);
      }
    };

    const submitVote = async (pollId, optionId) => {
      try {
        await axios.post(`${API}/votes`, {
          poll_id: pollId,
          option_id: optionId
        });
        
        // Marquer ce sondage comme voté
        setVotedPolls(prev => new Set([...prev, pollId]));
        
        // Recharger les sondages pour obtenir les résultats
        loadPolls();
      } catch (error) {
        console.error("Error submitting vote:", error);
        alert("Erreur lors du vote: " + (error.response?.data?.detail || "Erreur inconnue"));
      }
    };

    // Show meeting closed notification
    if (meetingClosed && closedMeetingInfo) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 bg-pattern-dots flex items-center justify-center p-4">
          <div className="glass-card-strong w-full max-w-2xl border-0 shadow-lg bg-white rounded-2xl overflow-hidden">
            <div className="bg-gradient-to-r from-red-500 to-red-600 text-white p-6">
              <div className="flex items-center justify-center mb-4">
                <div className="w-16 h-16 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                  <AlertCircle className="w-8 h-8" />
                </div>
              </div>
              <h1 className="text-2xl font-bold text-center mb-2">Réunion Fermée</h1>
              <p className="text-red-100 text-center">
                La réunion a été fermée par l'organisateur
              </p>
            </div>
            
            <div className="p-8 text-center">
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-slate-800 mb-4">
                  {closedMeetingInfo.title}
                </h2>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="font-semibold text-slate-700">Organisateur:</p>
                      <p className="text-slate-600">{closedMeetingInfo.organizerName}</p>
                    </div>
                    <div>
                      <p className="font-semibold text-slate-700">Code de réunion:</p>
                      <p className="text-slate-600 font-mono">{closedMeetingInfo.meetingCode}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
                <div className="flex items-start gap-3">
                  <FileText className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
                  <div className="text-left">
                    <h3 className="font-semibold text-red-800 mb-2">Rapport généré et données supprimées</h3>
                    <ul className="text-sm text-red-700 space-y-1">
                      <li>• Le rapport PDF de la réunion a été téléchargé par l'organisateur</li>
                      <li>• Toutes les données de cette réunion ont été définitivement supprimées</li>
                      <li>• Les résultats de vote ne sont plus accessibles</li>
                      <li>• Le code de réunion {closedMeetingInfo.meetingCode} n'est plus valide</li>
                    </ul>
                  </div>
                </div>
              </div>
              
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <div className="flex items-center justify-center gap-2 text-blue-700">
                  <Clock className="w-5 h-5" />
                  <span className="font-semibold">
                    Redirection automatique dans {redirectCountdown} seconde{redirectCountdown !== 1 ? 's' : ''}
                  </span>
                </div>
              </div>
              
              <Button
                onClick={() => {
                  setCurrentView("home");
                  setMeeting(null);
                  setParticipant(null);
                  setMeetingClosed(false);
                  setClosedMeetingInfo(null);
                  setRedirectCountdown(10);
                }}
                className="btn-gradient-primary px-8"
              >
                Retourner à l'accueil maintenant
              </Button>
            </div>
          </div>
        </div>
      );
    }

    if (status === "pending") {
      return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 bg-pattern-dots flex items-center justify-center p-4">
          <div className="glass-card-strong w-full max-w-md border-0 shadow-lg bg-white rounded-2xl overflow-hidden">
            <div className="text-center py-12 p-6">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <Clock className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold mb-4 text-slate-800">En attente d'approbation</h2>
              <p className="text-slate-600 mb-6">
                Votre demande de participation a été envoyée à l'organisateur.
                Veuillez patienter pendant qu'il examine votre demande.
              </p>
              <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                <p className="text-sm text-slate-700">
                  <strong>Réunion:</strong> {meeting?.title}<br />
                  <strong>Participant:</strong> {participant?.name}
                </p>
              </div>
            </div>
          </div>
        </div>
      );
    }

    if (status === "rejected") {
      return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-red-50 bg-pattern-dots flex items-center justify-center p-4">
          <div className="glass-card-strong w-full max-w-md border-0 shadow-lg bg-white rounded-2xl overflow-hidden">
            <div className="text-center py-12 p-6">
              <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-red-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <AlertCircle className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold mb-4 text-red-600">Accès refusé</h2>
              <p className="text-slate-600 mb-6">
                Votre demande de participation a été refusée par l'organisateur.
              </p>
              <Button onClick={() => setCurrentView("home")} className="btn-gradient-primary">
                Retour à l'accueil
              </Button>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 bg-pattern-dots p-4">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="glass-card-strong mb-8 border-0 shadow-lg bg-white rounded-2xl overflow-hidden">
            <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-white bg-opacity-20 rounded-xl flex items-center justify-center">
                    <CheckCircle className="w-6 h-6" />
                  </div>
                  <div>
                    <h1 className="text-xl font-bold">{meeting?.title}</h1>
                    <p className="text-blue-100">
                      Participant: {participant?.name} - Statut: Approuvé
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            {polls.map((poll) => {
              const hasVoted = votedPolls.has(poll.id);
              const canVote = poll.status === "active" && !hasVoted;
              const showResults = hasVoted || (poll.show_results_real_time && poll.status !== "draft");
              
              return (
                <div key={poll.id} className="glass-card border-0 shadow-lg bg-white rounded-2xl overflow-hidden">
                  <div className={`p-6 text-white ${
                    poll.status === "active" ? "bg-gradient-to-r from-blue-500 to-blue-600" :
                    poll.status === "closed" ? "bg-gradient-to-r from-slate-500 to-slate-600" :
                    "bg-gradient-to-r from-blue-400 to-blue-500"
                  }`}>
                    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                      <h2 className="text-lg font-semibold">{poll.question}</h2>
                      <div className="flex items-center gap-2">
                        {poll.status === "active" && (
                          <div className="bg-green-500 text-white px-2 py-1 rounded-full text-sm flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            En cours
                          </div>
                        )}
                        {poll.status === "closed" && (
                          <div className="bg-slate-500 text-white px-2 py-1 rounded-full text-sm">
                            Fermé
                          </div>
                        )}
                        {poll.status === "draft" && (
                          <div className="bg-white bg-opacity-20 text-white px-2 py-1 rounded-full text-sm">
                            À venir
                          </div>
                        )}
                      </div>
                    </div>
                    {canVote && (
                      <p className="text-blue-100 font-medium mt-2">
                        🔒 Votez pour voir les résultats
                      </p>
                    )}
                    {hasVoted && (
                      <p className="text-blue-100 font-medium mt-2">
                        ✅ Vous avez voté - Résultats {poll.show_results_real_time ? "en temps réel" : "finaux"}
                      </p>
                    )}
                    {!canVote && !hasVoted && poll.status !== "active" && (
                      <p className="text-blue-100 mt-2">
                        {poll.status === "closed" ? "Sondage terminé" : "Sondage pas encore lancé"}
                      </p>
                    )}
                  </div>
                  <div className="p-6 bg-white">
                    {canVote ? (
                      <div className="space-y-3">
                        {poll.options.map((option) => (
                          <Button
                            key={option.id}
                            variant="outline"
                            className="w-full justify-start h-12 vote-option border-blue-200 hover:border-blue-400 bg-white hover:bg-blue-50"
                            onClick={() => submitVote(poll.id, option.id)}
                          >
                            <div className="flex items-center gap-3">
                              <div className="w-6 h-6 rounded-full border-2 border-blue-300"></div>
                              <span className="font-medium text-slate-700">{option.text}</span>
                            </div>
                          </Button>
                        ))}
                        <div className="mt-6 bg-blue-50 border border-blue-200 p-4 rounded-xl">
                          <p className="text-sm text-blue-700 flex items-center gap-2">
                            <Shield className="w-4 h-4" />
                            <span className="font-semibold">Vote secret:</span> 
                            Les résultats {poll.show_results_real_time ? "s'affichent" : "ne s'affichent pas"} en temps réel
                          </p>
                        </div>
                      </div>
                    ) : showResults ? (
                      <div className="space-y-4">
                        {poll.options.map((option) => {
                          const totalVotes = poll.options.reduce((sum, opt) => sum + opt.votes, 0);
                          const percentage = totalVotes > 0 ? (option.votes / totalVotes) * 100 : 0;
                          
                          return (
                            <div key={option.id} className="space-y-2">
                              <div className="flex justify-between text-sm">
                                <span className="font-medium">{option.text}</span>
                                <span className="font-bold text-slate-600">
                                  {option.votes} votes ({percentage.toFixed(1)}%)
                                </span>
                              </div>
                              <Progress value={percentage} className="h-3 progress-animated" />
                            </div>
                          );
                        })}
                        {hasVoted && (
                          <div className="mt-4 bg-blue-50 border border-blue-200 p-4 rounded-xl">
                            <p className="text-sm text-blue-700 flex items-center gap-2">
                              <CheckCircle className="w-4 h-4" />
                              <span className="font-semibold">Vote enregistré!</span> 
                              Les résultats se mettent à jour automatiquement
                            </p>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                          <Vote className="w-6 h-6 text-blue-600" />
                        </div>
                        <p className="text-slate-500">
                          {poll.status === "draft" ? "Ce sondage n'est pas encore actif" : "Sondage fermé"}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {polls.length === 0 && (
              <div className="glass-card border-0 shadow-lg bg-white rounded-2xl overflow-hidden">
                <div className="text-center py-12 p-6">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Vote className="w-8 h-8 text-blue-600" />
                  </div>
                  <p className="text-slate-500 text-lg">Aucun sondage n'a encore été créé</p>
                  <p className="text-slate-400 text-sm mt-2">
                    Les sondages apparaîtront ici automatiquement
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  // WebSocket connection
  const connectWebSocket = (meetingId) => {
    const wsUrl = `${BACKEND_URL.replace('https://', 'wss://').replace('http://', 'ws://')}/ws/meetings/${meetingId}`;
    const websocket = new WebSocket(wsUrl);
    
    websocket.onopen = () => {
      console.log("WebSocket connected");
      setWs(websocket);
    };
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("WebSocket message:", data);
      
      // Handle real-time updates based on message type
      if (data.type === "participant_joined" || data.type === "participant_approved") {
        // Refresh participant list for organizer
        if (currentView === "organizer") {
          window.location.reload(); // Simple refresh for now
        }
      }
      
      if (data.type === "poll_started" || data.type === "poll_closed" || data.type === "vote_submitted") {
        // Refresh polls for both organizer and participants
        window.location.reload(); // Simple refresh for now
      }
    };
    
    websocket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
    
    websocket.onclose = () => {
      console.log("WebSocket disconnected");
      setWs(null);
    };
  };

  // Render current view
  const renderCurrentView = () => {
    switch (currentView) {
      case "home":
        return <Home />;
      case "create":
        return <CreateMeeting />;
      case "join":
        return <JoinMeeting />;
      case "organizer":
        return <OrganizerDashboard />;
      case "participant":
        return <ParticipantDashboard />;
      default:
        return <Home />;
    }
  };

  return (
    <div className="App">
      {renderCurrentView()}
    </div>
  );
}

export default App;