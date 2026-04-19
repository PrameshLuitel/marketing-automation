import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, TrendingUp, FileText, Palette, Video, ScrollText,
  Settings, Zap, Search, Image, Clapperboard
} from 'lucide-react';
import { useState, useEffect } from 'react';
import { api } from '../utils/api';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/trends', label: 'Trends', icon: TrendingUp },
  { path: '/campaigns', label: 'Campaigns', icon: FileText, badgeKey: 'pending_campaigns' },
  { path: '/studio/images', label: 'Image Studio', icon: Image },
  { path: '/studio/videos', label: 'Video Studio', icon: Clapperboard },
  { path: '/images', label: 'Image Gallery', icon: Palette },
  { path: '/videos', label: 'Video Gallery', icon: Video },
  { path: '/logs', label: 'Agent Logs', icon: ScrollText },
];

const bottomItems = [
  { path: '/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar() {
  const location = useLocation();
  const [pendingCount, setPendingCount] = useState(0);

  useEffect(() => {
    api.getDashboardSummary()
      .then(data => setPendingCount(data.pending_campaigns || 0))
      .catch(() => {});
  }, [location.pathname]);

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">M</div>
        <div className="sidebar-logo-text">
          <span>Marketing</span> AI
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section-label">Main</div>
        {navItems.map(item => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `nav-item ${isActive && (item.path === '/' ? location.pathname === '/' : true) ? 'active' : ''}`
            }
            end={item.path === '/'}
          >
            <item.icon className="nav-icon" />
            <span>{item.label}</span>
            {item.badgeKey && pendingCount > 0 && (
              <span className="nav-badge">{pendingCount}</span>
            )}
          </NavLink>
        ))}

        <div style={{ flex: 1 }} />

        <div className="nav-section-label">System</div>
        {bottomItems.map(item => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <item.icon className="nav-icon" />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
