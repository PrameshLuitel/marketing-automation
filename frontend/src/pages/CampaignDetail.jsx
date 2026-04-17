import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowLeft, Star, CheckCircle, XCircle, Download,
  FileText, Image, Clock, Database, MessageSquare, Presentation
} from 'lucide-react';
import { api } from '../utils/api';
import SlideViewer from '../components/SlideViewer';

export default function CampaignDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [campaign, setCampaign] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('brief');

  useEffect(() => {
    api.getCampaign(id)
      .then(setCampaign)
      .catch(() => setCampaign(null))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    let intervalId;
    if (campaign?.status === 'generating_video') {
      intervalId = setInterval(() => {
        api.getCampaign(id).then(setCampaign);
      }, 3000);
    }
    return () => clearInterval(intervalId);
  }, [campaign?.status, id]);

  const handleAction = async (action) => {
    try {
      await api.campaignAction(id, action);
      setCampaign(prev => ({
        ...prev,
        status: action === 'approve' ? 'generating_video' : 'rejected',
      }));
    } catch (err) {
      console.error('Action failed:', err);
    }
  };

  if (loading) {
    return <div className="loading-container"><div className="loading-spinner" /></div>;
  }

  if (!campaign) {
    return (
      <div className="empty-state">
        <p className="empty-state-title">Campaign not found</p>
        <button className="btn btn-ghost" onClick={() => navigate('/campaigns')}>
          <ArrowLeft size={14} /> Back to Campaigns
        </button>
      </div>
    );
  }

  const getQualityClass = (score) => {
    if (score >= 7) return 'high';
    if (score >= 4) return 'medium';
    return 'low';
  };

  const tabs = [
    { key: 'brief', label: 'Full Brief', icon: FileText },
    { key: 'strategy', label: 'Strategy', icon: FileText },
    { key: 'copy', label: 'Social Copy', icon: FileText },
    { key: 'creative', label: 'Creative', icon: Image },
    { key: 'review', label: 'Critic Review', icon: Star },
    { key: 'slides', label: 'Presentation', icon: Presentation },
    { key: 'raw', label: 'Raw Data', icon: Database },
    { key: 'debate', label: 'Agent Debates', icon: MessageSquare },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'brief':
        return (
          <div className="markdown-body" style={{ whiteSpace: 'pre-wrap' }}>
            {campaign.brief_markdown || 'No brief content available.'}
          </div>
        );
      case 'strategy':
        return (
          <div className="markdown-body" style={{ whiteSpace: 'pre-wrap' }}>
            {campaign.strategy || 'No strategy available.'}
          </div>
        );
      case 'copy':
        return (
          <div className="markdown-body" style={{ whiteSpace: 'pre-wrap' }}>
            {campaign.social_copy ? (
              typeof campaign.social_copy === 'string'
                ? JSON.parse(campaign.social_copy)?.raw || campaign.social_copy
                : campaign.social_copy
            ) : 'No copy available.'}
          </div>
        );
      case 'creative':
        return (
          <div>
            <div className="markdown-body" style={{ whiteSpace: 'pre-wrap', marginBottom: '24px' }}>
              {campaign.visual_direction || 'No creative direction available.'}
            </div>
            {campaign.assets && campaign.assets.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
                {/* Videos Section */}
                {campaign.assets.some(a => a.type === 'video') && (
                  <div>
                    <h3 style={{ marginBottom: '16px', fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Play size={16} /> Social Media Videos
                    </h3>
                    <div className="gallery-grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))' }}>
                      {campaign.assets.filter(a => a.type === 'video').map(asset => (
                        <div key={asset.id} className="gallery-item">
                          <video 
                              src={asset.file_path} 
                              controls
                              playsInline
                              style={{ width: '100%', aspectRatio: '9/16', border: 'none', borderRadius: '12px', background: '#000' }} 
                          />
                          <div className="gallery-info">
                            <p className="gallery-prompt">{asset.prompt}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Graphics Section */}
                {campaign.assets.some(a => a.type === 'image') && (
                  <div>
                    <h3 style={{ marginBottom: '16px', fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Image size={16} /> High-Fidelity Graphics
                    </h3>
                    <div className="gallery-grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))' }}>
                      {campaign.assets.filter(a => a.type === 'image').map(asset => (
                        <div key={asset.id} className="gallery-item">
                           <img
                            className="gallery-image"
                            src={asset.file_path.startsWith('/') ? asset.file_path : `/${asset.file_path}`}
                            alt={asset.prompt || 'Generated image'}
                            onError={(e) => { e.target.style.display = 'none'; }}
                          />
                          <div className="gallery-info">
                            <p className="gallery-prompt">{asset.prompt}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
            
            {campaign.status === 'generating_video' && (
              <div style={{ marginTop: '24px', padding: '32px', background: 'var(--bg-secondary)', borderRadius: '12px', textAlign: 'center', border: '1px solid var(--border-glass)' }}>
                <div className="loading-spinner" style={{ margin: '0 auto 16px auto', width: '32px', height: '32px' }}></div>
                <h3 style={{ color: 'var(--accent-primary)', marginBottom: '8px' }}>Generating Video with Remotion...</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>Your video is rendering behind the scenes. This may take a minute or two.</p>
              </div>
            )}

            {/* Video Script Section */}
            {campaign.video_script && (
              <div style={{ marginTop: '32px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                  <Clock size={16} style={{ color: 'var(--accent-primary)' }} />
                  <h3 style={{ fontSize: '16px', margin: 0 }}>Video Production Script</h3>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {(() => {
                    try {
                      const parsed = JSON.parse(campaign.video_script);
                      const scenes = Array.isArray(parsed) ? parsed : (parsed.scenes || parsed.video_scenes || []);
                      return scenes;
                    } catch(e) {
                      return [];
                    }
                  })().map((scene, idx) => (
                    <div key={idx} style={{ 
                      background: 'rgba(0,0,0,0.1)', 
                      padding: '16px', 
                      borderRadius: '10px', 
                      border: '1px solid var(--border-glass)',
                      display: 'flex',
                      gap: '16px'
                    }}>
                      <div style={{ 
                        width: '32px', 
                        height: '32px', 
                        borderRadius: '50%', 
                        background: 'var(--slushie-500)', 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'center',
                        fontSize: '12px',
                        fontWeight: 'bold',
                        flexShrink: 0
                      }}>
                        {idx + 1}
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px', fontSize: '14px' }}>
                          "{scene.text}"
                        </div>
                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)', fontStyle: 'italic', marginBottom: '8px' }}>
                          Voiceover: {scene.voiceover_prompt}
                        </div>
                        <div style={{ display: 'flex', gap: '12px' }}>
                          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>⏱️ {scene.durationInFrames / 30}s</span>
                          {scene.sfx_prompt && <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>🎵 {scene.sfx_prompt}</span>}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        );
      case 'review':
        return (
          <div className="markdown-body" style={{ whiteSpace: 'pre-wrap' }}>
            {campaign.critic_feedback || 'No critic review available.'}
          </div>
        );
      case 'slides':
        let parsedSlides = [];
        let templateId = 'clay_minimal_1';
        try {
          if (campaign.slides_json) {
            const raw = JSON.parse(campaign.slides_json);
            if (raw && !Array.isArray(raw) && raw.slides) {
              parsedSlides = raw.slides;
              templateId = raw.template_id || 'clay_minimal_1';
            } else {
              parsedSlides = Array.isArray(raw) ? raw : [];
            }
          }
        } catch (e) {
          console.error("Failed to parse slides JSON", e);
        }
        return (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '24px 0' }}>
            <SlideViewer slides={parsedSlides} templateId={templateId} />
          </div>
        );
      case 'raw':
        try {
          const rawParsed = campaign.raw_scraped_data ? JSON.parse(campaign.raw_scraped_data) : null;
          return (
            <div className="markdown-body" style={{ overflowX: 'auto', background: 'var(--bg-secondary)', padding: '16px', borderRadius: '8px' }}>
              <pre style={{ margin: 0, fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-secondary)' }}>
                {rawParsed ? JSON.stringify(rawParsed, null, 2) : 'No raw data available.'}
              </pre>
            </div>
          );
        } catch (e) {
          return <div className="markdown-body" style={{ whiteSpace: 'pre-wrap' }}>{campaign.raw_scraped_data || 'No raw data.'}</div>;
        }
      case 'debate':
        try {
          const debatesParsed = campaign.debate_logs ? JSON.parse(campaign.debate_logs) : null;
          return (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              {debatesParsed ? Object.entries(debatesParsed).map(([agent, text]) => {
                // Parse verdict vs raw debate from the text
                let verdict = '';
                let rawDebate = typeof text === 'string' ? text : '';
                if (typeof text === 'string' && text.includes('DEBATE VERDICT')) {
                  const parts = text.split('---');
                  verdict = parts[0] || '';
                  rawDebate = parts.slice(1).join('---') || text;
                }

                return (
                  <div key={agent} style={{ background: 'var(--bg-secondary)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border-glass)' }}>
                    <h3 style={{ marginTop: 0, marginBottom: '12px', color: 'var(--matcha-800)', textTransform: 'capitalize', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--matcha-300)', display: 'inline-block' }} />
                      {agent.replaceAll('_', ' ')} Debate
                    </h3>

                    {/* Verdict Banner */}
                    {verdict && (
                      <div style={{
                        background: 'var(--border-light)',
                        border: '1px dashed var(--border-primary)',
                        borderRadius: '12px',
                        padding: '14px 18px',
                        marginBottom: '16px',
                      }}>
                        <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '1.08px', marginBottom: '8px' }}>
                          ⚖️ Final Verdict
                        </div>
                        <div className="markdown-body" style={{ whiteSpace: 'pre-wrap', fontSize: '14px', color: 'var(--text-primary)', lineHeight: 1.6 }}>
                          {verdict.replace(/#+\s*DEBATE VERDICT\s*/gi, '').trim()}
                        </div>
                      </div>
                    )}

                    {/* Raw Debate Opinions */}
                    <details style={{ cursor: 'pointer' }}>
                      <summary style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '8px', userSelect: 'none' }}>
                        View Raw Debate Opinions
                      </summary>
                      <div className="markdown-body" style={{ whiteSpace: 'pre-wrap', fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-secondary)', marginTop: '8px', padding: '12px', background: 'var(--bg-primary)', borderRadius: '8px' }}>
                        {rawDebate || 'No raw opinions available.'}
                      </div>
                    </details>
                  </div>
                );
              }) : 'No debates recorded.'}
            </div>
          );
        } catch (e) {
          return <div className="markdown-body" style={{ whiteSpace: 'pre-wrap' }}>{campaign.debate_logs || 'No debate logs.'}</div>;
        }
      default:
        return null;
    }
  };

  return (
    <div>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <button
          className="btn btn-ghost btn-sm"
          onClick={() => navigate('/campaigns')}
          style={{ marginBottom: '16px' }}
        >
          <ArrowLeft size={14} /> Back to Campaigns
        </button>

        <div className="page-header">
          <div>
            <h1 className="page-title">{campaign.title}</h1>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginTop: '8px' }}>
              <span className={`badge badge-${campaign.status}`}>
                  {campaign.status === 'generating_video' ? 'Generating Video...' : campaign.status}
              </span>
              {campaign.quality_score && (
                <span className={`quality-score ${getQualityClass(campaign.quality_score)}`}>
                  <Star size={14} /> {campaign.quality_score.toFixed(1)}/10
                </span>
              )}
              <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                <Clock size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />
                {campaign.created_at && new Date(campaign.created_at).toLocaleString()}
              </span>
            </div>
          </div>

          {campaign.status === 'pending' && (
            <div style={{ display: 'flex', gap: '8px' }}>
              <button className="btn btn-success" onClick={() => handleAction('approve')}>
                <CheckCircle size={14} /> Approve
              </button>
              <button className="btn btn-danger" onClick={() => handleAction('reject')}>
                <XCircle size={14} /> Reject
              </button>
            </div>
          )}
        </div>
      </motion.div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '4px', marginBottom: '24px', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0' }}>
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            style={{
              padding: '10px 20px',
              background: activeTab === tab.key ? 'rgba(108, 99, 255, 0.12)' : 'transparent',
              border: 'none',
              borderBottom: activeTab === tab.key ? '2px solid var(--accent-primary)' : '2px solid transparent',
              color: activeTab === tab.key ? 'var(--accent-primary)' : 'var(--text-secondary)',
              cursor: 'pointer',
              fontFamily: 'var(--font-body)',
              fontSize: '13px',
              fontWeight: activeTab === tab.key ? 600 : 400,
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              transition: 'var(--transition-base)',
              borderRadius: '8px 8px 0 0',
            }}
          >
            <tab.icon size={14} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <motion.div
        className="glass-card"
        key={activeTab}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
      >
        {renderTabContent()}
      </motion.div>
    </div>
  );
}
