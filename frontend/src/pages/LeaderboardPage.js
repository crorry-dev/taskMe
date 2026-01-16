import React from 'react';
import { Box, Typography } from '@mui/material';
import Layout from '../components/Layout';
import Leaderboard from '../components/Leaderboard';
import { useAuth } from '../contexts/AuthContext';

const LeaderboardPage = () => {
  const { user } = useAuth();

  return (
    <Layout>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Leaderboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          See how you stack up against other CommitQuest players
        </Typography>
      </Box>

      <Leaderboard currentUserId={user?.id} />
    </Layout>
  );
};

export default LeaderboardPage;
