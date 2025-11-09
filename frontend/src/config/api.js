/**
 * API Configuration
 * Centralized configuration for backend API endpoints
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Health check
  HEALTH: `${API_BASE_URL}/api/v1/health`,
  
  // Authentication endpoints
  REGISTER: `${API_BASE_URL}/register`,
  LOGIN: `${API_BASE_URL}/token`,
  ME: `${API_BASE_URL}/me`,
  
  // Match endpoint
  MATCH: `${API_BASE_URL}/api/v1/match`,
  
  // Generate endpoint (to be implemented)
  GENERATE: `${API_BASE_URL}/api/v1/generate`,
  
  // TTS endpoint (to be implemented)
  TTS: `${API_BASE_URL}/api/v1/tts`,
  
  // Optimize endpoint (to be implemented)
  OPTIMIZE: `${API_BASE_URL}/api/v1/optimize`,
  
  // Campaigns endpoint (to be implemented)
  CAMPAIGNS: `${API_BASE_URL}/api/v1/campaigns`,
  
  // Metrics endpoints (to be implemented)
  METRICS_SIMULATE: `${API_BASE_URL}/api/v1/metrics/simulate`,
  METRICS_STREAM: `${API_BASE_URL}/api/v1/metrics/stream`,
  
  // Snowflake test endpoints
  SNOWFLAKE_QUERY: `${API_BASE_URL}/api/v1/snowflake/query`,
  SNOWFLAKE_VECTOR_SEARCH: `${API_BASE_URL}/api/v1/snowflake/vector-search`,
  
  // Video processing endpoints
  VIDEO_PROCESS_AND_MATCH: `${API_BASE_URL}/api/v1/video/process-and-match`,
  TRANSCRIBE: `${API_BASE_URL}/api/v1/transcribe`,

  PRODUCTS: `${API_BASE_URL}/api/v1/products`,
};

export default API_BASE_URL;

