import { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, CartesianGrid
} from 'recharts';
import { TrendingUp, Hash, Brain, Globe, Flame, Image as ImageIcon, MessageSquare, Activity } from 'lucide-react';
import { api } from '../utils/api';
import { SkeletonCard, SkeletonGraph } from '../components/Skeleton';

const EMOTION_COLORS = {
  joy: 'var(--matcha-600)',
  surprise: 'var(--slushie-500)',
  neutral: 'var(--text-secondary)',
  sadness: 'var(--ube-800)',
  anger: 'var(--pomegranate-400)',
  fear: 'var(--lemon-500)',
  disgust: 'var(--blueberry-800)',
};

const GEO_FLAGS = {
  "": "🌍",
  "US": "🇺🇸",
  "IN": "🇮🇳",
  "NP": "🇳🇵",
  "GB": "🇬🇧",
  "AU": "🇦🇺",
  "CA": "🇨🇦",
  "DE": "🇩🇪",
  "BR": "🇧🇷",
  "JP": "🇯🇵",
  "NG": "🇳🇬",
  "PH": "🇵🇭"
};

const GEO_LABELS = {
  "": "Worldwide Pulse",
  "US": "United States",
  "IN": "India",
  "NP": "Nepal",
  "GB": "United Kingdom",
  "AU": "Australia",
  "CA": "Canada",
  "DE": "Germany",
  "BR": "Brazil",
  "JP": "Japan",
  "NG": "Nigeria",
  "PH": "Philippines"
};

