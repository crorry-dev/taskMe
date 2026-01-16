/**
 * API Service functions for CommitQuest
 * Typed API calls for all endpoints
 */
import api from './api';

// ============ Auth ============
export const authService = {
  login: (email, password) => 
    api.post('/auth/login/', { email, password }),
  
  register: (data) => 
    api.post('/auth/register/', data),
  
  refreshToken: (refreshToken) => 
    api.post('/auth/token/refresh/', { refresh: refreshToken }),
  
  getProfile: () => 
    api.get('/auth/profile/'),
  
  updateProfile: (data) => 
    api.patch('/auth/profile/', data),
};

// ============ Challenges ============
export const challengeService = {
  list: (params = {}) => 
    api.get('/challenges/', { params }),
  
  get: (id) => 
    api.get(`/challenges/${id}/`),
  
  create: (data) => 
    api.post('/challenges/', data),
  
  update: (id, data) => 
    api.patch(`/challenges/${id}/`, data),
  
  delete: (id) => 
    api.delete(`/challenges/${id}/`),
  
  join: (id) => 
    api.post(`/challenges/${id}/join/`),
  
  leave: (id) => 
    api.post(`/challenges/${id}/leave/`),
  
  getContributions: (challengeId) => 
    api.get(`/contributions/`, { params: { challenge: challengeId } }),
  
  addContribution: (challengeId, data) => 
    api.post(`/contributions/`, { challenge_id: challengeId, ...data }),
  
  getLeaderboard: (challengeId) =>
    api.get(`/challenges/${challengeId}/leaderboard/`),
  
  getMyChallenges: () => 
    api.get('/challenges/my_challenges/'),
};

// ============ Proofs ============
export const proofService = {
  list: (params = {}) => 
    api.get('/proofs/', { params }),
  
  get: (id) => 
    api.get(`/proofs/${id}/`),
  
  create: (data) => {
    const formData = new FormData();
    Object.keys(data).forEach(key => {
      if (data[key] !== undefined && data[key] !== null) {
        formData.append(key, data[key]);
      }
    });
    return api.post('/proofs/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  review: (proofId, data) => 
    api.post(`/proofs/${proofId}/review/`, data),
  
  getPendingReviews: () => 
    api.get('/proofs/pending_reviews/'),
};

// ============ Rewards ============
export const rewardService = {
  getProgress: () => 
    api.get('/rewards/progress/'),
  
  getBadges: () => 
    api.get('/rewards/badges/'),
  
  getEarnedBadges: () => 
    api.get('/rewards/badges/earned/'),
  
  getEvents: (params = {}) => 
    api.get('/rewards/events/', { params }),
  
  getStreaks: () => 
    api.get('/rewards/streaks/'),
  
  getLeaderboard: (type = 'global', limit = 50) => 
    api.get('/rewards/leaderboard/', { params: { type, limit } }),
};

// ============ Teams ============
export const teamService = {
  list: (params = {}) => 
    api.get('/teams/', { params }),
  
  get: (id) => 
    api.get(`/teams/${id}/`),
  
  create: (data) => 
    api.post('/teams/', data),
  
  update: (id, data) => 
    api.patch(`/teams/${id}/`, data),
  
  delete: (id) => 
    api.delete(`/teams/${id}/`),
  
  join: (id) => 
    api.post(`/teams/${id}/join/`),
  
  leave: (id) => 
    api.post(`/teams/${id}/leave/`),
  
  getMembers: (id) => 
    api.get(`/teams/${id}/members/`),
  
  invite: (id, userId) => 
    api.post(`/teams/${id}/invite/`, { user_id: userId }),
  
  getMyTeams: () => 
    api.get('/teams/my_teams/'),
};

// ============ Tasks (Simple Todos) ============
export const taskService = {
  list: (params = {}) => 
    api.get('/tasks/', { params }),
  
  get: (id) => 
    api.get(`/tasks/${id}/`),
  
  create: (data) => 
    api.post('/tasks/', data),
  
  update: (id, data) => 
    api.patch(`/tasks/${id}/`, data),
  
  delete: (id) => 
    api.delete(`/tasks/${id}/`),
  
  complete: (id) => 
    api.post(`/tasks/${id}/complete/`),
};

// ============ Notifications ============
export const notificationService = {
  list: (params = {}) => 
    api.get('/notifications/', { params }),
  
  getUnreadCount: () => 
    api.get('/notifications/unread_count/'),
  
  markRead: (id) => 
    api.post(`/notifications/${id}/mark_read/`),
  
  markAllRead: () => 
    api.post('/notifications/mark_all_read/'),
  
  clearAll: () => 
    api.delete('/notifications/clear_all/'),
  
  getPreferences: () => 
    api.get('/notifications/preferences/'),
  
  updatePreferences: (data) => 
    api.patch('/notifications/preferences/', data),
};

const apiServices = {
  auth: authService,
  challenges: challengeService,
  proofs: proofService,
  rewards: rewardService,
  teams: teamService,
  tasks: taskService,
  notifications: notificationService,
};

export default apiServices;
