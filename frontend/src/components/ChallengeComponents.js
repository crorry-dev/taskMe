import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Box,
  Chip,
  Button,
  LinearProgress,
  Stack,
} from '@mui/material';
import {
  AccessTime as TimeIcon,
  People as PeopleIcon,
  Flag as FlagIcon,
  EmojiEvents as TrophyIcon,
} from '@mui/icons-material';

const challengeTypeConfig = {
  todo: { label: 'Todo', color: '#007AFF', icon: '✓' },
  streak: { label: 'Streak', color: '#FF6B35', icon: '🔥' },
  program: { label: 'Program', color: '#5856D6', icon: '📋' },
  quantified: { label: 'Goal', color: '#34C759', icon: '📊' },
  team: { label: 'Team', color: '#FF9500', icon: '👥' },
  duel: { label: 'Duel', color: '#FF3B30', icon: '⚔️' },
  community: { label: 'Community', color: '#AF52DE', icon: '🌍' },
};

const statusConfig = {
  draft: { label: 'Draft', color: 'default' },
  upcoming: { label: 'Upcoming', color: 'info' },
  active: { label: 'Active', color: 'success' },
  completed: { label: 'Completed', color: 'default' },
  cancelled: { label: 'Cancelled', color: 'error' },
};

/**
 * Challenge Card - Displays challenge summary
 */
export const ChallengeCard = ({ challenge, onJoin, onView }) => {
  const navigate = useNavigate();
  const typeConfig = challengeTypeConfig[challenge.challenge_type] || challengeTypeConfig.todo;
  const status = statusConfig[challenge.status] || statusConfig.draft;
  
  const progress = challenge.current_value && challenge.target_value 
    ? Math.min((challenge.current_value / challenge.target_value) * 100, 100)
    : 0;

  const daysLeft = challenge.end_date 
    ? Math.max(0, Math.ceil((new Date(challenge.end_date) - new Date()) / (1000 * 60 * 60 * 24)))
    : null;

  return (
    <Card 
      sx={{ 
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 4,
        },
        cursor: 'pointer',
      }}
      onClick={() => onView ? onView(challenge) : navigate(`/challenges/${challenge.id}`)}
    >
      <CardContent sx={{ flex: 1 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: 2,
              backgroundColor: `${typeConfig.color}15`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mr: 2,
              fontSize: 24,
            }}
          >
            {typeConfig.icon}
          </Box>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography variant="h6" fontWeight={600} noWrap>
              {challenge.title}
            </Typography>
            <Stack direction="row" spacing={1} sx={{ mt: 0.5 }}>
              <Chip 
                label={typeConfig.label} 
                size="small" 
                sx={{ 
                  backgroundColor: `${typeConfig.color}15`,
                  color: typeConfig.color,
                  fontWeight: 500,
                }}
              />
              <Chip 
                label={status.label} 
                size="small" 
                color={status.color}
                variant="outlined"
              />
            </Stack>
          </Box>
        </Box>

        {/* Description */}
        <Typography 
          variant="body2" 
          color="text.secondary" 
          sx={{ 
            mb: 2,
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
          }}
        >
          {challenge.description}
        </Typography>

        {/* Progress */}
        {challenge.target_value && (
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="caption" color="text.secondary">
                Progress
              </Typography>
              <Typography variant="caption" fontWeight={600}>
                {challenge.current_value || 0} / {challenge.target_value} {challenge.unit}
              </Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={progress}
              sx={{ 
                height: 6, 
                borderRadius: 3,
                backgroundColor: 'grey.200',
              }}
            />
          </Box>
        )}

        {/* Meta Info */}
        <Stack direction="row" spacing={2} sx={{ mt: 'auto' }}>
          {daysLeft !== null && (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <TimeIcon sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
              <Typography variant="caption" color="text.secondary">
                {daysLeft} days left
              </Typography>
            </Box>
          )}
          {challenge.participant_count !== undefined && (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <PeopleIcon sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
              <Typography variant="caption" color="text.secondary">
                {challenge.participant_count} participants
              </Typography>
            </Box>
          )}
          {challenge.reward_points > 0 && (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <TrophyIcon sx={{ fontSize: 16, mr: 0.5, color: '#FFD700' }} />
              <Typography variant="caption" color="text.secondary">
                {challenge.reward_points} XP
              </Typography>
            </Box>
          )}
        </Stack>
      </CardContent>

      {/* Actions */}
      {onJoin && !challenge.is_participant && challenge.status === 'active' && (
        <CardActions sx={{ px: 2, pb: 2 }}>
          <Button 
            fullWidth 
            variant="contained"
            onClick={(e) => {
              e.stopPropagation();
              onJoin(challenge);
            }}
          >
            Join Challenge
          </Button>
        </CardActions>
      )}
    </Card>
  );
};

/**
 * Challenge List - Grid of challenge cards
 */
export const ChallengeList = ({ challenges, onJoin, onView, emptyMessage }) => {
  if (!challenges || challenges.length === 0) {
    return (
      <Box 
        sx={{ 
          textAlign: 'center', 
          py: 8,
          px: 4,
          backgroundColor: 'grey.50',
          borderRadius: 3,
        }}
      >
        <FlagIcon sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
        <Typography variant="h6" color="text.secondary" gutterBottom>
          {emptyMessage || 'No challenges found'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Create a new challenge or join an existing one to get started!
        </Typography>
      </Box>
    );
  }

  return (
    <Box 
      sx={{ 
        display: 'grid',
        gridTemplateColumns: {
          xs: '1fr',
          sm: 'repeat(2, 1fr)',
          lg: 'repeat(3, 1fr)',
        },
        gap: 3,
      }}
    >
      {challenges.map((challenge) => (
        <ChallengeCard 
          key={challenge.id} 
          challenge={challenge}
          onJoin={onJoin}
          onView={onView}
        />
      ))}
    </Box>
  );
};

/**
 * Active Challenge Mini Card - For dashboard
 */
export const ActiveChallengeMini = ({ challenge }) => {
  const typeConfig = challengeTypeConfig[challenge.challenge_type] || challengeTypeConfig.todo;
  const progress = challenge.current_value && challenge.target_value 
    ? Math.min((challenge.current_value / challenge.target_value) * 100, 100)
    : 0;

  return (
    <Box
      sx={{
        p: 2,
        borderRadius: 2,
        backgroundColor: 'grey.50',
        display: 'flex',
        alignItems: 'center',
        gap: 2,
      }}
    >
      <Box sx={{ fontSize: 24 }}>{typeConfig.icon}</Box>
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Typography variant="subtitle2" fontWeight={600} noWrap>
          {challenge.title}
        </Typography>
        <LinearProgress 
          variant="determinate" 
          value={progress}
          sx={{ 
            height: 4, 
            borderRadius: 2,
            mt: 0.5,
            backgroundColor: 'grey.200',
          }}
        />
      </Box>
      <Typography variant="caption" fontWeight={600} color="primary">
        {Math.round(progress)}%
      </Typography>
    </Box>
  );
};

export default {
  ChallengeCard,
  ChallengeList,
  ActiveChallengeMini,
};
