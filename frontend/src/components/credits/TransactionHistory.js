/**
 * TransactionHistory Component
 * 
 * Displays a list of credit transactions with filtering.
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Skeleton,
  ToggleButtonGroup,
  ToggleButton,
  Divider,
} from '@mui/material';
import {
  Add,
  Remove,
  EmojiEvents,
  PlaylistAddCheck,
  LocalFireDepartment,
  Handshake,
  WorkspacePremium,
  PersonAdd,
  AdminPanelSettings,
  Replay,
} from '@mui/icons-material';
import { creditService } from '../../services';

// Map transaction types to icons and colors
const transactionConfig = {
  // Earning types
  signup_bonus: { icon: PersonAdd, color: 'success', label: 'Willkommensbonus' },
  challenge_complete: { icon: EmojiEvents, color: 'success', label: 'Challenge abgeschlossen' },
  task_complete: { icon: PlaylistAddCheck, color: 'success', label: 'Aufgabe erledigt' },
  streak_milestone: { icon: LocalFireDepartment, color: 'warning', label: 'Streak Milestone' },
  duel_won: { icon: EmojiEvents, color: 'success', label: 'Duel gewonnen' },
  peer_review: { icon: Handshake, color: 'info', label: 'Peer Review' },
  badge_earned: { icon: WorkspacePremium, color: 'secondary', label: 'Badge verdient' },
  referral_bonus: { icon: PersonAdd, color: 'success', label: 'Empfehlungsbonus' },
  admin_grant: { icon: AdminPanelSettings, color: 'primary', label: 'Admin Bonus' },
  refund: { icon: Replay, color: 'info', label: 'Rückerstattung' },
  
  // Spending types
  challenge_create: { icon: Remove, color: 'error', label: 'Challenge erstellt' },
  task_create: { icon: Remove, color: 'error', label: 'Aufgabe erstellt' },
  duel_stake: { icon: Remove, color: 'error', label: 'Duel Einsatz' },
  feature_unlock: { icon: Remove, color: 'error', label: 'Feature freigeschaltet' },
  admin_deduct: { icon: AdminPanelSettings, color: 'error', label: 'Admin Abzug' },
  expiry: { icon: Remove, color: 'error', label: 'Verfallen' },
};

const TransactionItem = ({ transaction }) => {
  const config = transactionConfig[transaction.transaction_type] || {
    icon: transaction.amount > 0 ? Add : Remove,
    color: transaction.amount > 0 ? 'success' : 'error',
    label: transaction.transaction_type_display || transaction.transaction_type,
  };

  const Icon = config.icon;
  const isPositive = transaction.amount > 0;

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return 'Heute';
    } else if (diffDays === 1) {
      return 'Gestern';
    } else if (diffDays < 7) {
      return `Vor ${diffDays} Tagen`;
    } else {
      return date.toLocaleDateString('de-DE', { 
        day: '2-digit', 
        month: '2-digit',
        year: '2-digit'
      });
    }
  };

  return (
    <ListItem
      sx={{
        borderRadius: 2,
        mb: 1,
        bgcolor: 'background.paper',
        border: '1px solid',
        borderColor: 'divider',
      }}
    >
      <ListItemIcon>
        <Box
          sx={{
            width: 40,
            height: 40,
            borderRadius: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            bgcolor: `${config.color}.50`,
          }}
        >
          <Icon sx={{ color: `${config.color}.main` }} />
        </Box>
      </ListItemIcon>
      <ListItemText
        primary={
          <Typography variant="body2" fontWeight={500}>
            {transaction.description || config.label}
          </Typography>
        }
        secondary={formatDate(transaction.created_at)}
      />
      <Box sx={{ textAlign: 'right' }}>
        <Typography
          variant="body1"
          fontWeight={600}
          color={isPositive ? 'success.main' : 'error.main'}
        >
          {isPositive ? '+' : ''}{transaction.amount.toLocaleString('de-DE')}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {transaction.balance_after.toLocaleString('de-DE')} Credits
        </Typography>
      </Box>
    </ListItem>
  );
};

const TransactionHistory = ({ limit = 10, showFilter = true }) => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // 'all' | 'earning' | 'spending'

  useEffect(() => {
    loadTransactions();
  }, [filter]);

  const loadTransactions = async () => {
    setLoading(true);
    try {
      const options = {};
      if (filter === 'earning') options.direction = 'earning';
      if (filter === 'spending') options.direction = 'spending';

      const data = await creditService.getTransactions(options);
      // Handle paginated response
      const txList = Array.isArray(data) ? data : data.results || [];
      setTransactions(txList.slice(0, limit));
    } catch (error) {
      console.error('Failed to load transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box>
        {[...Array(3)].map((_, i) => (
          <Skeleton 
            key={i} 
            variant="rectangular" 
            height={72} 
            sx={{ borderRadius: 2, mb: 1 }} 
          />
        ))}
      </Box>
    );
  }

  return (
    <Box>
      {showFilter && (
        <Box sx={{ mb: 2 }}>
          <ToggleButtonGroup
            value={filter}
            exclusive
            onChange={(e, val) => val && setFilter(val)}
            size="small"
            fullWidth
          >
            <ToggleButton value="all">Alle</ToggleButton>
            <ToggleButton value="earning">
              <Add sx={{ fontSize: 16, mr: 0.5 }} />
              Einnahmen
            </ToggleButton>
            <ToggleButton value="spending">
              <Remove sx={{ fontSize: 16, mr: 0.5 }} />
              Ausgaben
            </ToggleButton>
          </ToggleButtonGroup>
        </Box>
      )}

      {transactions.length === 0 ? (
        <Box 
          sx={{ 
            textAlign: 'center', 
            py: 4, 
            color: 'text.secondary' 
          }}
        >
          <Typography>Noch keine Transaktionen</Typography>
        </Box>
      ) : (
        <List disablePadding>
          {transactions.map((tx) => (
            <TransactionItem key={tx.id} transaction={tx} />
          ))}
        </List>
      )}
    </Box>
  );
};

export default TransactionHistory;
