import { motion } from 'framer-motion';
import { Edit3, Play, Image, Video } from 'lucide-react';

/**
 * TemplateCard Component
 * Reusable card for displaying image/video templates in the studio.
 */
export default function TemplateCard({ template, onEdit, onUse }) {
  const isVideo = template.type === 'video';
  const dimensions = template.dimensions;
  const dimLabel = dimensions ? `${dimensions.width}×${dimensions.height}` : '';

  return (
    <motion.div
      className="template-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4, scale: 1.02 }}
      style={{
        position: 'relative',
        borderRadius: '12px',
        overflow: 'hidden',
        background: 'var(--bg-secondary)',
        border: '1px solid var(--border-glass)',
        cursor: 'pointer',
        transition: 'all 0.2s'
      }}
    >
      {/* Preview Image/Placeholder */}
      <div style={{
        aspectRatio: dimensions ? `${dimensions.width}/${dimensions.height}` : '1/1',
        background: 'linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-primary) 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative'
      }}>
        {template.preview_url ? (
          <img 
            src={template.preview_url} 
            alt={template.name}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover'
            }}
          />
        ) : (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            {isVideo ? (
              <Play size={48} style={{ opacity: 0.3, marginBottom: '8px' }} />
            ) : (
              <Image size={48} style={{ opacity: 0.3, marginBottom: '8px' }} />
            )}
            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              {template.category}
            </div>
          </div>
        )}

        {/* Type Badge */}
        <div style={{
          position: 'absolute',
          top: '8px',
          left: '8px',
          padding: '4px 8px',
          borderRadius: '6px',
          background: isVideo ? 'rgba(139, 92, 246, 0.9)' : 'rgba(59, 130, 246, 0.9)',
          color: 'white',
          fontSize: '10px',
          fontWeight: 600,
          textTransform: 'uppercase',
          backdropFilter: 'blur(8px)'
        }}>
          {isVideo ? <Video size={12} style={{ marginRight: '4px' }} /> : <Image size={12} style={{ marginRight: '4px' }} />}
          {isVideo ? 'Video' : 'Image'}
        </div>

        {/* Dimensions Badge */}
        {dimLabel && (
          <div style={{
            position: 'absolute',
            top: '8px',
            right: '8px',
            padding: '4px 8px',
            borderRadius: '6px',
            background: 'rgba(0, 0, 0, 0.7)',
            color: 'white',
            fontSize: '10px',
            fontWeight: 600,
            backdropFilter: 'blur(8px)'
          }}>
            {dimLabel}
          </div>
        )}

        {/* Hover Actions */}
        <div style={{
          position: 'absolute',
          inset: 0,
          background: 'rgba(0, 0, 0, 0.6)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '12px',
          opacity: 0,
          transition: 'opacity 0.2s',
          backdropFilter: 'blur(4px)'
        }}
          onMouseEnter={(e) => e.currentTarget.style.opacity = '1'}
          onMouseLeave={(e) => e.currentTarget.style.opacity = '0'}
        >
          {onEdit && (
            <button
              onClick={(e) => { e.stopPropagation(); onEdit(template); }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '10px 20px',
                borderRadius: '8px',
                background: 'var(--accent-primary)',
                color: 'white',
                border: 'none',
                fontSize: '13px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
              onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
            >
              <Edit3 size={16} />
              Edit
            </button>
          )}
          {onUse && (
            <button
              onClick={(e) => { e.stopPropagation(); onUse(template); }}
              style={{
                padding: '10px 20px',
                borderRadius: '8px',
                background: 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                fontSize: '13px',
                fontWeight: 600,
                cursor: 'pointer',
                backdropFilter: 'blur(8px)',
                transition: 'all 0.2s'
              }}
              onMouseOver={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)'}
              onMouseOut={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)'}
            >
              Use Template
            </button>
          )}
        </div>
      </div>

      {/* Card Footer */}
      <div style={{ padding: '12px' }}>
        <h3 style={{
          fontSize: '14px',
          fontWeight: 600,
          color: 'var(--text-primary)',
          marginBottom: '6px',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap'
        }}>
          {template.name}
        </h3>
        
        {/* Tags */}
        {template.tags && template.tags.length > 0 && (
          <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', marginBottom: '8px' }}>
            {template.tags.slice(0, 3).map((tag, idx) => (
              <span key={idx} style={{
                padding: '2px 8px',
                borderRadius: '4px',
                background: 'var(--bg-tertiary)',
                color: 'var(--text-muted)',
                fontSize: '10px',
                fontWeight: 500
              }}>
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Usage Count */}
        <div style={{
          fontSize: '11px',
          color: 'var(--text-muted)',
          display: 'flex',
          alignItems: 'center',
          gap: '4px'
        }}>
          <span>🔥</span>
          <span>{template.usage_count || 0} uses</span>
        </div>
      </div>
    </motion.div>
  );
}
