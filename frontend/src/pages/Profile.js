import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Avatar,
  Button,
  Chip,
  Stack,
  LinearProgress,
  Skeleton,
  Tab,
  Tabs,
} from '@mui/material';
import {
  Edit as EditIcon,
  EmojiEvents as TrophyIcon,
  Star as StarIcon,
  TrendingUp as TrendingIcon,
  Flag as ChallengeIcon,
} from '@mui/icons-material';
import Layout from '../components/Layout';
import { useAuth } from '../contexts/AuthContext';
import { rewardService, challengeService } from '../services/apiService';

const ProfilePage = () => {
  const { user } = useAuth();
  const [tab, setTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [badges, setBadges] = useState([]);
  const [challenges, setChallenges] = useState([]);

  useEffect(() => {
    loadProfileData();
  }, []);

  const loadProfileData = async () => {
    setLoading(true);
    try {
      const [progressRes, badgesRes, challengesRes] = await Promise.all([
        rewardService.getProgress(),
        rewardService.getEarnedBadges(),
        challengeService.getMyChallenges(),
      ]);
      setStats(progressRes.data);
      setBadges(badgesRes.data.results || badgesRes.data || []);
      setChallenges(challengesRes.data.results || challengesRes.data || []);
    } catch (err) {
      console.error('Failed to load profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const xpProgress = stats?.xp?.progress_percent || 0;

  return (
    <Layout>
      {/* Profile Header */}
      <Card sx={{ mb: 4, overflow: 'visible' }}>
        <Box
          sx={{
            height: 120,
            background: 'linear-gradient(135deg, #007AFF 0%, #5856D6 100%)',
            position: 'relative',
          }}
        />
        <CardContent sx={{ pt: 0 }}>
          <Box sx={{ display: 'flex', alignItems: 'flex-end', gap: 3, mt: -6 }}>
            <Avatar
              src={user?.avatar}
              sx={{
                width: 120,
                height: 120,
                border: '4px solid white',
                boxShadow: 2,
                fontSize: 48,
              }}
            >
              {user?.username?.[0]?.toUpperCase()}
            </Avatar>
            <Box sx={{ flex: 1, pb: 1 }}>
              <Typography variant="h4" fontWeight={700}>
                {user?.first_name && user?.last_name 
                  ? `${user.first_name} ${user.last_name}`
                  : user?.username}
              </Typography>
              <Typography variant="body1" color="text.secondary">
                @{user?.username}
              </Typography>
            </Box>
            <Button variant="outlined" startIcon={<EditIcon />}>
              Edit Profile
            </Button>
          </Box>

          {/* Level & XP Bar */}
          <Box sx={{ mt: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip 
                  label={`Level ${user?.level || stats?.xp?.level || 1}`}
                  color="primary"
                  sx={{ fontWeight: 700 }}
                />
                <Typography variant="body2" color="text.secondary">
                  {stats?.xp?.total_xp?.toLocaleString() || user?.total_points || 0} XP total
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                {stats?.xp?.xp_in_level || 0} / {stats?.xp?.xp_needed || 100} to next level
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={xpProgress}
              sx={{
                height: 10,
                borderRadius: 5,
                backgroundColor: 'grey.200',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 5,
                  background: 'linear-gradient(90deg, #007AFF 0%, #5856D6 100%)',
                },
              }}
            />
          </Box>

          {/* Quick Stats */}
          <Grid container spacing={3} sx={{ mt: 2 }}>
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight={700} color="primary">
                  {stats?.xp?.weekly || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  XP This Week
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight={700} sx={{ color: '#FF6B35' }}>
                  {stats?.streaks?.current_best || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Day Streak
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight={700} sx={{ color: '#FFD700' }}>
                  {badges.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Badges Earned
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight={700} sx={{ color: '#34C759' }}>
                  {challenges.filter(c => c.status === 'completed').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Challenges Won
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Content Tabs */}
      <Tabs
        value={tab}
        onChange={(e, v) => setTab(v)}
        sx={{ mb: 3, borderBottom: 1, borderColor: 'divider' }}
      >
        <Tab icon={<TrophyIcon />} label="Badges" iconPosition="start" />
        <Tab icon={<ChallengeIcon />} label="Challenges" iconPosition="start" />
        <Tab icon={<TrendingIcon />} label="Activity" iconPosition="start" />
      </Tabs>

      {loading ? (
        <Grid container spacing={2}>
          {[...Array(6)].map((_, i) => (
            <Grid item xs={6} sm={4} md={3} key={i}>
              <Skeleton variant="rounded" height={120} />
            </Grid>
          ))}
        </Grid>
      ) : (
        <>
          {/* Badges Tab */}
          {tab === 0 && (
            <Grid container spacing={2}>
              {badges.length === 0 ? (
                <Grid item xs={12}>
                  <Box sx={{ textAlign: 'center', py: 6 }}>
                    <TrophyIcon sx={{ fontSize: 64, color: 'grey.300', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary">
                      No badges yet
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Complete challenges to earn badges!
                    </Typography>
                  </Box>
                </Grid>
              ) : (
                badges.map((userReward, index) => (
                  <Grid item xs={6} sm={4} md={3} key={index}>
                    <Card 
                      sx={{ 
                        textAlign: 'center', 
                        p: 2,
                        transition: 'transform 0.2s',
                        '&:hover': { transform: 'scale(1.05)' },
                      }}
                    >
                      <Avatar
                        sx={{
                          width: 64,
                          height: 64,
                          mx: 'auto',
                          mb: 1,
                          background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
                        }}
                      >
                        <StarIcon sx={{ fontSize: 32 }} />
                      </Avatar>
                      <Typography variant="subtitle2" fontWeight={600}>
                        {userReward.reward?.name || 'Badge'}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {userReward.reward?.description}
                      </Typography>
                    </Card>
                  </Grid>
                ))
              )}
            </Grid>
          )}

          {/* Challenges Tab */}
          {tab === 1 && (
            <Stack spacing={2}>
              {challenges.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 6 }}>
                  <ChallengeIcon sx={{ fontSize: 64, color: 'grey.300', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary">
                    No challenges yet
                  </Typography>
                </Box>
              ) : (
                challenges.map((challenge) => (
                  <Card key={challenge.id}>
                    <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Box sx={{ fontSize: 32 }}>
                        {challenge.challenge_type === 'streak' ? '🔥' : 
                         challenge.challenge_type === 'duel' ? '⚔️' : '✓'}
                      </Box>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="subtitle1" fontWeight={600}>
                          {challenge.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {challenge.description?.slice(0, 100)}
                        </Typography>
                      </Box>
                      <Chip 
                        label={challenge.status}
                        color={challenge.status === 'completed' ? 'success' : 
                               challenge.status === 'active' ? 'primary' : 'default'}
                        size="small"
                      />
                    </CardContent>
                  </Card>
                ))
              )}
            </Stack>
          )}

          {/* Activity Tab */}
          {tab === 2 && (
            <Box sx={{ textAlign: 'center', py: 6 }}>
              <TrendingIcon sx={{ fontSize: 64, color: 'grey.300', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                Activity feed coming soon
              </Typography>
            </Box>
          )}
        </>
      )}
    </Layout>
  );
};

export default ProfilePage;
