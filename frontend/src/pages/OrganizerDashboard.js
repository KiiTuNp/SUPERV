import React from 'react';
import Layout from '../components/Layout';
import { useOrganizer } from '../hooks/useOrganizer';

const OrganizerDashboard = () => {
  const { state } = useOrganizer();
  return (
    <Layout>
      <h1 className="text-2xl font-bold">Organizer Dashboard</h1>
      <pre>{JSON.stringify(state)}</pre>
    </Layout>
  );
};

export default OrganizerDashboard;
