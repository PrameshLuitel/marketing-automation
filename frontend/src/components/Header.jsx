import { useLocation } from 'react-router-dom';
import { Zap, Terminal, Trash2, X, MapPin, Tag, FileText, Clock, Image } from 'lucide-react';
import { useState } from 'react';
import { api } from '../utils/api';

const pageTitles = {
  '/': 'Command Center',
  '/trends': 'Trend Analysis',
  '/campaigns': 'Campaign Briefs',
  '/images': 'Image Studio',
  '/videos': 'Video Center',
  '/logs': 'Agent Logs',
  '/settings': 'Settings',
};

/* ══════════════ Duration presets ══════════════ */
const DURATION_OPTIONS = [
  { seconds: 5,  label: '5s',  scenes: 1, desc: 'Story / Quick Hit' },
  { seconds: 10, label: '10s', scenes: 2, desc: 'Reels / Shorts' },
  { seconds: 15, label: '15s', scenes: 3, desc: 'Instagram Reels' },
  { seconds: 20, label: '20s', scenes: 4, desc: 'TikTok Standard' },
  { seconds: 25, label: '25s', scenes: 5, desc: 'YouTube Shorts' },
  { seconds: 30, label: '30s', scenes: 6, desc: 'Full Production' },
];

/* ══════════════════════════════════════════════════
   30 VIDEO TEMPLATES — each with truly unique visual DNA
   ══════════════════════════════════════════════════ */
const VIDEO_TEMPLATES = [
  // MESH ABSTRACT — parametric particle flows
  { id: 'mesh_abstract_1', name: 'Nebula Drift',   cat: 'mesh',     bg: '#030308', g1: '#4ade80', g2: '#3b82f6', g3: '#8b5cf6', style: 'orbs' },
  { id: 'mesh_abstract_2', name: 'Arctic Pulse',   cat: 'mesh',     bg: '#020a14', g1: '#38bdf8', g2: '#818cf8', g3: '#22d3ee', style: 'wave' },
  { id: 'mesh_abstract_3', name: 'Sunset Blaze',   cat: 'mesh',     bg: '#0c0504', g1: '#f97316', g2: '#ef4444', g3: '#fbbf24', style: 'streak' },
  { id: 'mesh_abstract_4', name: 'Deep Violet',    cat: 'mesh',     bg: '#08030f', g1: '#a855f7', g2: '#6366f1', g3: '#c084fc', style: 'rings' },
  { id: 'mesh_abstract_5', name: 'Emerald Wave',   cat: 'mesh',     bg: '#020c06', g1: '#10b981', g2: '#14b8a6', g3: '#34d399', style: 'diamond' },
  { id: 'mesh_abstract_6', name: 'Rose Quartz',    cat: 'mesh',     bg: '#0c0408', g1: '#f472b6', g2: '#e879f9', g3: '#fb7185', style: 'vortex' },
  // PRODUCT SHOWCASE — centered hero device
  { id: 'product_showcase_1', name: 'Obsidian',    cat: 'product',  bg: '#050505', glow: '#8b5cf6', frame: 'rgba(255,255,255,0.10)' },
  { id: 'product_showcase_2', name: 'Glacier',     cat: 'product',  bg: '#050810', glow: '#38bdf8', frame: 'rgba(56,189,248,0.15)' },
  { id: 'product_showcase_3', name: 'Gold Rush',   cat: 'product',  bg: '#0a0804', glow: '#f59e0b', frame: 'rgba(245,158,11,0.15)' },
  { id: 'product_showcase_4', name: 'Neon Shelf',  cat: 'product',  bg: '#000505', glow: '#22d3ee', frame: 'rgba(34,211,238,0.15)' },
  { id: 'product_showcase_5', name: 'Ruby',        cat: 'product',  bg: '#0a0305', glow: '#f43f5e', frame: 'rgba(244,63,94,0.15)' },
  { id: 'product_showcase_6', name: 'Mint',        cat: 'product',  bg: '#030a08', glow: '#34d399', frame: 'rgba(52,211,153,0.15)' },
  // KINETIC TYPOGRAPHY — bold full-screen text
  { id: 'kinetic_typography_1', name: 'Flash Yellow', cat: 'kinetic', bg: '#facc15', fg: '#000', word: 'BOLD' },
  { id: 'kinetic_typography_2', name: 'Electric Blue', cat: 'kinetic', bg: '#2563eb', fg: '#fff', word: 'FAST' },
  { id: 'kinetic_typography_3', name: 'Hot Coral',    cat: 'kinetic', bg: '#f43f5e', fg: '#fff', word: 'FIRE' },
  { id: 'kinetic_typography_4', name: 'Acid Green',   cat: 'kinetic', bg: '#22c55e', fg: '#000', word: 'GROW' },
  { id: 'kinetic_typography_5', name: 'Void Black',   cat: 'kinetic', bg: '#09090b', fg: '#fff', word: 'DARK' },
  { id: 'kinetic_typography_6', name: 'Tangerine',    cat: 'kinetic', bg: '#f97316', fg: '#000', word: 'HYPE' },
  // NEON CIRCUIT — cyberpunk wires
  { id: 'neon_circuit_1', name: 'Cyan Matrix',   cat: 'neon', c1: 'cyan',    c2: '#f0f',    nodeColor: 'cyan' },
  { id: 'neon_circuit_2', name: 'Green Term',    cat: 'neon', c1: '#4ade80', c2: '#22d3ee', nodeColor: '#4ade80' },
  { id: 'neon_circuit_3', name: 'Red Alert',     cat: 'neon', c1: '#f43f5e', c2: '#f97316', nodeColor: '#f43f5e' },
  { id: 'neon_circuit_4', name: 'Purple Haze',   cat: 'neon', c1: '#a855f7', c2: '#6366f1', nodeColor: '#a855f7' },
  { id: 'neon_circuit_5', name: 'Gold Wire',     cat: 'neon', c1: '#f59e0b', c2: '#eab308', nodeColor: '#f59e0b' },
  { id: 'neon_circuit_6', name: 'Ice Blue',      cat: 'neon', c1: '#38bdf8', c2: '#7dd3fc', nodeColor: '#38bdf8' },
  // CINEMATIC FADE — elegant gradients
  { id: 'cinematic_fade_1', name: 'Corporate',     cat: 'cinematic', tint: '#3b82f6', lineColor: 'rgba(59,130,246,0.12)' },
  { id: 'cinematic_fade_2', name: 'Warm Sepia',    cat: 'cinematic', tint: '#d97706', lineColor: 'rgba(217,119,6,0.10)' },
  { id: 'cinematic_fade_3', name: 'Forest Calm',   cat: 'cinematic', tint: '#10b981', lineColor: 'rgba(16,185,129,0.10)' },
  { id: 'cinematic_fade_4', name: 'Rose Morning',  cat: 'cinematic', tint: '#f43f5e', lineColor: 'rgba(244,63,94,0.08)' },
  { id: 'cinematic_fade_5', name: 'Slate Mono',    cat: 'cinematic', tint: '#64748b', lineColor: 'rgba(100,116,139,0.10)' },
  { id: 'cinematic_fade_6', name: 'Lavender',      cat: 'cinematic', tint: '#a855f7', lineColor: 'rgba(168,85,247,0.08)' },
];

