import React from 'react';
import { Link } from 'react-router-dom';

const Layout = ({ children }) => (
  <div>
    <nav className="p-4 bg-gray-100 flex gap-4">
      <Link to="/">Home</Link>
      <Link to="/organizer">Organizer</Link>
      <Link to="/participant">Participant</Link>
      <Link to="/scrutator">Scrutator</Link>
    </nav>
    <main className="p-4">{children}</main>
  </div>
);

export default Layout;
