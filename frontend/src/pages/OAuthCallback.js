import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Container,
  Box,
  CircularProgress,
  Typography,
  Alert,
  Button,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

/**
 * OAuth callback handler.
 * Processes the callback from social auth providers.
 */
const OAuthCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Get the auth code and state from URL params
        const code = searchParams.get('code');
        const state = searchParams.get('state');
        const errorParam = searchParams.get('error');
        const errorDescription = searchParams.get('error_description');

        if (errorParam) {
          setError(errorDescription || `Authentication failed: ${errorParam}`);
          setLoading(false);
          return;
        }

        if (!code) {
          setError('No authorization code received');
          setLoading(false);
          return;
        }

        // Extract provider from the current path or state
        const pathParts = window.location.pathname.split('/');
        const provider = pathParts[pathParts.indexOf('callback') - 1] || 'unknown';

        // Exchange the code for tokens
        const response = await api.post(`/auth/social/${provider}/callback/`, {
          code,
          state,
        });

        if (response.data.access_token) {
          // Store the tokens
          localStorage.setItem('access_token', response.data.access_token);
          if (response.data.refresh_token) {
            localStorage.setItem('refresh_token', response.data.refresh_token);
          }

          // Fetch user profile
          const userResponse = await api.get('/auth/profile/');
          localStorage.setItem('user', JSON.stringify(userResponse.data));

          // Redirect to the saved location or dashboard
          const redirectPath = localStorage.getItem('social_auth_redirect') || '/dashboard';
          localStorage.removeItem('social_auth_redirect');
          navigate(redirectPath);
        } else {
          throw new Error('No access token in response');
        }
      } catch (err) {
        console.error('OAuth callback error:', err);
        setError(
          err.response?.data?.detail ||
          err.message ||
          'Authentication failed. Please try again.'
        );
      } finally {
        setLoading(false);
      }
    };

    handleCallback();
  }, [searchParams, navigate, login]);

  if (loading) {
    return (
      <Container maxWidth="sm">
        <Box
          sx={{
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 2,
          }}
        >
          <CircularProgress size={48} />
          <Typography variant="h6" color="text.secondary">
            Completing sign in...
          </Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="sm">
        <Box
          sx={{
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 3,
          }}
        >
          <Alert severity="error" sx={{ width: '100%' }}>
            {error}
          </Alert>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              onClick={() => navigate('/login')}
            >
              Back to Login
            </Button>
            <Button
              variant="outlined"
              onClick={() => window.location.reload()}
            >
              Try Again
            </Button>
          </Box>
        </Box>
      </Container>
    );
  }

  return null;
};

export default OAuthCallback;