/* ══════════════════════════════════════════════════
   30 PRESENTATION TEMPLATES
   ══════════════════════════════════════════════════ */
const PRES_TEMPLATES = [
  { id: 'clay_minimal_1', name: 'Oat Cream',     cat: 'clay',      bg: '#f5f0e8', title: '#2d6a4f', dot: '#2d6a4f', card: '#eee8d5' },
  { id: 'clay_minimal_2', name: 'Sage Mist',     cat: 'clay',      bg: '#ecf0eb', title: '#365314', dot: '#365314', card: '#d9e4d5' },
  { id: 'clay_minimal_3', name: 'Blush Sand',    cat: 'clay',      bg: '#f5ece8', title: '#9a3412', dot: '#9a3412', card: '#f0ddd5' },
  { id: 'clay_minimal_4', name: 'Ocean Foam',    cat: 'clay',      bg: '#e8f0f5', title: '#1e40af', dot: '#1e40af', card: '#d5e4f0' },
  { id: 'clay_minimal_5', name: 'Lilac Soft',    cat: 'clay',      bg: '#f0e8f5', title: '#7e22ce', dot: '#7e22ce', card: '#e4d5f0' },
  { id: 'clay_minimal_6', name: 'Honey Glow',    cat: 'clay',      bg: '#f5f0e0', title: '#92400e', dot: '#92400e', card: '#f0e8c8' },
  { id: 'dark_brutalist_1', name: 'Pure Mono',   cat: 'brutalist',  bg: '#09090b', title: '#fff',    dot: '#fff' },
  { id: 'dark_brutalist_2', name: 'Blood Red',   cat: 'brutalist',  bg: '#0a0000', title: '#ef4444', dot: '#ef4444' },
  { id: 'dark_brutalist_3', name: 'Acid Lime',   cat: 'brutalist',  bg: '#050a00', title: '#84cc16', dot: '#84cc16' },
  { id: 'dark_brutalist_4', name: 'Royal Gold',  cat: 'brutalist',  bg: '#0a0800', title: '#eab308', dot: '#eab308' },
  { id: 'dark_brutalist_5', name: 'Ice White',   cat: 'brutalist',  bg: '#0c0c0e', title: '#e2e8f0', dot: '#e2e8f0' },
  { id: 'dark_brutalist_6', name: 'Hot Pink',    cat: 'brutalist',  bg: '#0a0005', title: '#ec4899', dot: '#ec4899' },
  { id: 'neon_cyber_1', name: 'Cyan Grid',       cat: 'cyber',     bg: '#020617', title: '#38bdf8', dot: '#38bdf8', grid: 'rgba(56,189,248,0.06)' },
  { id: 'neon_cyber_2', name: 'Matrix Green',    cat: 'cyber',     bg: '#011a00', title: '#4ade80', dot: '#4ade80', grid: 'rgba(74,222,128,0.06)' },
  { id: 'neon_cyber_3', name: 'Plasma Purple',   cat: 'cyber',     bg: '#0d0017', title: '#a78bfa', dot: '#a78bfa', grid: 'rgba(167,139,250,0.06)' },
  { id: 'neon_cyber_4', name: 'Hot Ember',       cat: 'cyber',     bg: '#170500', title: '#fb923c', dot: '#fb923c', grid: 'rgba(251,146,60,0.06)' },
  { id: 'neon_cyber_5', name: 'Ice Pink',        cat: 'cyber',     bg: '#170010', title: '#f472b6', dot: '#f472b6', grid: 'rgba(244,114,182,0.06)' },
  { id: 'neon_cyber_6', name: 'Teal Laser',      cat: 'cyber',     bg: '#001210', title: '#2dd4bf', dot: '#2dd4bf', grid: 'rgba(45,212,191,0.06)' },
  { id: 'editorial_print_1', name: 'Classic Ivory', cat: 'editorial', bg: '#fdfbf7', title: '#1c1917', dot: '#78716c' },
  { id: 'editorial_print_2', name: 'Parchment',    cat: 'editorial', bg: '#faf6ef', title: '#422006', dot: '#a16207' },
  { id: 'editorial_print_3', name: 'Cool Gray',    cat: 'editorial', bg: '#f8fafc', title: '#0f172a', dot: '#475569' },
  { id: 'editorial_print_4', name: 'Rose Paper',   cat: 'editorial', bg: '#fdf2f8', title: '#831843', dot: '#be185d' },
  { id: 'editorial_print_5', name: 'Forest',       cat: 'editorial', bg: '#f0fdf4', title: '#14532d', dot: '#15803d' },
  { id: 'editorial_print_6', name: 'Ocean Script', cat: 'editorial', bg: '#f0f9ff', title: '#0c4a6e', dot: '#0284c7' },
  { id: 'clean_corporate_1', name: 'Blue Standard', cat: 'corporate', bg: '#fff', bar: '#3b82f6', title: '#0f172a', dot: '#3b82f6' },
  { id: 'clean_corporate_2', name: 'Green Growth',  cat: 'corporate', bg: '#fff', bar: '#10b981', title: '#064e3b', dot: '#10b981' },
  { id: 'clean_corporate_3', name: 'Purple Vision', cat: 'corporate', bg: '#fff', bar: '#8b5cf6', title: '#2e1065', dot: '#8b5cf6' },
  { id: 'clean_corporate_4', name: 'Red Power',     cat: 'corporate', bg: '#fff', bar: '#ef4444', title: '#7f1d1d', dot: '#ef4444' },
  { id: 'clean_corporate_5', name: 'Orange Warm',   cat: 'corporate', bg: '#fff', bar: '#f97316', title: '#7c2d12', dot: '#f97316' },
  { id: 'clean_corporate_6', name: 'Teal Fresh',    cat: 'corporate', bg: '#fff', bar: '#14b8a6', title: '#134e4a', dot: '#14b8a6' },
];

