/**
 * Wallet Page
 * 
 * Full wallet view with balance, transactions, and economy info.
 */
import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Paper,
  Grid,
  Skeleton,
  Card,
  CardContent,
  Divider,
  Alert,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Snackbar,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Savings,
  Info,
  AddCircle,
  ShoppingCart,
} from '@mui/icons-material';
import { CreditBalance, TransactionHistory } from '../components/credits';
import { creditService } from '../services';

const StatCard = ({ icon: Icon, label, value, color = 'primary', loading }) => (
  <Card 
    elevation={0} 
    sx={{ 
      height: '100%',
      border: '1px solid',
      borderColor: 'divider',
    }}
  >
    <CardContent>
      {loading ? (
        <Skeleton variant="rectangular" height={60} />
      ) : (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: `${color}.50`,
            }}
          >
            <Icon sx={{ color: `${color}.main`, fontSize: 24 }} />
          </Box>
          <Box>
            <Typography variant="h5" fontWeight={700}>
              {typeof value === 'number' ? value.toLocaleString('de-DE') : value}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {label}
            </Typography>
          </Box>
        </Box>
      )}
    </CardContent>
  </Card>
);

const Wallet = () => {
  const [wallet, setWallet] = useState(null);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [buyDialogOpen, setBuyDialogOpen] = useState(false);
  const [creditAmount, setCreditAmount] = useState(100);
  const [purchasing, setPurchasing] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // Credit packages for purchase
  const creditPackages = [
    { amount: 50, price: '4,99 €', popular: false },
    { amount: 100, price: '8,99 €', popular: true },
    { amount: 250, price: '19,99 €', popular: false },
    { amount: 500, price: '34,99 €', popular: false },
    { amount: 1000, price: '59,99 €', popular: false },
  ];

  useEffect(() => {
    loadWalletData();
  }, []);

  const loadWalletData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [walletData, configData] = await Promise.all([
        creditService.getWallet(),
        creditService.getConfig(),
      ]);
      setWallet(walletData);
      setConfig(configData);
    } catch (err) {
      console.error('Failed to load wallet:', err);
      setError('Wallet konnte nicht geladen werden');
    } finally {
      setLoading(false);
    }
  };

  const handleBuyCredits = async (amount) => {
    setPurchasing(true);
    try {
      // In production, this would integrate with a payment provider
      // For now, we simulate adding credits (admin only in real app)
      await creditService.addCredits(amount, 'Credit-Kauf');
      await loadWalletData();
      setBuyDialogOpen(false);
      setSnackbar({ 
        open: true, 
        message: `${amount} Credits erfolgreich hinzugefügt!`, 
        severity: 'success' 
      });
    } catch (err) {
      console.error('Failed to buy credits:', err);
      setSnackbar({ 
        open: true, 
        message: 'Kauf fehlgeschlagen. Bitte später erneut versuchen.', 
        severity: 'error' 
      });
    } finally {
      setPurchasing(false);
    }
  };

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Wallet
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Verwalte deine Credits und sieh deine Transaktionshistorie ein.
          </Typography>
        </Box>
        <Button
          variant="contained"
          size="large"
          startIcon={<AddCircle />}
          onClick={() => setBuyDialogOpen(true)}
          sx={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            px: 3,
            py: 1.5,
            '&:hover': {
              background: 'linear-gradient(135deg, #5a6fd6 0%, #6a4290 100%)',
            },
          }}
        >
          Credits kaufen
        </Button>
      </Box>

      {/* Main Balance Card */}
      <Box sx={{ mb: 4 }}>
        <CreditBalance
          balance={wallet?.balance || 0}
          loading={loading}
          variant="detailed"
          lifetimeEarned={wallet?.lifetime_earned}
          lifetimeSpent={wallet?.lifetime_spent}
        />
      </Box>

      {/* Stats Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={4}>
          <StatCard
            icon={TrendingUp}
            label="Gesamt verdient"
            value={wallet?.lifetime_earned || 0}
            color="success"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <StatCard
            icon={TrendingDown}
            label="Gesamt ausgegeben"
            value={wallet?.lifetime_spent || 0}
            color="error"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <StatCard
            icon={Savings}
            label="Netto-Bilanz"
            value={(wallet?.lifetime_earned || 0) - (wallet?.lifetime_spent || 0)}
            color="primary"
            loading={loading}
          />
        </Grid>
      </Grid>

      <Grid container spacing={4}>
        {/* Transaction History */}
        <Grid item xs={12} md={8}>
          <Paper 
            elevation={0} 
            sx={{ 
              p: 3, 
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 3,
            }}
          >
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Letzte Transaktionen
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <TransactionHistory limit={15} showFilter />
          </Paper>
        </Grid>

        {/* Cost Reference */}
        <Grid item xs={12} md={4}>
          <Paper 
            elevation={0} 
            sx={{ 
              p: 3, 
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 3,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Info sx={{ color: 'primary.main' }} />
              <Typography variant="h6" fontWeight={600}>
                Kostenübersicht
              </Typography>
            </Box>
            <Divider sx={{ mb: 2 }} />

            {loading ? (
              <Skeleton variant="rectangular" height={200} />
            ) : config ? (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                <Typography variant="subtitle2" color="text.secondary" sx={{ mt: 1 }}>
                  Challenge-Erstellung
                </Typography>
                <CostRow label="Todo" cost={config.cost_todo} />
                <CostRow label="Streak" cost={config.cost_streak} />
                <CostRow label="Quantified" cost={config.cost_quantified} />
                <CostRow label="Duel" cost={config.cost_duel} />
                <CostRow label="Team" cost={config.cost_team} />
                <CostRow label="Community" cost={config.cost_community} />

                <Divider sx={{ my: 1 }} />

                <Typography variant="subtitle2" color="text.secondary">
                  Proof-Anforderungen
                </Typography>
                <CostRow label="Foto-Proof" cost={config.cost_photo_proof} />
                <CostRow label="Video-Proof" cost={config.cost_video_proof} />
                <CostRow label="Peer Review" cost={config.cost_peer_review} />

                <Divider sx={{ my: 1 }} />

                <Typography variant="subtitle2" color="text.secondary">
                  Belohnungen
                </Typography>
                <CostRow label="Aufgabe erledigt" cost={`+${config.reward_task_complete}`} positive />
                <CostRow label="7-Tage-Streak" cost={`+${config.reward_streak_7}`} positive />
                <CostRow label="30-Tage-Streak" cost={`+${config.reward_streak_30}`} positive />
              </Box>
            ) : null}
          </Paper>
        </Grid>
      </Grid>

      {/* Buy Credits Dialog */}
      <Dialog 
        open={buyDialogOpen} 
        onClose={() => setBuyDialogOpen(false)} 
        maxWidth="sm" 
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ShoppingCart color="primary" />
            Credits kaufen
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Wähle ein Credit-Paket oder gib einen individuellen Betrag ein.
          </Typography>

          {/* Credit Packages */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            {creditPackages.map((pkg) => (
              <Grid item xs={6} sm={4} key={pkg.amount}>
                <Card 
                  sx={{ 
                    cursor: 'pointer',
                    border: creditAmount === pkg.amount ? 2 : 1,
                    borderColor: creditAmount === pkg.amount ? 'primary.main' : 'divider',
                    position: 'relative',
                    transition: 'all 0.2s',
                    '&:hover': { 
                      borderColor: 'primary.main',
                      transform: 'translateY(-2px)',
                    },
                  }}
                  onClick={() => setCreditAmount(pkg.amount)}
                >
                  {pkg.popular && (
                    <Box
                      sx={{
                        position: 'absolute',
                        top: -10,
                        right: 10,
                        bgcolor: 'secondary.main',
                        color: 'white',
                        px: 1,
                        py: 0.25,
                        borderRadius: 1,
                        fontSize: 10,
                        fontWeight: 600,
                      }}
                    >
                      BELIEBT
                    </Box>
                  )}
                  <CardContent sx={{ textAlign: 'center', py: 2 }}>
                    <Typography variant="h5" fontWeight={700} color="primary.main">
                      {pkg.amount}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Credits
                    </Typography>
                    <Divider sx={{ my: 1 }} />
                    <Typography variant="body2" fontWeight={600}>
                      {pkg.price}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Custom Amount */}
          <TextField
            fullWidth
            label="Individueller Betrag"
            type="number"
            value={creditAmount}
            onChange={(e) => setCreditAmount(Math.max(1, parseInt(e.target.value) || 0))}
            inputProps={{ min: 1 }}
            sx={{ mb: 2 }}
          />

          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              <strong>Demo-Modus:</strong> Credits werden kostenlos hinzugefügt. 
              In der finalen Version wird hier ein Zahlungsprozess integriert.
            </Typography>
          </Alert>
        </DialogContent>
        <DialogActions sx={{ p: 2, pt: 0 }}>
          <Button onClick={() => setBuyDialogOpen(false)}>
            Abbrechen
          </Button>
          <Button 
            variant="contained" 
            onClick={() => handleBuyCredits(creditAmount)}
            disabled={purchasing || creditAmount < 1}
            startIcon={<ShoppingCart />}
          >
            {purchasing ? 'Wird verarbeitet...' : `${creditAmount} Credits kaufen`}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

const CostRow = ({ label, cost, positive = false }) => (
  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
    <Typography variant="body2">{label}</Typography>
    <Typography 
      variant="body2" 
      fontWeight={600}
      color={positive ? 'success.main' : 'text.primary'}
    >
      {typeof cost === 'number' ? `${cost} Credits` : cost}
    </Typography>
  </Box>
);

export default Wallet;
