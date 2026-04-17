import { useState, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Image, Calendar, Play, Loader, Edit3, Video, X, ZoomIn, Download } from 'lucide-react';
import { api } from '../utils/api';
import { SkeletonCard } from '../components/Skeleton';
import PhotopeaEditor from '../components/PhotopeaEditor';

export default function Gallery({ viewMode = 'image' }) {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [editingAsset, setEditingAsset] = useState(null);
  const [previewAsset, setPreviewAsset] = useState(null);

  const loadAssets = useCallback(() => {
    setLoading(true);
    api.getGallery()
      .then(data => {
        const allAssets = data.assets || [];
        if (viewMode === 'image') {
          setAssets(allAssets.filter(a => a.type === 'image'));
        } else {
          setAssets(allAssets.filter(a => a.type === 'video' || a.type === 'draft_video'));
        }
      })
      .catch(() => setAssets([]))
      .finally(() => setLoading(false));
  }, [viewMode]);

  useEffect(() => {
    loadAssets();
  }, [loadAssets]);

  const handleSaveEdit = async (blob) => {
    if (!editingAsset) return;
    try {
      await api.updateAsset(editingAsset.id, blob);
      setEditingAsset(null);
      loadAssets();
    } catch (err) {
      alert("Failed to save changes: " + err.message);
    }
  };

  const pageInfo = useMemo(() => ({
    title: viewMode === 'image' ? 'Image Studio' : 'Video Center',
    subtitle: viewMode === 'image' 
      ? 'Professional layer-based marketing asset studio' 
      : 'Viral motion graphics and video production center',
    emptyTitle: viewMode === 'image' ? 'No designs yet' : 'No videos generated',
    emptyDesc: viewMode === 'image' 
      ? 'Run a pipeline to generate parametric JSX graphics and designs'
      : 'Run a pipeline to generate high-retention Remotion social ads',
    emptyIcon: viewMode === 'image' ? Image : Video
  }), [viewMode]);

  if (loading) {
    return (
      <div>
        <div className="page-header">
          <div><h1 className="page-title">{pageInfo.title}</h1><p className="page-subtitle">{pageInfo.subtitle}</p></div>
        </div>
        <div className="gallery-grid">
          {[1, 2, 3, 4, 5, 6].map(i => <SkeletonCard key={i} className="aspect-[9/16]" />)}
        </div>
      </div>
    );
  }

  const EmptyIcon = pageInfo.emptyIcon;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">{pageInfo.title}</h1>
          <p className="page-subtitle">{pageInfo.subtitle}</p>
        </div>
        <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
          {assets.length} {viewMode === 'image' ? 'designs' : 'videos'}
        </span>
      </div>

      {assets.length === 0 ? (
        <motion.div
          className="empty-state"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <EmptyIcon size={48} style={{ opacity: 0.2, marginBottom: 16 }} />
          <p className="empty-state-title">{pageInfo.emptyTitle}</p>
          <p style={{ color: 'var(--text-muted)' }}>
            {pageInfo.emptyDesc}
          </p>
        </motion.div>
      ) : (
        <div className="gallery-grid">
          {assets.map((asset, i) => (
            <AssetCard 
              key={asset.id} 
              asset={asset} 
              index={i} 
              onComplete={loadAssets}
              onClick={() => {
                if (asset.type === 'image') {
                  setPreviewAsset(asset);
                } else if (asset.type !== 'draft_video') {
                  setSelectedAsset(asset);
                }
              }} 
            />
          ))}
        </div>
      )}

      {/* Image Preview Modal */}
      <AnimatePresence>
        {previewAsset && (
          <ImagePreviewModal
            asset={previewAsset}
            onClose={() => setPreviewAsset(null)}
            onEdit={() => {
              setEditingAsset(previewAsset);
              setPreviewAsset(null);
            }}
          />
        )}
      </AnimatePresence>

      {/* Video Lightbox */}
      {selectedAsset && selectedAsset.type === 'video' && (
        <div
          style={{
            position: 'fixed', inset: 0,
            background: 'rgba(0,0,0,0.85)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            zIndex: 1000, cursor: 'pointer',
          }}
          onClick={() => setSelectedAsset(null)}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            style={{ maxWidth: '80vw', maxHeight: '80vh' }}
            onClick={e => e.stopPropagation()}
          >
            <video src={selectedAsset.file_path} controls autoPlay playsInline
              style={{ width: '400px', maxWidth: '90vw', aspectRatio: '9/16', borderRadius: '12px', boxShadow: 'var(--shadow-lg)', background: '#000' }}
            />
            <div style={{ marginTop: 12, textAlign: 'center', color: 'white' }}>
              <p style={{ fontWeight: 600 }}>{selectedAsset.prompt}</p>
            </div>
          </motion.div>
        </div>
      )}

      {/* Photopea Editor Modal */}
      {editingAsset && (
        <PhotopeaEditor
          title={editingAsset.prompt}
          imageUrl={editingAsset.file_path}
          onClose={() => setEditingAsset(null)}
          onSave={handleSaveEdit}
        />
      )}
    </div>
  );
}


