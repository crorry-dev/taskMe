import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Skeleton,
  Stack,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Flag as ChallengeIcon,
  TrendingUp as TrendingIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { rewardService, challengeService } from '../services/apiService';
import Layout from '../components/Layout';
import { XPProgressWidget, StreakWidget, StatsCard, BadgesWidget } from '../components/DashboardWidgets';
import { ActiveChallengeMini } from '../components/ChallengeComponents';
import { LeaderboardMini } from '../components/Leaderboard';
import CreateChallengeDialog from '../components/CreateChallengeDialog';

const DashboardNew = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [activeChallenges, setActiveChallenges] = useState([]);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  useEffect(() => {
    loadDashboardData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [progressRes, challengesRes] = await Promise.all([
        rewardService.getProgress().catch(() => ({ data: {} })),
        challengeService.getMyChallenges().catch(() => ({ data: { results: [] } })),
      ]);

      setStats(progressRes.data);
      setActiveChallenges(challengesRes.data.results || challengesRes.data || []);
      setError(null);
    } catch (err) {
      console.error('Dashboard load error:', err);
      setError('Failed to load some data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateChallenge = async (data) => {
    await challengeService.create(data);
    loadDashboardData();
  };

  const LoadingSkeleton = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Skeleton variant="rounded" height={160} />
      </Grid>
      <Grid item xs={12} md={4}>
        <Skeleton variant="rounded" height={160} />
      </Grid>
      <Grid item xs={12} md={4}>
        <Skeleton variant="rounded" height={160} />
      </Grid>
      <Grid item xs={12}>
        <Skeleton variant="rounded" height={300} />
      </Grid>
    </Grid>
  );

  return (
    <Layout>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Welcome back, {user?.username || 'Champion'}! 👋
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Track your progress and stay committed to your goals.
        </Typography>
      </Box>

      {error && (
        <Alert severity="warning" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading ? (
        <LoadingSkeleton />
      ) : (
        <Grid container spacing={3}>
          {/* XP Progress */}
          <Grid item xs={12} md={4}>
            <XPProgressWidget xp={stats?.xp || { level: user?.level || 1, total_xp: user?.total_points || 0 }} />
          </Grid>

          {/* Streak Widget */}
          <Grid item xs={12} md={4}>
            <StreakWidget streaks={stats?.streaks || {}} />
          </Grid>

          {/* Quick Stats */}
          <Grid item xs={12} md={4}>
            <StatsCard
              title="Active Challenges"
              value={stats?.challenges?.active || activeChallenges.filter(c => c.status === 'active').length || 0}
              subtitle={`${stats?.challenges?.completed || 0} completed`}
              icon={<ChallengeIcon />}
              color="#5856D6"
            />
          </Grid>

          {/* Active Challenges */}
          <Grid item xs={12} lg={8}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <ChallengeIcon color="primary" />
                    <Typography variant="h6" fontWeight={600}>
                      Active Challenges
                    </Typography>
                  </Box>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => setCreateDialogOpen(true)}
                    size="small"
                  >
                    New Challenge
                  </Button>
                </Box>

                {activeChallenges.length === 0 ? (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <ChallengeIcon sx={{ fontSize: 48, color: 'grey.400', mb: 1 }} />
                    <Typography variant="body1" color="text.secondary" gutterBottom>
                      No active challenges
                    </Typography>
                    <Button
                      variant="outlined"
                      startIcon={<AddIcon />}
                      onClick={() => setCreateDialogOpen(true)}
                      sx={{ mt: 1 }}
                    >
                      Create Your First Challenge
                    </Button>
                  </Box>
                ) : (
                  <Stack spacing={2}>
                    {activeChallenges.slice(0, 5).map((challenge) => (
                      <ActiveChallengeMini key={challenge.id} challenge={challenge} />
                    ))}
                  </Stack>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Leaderboard Mini */}
          <Grid item xs={12} lg={4}>
            <LeaderboardMini currentUserId={user?.id} />
          </Grid>

          {/* Recent Badges */}
          <Grid item xs={12} md={6}>
            <BadgesWidget badges={stats?.badges?.recent || []} />
          </Grid>

          {/* Weekly Progress */}
          <Grid item xs={12} md={6}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                  <TrendingIcon sx={{ color: '#34C759' }} />
                  <Typography variant="h6" fontWeight={600}>
                    This Week
                  </Typography>
                </Box>

                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center', p: 2, backgroundColor: 'grey.50', borderRadius: 2 }}>
                      <Typography variant="h4" fontWeight={700} color="primary">
                        {stats?.xp?.weekly || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        XP Earned
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center', p: 2, backgroundColor: 'grey.50', borderRadius: 2 }}>
                      <Typography variant="h4" fontWeight={700} sx={{ color: '#FF6B35' }}>
                        {stats?.streaks?.current_best || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Day Streak
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Create Challenge Dialog */}
      <CreateChallengeDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        onSubmit={handleCreateChallenge}
      />
    </Layout>
  );
};

export default DashboardNew;
