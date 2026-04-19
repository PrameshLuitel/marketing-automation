/**
 * API client for the Marketing Automation backend.
 */

const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }
    return await response.json();
  } catch (err) {
    console.error(`API Error [${endpoint}]:`, err);
    throw err;
  }
}

export const api = {
  // Health
  health: () => request('/health'),

  // Dashboard
  getDashboardSummary: () => request('/dashboard/summary'),

  // Pipeline
  triggerPipeline: (opts = {}) => request('/pipeline/run', {
    method: 'POST',
    body: JSON.stringify({
      campaign_topic: opts.campaign_topic || null,
      location: opts.location || null,
      custom_prompt: opts.custom_prompt || null,
      video_duration_seconds: opts.video_duration_seconds || 15,
      video_template_id: opts.video_template_id || null,
      presentation_template_id: opts.presentation_template_id || null,
    }),
  }),
  getPipelineStatus: (runId) => request(`/pipeline/status/${runId}`),
  deletePipelineRun: (runId) => request(`/pipeline/runs/${runId}`, { method: 'DELETE' }),

  // Database
  purgeDatabase: () => request('/database/purge', { method: 'DELETE' }),

  // Campaigns
  getCampaigns: (status = null) => {
    const params = status ? `?status=${status}` : '';
    return request(`/campaigns${params}`);
  },
  getCampaign: (id) => request(`/campaigns/${id}`),
  campaignAction: (id, action) =>
    request(`/campaigns/${id}/action`, {
      method: 'POST',
      body: JSON.stringify({ action }),
    }),
  getVideoProgress: (campaignId) => request(`/campaigns/${campaignId}/video-progress`),

  // Gallery
  getGallery: () => request('/gallery'),

  // Trends & Pulse
  getTrends: () => request('/trends'),
  getWorldPulse: () => request('/world-pulse'),

  // Logs
  getLogs: () => request('/logs'),

  // LLM Usage
  getLLMUsage: () => request('/llm-usage'),

  // Search
  search: (query) =>
    request('/search', {
      method: 'POST',
      body: JSON.stringify({ query, n_results: 20 }),
    }),

  // Scheduler
  getJobs: () => request('/scheduler/jobs'),

  // Upload & Update
  uploadAsset: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('Upload failed');
      return await response.json();
    } catch (err) {
      console.error('Upload Error:', err);
      throw err;
    }
  },
  updateAsset: async (assetId, blob) => {
    const formData = new FormData();
    formData.append('file', blob, 'edited_design.png');
    formData.append('asset_id', assetId);
    try {
      const response = await fetch(`${API_BASE}/assets/update`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('Update failed');
      return await response.json();
    } catch (err) {
      console.error('Update Error:', err);
      throw err;
    }
  },

  // Company Profile
  getProfile: () => request('/profile'),
  updateProfile: (data) =>
    request('/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // Templates
  getTemplates: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.type) params.append('type', filters.type);
    if (filters.category) params.append('category', filters.category);
    if (filters.limit) params.append('limit', filters.limit);
    return request(`/templates?${params.toString()}`);
  },
  getPopularTemplates: (limit = 20) => request(`/templates/popular?limit=${limit}`),
  getTemplate: (id) => request(`/templates/${id}`),
  useTemplate: (id) => request(`/templates/${id}/use`, { method: 'POST' }),
  getBackgrounds: (category = null) => {
    const params = category ? `?category=${category}` : '';
    return request(`/templates/backgrounds${params}`);
  },
};
