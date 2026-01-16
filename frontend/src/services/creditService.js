/**
 * Credit Economy Service
 * 
 * Handles all credit-related API calls.
 */
import api from './api';

const creditService = {
  /**
   * Get current user's wallet details
   */
  getWallet: async () => {
    const response = await api.get('/rewards/credits/');
    return response.data;
  },

  /**
   * Get current balance (quick check)
   * @param {number} checkAmount - Optional amount to check affordability
   */
  getBalance: async (checkAmount = null) => {
    const params = checkAmount ? { check_amount: checkAmount } : {};
    const response = await api.get('/rewards/credits/balance/', { params });
    return response.data;
  },

  /**
   * Get transaction history
   * @param {Object} options - Filter options
   * @param {string} options.type - Transaction type filter
   * @param {string} options.direction - 'earning' or 'spending'
   * @param {number} options.page - Page number for pagination
   */
  getTransactions: async (options = {}) => {
    const response = await api.get('/rewards/credits/transactions/', { params: options });
    return response.data;
  },

  /**
   * Calculate the cost of creating a challenge
   * @param {string} challengeType - Type of challenge
   * @param {string} proofType - Type of proof required
   */
  calculateCost: async (challengeType, proofType = null) => {
    const response = await api.post('/rewards/credits/cost/', {
      challenge_type: challengeType,
      proof_type: proofType,
    });
    return response.data;
  },

  /**
   * Get current credit economy configuration
   */
  getConfig: async () => {
    const response = await api.get('/rewards/credits/config/');
    return response.data;
  },

  /**
   * Check if user can afford an amount
   * @param {number} amount - Amount to check
   */
  canAfford: async (amount) => {
    const result = await creditService.getBalance(amount);
    return result.can_afford;
  },

  /**
   * Add credits to user wallet (purchase/bonus)
   * @param {number} amount - Amount to add
   * @param {string} reason - Reason for adding credits
   */
  addCredits: async (amount, reason = 'Credit-Kauf') => {
    const response = await api.post('/rewards/credits/add/', {
      amount,
      reason,
    });
    return response.data;
  },
};

export default creditService;