/* ══════════ Video Thumbnail Component ══════════ */
function VideoThumb({ t }) {
  const abs = { position: 'absolute', inset: 0 };

  if (t.cat === 'mesh') {
    // Each variation gets a unique arrangement of gradient blobs
    const positions = [
      { x1: '15%', y1: '20%', x2: '80%', y2: '75%', x3: '50%', y3: '10%' },
      { x1: '70%', y1: '15%', x2: '20%', y2: '80%', x3: '50%', y3: '50%' },
      { x1: '30%', y1: '70%', x2: '70%', y2: '20%', x3: '10%', y3: '40%' },
      { x1: '50%', y1: '10%', x2: '10%', y2: '90%', x3: '90%', y3: '50%' },
      { x1: '20%', y1: '50%', x2: '80%', y2: '30%', x3: '40%', y3: '80%' },
      { x1: '80%', y1: '80%', x2: '20%', y2: '20%', x3: '60%', y3: '60%' },
    ];
    const idx = parseInt(t.id.split('_').pop()) - 1;
    const p = positions[idx] || positions[0];
    return (
      <div style={{ ...abs, background: t.bg }}>
        <div style={{ ...abs, opacity: 0.55, background: `radial-gradient(circle at ${p.x1} ${p.y1}, ${t.g1}70 0%, transparent 45%), radial-gradient(circle at ${p.x2} ${p.y2}, ${t.g2}50 0%, transparent 45%), radial-gradient(circle at ${p.x3} ${p.y3}, ${t.g3}40 0%, transparent 40%)`, filter: 'blur(18px)' }} />
        <div style={{ ...abs, backgroundImage: 'linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px)', backgroundSize: '14px 14px' }} />
        {[0,1,2].map(i => <div key={i} style={{ position: 'absolute', width: 2, height: 2, borderRadius: '50%', background: `${t.g1}80`, left: `${15 + i * 28}%`, top: `${20 + i * 18}%`, boxShadow: `0 0 5px ${t.g1}` }} />)}
      </div>
    );
  }

  if (t.cat === 'product') {
    return (
      <div style={{ ...abs, background: t.bg }}>
        <div style={{ ...abs, opacity: 0.3, background: `radial-gradient(circle at 50% 40%, ${t.glow}40 0%, transparent 55%)`, filter: 'blur(20px)' }} />
        <div style={{ position: 'absolute', top: '14%', left: '50%', transform: 'translateX(-50%)', width: '44%', aspectRatio: '9/16', border: `2px solid ${t.frame}`, borderRadius: '10px', background: 'rgba(0,0,0,0.4)' }}>
          <div style={{ position: 'absolute', top: 0, left: '50%', transform: 'translateX(-50%)', width: '35%', height: 3, background: t.bg, borderRadius: '0 0 4px 4px' }} />
        </div>
        <div style={{ position: 'absolute', bottom: '10%', left: '50%', transform: 'translateX(-50%)', width: 20, height: 1, background: t.glow, opacity: 0.5 }} />
      </div>
    );
  }

  if (t.cat === 'kinetic') {
    return (
      <div style={{ ...abs, background: t.bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ fontSize: '20px', fontWeight: 900, color: t.fg, fontStyle: 'italic', lineHeight: 0.85, textAlign: 'center', letterSpacing: '-0.04em', textShadow: `2px 2px 0 ${t.fg === '#000' ? 'rgba(0,0,0,0.08)' : 'rgba(255,255,255,0.08)'}` }}>
          {t.word}
        </div>
        <div style={{ position: 'absolute', top: '8%', right: '8%', width: 4, height: 4, background: t.fg, opacity: 0.3 }} />
        <div style={{ position: 'absolute', bottom: '8%', left: '8%', width: 12, height: 1, background: t.fg, opacity: 0.2 }} />
      </div>
    );
  }

  if (t.cat === 'neon') {
    return (
      <div style={{ ...abs, background: '#000' }}>
        <div style={{ ...abs, backgroundImage: `repeating-linear-gradient(0deg, transparent, transparent 3px, ${t.c1}0d 3px, ${t.c1}0d 4px)` }} />
        <div style={{ position: 'absolute', top: 0, bottom: 0, left: '32%', width: 1.5, background: `linear-gradient(transparent, ${t.c1}, transparent)`, boxShadow: `0 0 10px ${t.c1}`, opacity: 0.8 }} />
        <div style={{ position: 'absolute', top: 0, bottom: 0, left: '68%', width: 1, background: `linear-gradient(transparent, ${t.c2}, transparent)`, boxShadow: `0 0 6px ${t.c2}`, opacity: 0.5 }} />
        <div style={{ position: 'absolute', top: '40%', left: '50%', transform: 'translate(-50%,-50%)', width: 10, height: 10, borderRadius: '50%', border: `1px solid ${t.nodeColor}40`, boxShadow: `0 0 8px ${t.nodeColor}30 inset` }} />
      </div>
    );
  }

  if (t.cat === 'cinematic') {
    return (
      <div style={{ ...abs, background: '#fff' }}>
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '45%', background: `linear-gradient(to bottom, ${t.lineColor}, transparent)` }} />
        <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: '45%', background: `linear-gradient(to top, ${t.lineColor}, transparent)` }} />
        <div style={{ position: 'absolute', top: '15%', left: '-15%', width: '130%', aspectRatio: '1', borderRadius: '50%', border: `12px solid ${t.lineColor}` }} />
        <div style={{ position: 'absolute', top: '10%', left: '8%', width: 10, height: 1, background: t.tint, opacity: 0.15 }} />
        <div style={{ position: 'absolute', top: '10%', left: '8%', width: 1, height: 10, background: t.tint, opacity: 0.15 }} />
      </div>
    );
  }

  return <div style={{ ...abs, background: '#222' }} />;
}

