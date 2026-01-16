/**
 * Voice Memo Service
 * 
 * Handles all voice memo (TaskMeMemo) related API calls.
 */
import api from './api';

const voiceMemoService = {
  /**
   * Upload a new voice memo
   * @param {File} audioFile - The audio file to upload
   * @param {number} duration - Duration in seconds
   */
  upload: async (audioFile, duration = null) => {
    const formData = new FormData();
    formData.append('audio_file', audioFile);
    if (duration) {
      formData.append('duration_seconds', duration);
    }
    
    const response = await api.post('/voice-memos/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Get all voice memos for the current user
   */
  list: async () => {
    const response = await api.get('/voice-memos/');
    return response.data;
  },

  /**
   * Get a specific voice memo
   * @param {number} id - Voice memo ID
   */
  get: async (id) => {
    const response = await api.get(`/voice-memos/${id}/`);
    return response.data;
  },

  /**
   * Process a voice memo (transcribe and parse)
   * @param {number} id - Voice memo ID
   */
  process: async (id) => {
    const response = await api.post(`/voice-memos/${id}/process/`);
    return response.data;
  },

  /**
   * Create a challenge from a parsed voice memo
   * @param {number} id - Voice memo ID
   * @param {Object} overrides - Optional overrides for parsed data
   */
  createChallenge: async (id, overrides = {}) => {
    const response = await api.post(`/voice-memos/${id}/create_challenge/`, overrides);
    return response.data;
  },

  /**
   * Dismiss a voice memo
   * @param {number} id - Voice memo ID
   */
  dismiss: async (id) => {
    const response = await api.post(`/voice-memos/${id}/dismiss/`);
    return response.data;
  },

  /**
   * Delete a voice memo
   * @param {number} id - Voice memo ID
   */
  delete: async (id) => {
    const response = await api.delete(`/voice-memos/${id}/`);
    return response.data;
  },
};

export default voiceMemoService;
