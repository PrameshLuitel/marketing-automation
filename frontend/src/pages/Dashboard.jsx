import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, AreaChart, Area, CartesianGrid
} from 'recharts';
import {
  FileText, TrendingUp, Database, Bot, Zap,
  CheckCircle, Clock, AlertTriangle
} from 'lucide-react';
import { api } from '../utils/api';
import { SkeletonCard, SkeletonGraph } from '../components/Skeleton';

const SENTIMENT_COLORS = {
  positive: 'var(--matcha-600)',
  negative: 'var(--pomegranate-400)',
  neutral: 'var(--lemon-500)',
};

const PROVIDER_COLORS = {
  groq: 'var(--pomegranate-400)',
  gemini: 'var(--slushie-500)',
  mistral: 'var(--ube-800)',
};

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i) => ({
    opacity: 1, y: 0,
    transition: { delay: i * 0.1, duration: 0.4, ease: 'easeOut' },
  }),
};

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getDashboardSummary()
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div>
        <div className="page-header">
          <div><h1 className="page-title">Command Center</h1><p className="page-subtitle">Real-time overview of your marketing automation pipeline</p></div>
        </div>
        <div className="stat-grid">
          {[1, 2, 3, 4].map(i => <SkeletonCard key={i} />)}
        </div>
        <div className="chart-grid mt-6">
          <SkeletonGraph />
          <SkeletonGraph />
        </div>
      </div>
    );
  }

  // If no data from API, show welcome state with demo data
  const summary = data || {
    total_content: 0,
    today_content: 0,
    platforms: {},
    total_campaigns: 0,
    pending_campaigns: 0,
    sentiment_distribution: {},
    recent_runs: [],
    llm_usage: {},
    vector_store: { content_count: 0 },
  };

  const sentimentData = Object.entries(summary.sentiment_distribution || {}).map(
    ([name, value]) => ({ name, value })
  );

  const platformData = Object.entries(summary.platforms || {}).map(
    ([name, value]) => ({ name, value })
  );

  const usageData = Object.entries(summary.llm_usage || {}).map(
    ([provider, info]) => ({
      provider,
      used: info.used || 0,
      limit: info.limit || 1,
      pct: info.usage_pct || 0,
    })
  );

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Command Center</h1>
          <p className="page-subtitle">Real-time overview of your marketing automation pipeline</p>
        </div>
      </div>

      {/* Stat Cards */}
      <div className="stat-grid">
        {[
          {
            label: 'Total Content',
            value: summary.total_content.toLocaleString(),
            detail: `${summary.today_content} scraped today`,
            accent: 'var(--accent-gradient)',
            icon: Database,
          },
          {
            label: 'Campaigns',
            value: summary.total_campaigns,
            detail: `${summary.pending_campaigns} pending review`,
            accent: 'var(--accent-gradient-purple)',
            icon: FileText,
          },
          {
            label: 'Embeddings',
            value: (summary.vector_store?.content_count || 0).toLocaleString(),
            detail: 'Semantic vectors stored',
            accent: 'var(--accent-gradient-green)',
            icon: Bot,
          },
          {
            label: 'Pipeline Runs',
            value: (summary.recent_runs || []).length,
            detail: summary.recent_runs?.[0]?.status === 'completed' 
              ? '✅ Last run succeeded' 
              : '⏳ Awaiting first run',
            accent: 'var(--accent-gradient-warm)',
            icon: Zap,
          },
        ].map((stat, i) => (
          <motion.div
            key={stat.label}
            className="stat-card"
            style={{ '--card-accent': stat.accent }}
            custom={i}
            initial="hidden"
            animate="visible"
            variants={cardVariants}
          >
            <div className="stat-label">{stat.label}</div>
            <div className="stat-value">{stat.value}</div>
            <div className="stat-detail">{stat.detail}</div>
          </motion.div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="chart-grid">
        {/* Sentiment Distribution */}
        <motion.div
          className="chart-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="chart-title">
            <TrendingUp size={16} style={{ color: 'var(--accent-secondary)' }} />
            Sentiment Distribution
          </div>
          {sentimentData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {sentimentData.map((entry) => (
                    <Cell
                      key={entry.name}
                      fill={SENTIMENT_COLORS[entry.name] || '#6c63ff'}
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: '#ffffff',
                    border: '1px solid var(--border-primary)',
                    borderRadius: '12px',
                    color: '#000000',
                    fontSize: '14px',
                    boxShadow: 'var(--shadow-clay)'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state" style={{ padding: '40px 0' }}>
              <p>No sentiment data yet. Run the pipeline to start analyzing!</p>
            </div>
          )}
          <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginTop: '8px' }}>
            {Object.entries(SENTIMENT_COLORS).map(([label, color]) => (
              <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: color }} />
                {label}
              </div>
            ))}
          </div>
        </motion.div>

        {/* Platform Volume */}
        <motion.div
          className="chart-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <div className="chart-title">
            <Database size={16} style={{ color: 'var(--accent-primary)' }} />
            Content by Platform
          </div>
          {platformData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={platformData} barSize={32}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.05)" />
                <XAxis
                  dataKey="name"
                  tick={{ fill: '#9f9b93', fontSize: 14 }}
                  axisLine={{ stroke: 'rgba(0,0,0,0.1)' }}
                />
                <YAxis
                  tick={{ fill: '#9f9b93', fontSize: 14 }}
                  axisLine={{ stroke: 'rgba(0,0,0,0.1)' }}
                />
                <Tooltip
                  contentStyle={{
                    background: '#ffffff',
                    border: '1px solid var(--border-primary)',
                    borderRadius: '12px',
                    color: '#000000',
                    fontSize: '14px',
                    boxShadow: 'var(--shadow-clay)'
                  }}
                />
                <Bar dataKey="value" fill="var(--slushie-500)" radius={[12, 12, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state" style={{ padding: '40px 0' }}>
              <p>No content scraped yet. Run the pipeline to start!</p>
            </div>
          )}
        </motion.div>
      </div>

      {/* LLM Usage + Recent Runs */}
      <div className="chart-grid">
        {/* LLM Provider Usage */}
        <motion.div
          className="chart-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <div className="chart-title">
            <Bot size={16} style={{ color: 'var(--accent-primary)' }} />
            LLM Provider Budget
          </div>
          {usageData.length > 0 ? (
            usageData.map((item) => (
              <div key={item.provider} className="usage-bar-container">
                <div className="usage-bar-label">
                  <span className={`provider-tag provider-${item.provider}`}>
                    {item.provider}
                  </span>
                  <span style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: '12px' }}>
                    {item.used} / {item.limit.toLocaleString()}
                  </span>
                </div>
                <div className="usage-bar-track">
                  <div
                    className="usage-bar-fill"
                    style={{
                      width: `${Math.min(item.pct, 100)}%`,
                      background: PROVIDER_COLORS[item.provider] || '#6c63ff',
                    }}
                  />
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state" style={{ padding: '40px 0' }}>
              <p>LLM usage will appear here after pipeline runs</p>
            </div>
          )}
        </motion.div>

        {/* Recent Pipeline Runs */}
        <motion.div
          className="chart-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          <div className="chart-title">
            <Clock size={16} style={{ color: 'var(--warning)' }} />
            Recent Pipeline Runs
          </div>
          {(summary.recent_runs || []).length > 0 ? (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Run ID</th>
                  <th>Status</th>
                  <th>Items</th>
                  <th>Campaigns</th>
                </tr>
              </thead>
              <tbody>
                {summary.recent_runs.map((run) => (
                  <tr key={run.run_id}>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{run.run_id}</td>
                    <td>
                      {run.status === 'completed' ? (
                        <span className="badge badge-approved">
                          <CheckCircle size={10} /> Done
                        </span>
                      ) : run.status === 'failed' ? (
                        <span className="badge badge-rejected">
                          <AlertTriangle size={10} /> Failed
                        </span>
                      ) : (
                        <span className="badge badge-pending">
                          <Clock size={10} /> Running
                        </span>
                      )}
                    </td>
                    <td>{run.items_scraped}</td>
                    <td>{run.campaigns_generated}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="empty-state" style={{ padding: '40px 0' }}>
              <p>No pipeline runs yet. Click "Run Pipeline" to start!</p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
