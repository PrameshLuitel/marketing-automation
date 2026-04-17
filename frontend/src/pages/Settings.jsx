import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Settings as SettingsIcon, Key, Clock, Bell, Database, Bot,
  Building2, Users, Target, Hash, Rss, Plus, X, Save, Check,
  Swords, TrendingUp, Globe
} from 'lucide-react';
import { api } from '../utils/api';

export default function Settings() {
  const [jobs, setJobs] = useState([]);
  const [usage, setUsage] = useState({});
  const [profile, setProfile] = useState(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [activeSection, setActiveSection] = useState('profile');

  useEffect(() => {
    api.getJobs().then(data => setJobs(data.jobs || [])).catch(() => {});
    api.getLLMUsage().then(setUsage).catch(() => {});
    api.getProfile().then(setProfile).catch(() => setProfile(null));
  }, []);

  const handleSaveProfile = async () => {
    if (!profile) return;
    setSaving(true);
    try {
      await api.updateProfile(profile);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error('Save failed:', err);
    }
    setSaving(false);
  };

  const updateField = (section, field, value) => {
    setProfile(prev => ({
      ...prev,
      [section]: { ...prev[section], [field]: value }
    }));
  };

  const updateListField = (section, field, value) => {
    const items = value.split('\n').map(s => s.trim()).filter(Boolean);
    setProfile(prev => ({
      ...prev,
      [section]: { ...prev[section], [field]: items }
    }));
  };

  const addCompetitor = () => {
    setProfile(prev => ({
      ...prev,
      competitors: [...(prev.competitors || []), {
        name: '', website: '', youtube_channel_id: '', tiktok_handle: '',
        strengths: '', weaknesses: ''
      }]
    }));
  };

  const removeCompetitor = (index) => {
    setProfile(prev => ({
      ...prev,
      competitors: prev.competitors.filter((_, i) => i !== index)
    }));
  };

  const updateCompetitor = (index, field, value) => {
    setProfile(prev => ({
      ...prev,
      competitors: prev.competitors.map((c, i) => i === index ? { ...c, [field]: value } : c)
    }));
  };

  const togglePlatform = (platform) => {
    setProfile(prev => ({
      ...prev,
      platforms: { ...prev.platforms, [platform]: !prev.platforms[platform] }
    }));
  };

  const PROVIDER_COLORS = {
    groq: 'var(--pomegranate-400)', mistral: 'var(--ube-800)',
  };

  const sections = [
    { key: 'profile', label: 'Company Profile', icon: Building2 },
    { key: 'competitors', label: 'Competitors', icon: Swords },
    { key: 'content', label: 'Content Focus', icon: Target },
    { key: 'platforms', label: 'Platforms', icon: Globe },
    { key: 'routing', label: 'Model Routing', icon: Bot },
    { key: 'api', label: 'API & Schedule', icon: Key },
  ];

  if (!profile) {
    return <div className="loading-container"><div className="loading-spinner" /></div>;
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Settings</h1>
          <p className="page-subtitle">Configure your company profile, competitors, content focus, and API keys</p>
        </div>
        <button
          className={`btn ${saved ? 'btn-success' : 'btn-primary'}`}
          onClick={handleSaveProfile}
          disabled={saving}
        >
          {saved ? <><Check size={14} /> Saved!</> : saving ? 'Saving...' : <><Save size={14} /> Save All Changes</>}
        </button>
      </div>

      {/* Section Tabs */}
      <div style={{ display: 'flex', gap: '4px', marginBottom: '24px', borderBottom: '1px solid var(--border-glass)' }}>
        {sections.map(s => (
          <button
            key={s.key}
            onClick={() => setActiveSection(s.key)}
            style={{
              padding: '10px 18px',
              background: activeSection === s.key ? 'rgba(108, 99, 255, 0.12)' : 'transparent',
              border: 'none',
              borderBottom: activeSection === s.key ? '2px solid var(--accent-primary)' : '2px solid transparent',
              color: activeSection === s.key ? 'var(--accent-primary)' : 'var(--text-secondary)',
              cursor: 'pointer', fontFamily: 'var(--font-body)', fontSize: '13px',
              fontWeight: activeSection === s.key ? 600 : 400,
              display: 'flex', alignItems: 'center', gap: '6px',
              transition: 'var(--transition-base)', borderRadius: '8px 8px 0 0',
            }}
          >
            <s.icon size={14} /> {s.label}
          </button>
        ))}
      </div>

      {/* ── Company Profile Section ── */}
      {activeSection === 'profile' && (
        <motion.div className="glass-card" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="chart-title"><Building2 size={16} style={{ color: 'var(--accent-primary)' }} /> Company Information</div>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '20px' }}>
            This information feeds into all AI agents so they generate content tailored to YOUR brand.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <InputField label="Company Name" value={profile.company?.name || ''} onChange={v => updateField('company', 'name', v)} />
            <InputField label="Industry" value={profile.company?.industry || ''} onChange={v => updateField('company', 'industry', v)} placeholder="e.g. Technology, Healthcare, E-commerce" />
            <InputField label="Niche / Sub-Industry" value={profile.company?.niche || ''} onChange={v => updateField('company', 'niche', v)} placeholder="e.g. SaaS, B2B Marketing" />
            <InputField label="Website" value={profile.company?.website || ''} onChange={v => updateField('company', 'website', v)} />
          </div>
          <div style={{ marginTop: '16px', display: 'grid', gap: '16px' }}>
            <TextAreaField label="Company Description" value={profile.company?.description || ''} onChange={v => updateField('company', 'description', v)} rows={3}
              placeholder="What does your company do? What problems do you solve?" />
            <TextAreaField label="Brand Voice" value={profile.company?.brand_voice || ''} onChange={v => updateField('company', 'brand_voice', v)} rows={2}
              placeholder="e.g. Professional yet approachable, data-driven, innovative" />
            <TextAreaField label="Target Audience" value={profile.company?.target_audience || ''} onChange={v => updateField('company', 'target_audience', v)} rows={2}
              placeholder="Who is your ideal customer? Demographics, role, pain points" />
            <TextAreaField label="Unique Selling Points (one per line)" rows={3}
              value={(profile.company?.unique_selling_points || []).join('\n')}
              onChange={v => updateListField('company', 'unique_selling_points', v)}
              placeholder="AI-powered automation\nFree-tier friendly\nAll-in-one platform" />
          </div>
          
          <div className="chart-title" style={{ marginTop: '32px' }}><div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><div style={{ width: 14, height: 14, borderRadius: '50%', background: 'var(--slushie-500)' }}></div> Brand Assets (Motion Graphics)</div></div>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '20px' }}>
            These assets are dynamically injected into 9:16 TikTok-style videos generated by the Remotion & VideoDB engine.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <InputField label="Primary Color (Hex)" value={profile.company?.brand_primary_color || ''} onChange={v => updateField('company', 'brand_primary_color', v)} placeholder="#FF6B6B" />
            <InputField label="Secondary Color (Hex)" value={profile.company?.brand_secondary_color || ''} onChange={v => updateField('company', 'brand_secondary_color', v)} placeholder="#4285F4" />
            <InputField label="Font Family" value={profile.company?.brand_font_family || ''} onChange={v => updateField('company', 'brand_font_family', v)} placeholder="e.g. Inter, Roboto, Outfit" />
            <ImageUploadField label="Brand Logo" value={profile.company?.logo_url || ''} onChange={v => updateField('company', 'logo_url', v)} placeholder="Upload or paste URL..." />
          </div>
          <div style={{ display: 'grid', gap: '16px', marginTop: '16px' }}>
             <MultiImageUploadField 
              label="Product Images" 
              values={profile.company?.product_image_urls || []}
              onChange={v => updateField('company', 'product_image_urls', v)}
             />
          </div>
        </motion.div>
      )}

      {/* ── Competitors Section ── */}
      {activeSection === 'competitors' && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <div className="chart-title" style={{ marginBottom: 4 }}><Swords size={16} style={{ color: 'var(--error)' }} /> Competitors & Similar Companies</div>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>The AI will analyze their content and position you against them.</p>
            </div>
            <button className="btn btn-ghost btn-sm" onClick={addCompetitor}><Plus size={14} /> Add Competitor</button>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {(profile.competitors || []).map((comp, i) => (
              <div key={i} className="glass-card" style={{ position: 'relative' }}>
                <button onClick={() => removeCompetitor(i)} style={{
                  position: 'absolute', top: '12px', right: '12px', background: 'var(--border-light)',
                  border: 'none', color: 'var(--error)', borderRadius: '6px', padding: '4px 8px',
                  cursor: 'pointer', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px'
                }}><X size={12} /> Remove</button>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <InputField label="Company Name" value={comp.name} onChange={v => updateCompetitor(i, 'name', v)} placeholder="e.g. HubSpot" />
                  <InputField label="Website" value={comp.website} onChange={v => updateCompetitor(i, 'website', v)} placeholder="https://competitor.com" />
                  <InputField label="YouTube Channel ID" value={comp.youtube_channel_id} onChange={v => updateCompetitor(i, 'youtube_channel_id', v)} placeholder="UCxxxxxx (optional)" />
                  <InputField label="TikTok Handle" value={comp.tiktok_handle} onChange={v => updateCompetitor(i, 'tiktok_handle', v)} placeholder="@handle (optional)" />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '12px' }}>
                  <TextAreaField label="Their Strengths" value={comp.strengths} onChange={v => updateCompetitor(i, 'strengths', v)} rows={2} placeholder="What are they good at?" />
                  <TextAreaField label="Their Weaknesses" value={comp.weaknesses} onChange={v => updateCompetitor(i, 'weaknesses', v)} rows={2} placeholder="Where do they fall short?" />
                </div>
              </div>
            ))}
            {(profile.competitors || []).length === 0 && (
              <div className="empty-state" style={{ padding: '40px' }}>
                <Swords size={40} style={{ opacity: 0.2, marginBottom: 12 }} />
                <p className="empty-state-title">No competitors added</p>
                <p style={{ color: 'var(--text-muted)', marginBottom: 16 }}>Add competitors to enable competitive analysis</p>
                <button className="btn btn-primary btn-sm" onClick={addCompetitor}><Plus size={14} /> Add Your First Competitor</button>
              </div>
            )}
          </div>
        </motion.div>
      )}

      {/* ── Content Focus Section ── */}
      {activeSection === 'content' && (
        <motion.div className="glass-card" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="chart-title"><Target size={16} style={{ color: 'var(--accent-secondary)' }} /> Content Focus</div>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '20px' }}>
            Define what topics to track, hashtags to monitor, and content sources to scrape. These feed directly into scrapers + Google Trends.
          </p>
          <div style={{ display: 'grid', gap: '16px' }}>
            <TextAreaField label="🔍 Industry Topics to Track (one per line)" rows={5}
              value={(profile.content_focus?.topics || []).join('\n')}
              onChange={v => updateListField('content_focus', 'topics', v)}
              placeholder="marketing automation\nAI in marketing\ncontent strategy\nsocial media trends" />
            <TextAreaField label="# Hashtags to Monitor (one per line, no # symbol)" rows={4}
              value={(profile.content_focus?.hashtags || []).join('\n')}
              onChange={v => updateListField('content_focus', 'hashtags', v)}
              placeholder="digitalmarketing\nmarketingtips\ncontentmarketing" />
            <TextAreaField label="🎬 YouTube Search Queries (one per line)" rows={4}
              value={(profile.content_focus?.youtube_search_queries || []).join('\n')}
              onChange={v => updateListField('content_focus', 'youtube_search_queries', v)}
              placeholder="marketing automation 2026\nAI marketing strategy" />
            <TextAreaField label="📡 RSS Feeds (one URL per line)" rows={5}
              value={(profile.content_focus?.rss_feeds || []).join('\n')}
              onChange={v => updateListField('content_focus', 'rss_feeds', v)}
              placeholder="https://blog.hubspot.com/marketing/rss.xml\nhttps://contentmarketinginstitute.com/feed/" />
          </div>
        </motion.div>
      )}

      {/* ── Platforms Section ── */}
      {activeSection === 'platforms' && (
        <motion.div className="glass-card" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="chart-title"><Globe size={16} style={{ color: 'var(--success)' }} /> Platform Configuration</div>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '20px' }}>
            Enable/disable data sources. Disabled platforms will be skipped during pipeline runs.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
            {[
              { key: 'youtube', name: 'YouTube', desc: 'Scrape video transcripts & metadata via RSS', color: '#ff0000', icon: '🎬' },
              { key: 'tiktok', name: 'TikTok', desc: 'Scrape trending hashtag content', color: '#00f2ea', icon: '📱' },
              { key: 'news_rss', name: 'News / RSS', desc: 'Industry blogs, news, and RSS feeds', color: '#ffa726', icon: '📰' },
              { key: 'google_trends', name: 'Google Trends', desc: 'Trending searches & industry keyword interest', color: '#4285f4', icon: '📈' },
            ].map(p => (
              <div
                key={p.key}
                onClick={() => togglePlatform(p.key)}
                style={{
                  padding: '20px', borderRadius: '12px', cursor: 'pointer',
                  background: profile.platforms?.[p.key] ? 'var(--matcha-300)' : 'var(--border-light)',
                  border: `1px solid ${profile.platforms?.[p.key] ? 'var(--matcha-600)' : 'var(--border-primary)'}`,
                  transition: 'var(--transition-base)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontSize: '20px' }}>{p.icon}</span>
                  <div style={{
                    width: '40px', height: '22px', borderRadius: '11px',
                    background: profile.platforms?.[p.key] ? 'var(--success)' : 'var(--border-primary)',
                    position: 'relative', transition: 'var(--transition-base)',
                  }}>
                    <div style={{
                      width: '16px', height: '16px', borderRadius: '50%', background: 'white',
                      position: 'absolute', top: '3px',
                      left: profile.platforms?.[p.key] ? '21px' : '3px',
                      transition: 'var(--transition-base)',
                    }} />
                  </div>
                </div>
                <div style={{ fontWeight: 600, fontSize: '14px', marginBottom: '4px' }}>{p.name}</div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{p.desc}</div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* ── API & Schedule Section ── */}
      {activeSection === 'api' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '20px' }}>
          <motion.div className="glass-card" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <div className="chart-title"><Key size={16} style={{ color: 'var(--accent-primary)' }} /> API Keys Status</div>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '16px' }}>
              Configured via <code>.env</code> file in the backend directory.
            </p>
            <table className="data-table">
              <thead><tr><th>Provider</th><th>Model</th><th>Daily Usage</th><th>Status</th></tr></thead>
              <tbody>
                {Object.entries(usage).map(([provider, info]) => (
                  <tr key={provider}>
                    <td><span className={`provider-tag provider-${provider}`}>{provider}</span></td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '11px' }}>{info.model || 'N/A'}</td>
                    <td>
                      <div className="usage-bar-container" style={{ marginBottom: 0, minWidth: '120px' }}>
                        <div className="usage-bar-track">
                          <div className="usage-bar-fill" style={{ width: `${Math.min(info.usage_pct || 0, 100)}%`, background: PROVIDER_COLORS[provider] || 'var(--pomegranate-400)' }} />
                        </div>
                        <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                          {info.used || 0} / {(info.limit || 0).toLocaleString()}
                        </span>
                      </div>
                    </td>
                    <td><span className="badge badge-approved" style={{ fontSize: '10px' }}>Connected</span></td>
                  </tr>
                ))}
                {Object.keys(usage).length === 0 && (
                  <tr><td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '20px' }}>
                    No LLM providers configured. Add API keys to the .env file.
                  </td></tr>
                )}
              </tbody>
            </table>
          </motion.div>

          <motion.div className="glass-card" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <div className="chart-title"><Clock size={16} style={{ color: 'var(--warning)' }} /> Scheduled Jobs</div>
            {jobs.length > 0 ? (
              <table className="data-table">
                <thead><tr><th>Job</th><th>Schedule</th><th>Next Run</th></tr></thead>
                <tbody>
                  {jobs.map(job => (
                    <tr key={job.id}>
                      <td style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{job.name}</td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '11px' }}>{job.trigger}</td>
                      <td style={{ fontSize: '12px' }}>{job.next_run ? new Date(job.next_run).toLocaleString() : 'Not scheduled'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="empty-state" style={{ padding: '30px 0' }}>
                <p>No scheduled jobs found. The scheduler starts with the backend.</p>
              </div>
            )}
          </motion.div>
        </div>
      )}

      {/* ── Model Routing Section ── */}
      {activeSection === 'routing' && (
        <motion.div className="glass-card" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="chart-title"><Bot size={16} style={{ color: 'var(--accent-primary)' }} /> Task → Provider Routing</div>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '20px' }}>
            Choose which LLM provider handles each agent task. Changes are saved with the rest of your profile.
          </p>
          <div style={{ display: 'grid', gap: '16px' }}>
            {[
              { key: 'trend_analysis', label: 'Trend Analysis' },
              { key: 'strategy_planning', label: 'Strategy Planning' },
              { key: 'copy_generation', label: 'Copywriting' },
              { key: 'creative_direction', label: 'Creative Direction' },
              { key: 'video_direction', label: 'Video Director' },
              { key: 'critic_review', label: 'Critic Review' },
            ].map(task => (
              <div key={task.key} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 16px', background: 'var(--bg-secondary)', borderRadius: '10px', border: '1px solid var(--border-glass)' }}>
                <span style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-primary)' }}>{task.label}</span>
                <select
                  value={(profile.task_routes || {})[task.key] || 'groq'}
                  onChange={e => {
                    setProfile(prev => ({
                      ...prev,
                      task_routes: { ...(prev.task_routes || {}), [task.key]: e.target.value }
                    }));
                  }}
                  style={{
                    padding: '8px 16px',
                    borderRadius: '8px',
                    background: 'var(--bg-tertiary)',
                    border: '1px solid var(--border-glass)',
                    color: 'var(--text-primary)',
                    fontSize: '13px',
                    fontFamily: 'var(--font-body)',
                    cursor: 'pointer',
                    outline: 'none',
                    minWidth: '160px',
                  }}
                >
                  <option value="groq-llama-8b">Groq (Llama 8b Fast)</option>
                  <option value="groq-llama-70b">Groq (Llama 70b Reasoning)</option>
                  <option value="mistral">Mistral (Strategy)</option>
                  <option value="gemini">Gemini (Creative)</option>
                  {task.key === 'critic_review' && <option value="multi">Multi-LLM Council (All)</option>}
                </select>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}

/* ── Reusable Input Components ── */

function InputField({ label, value, onChange, placeholder = '' }) {
  return (
    <div>
      <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--text-label)', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
        {label}
      </label>
      <input
        type="text"
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        style={{
          width: '100%', padding: '10px 14px', borderRadius: '8px',
          background: 'var(--bg-tertiary)', border: '1px solid var(--border-glass)',
          color: 'var(--text-primary)', fontSize: '13px', fontFamily: 'var(--font-body)',
          outline: 'none', transition: 'var(--transition-base)',
        }}
        onFocus={e => e.target.style.borderColor = 'var(--accent-primary)'}
        onBlur={e => e.target.style.borderColor = 'var(--border-glass)'}
      />
    </div>
  );
}

