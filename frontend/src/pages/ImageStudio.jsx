import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, Filter, Sparkles, Image, X, Loader2 } from 'lucide-react';
import { api } from '../utils/api';
import TemplateCard from '../components/TemplateCard';
import PhotopeaEditor from '../components/PhotopeaEditor';

const CATEGORIES = [
  { id: 'all', label: 'All Templates', icon: '📦' },
  { id: 'twitter', label: 'Twitter Posts', icon: '🐦' },
  { id: 'instagram', label: 'Instagram Posts', icon: '📷' },
  { id: 'story', label: 'Instagram Stories', icon: '📱' },
  { id: 'linkedin', label: 'LinkedIn Posts', icon: '💼' },
  { id: 'youtube', label: 'YouTube Thumbnails', icon: '🎥' },
  { id: 'product', label: 'Product Showcases', icon: '🛍️' },
];

export default function ImageStudio() {
  const navigate = useNavigate();
  const [templates, setTemplates] = useState([]);
  const [backgrounds, setBackgrounds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [showBackgrounds, setShowBackgrounds] = useState(false);
  const [profile, setProfile] = useState(null);

  // Load templates and backgrounds
  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [templatesRes, backgroundsRes, profileRes] = await Promise.all([
        api.getTemplates({ type: 'image', limit: 200 }),
        api.getBackgrounds(),
        api.getProfile()
      ]);
      setTemplates(templatesRes);
      setBackgrounds(backgroundsRes);
      setProfile(profileRes);
    } catch (err) {
      console.error('Failed to load studio data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Filter templates
  const filteredTemplates = templates.filter(template => {
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
    const matchesSearch = !searchQuery || 
      template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.tags?.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  // Handle template edit
  const handleEditTemplate = async (template) => {
    // Increment usage count
    try {
      await api.useTemplate(template.id);
    } catch (err) {
      console.error('Failed to increment usage:', err);
    }
    
    setEditingTemplate(template);
  };

  // Handle template use
  const handleUseTemplate = (template) => {
    handleEditTemplate(template);
  };

  // Handle Photopea save
  const handleSaveEdit = async (blob) => {
    if (!editingTemplate) return;
    try {
      await api.uploadAsset(blob);
      setEditingTemplate(null);
      loadData();
    } catch (err) {
      alert('Failed to save changes: ' + err.message);
    }
  };

  // Generate AI design
  const handleGenerateDesign = () => {
    navigate('/campaigns');
  };

  if (loading) {
    return (
      <div>
        <div className="page-header">
          <h1 className="page-title">Image Studio</h1>
          <p className="page-subtitle">Loading templates...</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '400px' }}>
          <Loader2 size={40} className="animate-spin" style={{ color: 'var(--accent-primary)' }} />
        </div>
      </div>
    );
  }

  return (
    <div style={{ height: 'calc(100vh - 80px)', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div className="page-header" style={{ padding: '20px 32px', borderBottom: '1px solid var(--border-glass)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
          <div>
            <h1 className="page-title" style={{ marginBottom: '4px' }}>🎨 Image Studio</h1>
            <p className="page-subtitle">Professional marketing design templates</p>
          </div>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <button
              onClick={() => setShowBackgrounds(!showBackgrounds)}
              style={{
                padding: '10px 20px',
                borderRadius: '8px',
                background: showBackgrounds ? 'var(--accent-primary)' : 'var(--bg-secondary)',
                color: showBackgrounds ? 'white' : 'var(--text-primary)',
                border: '1px solid var(--border-glass)',
                fontSize: '13px',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <Image size={16} />
              Backgrounds ({backgrounds.length})
            </button>
            <button
              onClick={handleGenerateDesign}
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
              <Sparkles size={16} />
              AI Generate
            </button>
          </div>
        </div>

        {/* Search & Filter Bar */}
        <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Search templates by name or tags..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 12px 10px 40px',
                borderRadius: '8px',
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-glass)',
                color: 'var(--text-primary)',
                fontSize: '13px'
              }}
            />
          </div>
          <button
            style={{
              padding: '10px 20px',
              borderRadius: '8px',
              background: 'var(--bg-secondary)',
              color: 'var(--text-primary)',
              border: '1px solid var(--border-glass)',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <Filter size={16} />
            Filter
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* Sidebar */}
        <div style={{
          width: showBackgrounds ? '320px' : '240px',
          borderRight: '1px solid var(--border-glass)',
          background: 'var(--bg-secondary)',
          overflowY: 'auto',
          padding: '20px'
        }}>
          {/* Categories */}
          <div style={{ marginBottom: '24px' }}>
            <h3 style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '12px', letterSpacing: '0.05em' }}>
              Categories
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {CATEGORIES.map(cat => (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id)}
                  style={{
                    padding: '10px 12px',
                    borderRadius: '8px',
                    background: selectedCategory === cat.id ? 'var(--accent-primary)' : 'transparent',
                    color: selectedCategory === cat.id ? 'white' : 'var(--text-primary)',
                    border: 'none',
                    fontSize: '13px',
                    fontWeight: 500,
                    cursor: 'pointer',
                    textAlign: 'left',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    transition: 'all 0.2s'
                  }}
                  onMouseOver={(e) => {
                    if (selectedCategory !== cat.id) {
                      e.currentTarget.style.background = 'var(--bg-tertiary)';
                    }
                  }}
                  onMouseOut={(e) => {
                    if (selectedCategory !== cat.id) {
                      e.currentTarget.style.background = 'transparent';
                    }
                  }}
                >
                  <span>{cat.icon}</span>
                  <span>{cat.label}</span>
                  <span style={{ marginLeft: 'auto', fontSize: '11px', opacity: 0.6 }}>
                    {cat.id === 'all' ? templates.length : templates.filter(t => t.category === cat.id).length}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Brand Kit (if profile loaded) */}
          {profile && (
            <div style={{ marginBottom: '24px' }}>
              <h3 style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '12px', letterSpacing: '0.05em' }}>
                Brand Kit
              </h3>
              <div style={{ padding: '12px', borderRadius: '8px', background: 'var(--bg-tertiary)' }}>
                <div style={{ fontSize: '13px', fontWeight: 600, marginBottom: '8px' }}>{profile.company_name || 'Your Company'}</div>
                {profile.brand_primary_color && (
                  <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
                    <div style={{ width: '24px', height: '24px', borderRadius: '4px', background: profile.brand_primary_color, border: '1px solid var(--border-glass)' }} />
                    <div style={{ width: '24px', height: '24px', borderRadius: '4px', background: profile.brand_secondary_color, border: '1px solid var(--border-glass)' }} />
                  </div>
                )}
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  {profile.product_images?.length || 0} products • {profile.logo_url ? 'Logo ✓' : 'No logo'}
                </div>
              </div>
            </div>
          )}

          {/* Backgrounds Panel */}
          {showBackgrounds && (
            <div>
              <h3 style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '12px', letterSpacing: '0.05em' }}>
                Background Library
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                {backgrounds.slice(0, 20).map((bg, idx) => (
                  <div
                    key={idx}
                    style={{
                      aspectRatio: '1/1',
                      borderRadius: '6px',
                      overflow: 'hidden',
                      border: '1px solid var(--border-glass)',
                      cursor: 'pointer'
                    }}
                  >
                    <img 
                      src={bg.path} 
                      alt={bg.filename}
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  </div>
                ))}
              </div>
              {backgrounds.length > 20 && (
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', textAlign: 'center', marginTop: '8px' }}>
                  +{backgrounds.length - 20} more backgrounds
                </div>
              )}
            </div>
          )}
        </div>

        {/* Template Gallery */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
          {filteredTemplates.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '60px 20px' }}>
              <Search size={48} style={{ opacity: 0.2, marginBottom: '16px' }} />
              <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>No templates found</h3>
              <p style={{ color: 'var(--text-muted)' }}>Try adjusting your search or filter criteria</p>
            </div>
          ) : (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
              gap: '20px'
            }}>
              {filteredTemplates.map((template, idx) => (
                <TemplateCard
                  key={template.id}
                  template={template}
                  onEdit={handleEditTemplate}
                  onUse={handleUseTemplate}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Photopea Editor Modal */}
      {editingTemplate && (
        <PhotopeaEditor
          imageUrl={editingTemplate.preview_url || '/outputs/backgrounds/bg_corporate_business_blue_v1.png'}
          onSave={handleSaveEdit}
          onClose={() => setEditingTemplate(null)}
          title={editingTemplate.name}
        />
      )}
    </div>
  );
}
