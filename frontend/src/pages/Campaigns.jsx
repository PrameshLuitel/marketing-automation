import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, Star, Clock, CheckCircle, XCircle, Filter, Plus } from 'lucide-react';
import { api } from '../utils/api';
import { SkeletonCard } from '../components/Skeleton';
import PipelineConfigurator from '../components/PipelineConfigurator';

export default function Campaigns() {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [showConfigurator, setShowConfigurator] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const statusParam = filter === 'all' ? null : filter;
    api.getCampaigns(statusParam)
      .then(data => setCampaigns(data.campaigns || []))
      .catch(() => setCampaigns([]))
      .finally(() => setLoading(false));
  }, [filter]);

  const handleAction = async (e, id, action) => {
    e.stopPropagation();
    try {
      await api.campaignAction(id, action);
      setCampaigns(prev =>
        prev.map(c => c.id === id ? { ...c, status: action === 'approve' ? 'approved' : 'rejected' } : c)
      );
    } catch (err) {
      console.error('Action failed:', err);
    }
  };

  const handleConfigComplete = async (config) => {
    try {
      // Trigger pipeline with selected template
      await api.triggerPipeline({
        video_template_id: config.templateId,
        video_duration_seconds: config.duration || 15
      });
      setShowConfigurator(false);
      navigate('/'); // Go to dashboard to see progress
    } catch (err) {
      alert('Failed to start pipeline: ' + err.message);
    }
  };

  const getQualityClass = (score) => {
    if (score >= 7) return 'high';
    if (score >= 4) return 'medium';
    return 'low';
  };

  if (loading) {
    return (
      <div>
        <div className="page-header">
          <div><h1 className="page-title">Campaign Briefs</h1><p className="page-subtitle">Review, approve, or reject AI-generated campaign briefs</p></div>
        </div>
        <div className="campaign-list">
          {[1, 2, 3, 4].map(i => <SkeletonCard key={i} />)}
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Campaign Briefs</h1>
          <p className="page-subtitle">Review, approve, or reject AI-generated campaign briefs</p>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <button
            onClick={() => setShowConfigurator(true)}
            style={{
              padding: '10px 20px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)'
            }}
          >
            <Plus size={16} />
            New Campaign
          </button>
          {['all', 'pending', 'approved', 'rejected'].map(f => (
            <button
              key={f}
              className={`btn btn-sm ${filter === f ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setFilter(f)}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {campaigns.length === 0 ? (
        <motion.div
          className="empty-state"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <FileText size={48} style={{ opacity: 0.2, marginBottom: 16 }} />
          <p className="empty-state-title">No campaigns yet</p>
          <p style={{ color: 'var(--text-muted)' }}>
            Run the pipeline to generate your first campaign brief
          </p>
        </motion.div>
      ) : (
        <div className="campaign-list">
          {campaigns.map((campaign, i) => (
            <motion.div
              key={campaign.id}
              className="campaign-card"
              onClick={() => navigate(`/campaigns/${campaign.id}`)}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
            >
              <div className="campaign-header">
                <div>
                  <div className="campaign-title">{campaign.title}</div>
                  <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '6px', lineHeight: '1.5' }}>
                    {campaign.summary || 'No summary available'}
                  </p>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexShrink: 0 }}>
                  {campaign.quality_score && (
                    <div className={`quality-score ${getQualityClass(campaign.quality_score)}`}>
                      <Star size={14} />
                      {campaign.quality_score.toFixed(1)}
                    </div>
                  )}
                  <span className={`badge badge-${campaign.status}`}>
                    {campaign.status}
                  </span>
                </div>
              </div>

              <div className="campaign-meta">
                <span>
                  <Clock size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />
                  {campaign.created_at ? new Date(campaign.created_at).toLocaleDateString('en-US', {
                    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                  }) : 'Unknown'}
                </span>
                {campaign.has_pdf && (
                  <span style={{ color: 'var(--accent-secondary)' }}>📄 PDF available</span>
                )}

                {campaign.status === 'pending' && (
                  <div style={{ marginLeft: 'auto', display: 'flex', gap: '8px' }}>
                    <button
                      className="btn btn-success btn-sm"
                      onClick={(e) => handleAction(e, campaign.id, 'approve')}
                    >
                      <CheckCircle size={12} /> Approve
                    </button>
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={(e) => handleAction(e, campaign.id, 'reject')}
                    >
                      <XCircle size={12} /> Reject
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Pipeline Configurator Modal */}
      <AnimatePresence>
        {showConfigurator && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(0, 0, 0, 0.8)',
              zIndex: 2000,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '40px',
              backdropFilter: 'blur(8px)'
            }}
            onClick={() => setShowConfigurator(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              style={{
                background: 'var(--bg-primary)',
                borderRadius: '16px',
                maxWidth: '1200px',
                width: '100%',
                maxHeight: '90vh',
                overflow: 'auto',
                padding: '40px',
                border: '1px solid var(--border-glass)',
                boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
                <h2 style={{ fontSize: '28px', fontWeight: 'bold', margin: 0 }}>Create New Campaign</h2>
                <button
                  onClick={() => setShowConfigurator(false)}
                  style={{
                    padding: '8px 16px',
                    borderRadius: '8px',
                    background: 'var(--bg-secondary)',
                    color: 'var(--text-primary)',
                    border: '1px solid var(--border-glass)',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: 600
                  }}
                >
                  ✕ Cancel
                </button>
              </div>
              <PipelineConfigurator onConfigComplete={handleConfigComplete} />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