export default function Trends() {
  const [activeTab, setActiveTab] = useState('world-pulse');
  const [trendsData, setTrendsData] = useState(null);
  const [pulseData, setPulseData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getTrends(),
      api.getWorldPulse()
    ])
      .then(([trends, pulse]) => {
        setTrendsData(trends);
        setPulseData(pulse);
      })
      .catch(() => {
        setTrendsData(null);
        setPulseData(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const groupedTrends = useMemo(() => {
    if (!pulseData || !pulseData.google_trends) return {};
    const grouped = {};
    pulseData.google_trends.forEach(item => {
      const geo = item.metadata.geo || "";
      if (!grouped[geo]) grouped[geo] = [];
      grouped[geo].push(item);
    });
    return grouped;
  }, [pulseData]);

  if (loading) {
    return (
      <div>
        <div className="page-header">
          <div><h1 className="page-title">Global Pulse</h1><p className="page-subtitle">Real-time worldwide trends & meme radar</p></div>
        </div>
        <div style={{ display: 'flex', gap: '16px', marginBottom: '32px' }}>
             <button style={{ padding: '8px 24px', borderRadius: '24px', background: 'var(--bg-secondary)', border: '1px solid var(--border-glass)' }}>World Pulse</button>
             <button style={{ padding: '8px 24px', borderRadius: '24px', background: 'var(--bg-secondary)', border: '1px solid var(--border-glass)' }}>Analytics</button>
        </div>
        <div className="chart-grid">
          <SkeletonGraph />
          <SkeletonGraph />
        </div>
      </div>
    );
  }

  const trends = trendsData || { top_topics: [], emotion_distribution: {}, sentiment_timeline: {} };
  const emotionData = Object.entries(trends.emotion_distribution || {}).map(
    ([name, count]) => ({ name, value: count })
  );
  const topicData = (trends.top_topics || []).slice(0, 15);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Global Intelligence</h1>
          <p className="page-subtitle">Worldwide search trends, viral memes, and deep sentiment analytics</p>
        </div>
      </div>

      <div style={{
        display: 'flex', gap: '12px', marginBottom: '32px',
        borderBottom: '1px solid var(--border-glass)', paddingBottom: '16px'
      }}>
        <button
          onClick={() => setActiveTab('world-pulse')}
          style={{
            display: 'flex', alignItems: 'center', gap: '8px',
            padding: '8px 20px', borderRadius: '20px',
            background: activeTab === 'world-pulse' ? 'var(--accent-primary)' : 'var(--bg-secondary)',
            color: activeTab === 'world-pulse' ? '#fff' : 'var(--text-secondary)',
            border: activeTab === 'world-pulse' ? 'none' : '1px solid var(--border-glass)',
            fontWeight: 600, fontSize: '14px', cursor: 'pointer', transition: 'all 0.2s'
          }}
        >
          <Globe size={16} /> World Pulse & Memes
        </button>
        <button
          onClick={() => setActiveTab('analytics')}
          style={{
            display: 'flex', alignItems: 'center', gap: '8px',
            padding: '8px 20px', borderRadius: '20px',
            background: activeTab === 'analytics' ? 'var(--accent-primary)' : 'var(--bg-secondary)',
            color: activeTab === 'analytics' ? '#fff' : 'var(--text-secondary)',
            border: activeTab === 'analytics' ? 'none' : '1px solid var(--border-glass)',
            fontWeight: 600, fontSize: '14px', cursor: 'pointer', transition: 'all 0.2s'
          }}
        >
          <Brain size={16} /> Analytics & Sentiments
        </button>
      </div>

      <AnimatePresence mode="wait">
        {activeTab === 'analytics' ? (
          <motion.div
            key="analytics"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            <div className="chart-grid">
              {/* Top Topics */}
              <div className="chart-card">
                <div className="chart-title">
                  <Hash size={16} style={{ color: 'var(--accent-secondary)' }} />
                  Top Topics
                </div>
                {topicData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={topicData} layout="vertical" barSize={16}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.05)" />
                      <XAxis type="number" tick={{ fill: '#9f9b93', fontSize: 13 }} axisLine={{ stroke: 'rgba(0,0,0,0.1)' }} />
                      <YAxis dataKey="name" type="category" tick={{ fill: '#9f9b93', fontSize: 13 }} axisLine={{ stroke: 'rgba(0,0,0,0.1)' }} width={140} />
                      <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid var(--border-primary)', borderRadius: '12px', color: '#000000', fontSize: '14px', boxShadow: 'var(--shadow-clay)' }} />
                      <Bar dataKey="count" fill="var(--slushie-500)" radius={[0, 12, 12, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="empty-state" style={{ padding: '60px 0' }}>
                    <TrendingUp size={48} style={{ opacity: 0.2, marginBottom: 16 }} />
                    <p className="empty-state-title">No topics discovered yet</p>
                  </div>
                )}
              </div>

              {/* Emotion Distribution */}
              <div className="chart-card">
                <div className="chart-title">
                  <Brain size={16} style={{ color: 'var(--accent-primary)' }} />
                  Emotion Distribution
                </div>
                {emotionData.length > 0 ? (
                  <>
                    <ResponsiveContainer width="100%" height={280}>
                      <PieChart>
                        <Pie data={emotionData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={3} dataKey="value">
                          {emotionData.map((entry) => <Cell key={entry.name} fill={EMOTION_COLORS[entry.name] || '#6c63ff'} />)}
                        </Pie>
                        <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid var(--border-primary)', borderRadius: '12px', color: '#000000', fontSize: '14px', boxShadow: 'var(--shadow-clay)' }} />
                      </PieChart>
                    </ResponsiveContainer>
                    <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '12px', marginTop: '12px' }}>
                      {emotionData.map(({ name }) => (
                        <div key={name} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                          <div style={{ width: 8, height: 8, borderRadius: '50%', background: EMOTION_COLORS[name] || '#6c63ff' }} />
                          {name}
                        </div>
                      ))}
                    </div>
                  </>
                ) : (
                  <div className="empty-state" style={{ padding: '60px 0' }}>
                    <Brain size={48} style={{ opacity: 0.2, marginBottom: 16 }} />
                    <p className="empty-state-title">No emotion data yet</p>
                  </div>
                )}
              </div>
            </div>

            {/* Sentiment Timeline */}
            <div className="chart-card" style={{ marginTop: '20px' }}>
              <div className="chart-title">
                <TrendingUp size={16} style={{ color: 'var(--success)' }} />
                Sentiment Over Time
              </div>
              {Object.keys(trends.sentiment_timeline || {}).length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={Object.entries(trends.sentiment_timeline).map(([date, vals]) => ({ date, positive: vals.positive || 0, negative: vals.negative || 0, neutral: vals.neutral || 0 }))}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.05)" />
                    <XAxis dataKey="date" tick={{ fill: '#9f9b93', fontSize: 13 }} />
                    <YAxis tick={{ fill: '#9f9b93', fontSize: 13 }} />
                    <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid var(--border-primary)', borderRadius: '12px', color: '#000000', fontSize: '14px', boxShadow: 'var(--shadow-clay)' }} />
                    <Bar dataKey="positive" stackId="a" fill="var(--matcha-600)" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="neutral" stackId="a" fill="var(--lemon-500)" />
                    <Bar dataKey="negative" stackId="a" fill="var(--pomegranate-400)" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="empty-state" style={{ padding: '40px 0' }}>
                  <p>Sentiment timeline appears after multiple pipeline runs</p>
                </div>
              )}
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="world-pulse"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            {(!pulseData || (pulseData.google_trends.length === 0 && pulseData.memes.length === 0)) ? (
               <div className="empty-state" style={{ padding: '80px 0', border: '1px dashed var(--border-primary)', borderRadius: '16px' }}>
                  <Globe size={48} style={{ opacity: 0.2, marginBottom: 16 }} />
                  <p className="empty-state-title">No pulse data found</p>
                  <p>Wait for the global scrapers to run their daily discovery sweeps.</p>
               </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.2fr) minmax(0, 0.8fr)', gap: '24px' }}>
                
                {/* Visual Memes Feed */}
                <div>
                  <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Flame size={20} style={{ color: 'var(--pomegranate-500)' }} /> Trending Memes & Viral Culture
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {pulseData.memes.slice(0, 30).map(meme => (
                      <div key={meme.id} style={{ 
                        background: 'var(--bg-secondary)', borderRadius: '16px', border: '1px solid var(--border-glass)',
                        overflow: 'hidden', display: 'flex', flexDirection: 'column'
                      }}>
                        {meme.metadata.image_url && (
                          <div style={{ width: '100%', maxHeight: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#000' }}>
                            <img src={meme.metadata.image_url} alt={meme.title} style={{ maxWidth: '100%', maxHeight: '400px', objectFit: 'contain' }} loading="lazy" />
                          </div>
                        )}
                        <div style={{ padding: '16px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                            <span style={{ fontSize: '11px', fontWeight: 600, padding: '4px 8px', borderRadius: '4px', background: 'var(--accent-primary)', color: 'white', textTransform: 'uppercase' }}>
                              {meme.metadata.subreddit ? `r/${meme.metadata.subreddit}` : meme.metadata.source || 'Viral'}
                            </span>
                             <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                               {new Date(meme.scraped_at).toLocaleDateString()}
                             </span>
                          </div>
                          <h4 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '8px', lineHeight: '1.4' }}>{meme.title}</h4>
                          <div style={{ display: 'flex', gap: '16px', color: 'var(--text-secondary)', fontSize: '13px' }}>
                             {meme.like_count > 0 && (
                               <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                 <TrendingUp size={14} /> {meme.like_count}
                               </span>
                             )}
                             {meme.comment_count > 0 && (
                               <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                 <MessageSquare size={14} /> {meme.comment_count}
                               </span>
                             )}
                          </div>
                          {meme.url && (
                            <a href={meme.url} target="_blank" rel="noreferrer" style={{ display: 'inline-block', marginTop: '12px', fontSize: '13px', color: 'var(--accent-primary)', textDecoration: 'none', fontWeight: 600 }}>
                              Source Link →
                            </a>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Regional Trends */}
                <div>
                   <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Activity size={20} style={{ color: 'var(--accent-secondary)' }} /> Local Google Trends
                  </h3>
                   
                   <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                     {Object.entries(groupedTrends).map(([geo, items]) => (
                        <div key={geo} style={{ background: 'var(--bg-secondary)', borderRadius: '12px', border: '1px solid var(--border-glass)', padding: '16px' }}>
                          <h4 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-primary)' }}>
                            <span style={{ fontSize: '18px' }}>{GEO_FLAGS[geo] || "🌐"}</span>
                            {GEO_LABELS[geo] || `Region: ${geo}`}
                          </h4>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                            {items.slice(0, 15).map(item => (
                              <div key={item.id} style={{ 
                                padding: '6px 12px', background: 'var(--bg-primary)', borderRadius: '8px', 
                                fontSize: '13px', color: 'var(--text-secondary)', border: '1px solid var(--border-primary)',
                                display: 'flex', alignItems: 'center', gap: '6px'
                              }}>
                                <Hash size={12} style={{ opacity: 0.5 }} /> {item.title || item.text.split('\n')[0].replace('REALTIME TREND:', '').trim()}
                              </div>
                            ))}
                          </div>
                        </div>
                     ))}
                   </div>
                </div>

              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
