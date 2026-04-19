import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Video, Play, Clock, Layers, Settings, Loader2 } from 'lucide-react';
import { api } from '../utils/api';
import TemplateCard from '../components/TemplateCard';

const VIDEO_CATEGORIES = [
  { id: 'all', label: 'All Videos', icon: '🎬' },
  { id: 'motion', label: 'Motion Graphics', icon: '✨' },
  { id: 'typography', label: 'Typography', icon: '🔤' },
  { id: 'product', label: 'Product Showcase', icon: '🛍️' },
  { id: 'ads', label: 'Social Ads', icon: '📱' },
  { id: 'branding', label: 'Branding', icon: '🎨' },
];

const ASPECT_RATIOS = [
  { id: '9:16', label: '9:16 Vertical', width: 1080, height: 1920 },
  { id: '16:9', label: '16:9 Horizontal', width: 1920, height: 1080 },
  { id: '1:1', label: '1:1 Square', width: 1080, height: 1080 },
];

const DURATIONS = [
  { id: 15, label: '15 seconds' },
  { id: 30, label: '30 seconds' },
  { id: 60, label: '60 seconds' },
];

export default function VideoStudio() {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedDuration, setSelectedDuration] = useState(15);
  const [selectedAspect, setSelectedAspect] = useState('9:16');
  const [showConfig, setShowConfig] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  // Load video templates
  const loadTemplates = useCallback(async () => {
    setLoading(true);
    try {
      const templatesRes = await api.getTemplates({ type: 'video', limit: 100 });
      setTemplates(templatesRes);
    } catch (err) {
      console.error('Failed to load video templates:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTemplates();
  }, [loadTemplates]);

  // Filter templates
  const filteredTemplates = templates.filter(template => {
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
    const matchesSearch = !searchQuery || 
      template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.tags?.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  // Handle template selection
  const handleSelectTemplate = async (template) => {
    setSelectedTemplate(template);
    setShowConfig(true);
    
    try {
      await api.useTemplate(template.id);
    } catch (err) {
      console.error('Failed to increment usage:', err);
    }
  };

  // Handle render video
  const handleRenderVideo = () => {
    if (!selectedTemplate) return;
    
    // Navigate to campaigns to trigger pipeline with this template
    alert(`Video rendering will be triggered for: ${selectedTemplate.name}\nDuration: ${selectedDuration}s\nAspect Ratio: ${selectedAspect}`);
    setShowConfig(false);
  };

  if (loading) {
    return (
      <div>
        <div className="page-header">
          <h1 className="page-title">Video Studio</h1>
          <p className="page-subtitle">Loading video templates...</p>
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
            <h1 className="page-title" style={{ marginBottom: '4px' }}>🎥 Video Studio</h1>
            <p className="page-subtitle">Professional motion graphics & video templates</p>
          </div>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
              {filteredTemplates.length} templates
            </span>
          </div>
        </div>

        {/* Search Bar */}
        <div style={{ marginTop: '16px' }}>
          <input
            type="text"
            placeholder="Search video templates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '10px 12px',
              borderRadius: '8px',
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-glass)',
              color: 'var(--text-primary)',
              fontSize: '13px'
            }}
          />
        </div>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* Sidebar */}
        <div style={{
          width: '240px',
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
              {VIDEO_CATEGORIES.map(cat => (
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
                >
                  <span>{cat.icon}</span>
                  <span>{cat.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Configuration Panel */}
          {selectedTemplate && (
            <div>
              <h3 style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '12px', letterSpacing: '0.05em' }}>
                Configuration
              </h3>
              
              {/* Duration Selector */}
              <div style={{ marginBottom: '16px' }}>
                <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                  <Clock size={12} />
                  Duration
                </label>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {DURATIONS.map(dur => (
                    <button
                      key={dur.id}
                      onClick={() => setSelectedDuration(dur.id)}
                      style={{
                        padding: '8px 12px',
                        borderRadius: '6px',
                        background: selectedDuration === dur.id ? 'var(--accent-primary)' : 'var(--bg-tertiary)',
                        color: selectedDuration === dur.id ? 'white' : 'var(--text-primary)',
                        border: 'none',
                        fontSize: '12px',
                        cursor: 'pointer',
                        textAlign: 'left'
                      }}
                    >
                      {dur.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Aspect Ratio Selector */}
              <div style={{ marginBottom: '16px' }}>
                <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                  <Layers size={12} />
                  Aspect Ratio
                </label>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {ASPECT_RATIOS.map(ratio => (
                    <button
                      key={ratio.id}
                      onClick={() => setSelectedAspect(ratio.id)}
                      style={{
                        padding: '8px 12px',
                        borderRadius: '6px',
                        background: selectedAspect === ratio.id ? 'var(--accent-primary)' : 'var(--bg-tertiary)',
                        color: selectedAspect === ratio.id ? 'white' : 'var(--text-primary)',
                        border: 'none',
                        fontSize: '12px',
                        cursor: 'pointer',
                        textAlign: 'left'
                      }}
                    >
                      {ratio.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Render Button */}
              <button
                onClick={handleRenderVideo}
                style={{
                  width: '100%',
                  padding: '12px',
                  borderRadius: '8px',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  border: 'none',
                  fontSize: '14px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)'
                }}
              >
                <Play size={16} />
                Render Video
              </button>
            </div>
          )}
        </div>

        {/* Template Gallery */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
          {filteredTemplates.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '60px 20px' }}>
              <Video size={48} style={{ opacity: 0.2, marginBottom: '16px' }} />
              <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>No video templates found</h3>
              <p style={{ color: 'var(--text-muted)' }}>Try adjusting your search or filter criteria</p>
            </div>
          ) : (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
              gap: '20px'
            }}>
              {filteredTemplates.map((template, idx) => (
                <TemplateCard
                  key={template.id}
                  template={template}
                  onUse={handleSelectTemplate}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
