import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, Presentation } from 'lucide-react';

export default function SlideViewer({ slides, templateId = 'clay_minimal_1' }) {
  const [currentSlide, setCurrentSlide] = useState(0);

  const templateCategory = templateId.split('_').slice(0, 2).join('_');
  const variation = parseInt(templateId.split('_').pop() || '1');

  // Styling Maps
  const containerStyleMap = {
    clay_minimal: {
      background: 'var(--bg-card)',
      border: '1px solid var(--border-primary)',
      boxShadow: 'var(--shadow-clay)',
      color: 'var(--text-primary)'
    },
    dark_brutalist: {
      background: '#09090b',
      border: '4px solid #fff',
      boxShadow: '12px 12px 0px rgba(255,255,255,1)',
      color: '#fff'
    },
    neon_cyber: {
      background: '#020617',
      border: '1px solid #38bdf8',
      boxShadow: '0 0 40px rgba(56,189,248,0.2) inset',
      color: '#e0f2fe'
    },
    editorial_print: {
      background: '#fdfbf7',
      border: '1px solid #e7e5e4',
      boxShadow: 'none',
      color: '#1c1917',
      fontFamily: 'Times New Roman, serif'
    },
    clean_corporate: {
      background: 'linear-gradient(135deg, #ffffff, #f8fafc)',
      border: '1px solid #cbd5e1',
      boxShadow: '0 10px 25px rgba(0,0,0,0.05)',
      color: '#0f172a'
    }
  };

  const headerStyleMap = {
    clay_minimal: { color: 'var(--accent-primary)', fontSize: '36px', fontWeight: 800 },
    dark_brutalist: { color: '#ffffff', fontSize: '48px', fontWeight: 900, textTransform: 'uppercase', letterSpacing: '-0.02em' },
    neon_cyber: { color: '#38bdf8', fontSize: '36px', fontWeight: 600, textShadow: '0 0 10px #38bdf8' },
    editorial_print: { color: '#1c1917', fontSize: '42px', fontWeight: 400, fontStyle: 'italic' },
    clean_corporate: { color: '#0f172a', fontSize: '32px', fontWeight: 700 }
  };

  const pointStyleMap = {
    clay_minimal: { color: 'var(--text-secondary)' },
    dark_brutalist: { color: '#a1a1aa' },
    neon_cyber: { color: '#7dd3fc' },
    editorial_print: { color: '#44403c', fontFamily: 'sans-serif' },
    clean_corporate: { color: '#475569' }
  };

  const activeContainer = containerStyleMap[templateCategory] || containerStyleMap.clay_minimal;
  const activeHeader = headerStyleMap[templateCategory] || headerStyleMap.clay_minimal;
  const activePoint = pointStyleMap[templateCategory] || pointStyleMap.clay_minimal;

  if (!slides || slides.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-muted)' }}>
        <Presentation size={48} style={{ opacity: 0.2, margin: '0 auto 16px' }} />
        <p>No presentation slides available for this campaign.</p>
      </div>
    );
  }

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % slides.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);
  };

  const slide = slides[currentSlide];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
      {/* Slide Container */}
      <div 
        style={{
          width: '100%',
          maxWidth: '900px',
          aspectRatio: '16/9',
          position: 'relative',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          transition: 'all 0.5s ease',
          borderRadius: templateCategory === 'dark_brutalist' ? '0px' : '16px',
          ...activeContainer
        }}
      >
        {/* Dynamic decorative elements based on variation */}
        {variation % 2 === 0 && templateCategory === 'clean_corporate' && (
           <div style={{ position: 'absolute', top: 0, right: 0, width: '30%', height: '100%', background: 'linear-gradient(to right, transparent, rgba(0,0,0,0.03))'}} />
        )}
        {templateCategory === 'neon_cyber' && (
           <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(#38bdf820 1px, transparent 1px), linear-gradient(90deg, #38bdf820 1px, transparent 1px)', backgroundSize: '40px 40px', opacity: 0.5 }} />
        )}
        <AnimatePresence mode="wait">
          <motion.div
            key={currentSlide}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            style={{ 
              flex: 1, 
              display: 'flex', 
              flexDirection: 'column', 
              justifyContent: 'center',
              padding: '60px',
              paddingTop: '80px',
            }}
          >
            <h2 style={{ marginBottom: '32px', lineHeight: 1.2, zIndex: 10, ...activeHeader }}>
              {slide.title}
            </h2>
            
            <ul style={{ listStyleType: 'none', padding: 0, margin: 0, fontSize: '20px', color: 'var(--text-primary)', display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {slide.points && slide.points.map((point, idx) => (
                <motion.li 
                  key={idx}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 + 0.3 }}
                  style={{ display: 'flex', alignItems: 'flex-start', gap: '16px', lineHeight: 1.5, zIndex: 10, ...activePoint }}
                >
                  <div style={{ 
                    marginTop: '8px', 
                    width: '8px', 
                    height: '8px', 
                    borderRadius: templateCategory === 'dark_brutalist' ? '0' : '50%', 
                    background: activeHeader.color,
                    flexShrink: 0
                  }} />
                  <span>{point}</span>
                </motion.li>
              ))}
            </ul>
          </motion.div>
        </AnimatePresence>

        {/* Footer info / Page Number */}
        <div style={{ 
          position: 'absolute', 
          bottom: '24px', 
          right: '32px', 
          fontSize: '14px', 
          fontWeight: 600,
          color: 'var(--text-muted)' 
        }}>
          {currentSlide + 1} / {slides.length}
        </div>
      </div>

      {/* Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '24px', marginTop: '32px' }}>
        <button 
          onClick={prevSlide}
          className="btn btn-secondary"
          style={{ width: '48px', height: '48px', padding: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%' }}
        >
          <ChevronLeft size={24} />
        </button>
        <div style={{ display: 'flex', gap: '8px' }}>
          {slides.map((_, i) => (
            <div 
              key={i} 
              onClick={() => setCurrentSlide(i)}
              style={{
                width: i === currentSlide ? '24px' : '8px',
                height: '8px',
                borderRadius: '4px',
                background: i === currentSlide ? 'var(--accent-primary)' : 'var(--bg-tertiary)',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            />
          ))}
        </div>
        <button 
          onClick={nextSlide}
          className="btn btn-secondary"
          style={{ width: '48px', height: '48px', padding: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%' }}
        >
          <ChevronRight size={24} />
        </button>
      </div>
    </div>
  );
}
