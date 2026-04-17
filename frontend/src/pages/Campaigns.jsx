import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FileText, Star, Clock, CheckCircle, XCircle, Filter } from 'lucide-react';
import { api } from '../utils/api';
import { SkeletonCard } from '../components/Skeleton';

export default function Campaigns() {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
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
        <div style={{ display: 'flex', gap: '8px' }}>
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
    </div>
  );
}
