import React from 'react';
import Layout from '../components/Layout';
import { useScrutator } from '../hooks/useScrutator';

const ScrutatorDashboard = () => {
  const { state } = useScrutator();
  return (
    <Layout>
      <h1 className="text-2xl font-bold">Scrutator Dashboard</h1>
      <pre>{JSON.stringify(state)}</pre>
    </Layout>
  );
};

export default ScrutatorDashboard;
