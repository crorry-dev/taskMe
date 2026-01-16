import React from 'react';
import { Box, Button, Typography, Divider } from '@mui/material';
import GoogleIcon from '@mui/icons-material/Google';
import AppleIcon from '@mui/icons-material/Apple';
import FacebookIcon from '@mui/icons-material/Facebook';

// Backend URL for social auth
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Social authentication buttons component.
 * Provides Google, Apple, and Facebook login options.
 */
const SocialAuthButtons = ({ mode = 'login' }) => {
  const actionText = mode === 'login' ? 'Sign in' : 'Sign up';

  /**
   * Initiate OAuth flow by redirecting to backend.
   * The backend handles the OAuth provider redirect.
   */
  const handleSocialLogin = (provider) => {
    // Store the current URL to redirect back after auth
    localStorage.setItem('social_auth_redirect', window.location.pathname);
    
    // Redirect to backend OAuth endpoint
    // allauth handles the OAuth flow and redirects back
    window.location.href = `${API_BASE_URL}/api/auth/social/${provider}/login/`;
  };

  const socialButtons = [
    {
      provider: 'google',
      label: `${actionText} with Google`,
      icon: <GoogleIcon />,
      color: '#4285F4',
      hoverColor: '#357ABD',
    },
    {
      provider: 'apple',
      label: `${actionText} with Apple`,
      icon: <AppleIcon />,
      color: '#000000',
      hoverColor: '#333333',
    },
    {
      provider: 'facebook',
      label: `${actionText} with Facebook`,
      icon: <FacebookIcon />,
      color: '#1877F2',
      hoverColor: '#166FE5',
    },
  ];

  return (
    <Box sx={{ width: '100%' }}>
      <Divider sx={{ my: 3 }}>
        <Typography variant="body2" color="text.secondary">
          or continue with
        </Typography>
      </Divider>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
        {socialButtons.map(({ provider, label, icon, color, hoverColor }) => (
          <Button
            key={provider}
            fullWidth
            variant="outlined"
            startIcon={icon}
            onClick={() => handleSocialLogin(provider)}
            aria-label={label}
            sx={{
              py: 1.2,
              borderColor: color,
              color: color,
              textTransform: 'none',
              fontSize: '0.95rem',
              fontWeight: 500,
              '&:hover': {
                borderColor: hoverColor,
                backgroundColor: `${color}10`,
              },
            }}
          >
            {label}
          </Button>
        ))}
      </Box>

      <Typography
        variant="caption"
        color="text.secondary"
        sx={{ display: 'block', textAlign: 'center', mt: 2 }}
      >
        By continuing, you agree to our{' '}
        <a href="/terms" style={{ color: 'inherit' }}>
          Terms of Service
        </a>{' '}
        and{' '}
        <a href="/privacy" style={{ color: 'inherit' }}>
          Privacy Policy
        </a>
      </Typography>
    </Box>
  );
};

export default SocialAuthButtons;