/* ══════════ Slide Thumbnail Component ══════════ */
function SlideThumb({ t }) {
  const abs = { position: 'absolute', inset: 0 };

  return (
    <div style={{ ...abs, background: t.bg, padding: '12% 10%', display: 'flex', flexDirection: 'column', justifyContent: 'center', overflow: 'hidden' }}>
      {t.cat === 'cyber' && <div style={{ ...abs, backgroundImage: `linear-gradient(${t.grid} 1px, transparent 1px), linear-gradient(90deg, ${t.grid} 1px, transparent 1px)`, backgroundSize: '10px 10px' }} />}
      {t.cat === 'corporate' && <div style={{ position: 'absolute', top: 0, left: 0, width: 3, height: '100%', background: t.bar }} />}
      {t.cat === 'clay' && <div style={{ position: 'absolute', top: '8%', right: '5%', width: '28%', height: '80%', background: t.card, borderRadius: '6px', boxShadow: '2px 2px 0 rgba(0,0,0,0.03)' }} />}
      
      <div style={{ fontSize: t.cat === 'brutalist' ? '11px' : t.cat === 'editorial' ? '10px' : '9px', fontWeight: t.cat === 'brutalist' ? 900 : t.cat === 'editorial' ? 400 : 700, color: t.title, textTransform: t.cat === 'brutalist' ? 'uppercase' : 'none', fontStyle: t.cat === 'editorial' ? 'italic' : 'normal', fontFamily: t.cat === 'editorial' ? 'Georgia, serif' : 'inherit', marginBottom: 4, textShadow: t.cat === 'cyber' ? `0 0 3px ${t.title}50` : 'none', position: 'relative', zIndex: 2, letterSpacing: t.cat === 'brutalist' ? '-0.02em' : '0' }}>Title</div>
      {t.cat === 'editorial' && <div style={{ width: '55%', height: 1, background: '#d6d3d1', marginBottom: 3, position: 'relative', zIndex: 2 }} />}
      {[0.55, 0.38].map((w, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 3, marginBottom: i === 0 ? 2 : 0, position: 'relative', zIndex: 2 }}>
          <div style={{ width: 3, height: 3, borderRadius: t.cat === 'brutalist' ? 0 : '50%', background: t.dot, flexShrink: 0 }} />
          <div style={{ height: 2, width: `${w * 100}%`, background: t.dot, borderRadius: 1, opacity: 0.25 }} />
        </div>
      ))}
    </div>
  );
}

