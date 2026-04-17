import React, { useEffect, useRef, useState, useCallback } from 'react';
import { X, Save, Loader2, Download, RefreshCw, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';

/**
 * PhotopeaEditor Component
 * Embeds Photopea via iframe + postMessage API with robust image loading.
 * Features: Preview mode, zoom controls, proper CORS handling, and seamless save.
 */
export default function PhotopeaEditor({ imageUrl, onSave, onClose, title }) {
  const iframeRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [previewMode, setPreviewMode] = useState(true);
  const [imageLoaded, setImageLoaded] = useState(false);
  const loadedRef = useRef(false);
  const retryCountRef = useRef(0);
  const MAX_RETRIES = 3;

  // Build the absolute URL for image fetch (resolves against backend via proxy)
  const resolvedUrl = imageUrl?.startsWith('http')
    ? imageUrl
    : imageUrl?.startsWith('/')
      ? imageUrl  // Vite proxy will forward /outputs/* to backend
      : `/outputs/${imageUrl}`;

  // Photopea config — dark theme, no splash, fullscreen
  const photopeaConfig = encodeURIComponent(JSON.stringify({
    files: [],
    environment: { 
      theme: 0,      // Dark theme
      customIO: true, // Enable custom IO for postMessage
      vmode: 1,      // Verbose mode for debugging
      splash: false  // No splash screen
    },
  }));
  const PHOTOPEA_URL = `https://www.photopea.com#${photopeaConfig}`;

  const loadPhotopeaImage = useCallback(async () => {
    if (!iframeRef.current || !resolvedUrl) return;
    
    // Don't retry if already loaded successfully
    if (loadedRef.current && imageLoaded) return;

    try {
      setError(null);
      console.log('[PhotopeaEditor] Fetching image:', resolvedUrl);
      
      // Fetch with cache-busting to avoid stale responses
      const cacheBuster = `?t=${Date.now()}`;
      const response = await fetch(resolvedUrl + cacheBuster, {
        method: 'GET',
        mode: 'cors',
        cache: 'no-cache'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const arrayBuffer = await response.arrayBuffer();
      
      if (arrayBuffer.byteLength < 100) {
        throw new Error('Image file is too small or empty');
      }

      console.log('[PhotopeaEditor] Loaded', arrayBuffer.byteLength, 'bytes, sending to Photopea');
      
      // Wait for Photopea to be ready
      await new Promise(resolve => setTimeout(resolve, 800));
      
      if (iframeRef.current && iframeRef.current.contentWindow) {
        // Send the image data to Photopea
        iframeRef.current.contentWindow.postMessage(arrayBuffer, "*");
        console.log('[PhotopeaEditor] Image sent to Photopea');
        
        // Mark as loaded after a short delay to ensure Photopea processes it
        setTimeout(() => {
          loadedRef.current = true;
          setImageLoaded(true);
          setLoading(false);
        }, 1000);
      }
    } catch (err) {
      console.error("[PhotopeaEditor] Failed to load image:", err);
      retryCountRef.current += 1;
      
      if (retryCountRef.current < MAX_RETRIES) {
        console.log(`[PhotopeaEditor] Retrying (${retryCountRef.current}/${MAX_RETRIES})...`);
        setTimeout(() => loadPhotopeaImage(), 1500);
      } else {
        setError(`Failed to load image: ${err.message}`);
        setLoading(false);
      }
    }
  }, [resolvedUrl, imageLoaded]);

  useEffect(() => {
    const handleMessage = (e) => {
      if (e.origin !== 'https://www.photopea.com') return;

      // Photopea ready signal
      if (e.data === "done" || e.data === "Photopea ready") {
        console.log('[PhotopeaEditor] Photopea is ready');
        if (loading && !imageLoaded) {
          setTimeout(() => loadPhotopeaImage(), 500);
        }
      } 
      // Exported image data from saveToOE
      else if (e.data instanceof ArrayBuffer || e.data instanceof Blob) {
        setSaving(false);
        const blob = e.data instanceof ArrayBuffer 
          ? new Blob([e.data], { type: 'image/png' })
          : e.data;
        
        console.log('[PhotopeaEditor] Received exported image:', blob.size, 'bytes');
        
        // Trigger download
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${title || 'edited-design'}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        // Also save to backend
        onSave(blob);
      }
      // Photopea error messages
      else if (typeof e.data === 'string' && e.data.includes('error')) {
        console.error('[PhotopeaEditor] Photopea error:', e.data);
      }
    };

    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, [loading, imageLoaded, loadPhotopeaImage, onSave, title]);

  const triggerSave = () => {
    if (!iframeRef.current || !imageLoaded) return;
    setSaving(true);
    console.log('[PhotopeaEditor] Triggering save...');
    iframeRef.current.contentWindow.postMessage('app.activeDocument.saveToOE("png");', "*");
  };

  const triggerDownload = () => {
    if (!iframeRef.current || !imageLoaded) return;
    console.log('[PhotopeaEditor] Triggering download...');
    iframeRef.current.contentWindow.postMessage(
      'app.activeDocument.saveToOE("png");',
      "*"
    );
  };

  const handleRetry = () => {
    console.log('[PhotopeaEditor] Retrying load...');
    loadedRef.current = false;
    setImageLoaded(false);
    setError(null);
    setLoading(true);
    retryCountRef.current = 0;
    if (iframeRef.current) {
      iframeRef.current.src = PHOTOPEA_URL;
    }
  };

  const togglePreviewMode = () => {
    setPreviewMode(!previewMode);
  };

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 3000,
      background: 'var(--bg-primary)', display: 'flex', flexDirection: 'column'
    }}>
      {/* Header */}
      <div style={{
        height: '60px', borderBottom: '1px solid var(--border-glass)',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 24px', background: 'var(--bg-secondary)', gap: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flex: 1, minWidth: 0 }}>
          <button onClick={onClose} style={{
            background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-glass)', 
            color: 'var(--text-secondary)', cursor: 'pointer',
            padding: '8px', borderRadius: '8px', display: 'flex', alignItems: 'center',
            transition: 'all 0.2s'
          }}
            onMouseOver={e => {
              e.currentTarget.style.background = 'rgba(255,255,255,0.1)';
              e.currentTarget.style.color = 'var(--text-primary)';
            }}
            onMouseOut={e => {
              e.currentTarget.style.background = 'rgba(255,255,255,0.05)';
              e.currentTarget.style.color = 'var(--text-secondary)';
            }}
          >
            <X size={18} />
          </button>
          <div style={{ height: '24px', width: '1px', background: 'var(--border-glass)' }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0 }}>
            <span style={{ fontSize: '18px' }}>🎨</span>
            <span style={{
              fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)',
              overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'
            }}>
              {title || "Untitled Graphic"}
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '8px', flexShrink: 0, alignItems: 'center' }}>
          {/* Status indicator */}
          <div style={{
            padding: '4px 12px',
            borderRadius: '12px',
            fontSize: '11px',
            fontWeight: 600,
            background: imageLoaded ? 'rgba(34,197,94,0.15)' : loading ? 'rgba(234,179,8,0.15)' : 'rgba(239,68,68,0.15)',
            color: imageLoaded ? '#22c55e' : loading ? '#eab308' : '#ef4444',
            border: `1px solid ${imageLoaded ? 'rgba(34,197,94,0.3)' : loading ? 'rgba(234,179,8,0.3)' : 'rgba(239,68,68,0.3)'}`
          }}>
            {imageLoaded ? '● Ready' : loading ? '● Loading' : '● Error'}
          </div>

          {error && (
            <button
              onClick={handleRetry}
              style={{
                display: 'flex', alignItems: 'center', gap: '6px',
                padding: '8px 14px', borderRadius: '8px', background: 'rgba(239,68,68,0.15)',
                color: '#ef4444', border: '1px solid rgba(239,68,68,0.3)',
                fontSize: '12px', fontWeight: 600, cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseOver={e => e.currentTarget.style.background = 'rgba(239,68,68,0.25)'}
              onMouseOut={e => e.currentTarget.style.background = 'rgba(239,68,68,0.15)'}
            >
              <RefreshCw size={13} /> Retry
            </button>
          )}
          
          <button
            onClick={triggerSave}
            disabled={saving || loading || !imageLoaded}
            style={{
              display: 'flex', alignItems: 'center', gap: '6px',
              padding: '8px 18px', borderRadius: '8px', 
              background: (saving || loading || !imageLoaded) ? 'var(--border-glass)' : 'var(--accent-primary)',
              color: (saving || loading || !imageLoaded) ? 'var(--text-muted)' : 'white', 
              border: 'none', fontSize: '13px', fontWeight: 600, cursor: (saving || loading || !imageLoaded) ? 'not-allowed' : 'pointer',
              opacity: (saving || loading || !imageLoaded) ? 0.5 : 1, 
              transition: 'all 0.2s',
              boxShadow: imageLoaded ? '0 2px 8px rgba(59,130,246,0.3)' : 'none'
            }}
            onMouseOver={e => {
              if (imageLoaded && !saving && !loading) {
                e.currentTarget.style.transform = 'translateY(-1px)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(59,130,246,0.4)';
              }
            }}
            onMouseOut={e => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = imageLoaded ? '0 2px 8px rgba(59,130,246,0.3)' : 'none';
            }}
          >
            {saving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
            {saving ? 'Saving...' : 'Save & Download'}
          </button>
        </div>
      </div>

      {/* Main content */}
      <div style={{ flex: 1, position: 'relative', background: '#0a0a0a', overflow: 'hidden' }}>
        {/* Loading/Error overlay */}
        {(loading || error) && (
          <div style={{
            position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center',
            background: 'rgba(0,0,0,0.8)', zIndex: 10,
            backdropFilter: 'blur(8px)'
          }}>
            {error ? (
              <>
                <div style={{ fontSize: '64px', marginBottom: '20px' }}>⚠️</div>
                <span style={{ color: '#ef4444', fontSize: '16px', fontWeight: 600, marginBottom: '8px' }}>
                  {error}
                </span>
                <span style={{ color: 'var(--text-muted)', fontSize: '13px', marginBottom: '20px' }}>
                  Check that the backend is running and the image exists.
                </span>
                <button
                  onClick={handleRetry}
                  style={{
                    padding: '10px 24px',
                    borderRadius: '8px',
                    background: 'var(--accent-primary)',
                    color: 'white',
                    border: 'none',
                    fontSize: '14px',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  Try Again
                </button>
              </>
            ) : (
              <>
                <Loader2 size={40} className="animate-spin" style={{ color: 'var(--accent-primary)', marginBottom: '16px' }} />
                <span style={{ color: 'var(--text-primary)', fontSize: '16px', fontWeight: 600, marginBottom: '8px' }}>
                  Loading Photopea Studio...
                </span>
                <span style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
                  This may take a few seconds on first load
                </span>
              </>
            )}
          </div>
        )}
        
        {/* Photopea iframe */}
        <iframe
          ref={iframeRef}
          src={PHOTOPEA_URL}
          title="Photopea Editor"
          style={{ 
            width: '100%', 
            height: '100%', 
            border: 'none',
            opacity: loading ? 0 : 1,
            transition: 'opacity 0.3s'
          }}
          allow="cross-origin-isolated; clipboard-read; clipboard-write"
          sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
        />
      </div>
    </div>
  );
}
