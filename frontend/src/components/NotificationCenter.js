import React, { useState, useEffect, useCallback } from 'react';
import {
  Badge,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Typography,
  Box,
  Divider,
  Button,
  CircularProgress,
  Avatar,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  EmojiEvents as TrophyIcon,
  LocalFireDepartment as StreakIcon,
  People as TeamIcon,
  Flag as ChallengeIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { notificationService } from '../services/apiService';

const notificationIcons = {
  badge_earned: <TrophyIcon sx={{ color: '#FFD700' }} />,
  level_up: <TrophyIcon sx={{ color: '#5856D6' }} />,
  streak_milestone: <StreakIcon sx={{ color: '#FF6B35' }} />,
  streak_warning: <WarningIcon sx={{ color: '#FF9500' }} />,
  streak_broken: <WarningIcon sx={{ color: '#FF3B30' }} />,
  challenge_invite: <ChallengeIcon sx={{ color: '#007AFF' }} />,
  challenge_reminder: <ChallengeIcon sx={{ color: '#FF9500' }} />,
  challenge_completed: <CheckIcon sx={{ color: '#34C759' }} />,
  duel_request: <ChallengeIcon sx={{ color: '#FF3B30' }} />,
  duel_accepted: <CheckIcon sx={{ color: '#34C759' }} />,
  duel_won: <TrophyIcon sx={{ color: '#FFD700' }} />,
  duel_lost: <InfoIcon sx={{ color: '#8E8E93' }} />,
  proof_approved: <CheckIcon sx={{ color: '#34C759' }} />,
  proof_rejected: <WarningIcon sx={{ color: '#FF3B30' }} />,
  proof_review_request: <InfoIcon sx={{ color: '#007AFF' }} />,
  team_invite: <TeamIcon sx={{ color: '#007AFF' }} />,
  team_joined: <TeamIcon sx={{ color: '#34C759' }} />,
  team_nudge: <TeamIcon sx={{ color: '#FF9500' }} />,
  system: <InfoIcon sx={{ color: '#8E8E93' }} />,
};

const NotificationCenter = () => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const open = Boolean(anchorEl);

  const fetchNotifications = useCallback(async () => {
    try {
      setLoading(true);
      const [notifRes, countRes] = await Promise.all([
        notificationService.list({ page_size: 10 }),
        notificationService.getUnreadCount(),
      ]);
      setNotifications(notifRes.data?.results || notifRes.data || []);
      setUnreadCount(countRes.data?.unread_count || 0);
    } catch (err) {
      console.error('Failed to fetch notifications:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
    
    // Poll for new notifications every 30 seconds
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
    fetchNotifications();
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationService.markAllRead();
      setUnreadCount(0);
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    } catch (err) {
      console.error('Failed to mark all as read:', err);
    }
  };

  const handleNotificationClick = async (notification) => {
    try {
      if (!notification.is_read) {
        await notificationService.markRead(notification.id);
        setUnreadCount(prev => Math.max(0, prev - 1));
        setNotifications(prev => 
          prev.map(n => n.id === notification.id ? { ...n, is_read: true } : n)
        );
      }
      
      if (notification.action_url) {
        window.location.href = notification.action_url;
      }
    } catch (err) {
      console.error('Failed to mark notification as read:', err);
    }
    handleClose();
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <>
      <IconButton
        color="inherit"
        onClick={handleClick}
        aria-label={`${unreadCount} unread notifications`}
      >
        <Badge badgeContent={unreadCount} color="error">
          <NotificationsIcon />
        </Badge>
      </IconButton>
      
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        PaperProps={{
          sx: {
            width: 360,
            maxHeight: 480,
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        {/* Header */}
        <Box sx={{ px: 2, py: 1.5, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6" fontWeight={600}>
            Notifications
          </Typography>
          {unreadCount > 0 && (
            <Button size="small" onClick={handleMarkAllRead}>
              Mark all read
            </Button>
          )}
        </Box>
        <Divider />
        
        {/* Loading State */}
        {loading && notifications.length === 0 && (
          <Box sx={{ py: 4, textAlign: 'center' }}>
            <CircularProgress size={24} />
          </Box>
        )}
        
        {/* Empty State */}
        {!loading && notifications.length === 0 && (
          <Box sx={{ py: 4, textAlign: 'center' }}>
            <NotificationsIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
            <Typography color="text.secondary">
              No notifications yet
            </Typography>
          </Box>
        )}
        
        {/* Notifications List */}
        {notifications.map((notification) => (
          <MenuItem
            key={notification.id}
            onClick={() => handleNotificationClick(notification)}
            sx={{
              py: 1.5,
              px: 2,
              alignItems: 'flex-start',
              bgcolor: notification.is_read ? 'transparent' : 'action.hover',
              '&:hover': {
                bgcolor: 'action.selected',
              },
            }}
          >
            <ListItemIcon sx={{ mt: 0.5, minWidth: 40 }}>
              <Avatar 
                sx={{ 
                  width: 32, 
                  height: 32, 
                  bgcolor: notification.is_read ? 'grey.200' : 'primary.light' 
                }}
              >
                {notificationIcons[notification.notification_type] || <InfoIcon />}
              </Avatar>
            </ListItemIcon>
            <ListItemText
              primary={
                <Typography 
                  variant="body2" 
                  fontWeight={notification.is_read ? 400 : 600}
                  sx={{ 
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    display: '-webkit-box',
                    WebkitLineClamp: 1,
                    WebkitBoxOrient: 'vertical',
                  }}
                >
                  {notification.title}
                </Typography>
              }
              secondary={
                <>
                  <Typography 
                    variant="caption" 
                    color="text.secondary"
                    sx={{ 
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                    }}
                  >
                    {notification.message}
                  </Typography>
                  <Typography variant="caption" color="text.disabled" sx={{ display: 'block', mt: 0.5 }}>
                    {formatTime(notification.created_at)}
                  </Typography>
                </>
              }
            />
          </MenuItem>
        ))}
        
        {/* Footer */}
        {notifications.length > 0 && (
          <>
            <Divider />
            <Box sx={{ p: 1, textAlign: 'center' }}>
              <Button size="small" href="/notifications">
                View All Notifications
              </Button>
            </Box>
          </>
        )}
      </Menu>
    </>
  );
};

export default NotificationCenter;
