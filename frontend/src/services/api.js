/**
 * API Service
 * Centralized API calls to backend
 */

import { API_ENDPOINTS } from '../config/api';

/**
 * Generic API request handler
 */
async function apiRequest(endpoint, options = {}) {
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const config = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(endpoint, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

/**
 * Health check
 */
export const checkHealth = async () => {
  return apiRequest(API_ENDPOINTS.HEALTH);
};

/**
 * Match content to ads
 * @param {Object} matchData - { content_id, ad_pool_id?, brief?, limit? }
 */
export const matchContent = async (matchData) => {
  return apiRequest(API_ENDPOINTS.MATCH, {
    method: 'POST',
    body: JSON.stringify(matchData),
  });
};

/**
 * Generate ad variants
 * @param {Object} generateData - To be defined
 */
export const generateVariants = async (generateData) => {
  return apiRequest(API_ENDPOINTS.GENERATE, {
    method: 'POST',
    body: JSON.stringify(generateData),
  });
};

/**
 * Text to speech
 * @param {Object} ttsData - { text, voice? }
 */
export const textToSpeech = async (ttsData) => {
  return apiRequest(API_ENDPOINTS.TTS, {
    method: 'POST',
    body: JSON.stringify(ttsData),
  });
};

/**
 * Optimize campaign
 * @param {Object} optimizeData - To be defined
 */
export const optimizeCampaign = async (optimizeData) => {
  return apiRequest(API_ENDPOINTS.OPTIMIZE, {
    method: 'POST',
    body: JSON.stringify(optimizeData),
  });
};

/**
 * Create or update campaign
 * @param {Object} campaignData - To be defined
 */
export const upsertCampaign = async (campaignData) => {
  return apiRequest(API_ENDPOINTS.CAMPAIGNS, {
    method: 'POST',
    body: JSON.stringify(campaignData),
  });
};

/**
 * Start metrics simulation
 * @param {string} campaignId - Campaign ID
 */
export const startMetricsSimulation = async (campaignId) => {
  return apiRequest(API_ENDPOINTS.METRICS_SIMULATE, {
    method: 'POST',
    body: JSON.stringify({ campaign_id: campaignId }),
  });
};

/**
 * Stream metrics (SSE)
 * @param {string} token - Stream token from startMetricsSimulation
 */
export const streamMetrics = (token) => {
  const eventSource = new EventSource(`${API_ENDPOINTS.METRICS_STREAM}?token=${token}`);
  return eventSource;
};

