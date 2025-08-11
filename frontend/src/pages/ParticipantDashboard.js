import React from 'react';
import Layout from '../components/Layout';
import { useParticipant } from '../hooks/useParticipant';

const ParticipantDashboard = () => {
  const { state } = useParticipant();
  return (
    <Layout>
      <h1 className="text-2xl font-bold">Participant Dashboard</h1>
      <pre>{JSON.stringify(state)}</pre>
    </Layout>
  );
};

export default ParticipantDashboard;
