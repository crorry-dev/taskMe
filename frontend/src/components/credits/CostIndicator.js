/**
 * CostIndicator Component
 * 
 * Shows the credit cost for creating challenges/tasks.
 * Includes affordability check and warning states.
 */
import React from 'react';
import { Box, Typography, Tooltip, Chip } from '@mui/material';
import { 
  AccountBalanceWallet, 
  Warning, 
  CheckCircle,
  Info,
} from '@mui/icons-material';

const CostIndicator = ({
  cost,
  currentBalance,
  showBalance = false,
  variant = 'default', // 'default' | 'inline' | 'detailed'
  breakdown = null, // { baseCost, proofCost } for detailed view
}) => {
  const canAfford = currentBalance >= cost;
  const isLow = canAfford && currentBalance < cost * 2;

  // Inline variant for forms
  if (variant === 'inline') {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Chip
          size="small"
          icon={<AccountBalanceWallet sx={{ fontSize: 14 }} />}
          label={`${cost} Credits`}
          color={canAfford ? 'primary' : 'error'}
          variant="outlined"
        />
        {!canAfford && (
          <Tooltip title="Du hast nicht genügend Credits">
            <Warning sx={{ fontSize: 16, color: 'error.main' }} />
          </Tooltip>
        )}
        {showBalance && (
          <Typography variant="caption" color="text.secondary">
            (Guthaben: {currentBalance})
          </Typography>
        )}
      </Box>
    );
  }

  // Detailed variant with breakdown
  if (variant === 'detailed' && breakdown) {
    return (
      <Box
        sx={{
          p: 2,
          borderRadius: 2,
          bgcolor: canAfford ? 'grey.50' : 'error.50',
          border: '1px solid',
          borderColor: canAfford ? 'grey.200' : 'error.200',
        }}
      >
        <Typography variant="subtitle2" fontWeight={600} gutterBottom>
          Kosten
        </Typography>
        
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="body2" color="text.secondary">
              Basis
            </Typography>
            <Typography variant="body2">
              {breakdown.baseCost} Credits
            </Typography>
          </Box>
          
          {breakdown.proofCost > 0 && (
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2" color="text.secondary">
                Proof-Typ
              </Typography>
              <Typography variant="body2">
                +{breakdown.proofCost} Credits
              </Typography>
            </Box>
          )}
          
          <Box 
            sx={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              pt: 1,
              mt: 1,
              borderTop: '1px solid',
              borderColor: 'divider',
            }}
          >
            <Typography variant="body1" fontWeight={600}>
              Gesamt
            </Typography>
            <Typography variant="body1" fontWeight={600} color="primary.main">
              {cost} Credits
            </Typography>
          </Box>
        </Box>

        <Box 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 1, 
            mt: 2,
            p: 1.5,
            borderRadius: 1,
            bgcolor: canAfford ? 'success.50' : 'error.100',
          }}
        >
          {canAfford ? (
            <>
              <CheckCircle sx={{ fontSize: 18, color: 'success.main' }} />
              <Typography variant="body2" color="success.dark">
                Ausreichend Guthaben ({currentBalance} Credits)
              </Typography>
            </>
          ) : (
            <>
              <Warning sx={{ fontSize: 18, color: 'error.main' }} />
              <Typography variant="body2" color="error.dark">
                Nicht genügend Credits ({currentBalance} von {cost} benötigt)
              </Typography>
            </>
          )}
        </Box>
      </Box>
    );
  }

  // Default variant
  return (
    <Tooltip 
      title={
        canAfford 
          ? `Diese Aktion kostet ${cost} Credits`
          : `Du benötigst ${cost} Credits, hast aber nur ${currentBalance}`
      }
    >
      <Box
        sx={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 0.75,
          px: 1.5,
          py: 0.75,
          borderRadius: 2,
          bgcolor: canAfford ? (isLow ? 'warning.50' : 'primary.50') : 'error.50',
          border: '1px solid',
          borderColor: canAfford ? (isLow ? 'warning.200' : 'primary.200') : 'error.200',
        }}
      >
        <AccountBalanceWallet 
          sx={{ 
            fontSize: 18, 
            color: canAfford ? (isLow ? 'warning.main' : 'primary.main') : 'error.main' 
          }} 
        />
        <Typography 
          variant="body2" 
          fontWeight={600}
          color={canAfford ? (isLow ? 'warning.dark' : 'primary.main') : 'error.main'}
        >
          {cost} Credits
        </Typography>
        {!canAfford && (
          <Warning sx={{ fontSize: 16, color: 'error.main' }} />
        )}
        {isLow && canAfford && (
          <Info sx={{ fontSize: 16, color: 'warning.main' }} />
        )}
      </Box>
    </Tooltip>
  );
};

export default CostIndicator;
