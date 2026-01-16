import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Skeleton,
  Stack,
} from '@mui/material';
import {
  EmojiEvents as TrophyIcon,
  TrendingUp as TrendingUpIcon,
  WorkspacePremium as MedalIcon,
} from '@mui/icons-material';
import { rewardService } from '../services/apiService';

const medalColors = {
  1: { bg: '#FFD700', color: '#B8860B' }, // Gold
  2: { bg: '#C0C0C0', color: '#696969' }, // Silver
  3: { bg: '#CD7F32', color: '#8B4513' }, // Bronze
};

/**
 * Leaderboard Entry Row
 */
const LeaderboardRow = ({ entry, isCurrentUser }) => {
  const medal = medalColors[entry.rank];
  
  return (
    <TableRow 
      sx={{ 
        backgroundColor: isCurrentUser ? 'primary.50' : 'inherit',
        '&:hover': { backgroundColor: isCurrentUser ? 'primary.100' : 'grey.50' },
      }}
    >
      <TableCell sx={{ width: 60 }}>
        {medal ? (
          <Box
            sx={{
              width: 32,
              height: 32,
              borderRadius: '50%',
              backgroundColor: medal.bg,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Typography variant="subtitle2" fontWeight={700} sx={{ color: medal.color }}>
              {entry.rank}
            </Typography>
          </Box>
        ) : (
          <Typography variant="body2" color="text.secondary" sx={{ pl: 1 }}>
            #{entry.rank}
          </Typography>
        )}
      </TableCell>
      
      <TableCell>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Avatar 
            src={entry.avatar} 
            alt={entry.username}
            sx={{ width: 36, height: 36 }}
          >
            {entry.username?.[0]?.toUpperCase()}
          </Avatar>
          <Box>
            <Typography variant="subtitle2" fontWeight={isCurrentUser ? 700 : 500}>
              {entry.username}
              {isCurrentUser && (
                <Chip 
                  label="You" 
                  size="small" 
                  color="primary"
                  sx={{ ml: 1, height: 20, fontSize: '0.7rem' }}
                />
              )}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Level {entry.level}
            </Typography>
          </Box>
        </Box>
      </TableCell>
      
      <TableCell align="right">
        <Typography variant="subtitle2" fontWeight={600}>
          {entry.total_points?.toLocaleString()}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          XP
        </Typography>
      </TableCell>
    </TableRow>
  );
};

/**
 * Main Leaderboard Component
 */
const Leaderboard = ({ currentUserId }) => {
  const [tab, setTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({ entries: [], current_user_rank: null });
  const [error, setError] = useState(null);

  const tabs = [
    { label: 'Global', value: 'global' },
    { label: 'This Week', value: 'weekly' },
  ];

  useEffect(() => {
    const fetchLeaderboard = async () => {
      setLoading(true);
      try {
        const response = await rewardService.getLeaderboard(tabs[tab].value, 50);
        setData(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to load leaderboard');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab]);

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <TrophyIcon sx={{ fontSize: 32, color: '#FFD700' }} />
          <Typography variant="h5" fontWeight={700}>
            Leaderboard
          </Typography>
        </Box>

        <Tabs 
          value={tab} 
          onChange={(e, v) => setTab(v)}
          sx={{ mb: 3, borderBottom: 1, borderColor: 'divider' }}
        >
          {tabs.map((t, i) => (
            <Tab key={t.value} label={t.label} />
          ))}
        </Tabs>

        {/* Current User Rank Banner */}
        {data.current_user_rank && !loading && (
          <Box
            sx={{
              p: 2,
              mb: 3,
              borderRadius: 2,
              background: 'linear-gradient(135deg, #007AFF 0%, #5856D6 100%)',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <MedalIcon sx={{ fontSize: 28 }} />
              <Box>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Your Rank
                </Typography>
                <Typography variant="h5" fontWeight={700}>
                  #{data.current_user_rank}
                </Typography>
              </Box>
            </Box>
            <TrendingUpIcon sx={{ fontSize: 32, opacity: 0.8 }} />
          </Box>
        )}

        {/* Leaderboard Table */}
        {loading ? (
          <Stack spacing={2}>
            {[...Array(10)].map((_, i) => (
              <Skeleton key={i} variant="rounded" height={56} />
            ))}
          </Stack>
        ) : error ? (
          <Typography color="error" textAlign="center" py={4}>
            {error}
          </Typography>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Rank</TableCell>
                  <TableCell>Player</TableCell>
                  <TableCell align="right">Points</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.entries.map((entry) => (
                  <LeaderboardRow 
                    key={entry.user_id}
                    entry={entry}
                    isCurrentUser={entry.user_id === currentUserId}
                  />
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {!loading && data.entries.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 6 }}>
            <TrophyIcon sx={{ fontSize: 48, color: 'grey.400', mb: 1 }} />
            <Typography variant="h6" color="text.secondary">
              No rankings yet
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Complete challenges to appear on the leaderboard!
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

/**
 * Mini Leaderboard Widget for Dashboard
 */
export const LeaderboardMini = ({ currentUserId }) => {
  const [data, setData] = useState({ entries: [], current_user_rank: null });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    rewardService.getLeaderboard('global', 5)
      .then(res => setData(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Skeleton variant="text" width="50%" height={32} />
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} variant="rounded" height={40} sx={{ my: 1 }} />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <TrophyIcon sx={{ color: '#FFD700' }} />
          <Typography variant="h6" fontWeight={600}>
            Top Players
          </Typography>
        </Box>

        <Stack spacing={1}>
          {data.entries.slice(0, 5).map((entry, index) => (
            <Box
              key={entry.user_id}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1.5,
                p: 1,
                borderRadius: 1,
                backgroundColor: entry.user_id === currentUserId ? 'primary.50' : 'grey.50',
              }}
            >
              <Typography 
                variant="caption" 
                fontWeight={700}
                sx={{ 
                  width: 20, 
                  color: medalColors[entry.rank]?.color || 'text.secondary' 
                }}
              >
                {entry.rank}
              </Typography>
              <Avatar src={entry.avatar} sx={{ width: 28, height: 28 }}>
                {entry.username?.[0]}
              </Avatar>
              <Typography variant="body2" sx={{ flex: 1 }} noWrap>
                {entry.username}
              </Typography>
              <Typography variant="caption" fontWeight={600}>
                {entry.total_points?.toLocaleString()}
              </Typography>
            </Box>
          ))}
        </Stack>

        {data.current_user_rank && data.current_user_rank > 5 && (
          <Box 
            sx={{ 
              mt: 2, 
              pt: 2, 
              borderTop: '1px dashed', 
              borderColor: 'divider',
              textAlign: 'center',
            }}
          >
            <Typography variant="body2" color="text.secondary">
              Your Rank: <strong>#{data.current_user_rank}</strong>
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default Leaderboard;