function TextAreaField({ label, value, onChange, rows = 3, placeholder = '' }) {
  return (
    <div>
      <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--text-label)', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
        {label}
      </label>
      <textarea
        value={value}
        onChange={e => onChange(e.target.value)}
        rows={rows}
        placeholder={placeholder}
        style={{
          width: '100%', padding: '10px 14px', borderRadius: '8px',
          background: 'var(--bg-tertiary)', border: '1px solid var(--border-glass)',
          color: 'var(--text-primary)', fontSize: '13px', fontFamily: 'var(--font-body)',
          outline: 'none', transition: 'var(--transition-base)', resize: 'vertical',
          lineHeight: '1.5',
        }}
        onFocus={e => e.target.style.borderColor = 'var(--accent-primary)'}
        onBlur={e => e.target.style.borderColor = 'var(--border-glass)'}
      />
    </div>
  );
}

function ImageUploadField({ label, value, onChange, placeholder = '' }) {
  const [uploading, setUploading] = useState(false);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    try {
      const res = await api.uploadAsset(file);
      // Construct a full URL to avoid CORS/relative path issues in the video renderer
      const fullUrl = window.location.origin + res.url.replace('/api/', '/');
      onChange(fullUrl);
    } catch (err) {
      alert("Failed to upload image. Please try again.");
    }
    setUploading(false);
  };

  return (
    <div>
      <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--text-label)', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
        {label}
      </label>
      <div style={{ display: 'flex', gap: '8px' }}>
        <div style={{ flex: 1, position: 'relative' }}>
          <input
            type="text"
            value={value}
            onChange={e => onChange(e.target.value)}
            placeholder={placeholder}
            style={{
              width: '100%', padding: '10px 14px', borderRadius: '8px',
              background: 'var(--bg-tertiary)', border: '1px solid var(--border-glass)',
              color: 'var(--text-primary)', fontSize: '13px', fontFamily: 'var(--font-body)',
              outline: 'none', transition: 'var(--transition-base)', boxSizing: 'border-box'
            }}
          />
        </div>
        <div style={{ position: 'relative', display: 'flex' }}>
          <button className="btn btn-secondary" style={{ padding: '9px 14px', height: '100%' }} disabled={uploading}>
            {uploading ? '...' : <Plus size={16} />} 
          </button>
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            style={{ position: 'absolute', inset: 0, opacity: 0, cursor: 'pointer', width: '100%', height: '100%', zIndex: 10 }}
            title="Upload Image"
          />
        </div>
      </div>
      {value && (
        <div style={{ marginTop: '8px', padding: '8px', background: 'var(--bg-tertiary)', borderRadius: '8px', display: 'inline-block', border: '1px solid var(--border-glass)' }}>
          <img src={value} alt="Preview" style={{ height: '32px', maxWidth: '200px', objectFit: 'contain' }} />
        </div>
      )}
    </div>
  );
}

