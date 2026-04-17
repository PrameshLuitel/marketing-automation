import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Trends from './pages/Trends';
import Campaigns from './pages/Campaigns';
import CampaignDetail from './pages/CampaignDetail';
import Gallery from './pages/Gallery';
import Logs from './pages/Logs';
import Settings from './pages/Settings';

export default function App() {
  return (
    <Router>
      <div className="app-layout">
        <Sidebar />
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/trends" element={<Trends />} />
            <Route path="/campaigns" element={<Campaigns />} />
            <Route path="/campaigns/:id" element={<CampaignDetail />} />
            <Route path="/images" element={<Gallery viewMode="image" />} />
            <Route path="/videos" element={<Gallery viewMode="video" />} />
            <Route path="/logs" element={<Logs />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
