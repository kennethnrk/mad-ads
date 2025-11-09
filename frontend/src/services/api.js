/**
 * API Service
 * Centralized API calls to backend
 */

import { API_ENDPOINTS } from '../config/api';

/**
 * Get stored auth token from localStorage
 */
const getAuthToken = () => {
  return localStorage.getItem('authToken');
};

/**
 * Generic API request handler
 */
async function apiRequest(endpoint, options = {}) {
  const token = getAuthToken();
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  // Add Authorization header if token exists
  if (token) {
    defaultOptions.headers['Authorization'] = `Bearer ${token}`;
  }

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

/**
 * Test Snowflake query
 * @param {Object} queryData - { query, params? }
 */
export const testSnowflakeQuery = async (queryData) => {
  return apiRequest(API_ENDPOINTS.SNOWFLAKE_QUERY, {
    method: 'POST',
    body: JSON.stringify(queryData),
  });
};

/**
 * Test Snowflake vector search
 * @param {Object} searchData - { text, k?, columns?, filter_obj? }
 */
export const testSnowflakeVectorSearch = async (searchData) => {
  return apiRequest(API_ENDPOINTS.SNOWFLAKE_VECTOR_SEARCH, {
    method: 'POST',
    body: JSON.stringify(searchData),
  });
};

/**
 * Process video and find matching ads
 * @param {File} videoFile - Video file to upload
 * @param {Object} options - { model_size?, limit? }
 */
export const processVideoAndMatch = async (videoFile, options = {}) => {
  console.log('[API] Processing video and finding matches', { 
    fileName: videoFile.name, 
    fileSize: videoFile.size,
    options 
  });
  
  const formData = new FormData();
  formData.append('file', videoFile);
  if (options.model_size) formData.append('model_size', options.model_size);
  if (options.limit) formData.append('limit', options.limit.toString());
  
  try {
    const response = await fetch(API_ENDPOINTS.VIDEO_PROCESS_AND_MATCH, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      console.error('[API] Video processing failed:', errorData);
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    console.log('[API] Video processing successful', { 
      success: result.success,
      adsFound: result.count,
      transcriptionLength: result.transcription?.text?.length 
    });
    return result;
  } catch (error) {
    console.error('[API] Video processing error:', error);
    throw error;
  }
};

/**
 * Insert ads into video at specified timestamps
 * @param {Array} placements - Array of {timestamp: number, adId?: string} objects
 */
export const insertAdIntoVideo = async (placements) => {
  console.log('[API] Inserting ads into video', { placements });
  
  if (!placements || placements.length === 0) {
    throw new Error('At least one placement is required');
  }
  
  try {
    const response = await fetch(API_ENDPOINTS.VIDEO_INSERT_AD, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        placements: placements.map(p => ({
          timestamp: p.timestamp,
          ad_id: p.adId || null,
        })),
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      console.error('[API] Ad insertion failed:', errorData);
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    console.log('[API] Ad insertion successful', { 
      success: result.success,
      outputPath: result.output_video_path,
      previewUrl: result.preview_url
    });
    return result;
  } catch (error) {
    console.error('[API] Ad insertion error:', error);
    throw error;
  }
};

/**
 * Register a new user
 * @param {Object} userData - { email, password, type }
 */
export const registerUser = async (userData) => {
  return apiRequest(API_ENDPOINTS.REGISTER, {
    method: 'POST',
    body: JSON.stringify(userData),
  });
};

/**
 * Login user
 * @param {Object} credentials - { username (email), password }
 */
export const loginUser = async (credentials) => {
  const formData = new URLSearchParams();
  formData.append('username', credentials.email || credentials.username);
  formData.append('password', credentials.password);

  const response = await fetch(API_ENDPOINTS.LOGIN, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  // Store token in localStorage
  if (data.access_token) {
    localStorage.setItem('authToken', data.access_token);
  }
  return data;
};

/**
 * Get current user info
 */
export const getCurrentUser = async () => {
  return apiRequest(API_ENDPOINTS.ME);
};

/**
 * Logout user (clear token)
 */
export const logoutUser = () => {
  localStorage.removeItem('authToken');
};

/**
 * Get products list
 * @param {Object} params - { skip?, limit?, company_id?, category?, is_active? }
 */
export const getProducts = async (params = {}) => {
  const queryParams = new URLSearchParams();
  if (params.skip !== undefined) queryParams.append('skip', params.skip);
  if (params.limit !== undefined) queryParams.append('limit', params.limit);
  if (params.company_id) queryParams.append('company_id', params.company_id);
  if (params.category) queryParams.append('category', params.category);
  if (params.is_active !== undefined) queryParams.append('is_active', params.is_active);
  
  const endpoint = `${API_ENDPOINTS.PRODUCTS}${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
  return apiRequest(endpoint, {
    method: 'GET',
  });
};

/**
 * Upload an ad video file
 * @param {Object} adData - { file, owner_id, product_id, title, description, tags? }
 */
export const uploadAd = async (adData) => {
  const { file, owner_id, product_id, title, description, tags } = adData;
  
  if (!file || !owner_id || !product_id || !title || !description) {
    throw new Error('Missing required fields: file, owner_id, product_id, title, and description are required');
  }
  
  const formData = new FormData();
  formData.append('file', file);
  formData.append('owner_id', owner_id);
  formData.append('product_id', product_id);
  formData.append('title', title);
  formData.append('description', description);
  if (tags) {
    formData.append('tags', tags);
  }
  
  try {
    const response = await fetch(API_ENDPOINTS.AD_UPLOAD, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('[API] Ad upload failed:', error);
    throw error;
  }
};

