/**
 * CreditBalance Component
 * 
 * Displays the user's current credit balance.
 * Can be used in header, dashboard, or anywhere balance visibility is needed.
 */
import React from 'react';
import { Box, Typography, Skeleton, Tooltip, Chip } from '@mui/material';
import { AccountBalanceWallet, TrendingUp, TrendingDown } from '@mui/icons-material';

const CreditBalance = ({ 
  balance = 0, 
  loading = false, 
  variant = 'default', // 'default' | 'compact' | 'detailed'
  showIcon = true,
  lifetimeEarned = null,
  lifetimeSpent = null,
  onClick = null,
}) => {
  if (loading) {
    return (
      <Skeleton 
        variant="rectangular" 
        width={variant === 'compact' ? 80 : 120} 
        height={32} 
        sx={{ borderRadius: 2 }}
      />
    );
  }

  // Compact version for header/navbar
  if (variant === 'compact') {
    return (
      <Tooltip title="Dein Credit-Guthaben">
        <Chip
          icon={showIcon ? <AccountBalanceWallet sx={{ fontSize: 16 }} /> : undefined}
          label={`${balance.toLocaleString('de-DE')}`}
          color="primary"
          variant="outlined"
          size="small"
          onClick={onClick}
          sx={{ 
            cursor: onClick ? 'pointer' : 'default',
            fontWeight: 600,
            '&:hover': onClick ? { backgroundColor: 'primary.light', color: 'primary.contrastText' } : {},
          }}
        />
      </Tooltip>
    );
  }

  // Detailed version with lifetime stats
  if (variant === 'detailed') {
    return (
      <Box
        onClick={onClick}
        sx={{
          p: 2.5,
          borderRadius: 3,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          cursor: onClick ? 'pointer' : 'default',
          transition: 'transform 0.2s, box-shadow 0.2s',
          '&:hover': onClick ? {
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 24px rgba(102, 126, 234, 0.4)',
          } : {},
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
          {showIcon && <AccountBalanceWallet sx={{ fontSize: 28 }} />}
          <Typography variant="h4" fontWeight={700}>
            {balance.toLocaleString('de-DE')}
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.9 }}>
            Credits
          </Typography>
        </Box>
        
        {(lifetimeEarned !== null || lifetimeSpent !== null) && (
          <Box sx={{ display: 'flex', gap: 3, mt: 1.5 }}>
            {lifetimeEarned !== null && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <TrendingUp sx={{ fontSize: 16, opacity: 0.9 }} />
                <Typography variant="caption" sx={{ opacity: 0.9 }}>
                  +{lifetimeEarned.toLocaleString('de-DE')} verdient
                </Typography>
              </Box>
            )}
            {lifetimeSpent !== null && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <TrendingDown sx={{ fontSize: 16, opacity: 0.9 }} />
                <Typography variant="caption" sx={{ opacity: 0.9 }}>
                  -{lifetimeSpent.toLocaleString('de-DE')} ausgegeben
                </Typography>
              </Box>
            )}
          </Box>
        )}
      </Box>
    );
  }

  // Default version
  return (
    <Box
      onClick={onClick}
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        p: 1.5,
        borderRadius: 2,
        bgcolor: 'primary.50',
        border: '1px solid',
        borderColor: 'primary.200',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.2s',
        '&:hover': onClick ? {
          bgcolor: 'primary.100',
          borderColor: 'primary.300',
        } : {},
      }}
    >
      {showIcon && (
        <AccountBalanceWallet sx={{ color: 'primary.main', fontSize: 24 }} />
      )}
      <Box>
        <Typography variant="h6" fontWeight={600} color="primary.main">
          {balance.toLocaleString('de-DE')}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Credits
        </Typography>
      </Box>
    </Box>
  );
};

export default CreditBalance;