function MultiImageUploadField({ label, values, onChange }) {
  const [uploading, setUploading] = useState(false);

  const handleFileChange = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;
    setUploading(true);
    try {
      const newUrls = [...values];
      for (const file of files) {
        const res = await api.uploadAsset(file);
        const fullUrl = window.location.origin + res.url.replace('/api/', '/');
        newUrls.push(fullUrl);
      }
      onChange(newUrls);
    } catch (err) {
      alert("Failed to upload image(s). Please try again.");
    }
    setUploading(false);
  };

  const removeImage = (index) => {
    const newUrls = [...values];
    newUrls.splice(index, 1);
    onChange(newUrls);
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
        <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--text-label)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
          {label}
        </label>
        <div style={{ position: 'relative', display: 'flex' }}>
          <button className="btn btn-secondary btn-sm" disabled={uploading}>
            {uploading ? '...' : <><Plus size={14} /> Upload Images</>}
          </button>
          <input
            type="file"
            accept="image/*"
            multiple
            onChange={handleFileChange}
            style={{ position: 'absolute', inset: 0, opacity: 0, cursor: 'pointer', width: '100%', height: '100%', zIndex: 10 }}
            title="Upload Images"
          />
        </div>
      </div>
      
      {values.length === 0 ? (
        <div style={{ padding: '24px', textAlign: 'center', background: 'var(--bg-tertiary)', border: '1px dashed var(--border-glass)', borderRadius: '8px', color: 'var(--text-muted)', fontSize: '12px' }}>
          No product images added yet. Click &quot;Upload Images&quot; to add some.
        </div>
      ) : (
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', background: 'var(--bg-tertiary)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-glass)' }}>
          {values.map((url, i) => (
            <div key={i} style={{ position: 'relative', width: '80px', height: '80px', borderRadius: '6px', overflow: 'hidden', border: '1px solid var(--border-glass)', background: 'var(--bg-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <img src={url} alt={`Product ${i+1}`} style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }} />
              <button 
                onClick={() => removeImage(i)}
                style={{ position: 'absolute', top: 4, right: 4, background: 'rgba(0,0,0,0.6)', border: 'none', color: '#fff', borderRadius: '50%', width: '20px', height: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}
              >
                <X size={12} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
