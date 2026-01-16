import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Chip,
  Stack,
  Skeleton,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckIcon,
  RadioButtonUnchecked as UncheckedIcon,
} from '@mui/icons-material';
import Layout from '../components/Layout';
import { taskService } from '../services/apiService';

const priorityConfig = {
  low: { color: 'default', label: 'Low' },
  medium: { color: 'warning', label: 'Medium' },
  high: { color: 'error', label: 'High' },
};

const TasksPage = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [filter, setFilter] = useState('all');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    priority: 'medium',
    reward_points: 10,
  });

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    setLoading(true);
    try {
      const response = await taskService.list();
      setTasks(response.data.results || response.data || []);
      setError(null);
    } catch (err) {
      console.error('Failed to load tasks:', err);
      setError('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await taskService.create(newTask);
      setCreateDialogOpen(false);
      setNewTask({ title: '', description: '', priority: 'medium', reward_points: 10 });
      loadTasks();
    } catch (err) {
      setError('Failed to create task');
    }
  };

  const handleComplete = async (taskId) => {
    try {
      await taskService.complete(taskId);
      loadTasks();
    } catch (err) {
      setError('Failed to complete task');
    }
  };

  const handleDelete = async (taskId) => {
    try {
      await taskService.delete(taskId);
      loadTasks();
    } catch (err) {
      setError('Failed to delete task');
    }
  };

  const filteredTasks = tasks.filter(task => {
    if (filter === 'active') return !task.completed;
    if (filter === 'completed') return task.completed;
    return true;
  });

  const activeTasks = tasks.filter(t => !t.completed).length;
  const completedTasks = tasks.filter(t => t.completed).length;

  return (
    <Layout>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Tasks
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {activeTasks} active, {completedTasks} completed
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
          size="large"
        >
          Add Task
        </Button>
      </Box>

      {/* Filter Chips */}
      <Stack direction="row" spacing={1} sx={{ mb: 3 }}>
        {['all', 'active', 'completed'].map((f) => (
          <Chip
            key={f}
            label={f.charAt(0).toUpperCase() + f.slice(1)}
            onClick={() => setFilter(f)}
            color={filter === f ? 'primary' : 'default'}
            variant={filter === f ? 'filled' : 'outlined'}
          />
        ))}
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Tasks List */}
      {loading ? (
        <Stack spacing={2}>
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} variant="rounded" height={72} />
          ))}
        </Stack>
      ) : filteredTasks.length === 0 ? (
        <Box 
          sx={{ 
            textAlign: 'center', 
            py: 8, 
            backgroundColor: 'grey.50', 
            borderRadius: 2 
          }}
        >
          <CheckIcon sx={{ fontSize: 48, color: 'grey.400', mb: 1 }} />
          <Typography variant="h6" color="text.secondary">
            {filter === 'all' ? 'No tasks yet' : `No ${filter} tasks`}
          </Typography>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
            sx={{ mt: 2 }}
          >
            Add Your First Task
          </Button>
        </Box>
      ) : (
        <Stack spacing={1.5}>
          {filteredTasks.map((task) => (
            <Card 
              key={task.id}
              sx={{ 
                opacity: task.completed ? 0.7 : 1,
                transition: 'all 0.2s',
              }}
            >
              <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2, py: 1.5 }}>
                <IconButton
                  onClick={() => handleComplete(task.id)}
                  disabled={task.completed}
                  color={task.completed ? 'success' : 'default'}
                >
                  {task.completed ? <CheckIcon /> : <UncheckedIcon />}
                </IconButton>
                
                <Box sx={{ flex: 1 }}>
                  <Typography 
                    variant="subtitle1" 
                    fontWeight={500}
                    sx={{ 
                      textDecoration: task.completed ? 'line-through' : 'none',
                    }}
                  >
                    {task.title}
                  </Typography>
                  {task.description && (
                    <Typography variant="body2" color="text.secondary">
                      {task.description}
                    </Typography>
                  )}
                </Box>

                <Chip 
                  label={priorityConfig[task.priority]?.label || task.priority}
                  size="small"
                  color={priorityConfig[task.priority]?.color || 'default'}
                  variant="outlined"
                />

                <Chip
                  label={`+${task.reward_points} XP`}
                  size="small"
                  color="primary"
                  variant="outlined"
                />

                <IconButton
                  onClick={() => handleDelete(task.id)}
                  color="error"
                  size="small"
                >
                  <DeleteIcon />
                </IconButton>
              </CardContent>
            </Card>
          ))}
        </Stack>
      )}

      {/* Create Task Dialog */}
      <Dialog 
        open={createDialogOpen} 
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Add New Task</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Title"
            value={newTask.title}
            onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
            margin="normal"
            required
            autoFocus
          />
          <TextField
            fullWidth
            label="Description"
            value={newTask.description}
            onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
            margin="normal"
            multiline
            rows={2}
          />
          <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
            <FormControl sx={{ flex: 1 }}>
              <InputLabel>Priority</InputLabel>
              <Select
                value={newTask.priority}
                label="Priority"
                onChange={(e) => setNewTask({ ...newTask, priority: e.target.value })}
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="XP Reward"
              type="number"
              value={newTask.reward_points}
              onChange={(e) => setNewTask({ ...newTask, reward_points: parseInt(e.target.value) })}
              sx={{ flex: 1 }}
              inputProps={{ min: 1, max: 100 }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={handleCreate}
            disabled={!newTask.title}
          >
            Add Task
          </Button>
        </DialogActions>
      </Dialog>
    </Layout>
  );
};

export default TasksPage;
