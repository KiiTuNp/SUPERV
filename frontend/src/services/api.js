import axios from 'axios';

const BASE_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

const apiClient = axios.create();

// Inject base URL and common headers
apiClient.interceptors.request.use(
  (config) => {
    config.baseURL = `${BASE_URL}/api`;
    config.headers = {
      'Content-Type': 'application/json',
      ...config.headers,
    };
    return config;
  },
  (error) => Promise.reject(error)
);

// Global error handler
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API error:', error);
    return Promise.reject(error);
  }
);

const api = {
  heartbeat: (meetingId, data) => apiClient.post(`/meetings/${meetingId}/heartbeat`, data),
  canCloseMeeting: (meetingId) => apiClient.get(`/meetings/${meetingId}/can-close`),
  recoverMeeting: (data) => apiClient.post('/meetings/recover', data),
  createMeeting: (data) => apiClient.post('/meetings', data),
  joinScrutator: (data) => apiClient.post('/scrutators/join', data),
  joinParticipant: (data) => apiClient.post('/participants/join', data),
  getMeeting: (code) => apiClient.get(`/meetings/${code}`),
  getOrganizer: (meetingId) => apiClient.get(`/meetings/${meetingId}/organizer`),
  approveParticipant: (participantId, approved) =>
    apiClient.post(`/participants/${participantId}/approve`, {
      participant_id: participantId,
      approved,
    }),
  createPoll: (meetingId, data) => apiClient.post(`/meetings/${meetingId}/polls`, data),
  startPoll: (pollId) => apiClient.post(`/polls/${pollId}/start`),
  closePoll: (pollId) => apiClient.post(`/polls/${pollId}/close`),
  addScrutator: (meetingId, data) => apiClient.post(`/meetings/${meetingId}/scrutators`, data),
  listScrutators: (meetingId) => apiClient.get(`/meetings/${meetingId}/scrutators`),
  generateRecovery: (meetingId) => apiClient.post(`/meetings/${meetingId}/generate-recovery`),
  getParticipantStatus: (participantId) => apiClient.get(`/participants/${participantId}/status`),
  getParticipantPolls: (meetingId) => apiClient.get(`/meetings/${meetingId}/polls/participant`),
  submitVote: (data) => apiClient.post('/votes', data),
};

export default api;
