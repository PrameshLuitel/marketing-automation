import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ScrollText, Clock, Cpu, AlertTriangle } from 'lucide-react';
import { api } from '../utils/api';
import { SkeletonCard } from '../components/Skeleton';

const PROVIDER_COLORS = {
  groq: { bg: 'rgba(255, 107, 107, 0.15)', color: '#ff6b6b' },
  gemini: { bg: 'rgba(0, 212, 255, 0.15)', color: '#00d4ff' },
  mistral: { bg: 'rgba(168, 85, 247, 0.15)', color: '#a855f7' },
};

const AGENT_ICONS = {
  trend_analyst: '🔍',
  strategy_planner: '🎯',
  copywriter: '✍️',
  creative_director: '🎨',
  critic: '📝',
};

export default function Logs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getLogs()
      .then(data => setLogs(data.logs || []))
      .catch(() => setLogs([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div>
        <div className="page-header">
          <div><h1 className="page-title">Agent Execution Logs</h1><p className="page-subtitle">Detailed history of agent council runs, LLM usage, and performance</p></div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {[1, 2, 3].map(i => <SkeletonCard key={i} />)}
        </div>
      </div>
    );
  }

  // Group logs by run_id
  const groupedLogs = {};
  logs.forEach(log => {
    if (!groupedLogs[log.run_id]) {
      groupedLogs[log.run_id] = [];
    }
    groupedLogs[log.run_id].push(log);
  });

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Agent Execution Logs</h1>
          <p className="page-subtitle">Detailed history of agent council runs, LLM usage, and performance</p>
        </div>
        <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
          {logs.length} log entries | {Object.keys(groupedLogs).length} runs
        </span>
      </div>

      {logs.length === 0 ? (
        <motion.div
          className="empty-state"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <ScrollText size={48} style={{ opacity: 0.2, marginBottom: 16 }} />
          <p className="empty-state-title">No agent logs yet</p>
          <p style={{ color: 'var(--text-muted)' }}>
            Logs will appear after the agent council runs during a pipeline execution
          </p>
        </motion.div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {Object.entries(groupedLogs).map(([runId, runLogs], i) => {
            const totalTokens = runLogs.reduce((sum, l) => sum + (l.tokens || 0), 0);
            const totalDuration = runLogs.reduce((sum, l) => sum + (l.duration || 0), 0);

            return (
              <motion.div
                key={runId}
                className="glass-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
              >
                {/* Run Header */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '16px',
                  paddingBottom: '12px',
                  borderBottom: '1px solid var(--border-glass)',
                }}>
                  <div>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, fontSize: '15px' }}>
                      Run: {runId}
                    </span>
                    <span style={{ fontSize: '12px', color: 'var(--text-muted)', marginLeft: '12px' }}>
                      <Clock size={11} style={{ marginRight: 3, verticalAlign: 'middle' }} />
                      {runLogs[0]?.created_at && new Date(runLogs[0].created_at).toLocaleString()}
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <div style={{ display: 'flex', gap: '16px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                      <span style={{ fontFamily: 'var(--font-mono)' }}>
                        <Cpu size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />
                        {totalTokens.toLocaleString()} tokens
                      </span>
                      <span style={{ fontFamily: 'var(--font-mono)' }}>
                        <Clock size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />
                        {totalDuration.toFixed(1)}s
                      </span>
                    </div>
                    <button 
                      onClick={() => {
                        if (window.confirm(`Are you sure you want to delete run ${runId}? This will also delete the associated campaign.`)) {
                          api.deletePipelineRun(runId)
                            .then(() => {
                              setLogs(prev => prev.filter(l => l.run_id !== runId));
                            })
                            .catch(err => alert(`Failed to delete: ${err.message}`));
                        }
                      }}
                      className="btn-icon"
                      style={{ 
                        color: 'var(--status-rejected)', 
                        padding: '4px',
                        borderRadius: '6px',
                        background: 'rgba(239, 68, 68, 0.1)',
                        border: 'none',
                        cursor: 'pointer'
                      }}
                      title="Delete Run"
                    >
                      <AlertTriangle size={14} />
                    </button>
                  </div>
                </div>

                {/* Agent Entries */}
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Agent</th>
                      <th>Provider</th>
                      <th>Tokens</th>
                      <th>Duration</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {runLogs.map((log) => {
                      const pColors = PROVIDER_COLORS[log.provider] || { bg: 'var(--bg-glass)', color: 'var(--text-secondary)' };
                      return (
                        <tr key={log.id}>
                          <td style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span>{AGENT_ICONS[log.agent] || '🤖'}</span>
                            <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>
                              {log.agent.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </span>
                          </td>
                          <td>
                            <span className={`provider-tag provider-${log.provider}`}>
                              {log.provider}
                            </span>
                          </td>
                          <td style={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}>
                            {(log.tokens || 0).toLocaleString()}
                          </td>
                          <td style={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}>
                            {(log.duration || 0).toFixed(1)}s
                          </td>
                          <td>
                            {log.error ? (
                              <span className="badge badge-rejected">
                                <AlertTriangle size={10} /> Error
                              </span>
                            ) : (
                              <span className="badge badge-approved">✓ Done</span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
