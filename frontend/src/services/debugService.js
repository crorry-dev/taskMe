/**
 * Debug Feedback Service
 * 
 * API service for debug/QA feedback system.
 */
import api from './api';

const debugService = {
  /**
   * Submit new debug feedback
   */
  submitFeedback: async (data) => {
    const formData = new FormData();
    
    if (data.text_input) {
      formData.append('text_input', data.text_input);
    }
    if (data.voice_memo) {
      formData.append('voice_memo', data.voice_memo);
    }
    if (data.page_url) {
      formData.append('page_url', data.page_url);
    }
    if (data.screenshot) {
      formData.append('screenshot', data.screenshot);
    }
    if (data.browser_info) {
      formData.append('browser_info', JSON.stringify(data.browser_info));
    }
    
    const response = await api.post('/debug/feedback/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  /**
   * Get list of feedback
   */
  getFeedbackList: async (params = {}) => {
    const response = await api.get('/debug/feedback/', { params });
    return response.data;
  },

  /**
   * Get single feedback detail
   */
  getFeedback: async (id) => {
    const response = await api.get(`/debug/feedback/${id}/`);
    return response.data;
  },

  /**
   * Trigger re-analysis of feedback
   */
  analyzeFeedback: async (id) => {
    const response = await api.post(`/debug/feedback/${id}/analyze/`);
    return response.data;
  },

  /**
   * Approve and implement changes (admin only)
   */
  approveFeedback: async (id, data = {}) => {
    const response = await api.post(`/debug/feedback/${id}/approve/`, data);
    return response.data;
  },

  /**
   * Reject feedback (admin only)
   */
  rejectFeedback: async (id) => {
    const response = await api.post(`/debug/feedback/${id}/reject/`);
    return response.data;
  },

  /**
   * Get feedback comments
   */
  getComments: async (feedbackId) => {
    const response = await api.get(`/debug/feedback/${feedbackId}/comments/`);
    return response.data;
  },

  /**
   * Add comment to feedback
   */
  addComment: async (feedbackId, text) => {
    const response = await api.post(`/debug/feedback/${feedbackId}/comments/`, { text });
    return response.data;
  },

  /**
   * Get debug config
   */
  getConfig: async () => {
    const response = await api.get('/debug/config/');
    return response.data;
  },

  /**
   * Update debug config (admin only)
   */
  updateConfig: async (data) => {
    const response = await api.post('/debug/config/', data);
    return response.data;
  },

  /**
   * Get debug stats (admin only)
   */
  getStats: async () => {
    const response = await api.get('/debug/stats/');
    return response.data;
  },

  /**
   * Get browser info for feedback context
   */
  getBrowserInfo: () => {
    return {
      userAgent: navigator.userAgent,
      language: navigator.language,
      platform: navigator.platform,
      screenWidth: window.screen.width,
      screenHeight: window.screen.height,
      windowWidth: window.innerWidth,
      windowHeight: window.innerHeight,
      timestamp: new Date().toISOString(),
    };
  },
};

export default debugService;
