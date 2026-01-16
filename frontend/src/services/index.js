import api from './api';

export const authService = {
  register: async (userData) => {
    const response = await api.post('/auth/register/', userData);
    return response.data;
  },

  login: async (email, password) => {
    const response = await api.post('/auth/login/', { email, password });
    const { access, refresh } = response.data;
    
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/profile/');
    return response.data;
  },

  updateProfile: async (profileData) => {
    const response = await api.put('/auth/profile/', profileData);
    return response.data;
  },

  changePassword: async (passwordData) => {
    const response = await api.post('/auth/profile/change-password/', passwordData);
    return response.data;
  },

  getLeaderboard: async () => {
    const response = await api.get('/auth/leaderboard/');
    return response.data;
  },
};

export const taskService = {
  getTasks: async (filters = {}) => {
    const response = await api.get('/tasks/', { params: filters });
    return response.data;
  },

  getTask: async (id) => {
    const response = await api.get(`/tasks/${id}/`);
    return response.data;
  },

  createTask: async (taskData) => {
    const response = await api.post('/tasks/', taskData);
    return response.data;
  },

  updateTask: async (id, taskData) => {
    const response = await api.put(`/tasks/${id}/`, taskData);
    return response.data;
  },

  deleteTask: async (id) => {
    const response = await api.delete(`/tasks/${id}/`);
    return response.data;
  },

  completeTask: async (id) => {
    const response = await api.post(`/tasks/${id}/complete/`);
    return response.data;
  },

  submitProof: async (id, proofData) => {
    const formData = new FormData();
    Object.keys(proofData).forEach((key) => {
      if (proofData[key]) {
        formData.append(key, proofData[key]);
      }
    });

    const response = await api.post(`/tasks/${id}/submit_proof/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export const proofService = {
  getProofs: async () => {
    const response = await api.get('/proofs/');
    return response.data;
  },

  getProof: async (id) => {
    const response = await api.get(`/proofs/${id}/`);
    return response.data;
  },

  approveProof: async (id) => {
    const response = await api.post(`/proofs/${id}/approve/`);
    return response.data;
  },

  rejectProof: async (id, rejectionReason) => {
    const response = await api.post(`/proofs/${id}/reject/`, {
      rejection_reason: rejectionReason,
    });
    return response.data;
  },
};
