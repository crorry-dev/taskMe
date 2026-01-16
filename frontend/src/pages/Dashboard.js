import React, { useState, useEffect, useMemo } from 'react';
import {
  Container,
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  AppBar,
  Toolbar,
  Snackbar,
  Alert,
  ToggleButtonGroup,
  ToggleButton,
  LinearProgress,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  CheckCircle as CheckIcon,
  EmojiEvents as TrophyIcon,
  Star as StarIcon,
  Logout as LogoutIcon,
  AccountBalanceWallet as WalletIcon,
  Sort as SortIcon,
  Warning as WarningIcon,
  Schedule as ScheduleIcon,
  PriorityHigh as PriorityIcon,
  BugReport as BugReportIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { taskService } from '../services';
import { useNavigate } from 'react-router-dom';
import { VoiceMemoButton } from '../components/voice';
import { CreditBalance } from '../components/credits';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [sortBy, setSortBy] = useState('urgency'); // 'urgency' | 'priority' | 'created' | 'due_date'
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    priority: 'medium',
    reward_points: 10,
    requires_proof: false,
    due_date: '',
  });

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      const response = await taskService.getTasks();
      setTasks(response.results || response);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  // Calculate urgency score for tasks (higher = more urgent)
  const calculateUrgency = (task) => {
    if (task.status === 'completed') return -1000; // Completed tasks at bottom
    
    let score = 0;
    
    // Priority weight
    const priorityWeights = { urgent: 100, high: 50, medium: 20, low: 5 };
    score += priorityWeights[task.priority] || 10;
    
    // Due date urgency
    if (task.due_date) {
      const now = new Date();
      const due = new Date(task.due_date);
      const hoursUntilDue = (due - now) / (1000 * 60 * 60);
      
      if (hoursUntilDue < 0) {
        score += 500; // Overdue
      } else if (hoursUntilDue < 2) {
        score += 200; // Due in 2 hours
      } else if (hoursUntilDue < 24) {
        score += 100; // Due today
      } else if (hoursUntilDue < 48) {
        score += 50; // Due tomorrow
      }
    }
    
    return score;
  };

  // Get time-critical status
  const getTimeCriticalStatus = (task) => {
    if (!task.due_date) return null;
    
    const now = new Date();
    const due = new Date(task.due_date);
    const hoursUntilDue = (due - now) / (1000 * 60 * 60);
    
    if (hoursUntilDue < 0) {
      return { label: 'Überfällig!', color: 'error', progress: 100 };
    } else if (hoursUntilDue < 2) {
      return { label: `${Math.ceil(hoursUntilDue * 60)} Min übrig`, color: 'error', progress: 90 };
    } else if (hoursUntilDue < 24) {
      return { label: `${Math.ceil(hoursUntilDue)} Std übrig`, color: 'warning', progress: 70 };
    } else if (hoursUntilDue < 48) {
      return { label: 'Morgen fällig', color: 'info', progress: 40 };
    }
    return null;
  };

  // Sorted open tasks
  const sortedOpenTasks = useMemo(() => {
    const openTasks = tasks.filter(t => t.status !== 'completed');
    
    return openTasks.sort((a, b) => {
      switch (sortBy) {
        case 'urgency':
          return calculateUrgency(b) - calculateUrgency(a);
        case 'priority':
          const priorityOrder = { urgent: 0, high: 1, medium: 2, low: 3 };
          return (priorityOrder[a.priority] || 2) - (priorityOrder[b.priority] || 2);
        case 'due_date':
          if (!a.due_date && !b.due_date) return 0;
          if (!a.due_date) return 1;
          if (!b.due_date) return -1;
          return new Date(a.due_date) - new Date(b.due_date);
        case 'created':
        default:
          return new Date(b.created_at) - new Date(a.created_at);
      }
    });
  }, [tasks, sortBy]);

  // Completed tasks (separate)
  const completedTasks = useMemo(() => 
    tasks.filter(t => t.status === 'completed'), 
    [tasks]
  );

  const handleCreateTask = async () => {
    try {
      const taskData = { ...newTask };
      if (!taskData.due_date) delete taskData.due_date;
      await taskService.createTask(taskData);
      setOpenDialog(false);
      setNewTask({
        title: '',
        description: '',
        priority: 'medium',
        reward_points: 10,
        requires_proof: false,
        due_date: '',
      });
      loadTasks();
      setSnackbar({ open: true, message: 'Task erstellt!', severity: 'success' });
    } catch (error) {
      console.error('Failed to create task:', error);
      setSnackbar({ open: true, message: 'Fehler beim Erstellen', severity: 'error' });
    }
  };

  const handleCompleteTask = async (taskId) => {
    try {
      await taskService.completeTask(taskId);
      loadTasks();
    } catch (error) {
      console.error('Failed to complete task:', error);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getPriorityColor = (priority) => {
    const colors = {
      low: 'success',
      medium: 'info',
      high: 'warning',
      urgent: 'error',
    };
    return colors[priority] || 'default';
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'default',
      in_progress: 'primary',
      awaiting_proof: 'warning',
      completed: 'success',
      failed: 'error',
    };
    return colors[status] || 'default';
  };

  if (loading) {
    return (
      <Container>
        <Box sx={{ textAlign: 'center', mt: 8 }}>
          <Typography>Loading...</Typography>
        </Box>
      </Container>
    );
  }

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            TaskMe
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {/* Credit Balance */}
            <CreditBalance variant="compact" onClick={() => navigate('/wallet')} />
            
            <Box sx={{ textAlign: 'right' }}>
              <Typography variant="body2">{user?.username}</Typography>
              <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <StarIcon sx={{ fontSize: 16 }} />
                Level {user?.level} | {user?.total_points} pts
              </Typography>
            </Box>
            <IconButton color="inherit" onClick={() => navigate('/wallet')} title="Wallet">
              <WalletIcon />
            </IconButton>
            <Tooltip title="Debug Feedback (Ctrl+Shift+D)">
              <IconButton 
                color="inherit" 
                onClick={() => {
                  // Trigger the global debug panel via custom event
                  window.dispatchEvent(new CustomEvent('openDebugPanel'));
                }}
                sx={{ 
                  bgcolor: 'rgba(255,255,255,0.1)',
                  '&:hover': { bgcolor: 'rgba(255,255,255,0.2)' }
                }}
              >
                <BugReportIcon />
              </IconButton>
            </Tooltip>
            <IconButton color="inherit" onClick={handleLogout}>
              <LogoutIcon />
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ mb: 4 }}>
          <Grid container spacing={3}>
            <Grid item xs={6} sm={3}>
              <Card sx={{ bgcolor: 'primary.main', color: 'white' }}>
                <CardContent sx={{ py: 2 }}>
                  <Typography variant="body2">Gesamt</Typography>
                  <Typography variant="h4">{tasks.length}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card sx={{ bgcolor: 'error.main', color: 'white' }}>
                <CardContent sx={{ py: 2 }}>
                  <Typography variant="body2">Offen</Typography>
                  <Typography variant="h4">{sortedOpenTasks.length}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card sx={{ bgcolor: 'success.main', color: 'white' }}>
                <CardContent sx={{ py: 2 }}>
                  <Typography variant="body2">Erledigt</Typography>
                  <Typography variant="h4">{completedTasks.length}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card sx={{ bgcolor: 'warning.main', color: 'white' }}>
                <CardContent sx={{ py: 2 }}>
                  <Typography variant="body2">Punkte</Typography>
                  <Typography variant="h4">{user?.total_points || 0}</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>

        {/* Open Tasks Section */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="h5">Offene Tasks</Typography>
              {sortedOpenTasks.some(t => getTimeCriticalStatus(t)?.color === 'error') && (
                <Tooltip title="Zeitkritische Tasks vorhanden!">
                  <WarningIcon color="error" />
                </Tooltip>
              )}
            </Box>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <ToggleButtonGroup
                value={sortBy}
                exclusive
                onChange={(e, val) => val && setSortBy(val)}
                size="small"
              >
                <ToggleButton value="urgency">
                  <Tooltip title="Nach Dringlichkeit">
                    <WarningIcon fontSize="small" />
                  </Tooltip>
                </ToggleButton>
                <ToggleButton value="priority">
                  <Tooltip title="Nach Priorität">
                    <PriorityIcon fontSize="small" />
                  </Tooltip>
                </ToggleButton>
                <ToggleButton value="due_date">
                  <Tooltip title="Nach Fälligkeit">
                    <ScheduleIcon fontSize="small" />
                  </Tooltip>
                </ToggleButton>
                <ToggleButton value="created">
                  <Tooltip title="Nach Erstellung">
                    <SortIcon fontSize="small" />
                  </Tooltip>
                </ToggleButton>
              </ToggleButtonGroup>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setOpenDialog(true)}
              >
                Neuer Task
              </Button>
            </Box>
          </Box>

          <Grid container spacing={2}>
            {sortedOpenTasks.map((task) => {
              const timeCritical = getTimeCriticalStatus(task);
              return (
                <Grid item xs={12} sm={6} md={4} key={task.id}>
                  <Card 
                    sx={{ 
                      borderLeft: timeCritical ? 4 : 0,
                      borderColor: timeCritical ? `${timeCritical.color}.main` : 'transparent',
                      transition: 'all 0.2s',
                      '&:hover': { transform: 'translateY(-2px)', boxShadow: 3 },
                    }}
                  >
                    <CardContent>
                      {timeCritical && (
                        <Box sx={{ mb: 1.5 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                            <ScheduleIcon sx={{ fontSize: 14, color: `${timeCritical.color}.main` }} />
                            <Typography variant="caption" color={`${timeCritical.color}.main`} fontWeight={600}>
                              {timeCritical.label}
                            </Typography>
                          </Box>
                          <LinearProgress 
                            variant="determinate" 
                            value={timeCritical.progress} 
                            color={timeCritical.color}
                            sx={{ height: 3, borderRadius: 1 }}
                          />
                        </Box>
                      )}
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Chip
                          label={task.priority}
                          size="small"
                          color={getPriorityColor(task.priority)}
                        />
                        <Chip
                          label={task.status}
                          size="small"
                          color={getStatusColor(task.status)}
                        />
                      </Box>
                      <Typography variant="h6" gutterBottom noWrap>
                        {task.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2, height: 40, overflow: 'hidden' }}>
                        {task.description || 'Keine Beschreibung'}
                      </Typography>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Chip
                          icon={<TrophyIcon />}
                          label={`${task.reward_points} pts`}
                          size="small"
                          variant="outlined"
                        />
                        <Button
                          size="small"
                          variant="contained"
                          color="success"
                          startIcon={<CheckIcon />}
                          onClick={() => handleCompleteTask(task.id)}
                          disabled={task.requires_proof && !task.proof}
                        >
                          Erledigt
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>

          {sortedOpenTasks.length === 0 && (
            <Box sx={{ textAlign: 'center', py: 6, bgcolor: 'success.50', borderRadius: 2 }}>
              <CheckIcon sx={{ fontSize: 48, color: 'success.main', mb: 1 }} />
              <Typography variant="h6" color="success.main">
                Alle Tasks erledigt! 🎉
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Erstelle einen neuen Task um weiterzumachen.
              </Typography>
            </Box>
          )}
        </Box>

        {/* Completed Tasks Section */}
        {completedTasks.length > 0 && (
          <Box sx={{ mb: 4 }}>
            <Typography variant="h5" sx={{ mb: 2, color: 'text.secondary' }}>
              Erledigte Tasks ({completedTasks.length})
            </Typography>
            <Grid container spacing={2}>
              {completedTasks.slice(0, 6).map((task) => (
                <Grid item xs={12} sm={6} md={4} key={task.id}>
                  <Card sx={{ opacity: 0.7 }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Chip label={task.priority} size="small" color="default" />
                        <Chip label="✓ Erledigt" size="small" color="success" />
                      </Box>
                      <Typography variant="h6" gutterBottom noWrap sx={{ textDecoration: 'line-through' }}>
                        {task.title}
                      </Typography>
                      <Chip icon={<TrophyIcon />} label={`+${task.reward_points} pts`} size="small" color="success" variant="outlined" />
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </Container>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Neuer Task</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Titel"
            value={newTask.title}
            onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Beschreibung"
            value={newTask.description}
            onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
            margin="normal"
            multiline
            rows={3}
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Priorität</InputLabel>
            <Select
              value={newTask.priority}
              label="Priorität"
              onChange={(e) => setNewTask({ ...newTask, priority: e.target.value })}
            >
              <MenuItem value="low">Niedrig</MenuItem>
              <MenuItem value="medium">Mittel</MenuItem>
              <MenuItem value="high">Hoch</MenuItem>
              <MenuItem value="urgent">Dringend</MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Fällig am"
            type="datetime-local"
            value={newTask.due_date}
            onChange={(e) => setNewTask({ ...newTask, due_date: e.target.value })}
            margin="normal"
            InputLabelProps={{ shrink: true }}
          />
          <TextField
            fullWidth
            label="Belohnungspunkte"
            type="number"
            value={newTask.reward_points}
            onChange={(e) => setNewTask({ ...newTask, reward_points: parseInt(e.target.value) })}
            margin="normal"
            inputProps={{ min: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Abbrechen</Button>
          <Button onClick={handleCreateTask} variant="contained" disabled={!newTask.title}>
            Erstellen
          </Button>
        </DialogActions>
      </Dialog>

      {/* Voice Memo FAB */}
      <VoiceMemoButton
        onChallengeCreated={(challenge) => {
          setSnackbar({
            open: true,
            message: `Challenge "${challenge.title}" erstellt!`,
            severity: 'success',
          });
          loadTasks();
        }}
      />

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </>
  );
};

export default Dashboard;