export default function Header() {
  const location = useLocation();
  const [running, setRunning] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [campaignTopic, setCampaignTopic] = useState('');
  const [campaignLocation, setCampaignLocation] = useState('');
  const [customPrompt, setCustomPrompt] = useState('');
  const [videoDuration, setVideoDuration] = useState(15);
  const [videoTemplate, setVideoTemplate] = useState(VIDEO_TEMPLATES[0].id);
  const [presentationTemplate, setPresentationTemplate] = useState(PRES_TEMPLATES[0].id);
  const [graphicSize, setGraphicSize] = useState('both');
  const [pipelineState, setPipelineState] = useState(null);

  const title = pageTitles[location.pathname] || 'Marketing AI';

  const streamStatus = (runId) => {
    let eventSource = new EventSource(`http://127.0.0.1:8000/api/pipeline/stream/${runId}`);
    let retryCount = 0;
    const maxRetries = 30; // Allow up to 30 retries (15 minutes with 30s intervals)
    let lastActivity = Date.now();
    const maxInactiveTime = 15 * 60 * 1000; // 15 minutes timeout
    
    const reconnect = () => {
      if (retryCount >= maxRetries) {
        console.error("Max retries reached");
        eventSource.close();
        setPipelineState(prev => ({ ...prev, status: 'failed', message: 'Pipeline timed out after 15 minutes. Check gallery for results.' }));
        setRunning(false);
        return;
      }
      
      retryCount++;
      console.log(`SSE reconnect attempt ${retryCount}/${maxRetries}`);
      
      // Close old connection
      eventSource.close();
      
      // Wait 30 seconds before reconnecting
      setTimeout(() => {
        eventSource = new EventSource(`http://127.0.0.1:8000/api/pipeline/stream/${runId}`);
        
        eventSource.onmessage = handleMessage;
        eventSource.onerror = handleError;
      }, 30000);
    };
    
    const handleMessage = (event) => {
      lastActivity = Date.now(); // Reset activity timer
      retryCount = 0; // Reset retry count on successful message
      
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'end') {
          eventSource.close();
          setPipelineState(prev => ({ ...prev, status: 'completed', message: 'Pipeline completed successfully!' }));
          setTimeout(() => setPipelineState(null), 5000);
          setRunning(false);
        } else if (data.type === 'log') {
          // It's a live log from the agent council
          setPipelineState(prev => {
            const currentLogs = prev?.live_logs || [];
            // Parse agent name and message from the structured string
            const match = data.text.match(/^\[(.*?)\] (.*)/s);
            let agent = "System";
            let message = data.text;
            if (match) {
              agent = match[1];
              message = match[2];
            }
            return {
              ...prev,
              live_logs: [...currentLogs, { agent, message }]
            };
          });
        } else if (data.type === 'progress') {
          setPipelineState(prev => ({
            ...prev,
            step: data.step,
            message: data.message,
            total_steps: data.total_steps || prev.total_steps
          }));
        }
      } catch (err) {
        console.error("SSE parse error", err);
      }
    };

    const handleError = (err) => {
      console.warn("SSE connection error, will retry:", err);
      // Don't immediately fail - try to reconnect
      eventSource.close();
      reconnect();
    };
    
    eventSource.onmessage = handleMessage;
    eventSource.onerror = handleError;
    
    // Store eventSource reference for cleanup
    window._pipelineEventSource = eventSource;
  };

  const handleRunPipeline = async () => {
    if (running) return;
    setRunning(true);
    setShowModal(false);
    setPipelineState({ status: 'running', step: 0, total_steps: 5, message: 'Starting pipeline...' });
    try {
      const res = await api.triggerPipeline({
        campaign_topic: campaignTopic.trim() || null,
        location: campaignLocation.trim() || null,
        custom_prompt: customPrompt.trim() || null,
        video_duration_seconds: videoDuration,
        video_template_id: videoTemplate,
        presentation_template_id: presentationTemplate,
        graphic_size: graphicSize,
      });
      streamStatus(res.run_id);
    } catch (err) {
      console.error('Pipeline trigger failed:', err);
      setPipelineState({ status: 'failed', message: 'Failed to start pipeline' });
      setRunning(false);
      setTimeout(() => setPipelineState(null), 5000);
    }
  };

  const handlePurgeData = async () => {
    if (window.confirm("Delete ALL data?")) {
      try { await api.purgeDatabase(); window.location.reload(); }
      catch { alert('Failed.'); }
    }
  };

  const selectedVid = VIDEO_TEMPLATES.find(t => t.id === videoTemplate);
  const selectedSlide = PRES_TEMPLATES.find(t => t.id === presentationTemplate);
  const selectedDur = DURATION_OPTIONS.find(d => d.seconds === videoDuration);

  const cardStyle = (sel) => ({
    position: 'relative', aspectRatio: '9/14', borderRadius: '8px', overflow: 'hidden', cursor: 'pointer',
    border: sel ? '2px solid var(--accent-primary)' : '2px solid rgba(255,255,255,0.06)',
    boxShadow: sel ? '0 0 0 1px var(--accent-primary), 0 4px 16px rgba(0,0,0,0.35)' : '0 2px 8px rgba(0,0,0,0.2)',
    transition: 'all 0.15s ease', transform: sel ? 'scale(1.03)' : 'scale(1)',
  });

  const slideCardStyle = (sel) => ({
    ...cardStyle(sel), aspectRatio: '16/10',
  });

  const inputStyle = { width: '100%', padding: '9px 12px', background: 'var(--bg-secondary)', border: '1px solid var(--border-glass)', borderRadius: '8px', color: 'var(--text-primary)', fontFamily: 'var(--font-body)', fontSize: '13px', outline: 'none', boxSizing: 'border-box' };

  return (
    <>
      <header className="header" style={{ flexDirection: 'column', alignItems: 'stretch', padding: '0' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 32px', height: 'var(--header-height)' }}>
          <div><h1 className="header-title">{title}</h1></div>
          <div className="header-actions" style={{ display: 'flex', gap: '8px' }}>
            <button className="btn btn-ghost btn-sm" onClick={handlePurgeData} title="Purge" style={{ color: 'var(--text-muted)' }}><Trash2 size={16} /></button>
            <button className={`btn ${running ? 'btn-ghost' : 'btn-primary'} btn-sm`} onClick={() => !running && setShowModal(true)} disabled={running} id="run-pipeline-btn">
              <Zap size={14} />{running ? 'Pipeline Running...' : 'Run Pipeline'}
            </button>
          </div>
        </div>
        {pipelineState && (
          <div style={{ background: 'var(--bg-secondary)', borderTop: '1px solid var(--border-glass)', padding: '8px 32px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
              <span style={{ fontWeight: 600, color: pipelineState.status === 'failed' ? 'var(--error)' : 'var(--accent-secondary)' }}>{pipelineState.message || 'Processing...'}</span>
              <span style={{ color: 'var(--text-muted)' }}>{pipelineState.status === 'completed' || pipelineState.status === 'failed' ? pipelineState.status.toUpperCase() : `Step ${Math.max(1, pipelineState.step || 1)} / ${pipelineState.total_steps || 5}`}</span>
            </div>
            <div style={{ height: '4px', background: 'var(--bg-tertiary)', borderRadius: '2px', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${Math.min(100, ((pipelineState.step||0)/(pipelineState.total_steps||5))*100)}%`, background: pipelineState.status === 'failed' ? 'var(--error)' : 'var(--accent-gradient)', transition: 'width 0.5s ease-out' }} />
            </div>
            {pipelineState.live_logs?.length > 0 && (
              <div style={{ marginTop: '6px', padding: '8px 12px', background: 'rgba(0,0,0,0.2)', borderRadius: '6px', border: '1px solid var(--border-glass)', maxHeight: '120px', overflowY: 'auto', fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--accent-primary)', marginBottom: '4px', fontWeight: 600 }}><Terminal size={12} />Live LLM Engine</div>
                {pipelineState.live_logs.slice(-10).map((log, i) => (
                  <div key={i} style={{ display: 'flex', gap: '8px' }}><span style={{ color: 'var(--accent-secondary)', textTransform: 'uppercase', minWidth: '80px' }}>[{log.agent.replace('_',' ')}]</span><span style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', color: 'var(--text-primary)' }}>{log.message}</span></div>
                ))}
              </div>
            )}
          </div>
        )}
      </header>

      {/* ═══════════════ MODAL ═══════════════ */}
      {showModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 2000 }} onClick={() => setShowModal(false)}>
          <div onClick={e => e.stopPropagation()} style={{ display: 'flex', width: '95vw', maxWidth: '1400px', height: '92vh', borderRadius: '20px', overflow: 'hidden', border: '1px solid var(--border-glass)', boxShadow: '0 40px 80px rgba(0,0,0,0.6)' }}>

            {/* LEFT — Config */}
            <div style={{ width: '340px', minWidth: '300px', background: 'var(--bg-primary)', borderRight: '1px solid var(--border-glass)', padding: '22px 20px', overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h2 style={{ margin: 0, fontSize: '16px', fontWeight: 700 }}><Zap size={14} style={{ marginRight: 5, color: 'var(--accent-primary)', verticalAlign: 'text-bottom' }} />Launch Campaign</h2>
                <button onClick={() => setShowModal(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}><X size={16} /></button>
              </div>

              <label style={{ fontSize: '11px', fontWeight: 600, marginBottom: '4px', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 4 }}><Tag size={11} style={{ color: 'var(--accent-primary)' }} />Campaign Theme</label>
              <input type="text" value={campaignTopic} onChange={e => setCampaignTopic(e.target.value)} placeholder="e.g. Black Friday, Product Launch..." style={{ ...inputStyle, marginBottom: '10px' }} />

              <label style={{ fontSize: '11px', fontWeight: 600, marginBottom: '4px', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 4 }}><MapPin size={11} style={{ color: 'var(--accent-secondary)' }} />Target Location</label>
              <input type="text" value={campaignLocation} onChange={e => setCampaignLocation(e.target.value)} placeholder="e.g. US, Nepal, Japan..." style={{ ...inputStyle, marginBottom: '10px' }} />

              {/* Custom Prompt / Brief */}
              <label style={{ fontSize: '11px', fontWeight: 600, marginBottom: '4px', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 4 }}><FileText size={11} style={{ color: 'var(--accent-primary)' }} />Custom Brief / Prompt</label>
              <textarea value={customPrompt} onChange={e => setCustomPrompt(e.target.value)} placeholder="Add extra context, product details, or creative direction for the AI agents..." rows={3}
                style={{ ...inputStyle, resize: 'vertical', marginBottom: '12px', minHeight: '60px', fontFamily: 'var(--font-body)' }}
              />
              <p style={{ fontSize: '10px', color: 'var(--text-muted)', marginBottom: '14px', lineHeight: 1.4 }}>
                This context is injected into every AI agent alongside brand & competitor data.
              </p>

              <div style={{ height: 1, background: 'var(--border-glass)', marginBottom: '14px' }} />

              {/* Video Duration */}
              <label style={{ fontSize: '11px', fontWeight: 700, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: 4, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}><Clock size={11} />Video Duration</label>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '6px', marginBottom: '14px' }}>
                {DURATION_OPTIONS.map(d => (
                  <button key={d.seconds} onClick={() => setVideoDuration(d.seconds)}
                    style={{
                      padding: '8px 4px', borderRadius: '8px', border: videoDuration === d.seconds ? '2px solid var(--accent-primary)' : '1px solid var(--border-glass)',
                      background: videoDuration === d.seconds ? 'rgba(74,222,128,0.08)' : 'var(--bg-secondary)', cursor: 'pointer', textAlign: 'center',
                      color: videoDuration === d.seconds ? 'var(--accent-primary)' : 'var(--text-secondary)',
                    }}>
                    <div style={{ fontSize: '14px', fontWeight: 800 }}>{d.label}</div>
                    <div style={{ fontSize: '8px', opacity: 0.7, marginTop: 1 }}>{d.scenes} scene{d.scenes > 1 ? 's' : ''}</div>
                    <div style={{ fontSize: '7px', opacity: 0.5, marginTop: 1 }}>{d.desc}</div>
                  </button>
                ))}
              </div>

              <div style={{ height: 1, background: 'var(--border-glass)', marginBottom: '14px' }} />

              {/* Graphic Size */}
              <label style={{ fontSize: '11px', fontWeight: 700, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: 4, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}><Image size={11} />Graphics Size</label>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '6px', marginBottom: '14px' }}>
                {['square', 'portrait', 'both'].map(size => (
                  <button key={size} onClick={() => setGraphicSize(size)}
                    style={{
                      padding: '8px 4px', borderRadius: '8px', border: graphicSize === size ? '2px solid var(--accent-secondary)' : '1px solid var(--border-glass)',
                      background: graphicSize === size ? 'rgba(56,189,248,0.08)' : 'var(--bg-secondary)', cursor: 'pointer', textAlign: 'center',
                      color: graphicSize === size ? 'var(--accent-secondary)' : 'var(--text-secondary)',
                      textTransform: 'capitalize'
                    }}>
                    <div style={{ fontSize: '12px', fontWeight: 700 }}>{size}</div>
                  </button>
                ))}
              </div>

              <div style={{ height: 1, background: 'var(--border-glass)', marginBottom: '14px' }} />

              {/* Selected summary */}
              <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 700, marginBottom: '6px' }}>Selected</div>
              <div style={{ padding: '8px 10px', background: 'var(--bg-secondary)', borderRadius: '8px', marginBottom: '6px', border: '1px solid var(--border-glass)', fontSize: '11px' }}>
                <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>🎬 {selectedVid?.name}</span>
                <span style={{ color: 'var(--text-muted)', marginLeft: 6 }}>{selectedDur?.label} · {selectedDur?.scenes} scenes</span>
              </div>
              <div style={{ padding: '8px 10px', background: 'var(--bg-secondary)', borderRadius: '8px', marginBottom: '14px', border: '1px solid var(--border-glass)', fontSize: '11px' }}>
                <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>📊 {selectedSlide?.name}</span>
              </div>

              <div style={{ flex: 1 }} />
              <div style={{ display: 'flex', gap: '8px' }}>
                <button className="btn btn-ghost btn-sm" onClick={() => setShowModal(false)} style={{ flex: 1 }}>Cancel</button>
                <button className="btn btn-primary" onClick={handleRunPipeline} style={{ flex: 2, padding: '11px 14px' }}>
                  <Zap size={13} />{campaignTopic.trim() ? `Launch "${campaignTopic.trim()}"` : 'Launch Campaign'}
                </button>
              </div>
            </div>

            {/* RIGHT — Template Gallery */}
            <div style={{ flex: 1, background: '#0e0e11', overflowY: 'auto', padding: '22px 28px' }}>
              <div style={{ fontSize: '11px', fontWeight: 700, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '0.14em', marginBottom: '20px' }}>● Choose Your Templates</div>

              {/* VIDEO */}
              <div style={{ marginBottom: '28px' }}>
                <div style={{ fontSize: '14px', fontWeight: 700, color: '#fff', marginBottom: '4px' }}>🎬 Video Templates</div>
                <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.35)', marginBottom: '16px' }}>Select a motion graphics style for your {selectedDur?.label} vertical video</div>
                {[
                  { label: 'Mesh Abstract', prefix: 'mesh_abstract' },
                  { label: 'Product Showcase', prefix: 'product_showcase' },
                  { label: 'Kinetic Typography', prefix: 'kinetic_typography' },
                  { label: 'Neon Circuit', prefix: 'neon_circuit' },
                  { label: 'Cinematic Fade', prefix: 'cinematic_fade' },
                ].map(group => (
                  <div key={group.prefix} style={{ marginBottom: '18px' }}>
                    <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.25)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '8px', fontWeight: 600 }}>{group.label}</div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '8px' }}>
                      {VIDEO_TEMPLATES.filter(t => t.id.startsWith(group.prefix)).map(t => (
                        <div key={t.id}>
                          <div onClick={() => setVideoTemplate(t.id)} style={cardStyle(videoTemplate === t.id)}>
                            <VideoThumb t={t} />
                            {videoTemplate === t.id && <div style={{ position: 'absolute', top: 3, right: 3, width: 14, height: 14, borderRadius: '50%', background: 'var(--accent-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '8px', color: '#fff', zIndex: 5 }}>✓</div>}
                          </div>
                          <div style={{ fontSize: '8px', color: videoTemplate === t.id ? 'var(--accent-primary)' : 'rgba(255,255,255,0.3)', fontWeight: videoTemplate === t.id ? 700 : 400, textAlign: 'center', marginTop: '3px', cursor: 'pointer' }} onClick={() => setVideoTemplate(t.id)}>{t.name}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              <div style={{ height: 1, background: 'rgba(255,255,255,0.05)', marginBottom: '24px' }} />

              {/* SLIDES */}
              <div>
                <div style={{ fontSize: '14px', fontWeight: 700, color: '#fff', marginBottom: '4px' }}>📊 Slide Templates</div>
                <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.35)', marginBottom: '16px' }}>Select a presentation design for your campaign deck</div>
                {[
                  { label: 'Clay Minimal', prefix: 'clay_minimal' },
                  { label: 'Dark Brutalist', prefix: 'dark_brutalist' },
                  { label: 'Neon Cyber', prefix: 'neon_cyber' },
                  { label: 'Editorial Print', prefix: 'editorial_print' },
                  { label: 'Clean Corporate', prefix: 'clean_corporate' },
                ].map(group => (
                  <div key={group.prefix} style={{ marginBottom: '18px' }}>
                    <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.25)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '8px', fontWeight: 600 }}>{group.label}</div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '8px' }}>
                      {PRES_TEMPLATES.filter(t => t.id.startsWith(group.prefix)).map(t => (
                        <div key={t.id}>
                          <div onClick={() => setPresentationTemplate(t.id)} style={{ ...slideCardStyle(presentationTemplate === t.id), borderRadius: t.cat === 'brutalist' ? 0 : '8px' }}>
                            <SlideThumb t={t} />
                            {presentationTemplate === t.id && <div style={{ position: 'absolute', top: 3, right: 3, width: 14, height: 14, borderRadius: '50%', background: 'var(--accent-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '8px', color: '#fff', zIndex: 5 }}>✓</div>}
                          </div>
                          <div style={{ fontSize: '8px', color: presentationTemplate === t.id ? 'var(--accent-primary)' : 'rgba(255,255,255,0.3)', fontWeight: presentationTemplate === t.id ? 700 : 400, textAlign: 'center', marginTop: '3px', cursor: 'pointer' }} onClick={() => setPresentationTemplate(t.id)}>{t.name}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
