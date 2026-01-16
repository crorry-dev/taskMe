import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  Avatar,
  Stack,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  LocalFireDepartment as StreakIcon,
  EmojiEvents as TrophyIcon,
  Star as StarIcon,
} from '@mui/icons-material';

/**
 * XP Progress Widget - Shows level and XP progress
 */
export const XPProgressWidget = ({ xp = {} }) => {
  const { level = 1, total_xp = 0, xp_in_level = 0, xp_needed = 100, progress_percent = 0 } = xp;
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #007AFF 0%, #5856D6 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mr: 2,
            }}
          >
            <Typography variant="h6" color="white" fontWeight={700}>
              {level}
            </Typography>
          </Box>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" fontWeight={600}>
              Level {level}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {total_xp.toLocaleString()} XP total
            </Typography>
          </Box>
        </Box>
        
        <Box sx={{ mb: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="caption" color="text.secondary">
              Progress to Level {level + 1}
            </Typography>
            <Typography variant="caption" fontWeight={600}>
              {xp_in_level} / {xp_needed} XP
            </Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={progress_percent} 
            sx={{ 
              height: 8, 
              borderRadius: 4,
              backgroundColor: 'grey.200',
              '& .MuiLinearProgress-bar': {
                borderRadius: 4,
                background: 'linear-gradient(90deg, #007AFF 0%, #5856D6 100%)',
              }
            }} 
          />
        </Box>
      </CardContent>
    </Card>
  );
};

/**
 * Streak Widget - Shows current streak
 */
export const StreakWidget = ({ streaks = {} }) => {
  const { current_best = 0, all_time_best = 0, active_count = 0 } = streaks;
  
  const getStreakColor = (count) => {
    if (count >= 30) return '#FF9500';
    if (count >= 7) return '#FF6B35';
    return '#FF3B30';
  };
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <StreakIcon sx={{ fontSize: 32, color: getStreakColor(current_best), mr: 1.5 }} />
          <Typography variant="h6" fontWeight={600}>
            Streaks
          </Typography>
        </Box>
        
        <Box sx={{ textAlign: 'center', py: 2 }}>
          <Typography 
            variant="h2" 
            fontWeight={700}
            sx={{ 
              background: `linear-gradient(135deg, ${getStreakColor(current_best)} 0%, #FF9500 100%)`,
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              color: 'transparent',
            }}
          >
            {current_best}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            days current streak
          </Typography>
        </Box>
        
        <Stack direction="row" spacing={2} justifyContent="center">
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h6" fontWeight={600}>{all_time_best}</Typography>
            <Typography variant="caption" color="text.secondary">Best Ever</Typography>
          </Box>
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h6" fontWeight={600}>{active_count}</Typography>
            <Typography variant="caption" color="text.secondary">Active</Typography>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
};

/**
 * Stats Card - Generic stat display
 */
export const StatsCard = ({ title, value, subtitle, icon, color = 'primary.main' }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {title}
          </Typography>
          <Typography variant="h4" fontWeight={700}>
            {value}
          </Typography>
          {subtitle && (
            <Typography variant="caption" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Box>
        {icon && (
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: 2,
              backgroundColor: `${color}15`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {React.cloneElement(icon, { sx: { color, fontSize: 28 } })}
          </Box>
        )}
      </Box>
    </CardContent>
  </Card>
);

/**
 * Recent Badges Widget
 */
export const BadgesWidget = ({ badges = [] }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <TrophyIcon sx={{ fontSize: 28, color: '#FFD700', mr: 1.5 }} />
        <Typography variant="h6" fontWeight={600}>
          Recent Badges
        </Typography>
      </Box>
      
      {badges.length === 0 ? (
        <Typography variant="body2" color="text.secondary" sx={{ py: 3, textAlign: 'center' }}>
          Complete challenges to earn badges!
        </Typography>
      ) : (
        <Stack spacing={1.5}>
          {badges.map((badge, index) => (
            <Box 
              key={index}
              sx={{ 
                display: 'flex', 
                alignItems: 'center',
                p: 1.5,
                borderRadius: 2,
                backgroundColor: 'grey.50',
              }}
            >
              <Avatar
                sx={{ 
                  width: 40, 
                  height: 40, 
                  mr: 1.5,
                  background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
                }}
              >
                <StarIcon sx={{ color: 'white' }} />
              </Avatar>
              <Box sx={{ flex: 1 }}>
                <Typography variant="subtitle2" fontWeight={600}>
                  {badge.name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {badge.description}
                </Typography>
              </Box>
            </Box>
          ))}
        </Stack>
      )}
    </CardContent>
  </Card>
);

/**
 * Quick Stats Row
 */
export const QuickStats = ({ stats }) => (
  <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
    <Chip
      icon={<TrendingUpIcon />}
      label={`${stats?.weekly || 0} XP this week`}
      color="primary"
      variant="outlined"
    />
    <Chip
      icon={<StreakIcon />}
      label={`${stats?.streaks?.current_best || 0} day streak`}
      sx={{ borderColor: '#FF6B35', color: '#FF6B35' }}
      variant="outlined"
    />
    <Chip
      icon={<TrophyIcon />}
      label={`${stats?.badges?.total || 0} badges`}
      sx={{ borderColor: '#FFD700', color: '#B8860B' }}
      variant="outlined"
    />
  </Box>
);

export default {
  XPProgressWidget,
  StreakWidget,
  StatsCard,
  BadgesWidget,
  QuickStats,
};
