import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import OrganizerDashboard from './pages/OrganizerDashboard';
import ParticipantDashboard from './pages/ParticipantDashboard';
import ScrutatorDashboard from './pages/ScrutatorDashboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/organizer" element={<OrganizerDashboard />} />
        <Route path="/participant" element={<ParticipantDashboard />} />
        <Route path="/scrutator" element={<ScrutatorDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