function AssetCard({ asset, index, onClick, onComplete }) {
  const [status, setStatus] = useState(asset.status || 'ready');
  const [progress, setProgress] = useState(null);

  // Poll progress when generating
  useEffect(() => {
    let interval;
    if (status === 'generating_video') {
      interval = setInterval(() => {
        api.getVideoProgress(asset.campaign_id)
          .then(data => {
            setProgress(data);
            if (data.percent >= 100 || data.message === 'Video ready!') {
              clearInterval(interval);
              setTimeout(() => onComplete(), 1500);
            }
          })
          .catch(() => {});
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [status, asset.campaign_id, onComplete]);

  const handleExecute = (e) => {
    e.stopPropagation();
    setStatus('generating_video');
    setProgress({ step: 0, total_steps: 1, message: 'Starting...', percent: 0 });
    api.campaignAction(asset.campaign_id, 'approve')
      .catch(err => {
        alert(`Execution failed: ${err.message}`);
        setStatus('pending');
        setProgress(null);
      });
  };

  // ── Rendered Video Card ──
  if (asset.type === 'video') {
    return (
      <motion.div className="gallery-item" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: index * 0.05 }} onClick={onClick} style={{ cursor: 'pointer' }}>
        <video src={asset.file_path} style={{ width: '100%', aspectRatio: '9/16', background: '#000' }} muted autoPlay loop playsInline />
        <div className="gallery-info">
          <p className="gallery-prompt">{asset.prompt || 'Rendered Video'}</p>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Calendar size={10} /> {asset.created_at ? new Date(asset.created_at).toLocaleDateString() : ''}
            </span>
            <span className="badge badge-approved" style={{ fontSize: '10px' }}>video</span>
          </div>
        </div>
      </motion.div>
    );
  }

  // ── Image Card ──
  if (asset.type === 'image') {
    return (
      <motion.div className="gallery-item" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: index * 0.05 }} onClick={onClick} style={{ cursor: 'pointer' }}>
        <img className="gallery-image" src={asset.file_path.startsWith('/') ? asset.file_path : `/${asset.file_path}`}
          alt={asset.prompt || 'Generated image'} loading="lazy" />
        <div className="gallery-info">
          <p className="gallery-prompt">{asset.prompt || 'No description'}</p>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Calendar size={10} /> {asset.created_at ? new Date(asset.created_at).toLocaleDateString() : ''}
            </span>
            <span className="badge badge-approved" style={{ fontSize: '10px' }}>image</span>
          </div>
        </div>
      </motion.div>
    );
  }

  // ── Draft Video Card (the main one) ──
  if (asset.type === 'draft_video') {
    const scenes = asset.scenes || [];
    return (
      <motion.div className="gallery-item" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: index * 0.05 }} style={{ cursor: 'default' }}>
        
        <div className="gallery-image" style={{
          display: 'flex', flexDirection: 'column', alignItems: 'stretch',
          background: 'var(--matcha-800)', padding: '0',
          position: 'relative', overflow: 'hidden', color: 'white'
        }}>
          {/* Header */}
          <div style={{ padding: '16px 16px 8px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span style={{ fontSize: '20px' }}>🎬</span>
              <span style={{ fontSize: '14px', fontWeight: 600, color: '#ffffff' }}>
                {asset.campaign_title || 'Campaign Video'}
              </span>
            </div>
            {asset.campaign_summary && (
              <p style={{ fontSize: '10px', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>
                {asset.campaign_summary.slice(0, 100)}...
              </p>
            )}
          </div>

          {/* Scenes List */}
          <div style={{ padding: '8px 12px', flex: 1, overflowY: 'auto', maxHeight: '160px' }}>
            {scenes.map((scene, idx) => (
              <div key={idx} style={{
                display: 'flex', gap: '8px', padding: '6px 0',
                borderBottom: idx < scenes.length - 1 ? '1px solid rgba(255,255,255,0.04)' : 'none',
              }}>
                <div style={{
                  width: '20px', height: '20px', borderRadius: '50%',
                  background: 'var(--matcha-300)', color: 'var(--text-primary)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '9px', fontWeight: 'bold', flexShrink: 0,
                }}>
                  {idx + 1}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <p style={{ fontSize: '12px', fontWeight: 600, color: '#ffffff', margin: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    "{scene.text}"
                  </p>
                  <p style={{ fontSize: '9px', color: 'var(--text-muted)', margin: '2px 0 0', fontStyle: 'italic' }}>
                    🎙️ {scene.voiceover?.slice(0, 40) || 'No voiceover'}... · {scene.duration_sec}s
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* Action / Progress Area */}
          <div style={{ padding: '12px 16px', borderTop: '1px solid rgba(255,255,255,0.06)', background: 'var(--matcha-800)' }}>
            {status === 'generating_video' && progress ? (
              <div>
                {/* Step indicator */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span style={{ fontSize: '10px', color: 'var(--accent-primary)', fontWeight: 600 }}>
                    <Loader size={10} style={{ marginRight: 4, verticalAlign: 'middle', animation: 'spin 1s linear infinite' }} />
                    Step {progress.step}/{progress.total_steps}
                  </span>
                  <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                    {progress.percent}%
                  </span>
                </div>
                {/* Progress bar */}
                <div style={{ height: '4px', background: 'rgba(255,255,255,0.2)', borderRadius: '2px', overflow: 'hidden', marginBottom: '6px' }}>
                  <motion.div 
                    animate={{ width: `${progress.percent}%` }}
                    transition={{ duration: 0.5 }}
                    style={{ height: '100%', background: 'var(--matcha-300)', borderRadius: '2px' }} 
                  />
                </div>
                {/* Status message */}
                <p style={{ fontSize: '10px', color: 'var(--text-secondary)', margin: 0 }}>
                  {progress.message}
                </p>
                {progress.detail && (
                  <p style={{ fontSize: '9px', color: 'var(--text-muted)', margin: '2px 0 0', fontStyle: 'italic' }}>
                    {progress.detail.slice(0, 80)}
                  </p>
                )}
              </div>
            ) : (
              <button onClick={handleExecute} style={{
                width: '100%', padding: '10px 16px', fontSize: '14px', fontWeight: 500, fontFamily: 'var(--font-body)',
                background: 'var(--bg-card)', color: 'var(--text-primary)', border: 'none', borderRadius: '8px', cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px',
                transition: 'transform 0.2s, box-shadow 0.2s',
              }}
              onMouseOver={e => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = 'var(--shadow-hard)'; }}
              onMouseOut={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none'; }}
              >
                <Play size={14} /> Execute Remotion Render
              </button>
            )}
          </div>
        </div>

        <div className="gallery-info">
          <p className="gallery-prompt">{asset.preview_text || 'Draft Video'}</p>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Calendar size={10} /> {asset.created_at ? new Date(asset.created_at).toLocaleDateString() : ''}
            </span>
            <span className="badge badge-pending" style={{ fontSize: '10px' }}>
              {scenes.length} scene{scenes.length !== 1 ? 's' : ''}
            </span>
          </div>
        </div>
      </motion.div>
    );
  }

  // ── Fallback (PDF, etc.) ──
  return (
    <motion.div className="gallery-item" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: index * 0.05 }} onClick={onClick} style={{ cursor: 'pointer' }}>
      <div className="gallery-image" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--border-light)', fontSize: '32px' }}>
        📄
      </div>
      <div className="gallery-info">
        <p className="gallery-prompt">{asset.prompt || 'Document'}</p>
      </div>
    </motion.div>
  );
}

/**
 * ImagePreviewModal - Beautiful preview before editing in Photopea
 */
function ImagePreviewModal({ asset, onClose, onEdit }) {
  const imageUrl = asset.file_path?.startsWith('/') 
    ? asset.file_path 
    : `/${asset.file_path}`;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 2000,
        background: 'rgba(0, 0, 0, 0.9)',
        backdropFilter: 'blur(12px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '40px'
      }}
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
        style={{
          maxWidth: '90vw',
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          gap: '24px'
        }}
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '0 8px'
        }}>
          <div>
            <h3 style={{
              color: 'white',
              fontSize: '20px',
              fontWeight: 600,
              margin: 0,
              marginBottom: '4px'
            }}>
              {asset.prompt || 'Marketing Graphic'}
            </h3>
            <p style={{
              color: 'rgba(255,255,255,0.6)',
              fontSize: '13px',
              margin: 0
            }}>
              {asset.created_at ? new Date(asset.created_at).toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              }) : 'Unknown date'}
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'rgba(255,255,255,0.1)',
              border: '1px solid rgba(255,255,255,0.2)',
              color: 'white',
              padding: '8px',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              transition: 'all 0.2s'
            }}
            onMouseOver={e => e.currentTarget.style.background = 'rgba(255,255,255,0.2)'}
            onMouseOut={e => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
          >
            <X size={20} />
          </button>
        </div>

        {/* Image Container */}
        <div style={{
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'rgba(255,255,255,0.02)',
          borderRadius: '16px',
          border: '1px solid rgba(255,255,255,0.1)',
          padding: '24px',
          minHeight: '400px',
          maxHeight: '60vh'
        }}>
          <img
            src={imageUrl}
            alt={asset.prompt || 'Preview'}
            style={{
              maxWidth: '100%',
              maxHeight: '60vh',
              objectFit: 'contain',
              borderRadius: '8px',
              boxShadow: '0 8px 32px rgba(0,0,0,0.4)'
            }}
          />
        </div>

        {/* Action Buttons */}
        <div style={{
          display: 'flex',
          gap: '12px',
          justifyContent: 'center',
          padding: '0 8px'
        }}>
          <button
            onClick={() => {
              const link = document.createElement('a');
              link.href = imageUrl;
              link.download = asset.prompt || 'design.png';
              link.click();
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 24px',
              borderRadius: '10px',
              background: 'rgba(255,255,255,0.1)',
              border: '1px solid rgba(255,255,255,0.2)',
              color: 'white',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseOver={e => {
              e.currentTarget.style.background = 'rgba(255,255,255,0.2)';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseOut={e => {
              e.currentTarget.style.background = 'rgba(255,255,255,0.1)';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <Download size={16} />
            Download
          </button>
          
          <button
            onClick={onEdit}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 32px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)',
              border: 'none',
              color: 'white',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
              boxShadow: '0 4px 16px rgba(59,130,246,0.4)'
            }}
            onMouseOver={e => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 6px 20px rgba(59,130,246,0.5)';
            }}
            onMouseOut={e => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 16px rgba(59,130,246,0.4)';
            }}
          >
            <Edit3 size={16} />
            Edit in Photopea
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}
