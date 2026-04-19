/**
 * PipelineConfigurator Component
 * Visual interface for selecting video/image templates before running pipeline.
 * Shows exactly what output you'll get with live previews.
 */
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Video, Image, Check, ArrowRight, Settings, Eye } from 'lucide-react';
import { api } from '../utils/api';

export default function PipelineConfigurator({ onConfigComplete, initialConfig = {} }) {
  const [step, setStep] = useState(1); // 1: Type, 2: Template, 3: Settings, 4: Review
  const [contentType, setContentType] = useState(initialConfig.contentType || 'video');
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [config, setConfig] = useState({
    contentType: initialConfig.contentType || 'video',
    templateId: initialConfig.templateId || null,
    templateName: initialConfig.templateName || '',
    duration: initialConfig.duration || 15,
    aspectRatio: initialConfig.aspectRatio || '9:16',
    scenes: initialConfig.scenes || [],
    style: initialConfig.style || 'modern'
  });

  // Load templates based on content type
  useEffect(() => {
    api.getTemplates({ type: contentType, limit: 100 })
      .then(data => setTemplates(data))
      .catch(err => console.error('Failed to load templates:', err));
  }, [contentType]);

  const handleSelectTemplate = (template) => {
    setSelectedTemplate(template);
    setConfig({
      ...config,
      templateId: template.id,
      templateName: template.name
    });
  };

  const handleNext = () => {
    if (step < 4) {
      setStep(step + 1);
    } else {
      // Submit configuration
      onConfigComplete(config);
    }
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
      {/* Progress Steps */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '40px', position: 'relative' }}>
        <div style={{ position: 'absolute', top: '20px', left: 0, right: 0, height: '2px', background: 'var(--border-glass)', zIndex: 0 }} />
        
        {['Content Type', 'Choose Template', 'Settings', 'Review'].map((label, idx) => {
          const stepNum = idx + 1;
          const isActive = stepNum === step;
          const isCompleted = stepNum < step;
          
          return (
            <div key={idx} style={{ flex: 1, textAlign: 'center', position: 'relative', zIndex: 1 }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                background: isCompleted ? 'var(--accent-primary)' : isActive ? 'var(--accent-primary)' : 'var(--bg-tertiary)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 8px',
                fontWeight: 'bold',
                fontSize: '16px'
              }}>
                {isCompleted ? <Check size={20} /> : stepNum}
              </div>
              <div style={{ fontSize: '12px', color: isActive ? 'var(--text-primary)' : 'var(--text-muted)', fontWeight: isActive ? 600 : 400 }}>
                {label}
              </div>
            </div>
          );
        })}
      </div>

      {/* Step 1: Content Type */}
      {step === 1 && (
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
          <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '24px', textAlign: 'center' }}>
            What are you creating?
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', maxWidth: '600px', margin: '0 auto' }}>
            <button
              onClick={() => { setContentType('video'); setConfig({ ...config, contentType: 'video' }); }}
              style={{
                padding: '40px',
                borderRadius: '12px',
                background: contentType === 'video' ? 'var(--accent-primary)' : 'var(--bg-secondary)',
                border: `2px solid ${contentType === 'video' ? 'var(--accent-primary)' : 'var(--border-glass)'}`,
                color: contentType === 'video' ? 'white' : 'var(--text-primary)',
                cursor: 'pointer',
                textAlign: 'center'
              }}
            >
              <Video size={48} style={{ marginBottom: '16px' }} />
              <h3 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '8px' }}>Video</h3>
              <p style={{ fontSize: '13px', opacity: 0.8 }}>Motion graphics, ads, animations</p>
            </button>
            
            <button
              onClick={() => { setContentType('image'); setConfig({ ...config, contentType: 'image' }); }}
              style={{
                padding: '40px',
                borderRadius: '12px',
                background: contentType === 'image' ? 'var(--accent-primary)' : 'var(--bg-secondary)',
                border: `2px solid ${contentType === 'image' ? 'var(--accent-primary)' : 'var(--border-glass)'}`,
                color: contentType === 'image' ? 'white' : 'var(--text-primary)',
                cursor: 'pointer',
                textAlign: 'center'
              }}
            >
              <Image size={48} style={{ marginBottom: '16px' }} />
              <h3 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '8px' }}>Image</h3>
              <p style={{ fontSize: '13px', opacity: 0.8 }}>Social posts, banners, graphics</p>
            </button>
          </div>
        </motion.div>
      )}

      {/* Step 2: Template Selection */}
      {step === 2 && (
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
          <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '8px', textAlign: 'center' }}>
            Choose Your Template
          </h2>
          <p style={{ textAlign: 'center', color: 'var(--text-muted)', marginBottom: '32px' }}>
            Select a template to see exactly what you'll get
          </p>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px', maxHeight: '500px', overflowY: 'auto', padding: '20px 0' }}>
            {templates.map(template => {
              const metadata = template.metadata_json ? JSON.parse(template.metadata_json) : {};
              const dimensions = template.dimensions || {};
              
              return (
                <div
                  key={template.id}
                  onClick={() => handleSelectTemplate(template)}
                  style={{
                    padding: '24px',
                    borderRadius: '12px',
                    background: selectedTemplate?.id === template.id ? 'var(--accent-primary)' : 'var(--bg-secondary)',
                    border: `2px solid ${selectedTemplate?.id === template.id ? 'var(--accent-primary)' : 'var(--border-glass)'}`,
                    color: selectedTemplate?.id === template.id ? 'white' : 'var(--text-primary)',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                    {contentType === 'video' ? <Video size={24} /> : <Image size={24} />}
                    <h3 style={{ fontSize: '18px', fontWeight: 'bold', flex: 1 }}>{template.name}</h3>
                  </div>
                  
                  {metadata.description && (
                    <p style={{ fontSize: '13px', opacity: 0.8, marginBottom: '12px', lineHeight: 1.5 }}>
                      {metadata.description}
                    </p>
                  )}
                  
                  <div style={{ display: 'flex', gap: '12px', marginBottom: '12px', fontSize: '12px', opacity: 0.7 }}>
                    {dimensions.width && dimensions.height && (
                      <span>{dimensions.width}×{dimensions.height}</span>
                    )}
                    {metadata.scene_count && (
                      <span>• {metadata.scene_count} scenes</span>
                    )}
                    {metadata.duration_seconds && (
                      <span>• {metadata.duration_seconds}s</span>
                    )}
                  </div>
                  
                  {metadata.output_format && (
                    <div style={{ 
                      fontSize: '11px', 
                      padding: '6px 10px', 
                      background: selectedTemplate?.id === template.id ? 'rgba(255,255,255,0.2)' : 'var(--bg-tertiary)',
                      borderRadius: '6px',
                      marginBottom: '12px',
                      display: 'inline-block'
                    }}>
                      Output: {metadata.output_format} @ {metadata.fps || 30}fps
                    </div>
                  )}
                  
                  {template.tags && (
                    <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                      {template.tags.slice(0, 4).map((tag, idx) => (
                        <span key={idx} style={{
                          padding: '4px 10px',
                          borderRadius: '6px',
                          background: selectedTemplate?.id === template.id ? 'rgba(255,255,255,0.2)' : 'var(--bg-tertiary)',
                          fontSize: '11px',
                          fontWeight: 500
                        }}>
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </motion.div>
      )}

      {/* Step 3: Settings */}
      {step === 3 && contentType === 'video' && (
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
          <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '32px', textAlign: 'center' }}>
            Configure Your Video
          </h2>
          
          <div style={{ maxWidth: '600px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Duration */}
            <div>
              <label style={{ fontSize: '14px', fontWeight: 600, display: 'block', marginBottom: '12px' }}>
                Duration
              </label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
                {[15, 30, 60].map(dur => (
                  <button
                    key={dur}
                    onClick={() => setConfig({ ...config, duration: dur })}
                    style={{
                      padding: '16px',
                      borderRadius: '8px',
                      background: config.duration === dur ? 'var(--accent-primary)' : 'var(--bg-secondary)',
                      border: `2px solid ${config.duration === dur ? 'var(--accent-primary)' : 'var(--border-glass)'}`,
                      color: config.duration === dur ? 'white' : 'var(--text-primary)',
                      cursor: 'pointer',
                      fontWeight: 600
                    }}
                  >
                    {dur}s
                  </button>
                ))}
              </div>
            </div>

            {/* Aspect Ratio */}
            <div>
              <label style={{ fontSize: '14px', fontWeight: 600, display: 'block', marginBottom: '12px' }}>
                Aspect Ratio
              </label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
                {[
                  { id: '9:16', label: 'Vertical', desc: 'TikTok/Reels' },
                  { id: '16:9', label: 'Horizontal', desc: 'YouTube' },
                  { id: '1:1', label: 'Square', desc: 'Instagram' }
                ].map(ratio => (
                  <button
                    key={ratio.id}
                    onClick={() => setConfig({ ...config, aspectRatio: ratio.id })}
                    style={{
                      padding: '16px',
                      borderRadius: '8px',
                      background: config.aspectRatio === ratio.id ? 'var(--accent-primary)' : 'var(--bg-secondary)',
                      border: `2px solid ${config.aspectRatio === ratio.id ? 'var(--accent-primary)' : 'var(--border-glass)'}`,
                      color: config.aspectRatio === ratio.id ? 'white' : 'var(--text-primary)',
                      cursor: 'pointer',
                      textAlign: 'center'
                    }}
                  >
                    <div style={{ fontWeight: 600, marginBottom: '4px' }}>{ratio.label}</div>
                    <div style={{ fontSize: '11px', opacity: 0.7 }}>{ratio.desc}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Step 4: Review */}
      {step === 4 && (
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
          <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '32px', textAlign: 'center' }}>
            Review Your Configuration
          </h2>
          
          <div style={{ maxWidth: '800px', margin: '0 auto' }}>
            {/* Configuration Summary */}
            <div style={{ background: 'var(--bg-secondary)', borderRadius: '12px', padding: '32px', border: '1px solid var(--border-glass)', marginBottom: '24px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Settings size={20} />
                Configuration Details
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '16px', borderBottom: '1px solid var(--border-glass)' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Content Type</span>
                  <span style={{ fontWeight: 600, textTransform: 'capitalize' }}>{config.contentType}</span>
                </div>
                
                <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '16px', borderBottom: '1px solid var(--border-glass)' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Template</span>
                  <span style={{ fontWeight: 600 }}>{config.templateName || 'Not selected'}</span>
                </div>
                
                {config.contentType === 'video' && selectedTemplate && (() => {
                  const metadata = selectedTemplate.metadata_json ? JSON.parse(selectedTemplate.metadata_json) : {};
                  const dimensions = selectedTemplate.dimensions || {};
                  
                  return (
                    <>
                      <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '16px', borderBottom: '1px solid var(--border-glass)' }}>
                        <span style={{ color: 'var(--text-muted)' }}>Video Engine</span>
                        <span style={{ fontWeight: 600, fontFamily: 'monospace' }}>{metadata.engine_id || 'N/A'}</span>
                      </div>
                      
                      <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '16px', borderBottom: '1px solid var(--border-glass)' }}>
                        <span style={{ color: 'var(--text-muted)' }}>Resolution</span>
                        <span style={{ fontWeight: 600 }}>{dimensions.width || 1080}×{dimensions.height || 1920}</span>
                      </div>
                      
                      <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '16px', borderBottom: '1px solid var(--border-glass)' }}>
                        <span style={{ color: 'var(--text-muted)' }}>Duration</span>
                        <span style={{ fontWeight: 600 }}>{metadata.duration_seconds || config.duration} seconds</span>
                      </div>
                      
                      <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '16px', borderBottom: '1px solid var(--border-glass)' }}>
                        <span style={{ color: 'var(--text-muted)' }}>Frame Rate</span>
                        <span style={{ fontWeight: 600 }}>{metadata.fps || 30} fps</span>
                      </div>
                      
                      <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '16px', borderBottom: '1px solid var(--border-glass)' }}>
                        <span style={{ color: 'var(--text-muted)' }}>Total Frames</span>
                        <span style={{ fontWeight: 600 }}>{(metadata.duration_seconds || config.duration) * (metadata.fps || 30)} frames</span>
                      </div>
                      
                      <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '16px', borderBottom: '1px solid var(--border-glass)' }}>
                        <span style={{ color: 'var(--text-muted)' }}>Scene Count</span>
                        <span style={{ fontWeight: 600 }}>{metadata.scene_count || 3} scenes</span>
                      </div>
                      
                      <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '16px' }}>
                        <span style={{ color: 'var(--text-muted)' }}>Aspect Ratio</span>
                        <span style={{ fontWeight: 600 }}>{config.aspectRatio}</span>
                      </div>
                    </>
                  );
                })()}
              </div>
            </div>

            {/* Expected Output Preview */}
            <div style={{ background: 'var(--bg-secondary)', borderRadius: '12px', padding: '32px', border: '1px solid var(--border-glass)' }}>
              <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Eye size={20} />
                Expected Output
              </h3>
              
              {config.contentType === 'video' && selectedTemplate && (() => {
                const metadata = selectedTemplate.metadata_json ? JSON.parse(selectedTemplate.metadata_json) : {};
                const dimensions = selectedTemplate.dimensions || {};
                const width = dimensions.width || 1080;
                const height = dimensions.height || 1920;
                const duration = metadata.duration_seconds || config.duration;
                const fps = metadata.fps || 30;
                
                return (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    {/* Visual Preview Box */}
                    <div style={{ 
                      background: '#000', 
                      borderRadius: '8px', 
                      padding: '24px',
                      textAlign: 'center'
                    }}>
                      <div style={{
                        width: '200px',
                        height: `${(200 / width) * height}px`,
                        maxWidth: '100%',
                        maxHeight: '300px',
                        margin: '0 auto 16px',
                        background: `linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))`,
                        borderRadius: '4px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                        fontSize: '48px',
                        fontWeight: 'bold'
                      }}>
                        ▶
                      </div>
                      <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '14px' }}>
                        Preview aspect ratio: {config.aspectRatio}
                      </p>
                    </div>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                      <div style={{ padding: '16px', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>Format</div>
                        <div style={{ fontSize: '16px', fontWeight: 600 }}>{metadata.output_format || 'MP4 (H.264)'}</div>
                      </div>
                      
                      <div style={{ padding: '16px', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>Resolution</div>
                        <div style={{ fontSize: '16px', fontWeight: 600 }}>{width}×{height}</div>
                      </div>
                      
                      <div style={{ padding: '16px', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>Duration</div>
                        <div style={{ fontSize: '16px', fontWeight: 600 }}>{duration}s</div>
                      </div>
                      
                      <div style={{ padding: '16px', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>Frame Rate</div>
                        <div style={{ fontSize: '16px', fontWeight: 600 }}>{fps} fps</div>
                      </div>
                      
                      <div style={{ padding: '16px', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>Total Frames</div>
                        <div style={{ fontSize: '16px', fontWeight: 600 }}>{duration * fps}</div>
                      </div>
                      
                      <div style={{ padding: '16px', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>Scenes</div>
                        <div style={{ fontSize: '16px', fontWeight: 600 }}>{metadata.scene_count || 3}</div>
                      </div>
                    </div>
                    
                    <div style={{ padding: '20px', background: 'var(--bg-tertiary)', borderRadius: '8px', marginTop: '8px' }}>
                      <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '12px' }}>What You'll Get:</h4>
                      <ul style={{ margin: 0, paddingLeft: '20px', color: 'var(--text-secondary)', fontSize: '14px', lineHeight: 1.8 }}>
                        <li>Professional {width}×{height} video at {fps}fps</li>
                        <li>{duration}-second duration with {metadata.scene_count || 3} animated scenes</li>
                        <li>Branded with your company colors: {config.style || 'custom'}</li>
                        <li>Optimized for {config.aspectRatio === '9:16' ? 'TikTok/Instagram Reels/YouTube Shorts' : config.aspectRatio === '16:9' ? 'YouTube/Facebook' : 'Instagram Feed'}</li>
                        <li>High-quality H.264 encoding for web and social media</li>
                        {metadata.description && <li>Style: {metadata.description}</li>}
                      </ul>
                    </div>
                  </div>
                );
              })()}
              
              {config.contentType === 'image' && (
                <ul style={{ margin: 0, paddingLeft: '20px', color: 'var(--text-secondary)', fontSize: '14px', lineHeight: 1.8 }}>
                  <li>High-quality image with selected template</li>
                  <li>Format: PNG (lossless)</li>
                  <li>Optimized for social media</li>
                  <li>Branded with your company colors and logo</li>
                </ul>
              )}
            </div>
          </div>
        </motion.div>
      )}

      {/* Navigation Buttons */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '40px', maxWidth: '700px', margin: '40px auto 0' }}>
        <button
          onClick={handleBack}
          disabled={step === 1}
          style={{
            padding: '12px 32px',
            borderRadius: '8px',
            background: step === 1 ? 'var(--bg-tertiary)' : 'var(--bg-secondary)',
            color: step === 1 ? 'var(--text-muted)' : 'var(--text-primary)',
            border: '1px solid var(--border-glass)',
            fontSize: '14px',
            fontWeight: 600,
            cursor: step === 1 ? 'not-allowed' : 'pointer',
            opacity: step === 1 ? 0.5 : 1
          }}
        >
          Back
        </button>
        
        <button
          onClick={handleNext}
          disabled={step === 2 && !selectedTemplate}
          style={{
            padding: '12px 32px',
            borderRadius: '8px',
            background: (step === 2 && !selectedTemplate) ? 'var(--bg-tertiary)' : 'var(--accent-primary)',
            color: (step === 2 && !selectedTemplate) ? 'var(--text-muted)' : 'white',
            border: 'none',
            fontSize: '14px',
            fontWeight: 600,
            cursor: (step === 2 && !selectedTemplate) ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            opacity: (step === 2 && !selectedTemplate) ? 0.5 : 1
          }}
        >
          {step === 4 ? 'Run Pipeline' : 'Next'}
          <ArrowRight size={16} />
        </button>
      </div>
    </div>
  );
}
