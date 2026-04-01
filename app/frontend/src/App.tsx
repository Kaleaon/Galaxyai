import { NavLink, Route, Routes } from 'react-router-dom';
import { MOCK_MODE } from './api/client';
import { DomainRegistrationPage } from './pages/DomainRegistrationPage';
import { FactIngestionPage } from './pages/FactIngestionPage';
import { Map3DPage } from './pages/Map3DPage';
import { QueryResultsPage } from './pages/QueryResultsPage';

const tabs = [
  { to: '/', label: 'Domain Registration' },
  { to: '/ingest', label: 'Fact Ingestion' },
  { to: '/query', label: 'Query Results' },
  { to: '/map3d', label: '3D Map View' },
];

export default function App() {
  return (
    <main className="app-shell">
      <header>
        <h1>GalaxyAI Knowledge Console</h1>
        <p>{MOCK_MODE ? 'Mock mode enabled (VITE_API_MOCK_MODE=true)' : 'Live API mode'}</p>
        <nav className="tabs">
          {tabs.map((tab) => (
            <NavLink key={tab.to} to={tab.to} className={({ isActive }) => (isActive ? 'tab active' : 'tab')} end={tab.to === '/'}>
              {tab.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <Routes>
        <Route path="/" element={<DomainRegistrationPage />} />
        <Route path="/ingest" element={<FactIngestionPage />} />
        <Route path="/query" element={<QueryResultsPage />} />
        <Route path="/map3d" element={<Map3DPage />} />
      </Routes>
    </main>
  );
}
