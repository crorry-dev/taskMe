import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardActions,
  Grid,
  Button,
  Avatar,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControlLabel,
  Switch,
  Skeleton,
  Alert,
  Stack,
} from '@mui/material';
import {
  Add as AddIcon,
  Group as TeamIcon,
  People as PeopleIcon,
  ExitToApp as LeaveIcon,
  Login as JoinIcon,
} from '@mui/icons-material';
import Layout from '../components/Layout';
import { teamService } from '../services/apiService';

const TeamsPage = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [myTeams, setMyTeams] = useState([]);
  const [publicTeams, setPublicTeams] = useState([]);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newTeam, setNewTeam] = useState({
    name: '',
    description: '',
    is_public: true,
    max_members: 10,
  });

  useEffect(() => {
    loadTeams();
  }, []);

  const loadTeams = async () => {
    setLoading(true);
    try {
      const [myRes, publicRes] = await Promise.all([
        teamService.getMyTeams(),
        teamService.list({ is_public: true }),
      ]);
      setMyTeams(myRes.data.results || myRes.data || []);
      setPublicTeams((publicRes.data.results || publicRes.data || []).filter(
        t => !myRes.data.some?.(mt => mt.id === t.id) && 
             !(myRes.data.results || []).some(mt => mt.id === t.id)
      ));
      setError(null);
    } catch (err) {
      console.error('Failed to load teams:', err);
      setError('Failed to load teams');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await teamService.create(newTeam);
      setCreateDialogOpen(false);
      setNewTeam({ name: '', description: '', is_public: true, max_members: 10 });
      loadTeams();
    } catch (err) {
      setError('Failed to create team');
    }
  };

  const handleJoin = async (teamId) => {
    try {
      await teamService.join(teamId);
      loadTeams();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to join team');
    }
  };

  const handleLeave = async (teamId) => {
    try {
      await teamService.leave(teamId);
      loadTeams();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to leave team');
    }
  };

  const TeamCard = ({ team, isMember }) => (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flex: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2 }}>
          <Avatar
            src={team.avatar}
            sx={{
              width: 56,
              height: 56,
              background: 'linear-gradient(135deg, #007AFF 0%, #5856D6 100%)',
            }}
          >
            <TeamIcon />
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" fontWeight={600}>
              {team.name}
            </Typography>
            <Stack direction="row" spacing={1} sx={{ mt: 0.5 }}>
              <Chip
                icon={<PeopleIcon />}
                label={`${team.member_count || 0} members`}
                size="small"
                variant="outlined"
              />
              {team.is_public && (
                <Chip label="Public" size="small" color="success" variant="outlined" />
              )}
            </Stack>
          </Box>
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {team.description || 'No description'}
        </Typography>

        {/* Team Stats */}
        <Box sx={{ display: 'flex', gap: 3 }}>
          <Box>
            <Typography variant="h6" fontWeight={700}>
              {team.total_points?.toLocaleString() || 0}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Total XP
            </Typography>
          </Box>
          <Box>
            <Typography variant="h6" fontWeight={700}>
              {team.level || 1}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Level
            </Typography>
          </Box>
        </Box>
      </CardContent>

      <CardActions sx={{ px: 2, pb: 2 }}>
        {isMember ? (
          <Button
            fullWidth
            variant="outlined"
            color="error"
            startIcon={<LeaveIcon />}
            onClick={() => handleLeave(team.id)}
          >
            Leave Team
          </Button>
        ) : (
          <Button
            fullWidth
            variant="contained"
            startIcon={<JoinIcon />}
            onClick={() => handleJoin(team.id)}
            disabled={team.max_members && team.member_count >= team.max_members}
          >
            {team.max_members && team.member_count >= team.max_members 
              ? 'Team Full' 
              : 'Join Team'}
          </Button>
        )}
      </CardActions>
    </Card>
  );

  return (
    <Layout>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Teams
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Join forces and compete together
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
          size="large"
        >
          Create Team
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Grid container spacing={3}>
          {[...Array(4)].map((_, i) => (
            <Grid item xs={12} sm={6} md={4} key={i}>
              <Skeleton variant="rounded" height={240} />
            </Grid>
          ))}
        </Grid>
      ) : (
        <>
          {/* My Teams */}
          <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
            My Teams
          </Typography>
          {myTeams.length === 0 ? (
            <Box 
              sx={{ 
                textAlign: 'center', 
                py: 6, 
                backgroundColor: 'grey.50', 
                borderRadius: 2,
                mb: 4,
              }}
            >
              <TeamIcon sx={{ fontSize: 48, color: 'grey.400', mb: 1 }} />
              <Typography variant="body1" color="text.secondary">
                You're not part of any team yet
              </Typography>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={() => setCreateDialogOpen(true)}
                sx={{ mt: 2 }}
              >
                Create a Team
              </Button>
            </Box>
          ) : (
            <Grid container spacing={3} sx={{ mb: 4 }}>
              {myTeams.map((team) => (
                <Grid item xs={12} sm={6} md={4} key={team.id}>
                  <TeamCard team={team} isMember />
                </Grid>
              ))}
            </Grid>
          )}

          {/* Discover Teams */}
          {publicTeams.length > 0 && (
            <>
              <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                Discover Teams
              </Typography>
              <Grid container spacing={3}>
                {publicTeams.map((team) => (
                  <Grid item xs={12} sm={6} md={4} key={team.id}>
                    <TeamCard team={team} isMember={false} />
                  </Grid>
                ))}
              </Grid>
            </>
          )}
        </>
      )}

      {/* Create Team Dialog */}
      <Dialog 
        open={createDialogOpen} 
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Create Team</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Team Name"
            value={newTeam.name}
            onChange={(e) => setNewTeam({ ...newTeam, name: e.target.value })}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Description"
            value={newTeam.description}
            onChange={(e) => setNewTeam({ ...newTeam, description: e.target.value })}
            margin="normal"
            multiline
            rows={3}
          />
          <TextField
            fullWidth
            label="Max Members"
            type="number"
            value={newTeam.max_members}
            onChange={(e) => setNewTeam({ ...newTeam, max_members: parseInt(e.target.value) })}
            margin="normal"
            inputProps={{ min: 2, max: 100 }}
          />
          <FormControlLabel
            control={
              <Switch
                checked={newTeam.is_public}
                onChange={(e) => setNewTeam({ ...newTeam, is_public: e.target.checked })}
              />
            }
            label="Public Team (anyone can join)"
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={handleCreate}
            disabled={!newTeam.name}
          >
            Create Team
          </Button>
        </DialogActions>
      </Dialog>
    </Layout>
  );
};

export default TeamsPage;
