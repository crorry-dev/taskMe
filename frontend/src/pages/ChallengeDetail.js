import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  Stack,
  LinearProgress,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider,
  Skeleton,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Tab,
  Tabs,
  IconButton,
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Add as AddIcon,
  EmojiEvents as TrophyIcon,
  People as PeopleIcon,
  AccessTime as TimeIcon,
  Flag as FlagIcon,
  CheckCircle as CheckIcon,
  LocalFireDepartment as StreakIcon,
  CameraAlt as CameraIcon,
} from '@mui/icons-material';
import Layout from '../components/Layout';
import { challengeService, proofService } from '../services/apiService';
import { PhotoUpload, ProofCard, PendingReviewsList } from '../components/ProofComponents';
import { useToast } from '../contexts/ToastContext';

const challengeTypeConfig = {
  todo: { label: 'Todo', color: '#007AFF', icon: '✓' },
  streak: { label: 'Streak', color: '#FF6B35', icon: '🔥' },
  program: { label: 'Program', color: '#5856D6', icon: '📋' },
  quantified: { label: 'Goal', color: '#34C759', icon: '📊' },
  team: { label: 'Team', color: '#FF9500', icon: '👥' },
  duel: { label: 'Duel', color: '#FF3B30', icon: '⚔️' },
};

const statusConfig = {
  active: { label: 'Active', color: 'success' },
  completed: { label: 'Completed', color: 'info' },
  failed: { label: 'Failed', color: 'error' },
  pending: { label: 'Pending', color: 'warning' },
};

const ChallengeDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { success, error: showError } = useToast();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [challenge, setChallenge] = useState(null);
  const [contributions, setContributions] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [tab, setTab] = useState(0);
  
  // Contribution dialog state
  const [contributionDialogOpen, setContributionDialogOpen] = useState(false);
  const [contributionValue, setContributionValue] = useState('1');
  const [contributionNote, setContributionNote] = useState('');
  const [proofFile, setProofFile] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const loadChallenge = useCallback(async () => {
    try {
      setLoading(true);
      const [challengeRes, contributionsRes, leaderboardRes] = await Promise.all([
        challengeService.getById(id),
        challengeService.getContributions(id).catch(() => ({ data: [] })),
        challengeService.getLeaderboard(id).catch(() => ({ data: [] })),
      ]);
      
      setChallenge(challengeRes.data);
      setContributions(contributionsRes.data?.results || contributionsRes.data || []);
      setLeaderboard(leaderboardRes.data?.results || leaderboardRes.data || []);
      setError(null);
    } catch (err) {
      console.error('Failed to load challenge:', err);
      setError('Failed to load challenge details');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadChallenge();
  }, [loadChallenge]);

  const handleAddContribution = async () => {
    try {
      setSubmitting(true);
      
      // Create contribution
      const contributionRes = await challengeService.addContribution(id, {
        value: parseFloat(contributionValue),
        note: contributionNote,
      });
      
      // If there's a proof file, upload it
      if (proofFile && contributionRes.data?.id) {
        const formData = new FormData();
        formData.append('contribution_id', contributionRes.data.id);
        formData.append('proof_type', 'PHOTO');
        formData.append('proof_file', proofFile);
        
        await proofService.create(formData);
      }
      
      // Reload data
      await loadChallenge();
      
      // Reset form
      setContributionDialogOpen(false);
      setContributionValue('1');
      setContributionNote('');
      setProofFile(null);
      
      success('Contribution added successfully! 🎉');
    } catch (err) {
      console.error('Failed to add contribution:', err);
      showError('Failed to add contribution');
    } finally {
      setSubmitting(false);
    }
  };

  const handleJoinChallenge = async () => {
    try {
      await challengeService.join(id);
      await loadChallenge();
      success('You joined the challenge! 💪');
    } catch (err) {
      console.error('Failed to join challenge:', err);
      showError('Failed to join challenge');
    }
  };

  const handleLeaveChallenge = async () => {
    try {
      await challengeService.leave(id);
      await loadChallenge();
      success('You left the challenge');
    } catch (err) {
      console.error('Failed to leave challenge:', err);
      showError('Failed to leave challenge');
    }
  };

  const typeConfig = challenge ? challengeTypeConfig[challenge.challenge_type] || challengeTypeConfig.todo : null;
  const statusCfg = challenge ? statusConfig[challenge.status] || statusConfig.active : null;

  if (loading) {
    return (
      <Layout>
        <Box sx={{ p: 3 }}>
          <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 2, mb: 3 }} />
          <Skeleton variant="rectangular" height={300} sx={{ borderRadius: 2 }} />
        </Box>
      </Layout>
    );
  }

  if (error || !challenge) {
    return (
      <Layout>
        <Box sx={{ p: 3 }}>
          <Alert severity="error">{error || 'Challenge not found'}</Alert>
          <Button startIcon={<BackIcon />} onClick={() => navigate('/challenges')} sx={{ mt: 2 }}>
            Back to Challenges
          </Button>
        </Box>
      </Layout>
    );
  }

  const progress = challenge.target_value 
    ? Math.min(100, (challenge.current_progress / challenge.target_value) * 100)
    : 0;

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <IconButton onClick={() => navigate('/challenges')}>
            <BackIcon />
          </IconButton>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h4" fontWeight={700}>
              {typeConfig?.icon} {challenge.title}
            </Typography>
            <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
              <Chip 
                label={typeConfig?.label} 
                size="small" 
                sx={{ bgcolor: typeConfig?.color, color: 'white' }}
              />
              <Chip 
                label={statusCfg?.label} 
                size="small" 
                color={statusCfg?.color}
              />
              <Chip 
                icon={<TrophyIcon />}
                label={`${challenge.reward_points} XP`} 
                size="small" 
                variant="outlined"
              />
            </Stack>
          </Box>
          
          {challenge.is_participating ? (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setContributionDialogOpen(true)}
            >
              Log Progress
            </Button>
          ) : (
            <Button
              variant="contained"
              color="primary"
              onClick={handleJoinChallenge}
            >
              Join Challenge
            </Button>
          )}
        </Box>

        {/* Progress Card */}
        <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
          <CardContent>
            <Typography variant="h6" color="white" gutterBottom>
              Progress
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <Box sx={{ flex: 1 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={progress}
                  sx={{ 
                    height: 12, 
                    borderRadius: 6,
                    bgcolor: 'rgba(255,255,255,0.3)',
                    '& .MuiLinearProgress-bar': {
                      bgcolor: 'white',
                      borderRadius: 6,
                    }
                  }}
                />
              </Box>
              <Typography variant="h5" color="white" fontWeight={700}>
                {Math.round(progress)}%
              </Typography>
            </Box>
            <Typography color="rgba(255,255,255,0.8)">
              {challenge.current_progress || 0} / {challenge.target_value} {challenge.unit || 'completed'}
            </Typography>
          </CardContent>
        </Card>

        {/* Details Grid */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Description</Typography>
                <Typography color="text.secondary" sx={{ whiteSpace: 'pre-line' }}>
                  {challenge.description || 'No description provided.'}
                </Typography>
                
                <Divider sx={{ my: 2 }} />
                
                <Grid container spacing={2}>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <TimeIcon color="action" />
                      <Typography variant="body2" color="text.secondary">Start</Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {challenge.start_date ? new Date(challenge.start_date).toLocaleDateString() : 'Anytime'}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <FlagIcon color="action" />
                      <Typography variant="body2" color="text.secondary">End</Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {challenge.end_date ? new Date(challenge.end_date).toLocaleDateString() : 'No deadline'}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <PeopleIcon color="action" />
                      <Typography variant="body2" color="text.secondary">Participants</Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {challenge.participant_count || 0}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <CheckIcon color="action" />
                      <Typography variant="body2" color="text.secondary">Proof</Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {challenge.required_proof_types?.join(', ') || 'Self'}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <TrophyIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
                  Leaderboard
                </Typography>
                <List dense>
                  {leaderboard.slice(0, 5).map((participant, index) => (
                    <ListItem key={participant.id} sx={{ px: 0 }}>
                      <ListItemAvatar>
                        <Avatar 
                          sx={{ 
                            bgcolor: index === 0 ? 'gold' : index === 1 ? 'silver' : index === 2 ? '#CD7F32' : 'grey.300',
                            width: 32,
                            height: 32,
                            fontSize: '0.875rem',
                          }}
                        >
                          {index + 1}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText 
                        primary={participant.username}
                        secondary={`${participant.current_progress || 0} ${challenge.unit || 'pts'}`}
                      />
                      {participant.streak_current > 0 && (
                        <Chip 
                          icon={<StreakIcon />}
                          label={participant.streak_current}
                          size="small"
                          color="warning"
                        />
                      )}
                    </ListItem>
                  ))}
                  {leaderboard.length === 0 && (
                    <Typography variant="body2" color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
                      No participants yet
                    </Typography>
                  )}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Tabs for Contributions and Proofs */}
        <Card>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tab} onChange={(e, v) => setTab(v)}>
              <Tab label="My Contributions" />
              <Tab label="Pending Reviews" />
            </Tabs>
          </Box>
          <CardContent>
            {tab === 0 && (
              <Box>
                {contributions.length > 0 ? (
                  <List>
                    {contributions.map((contribution) => (
                      <React.Fragment key={contribution.id}>
                        <ListItem alignItems="flex-start">
                          <ListItemAvatar>
                            <Avatar sx={{ bgcolor: contribution.status === 'approved' ? 'success.main' : 'warning.main' }}>
                              {contribution.status === 'approved' ? <CheckIcon /> : <TimeIcon />}
                            </Avatar>
                          </ListItemAvatar>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Typography fontWeight={600}>
                                  +{contribution.value} {challenge.unit || 'pts'}
                                </Typography>
                                <Chip 
                                  label={contribution.status} 
                                  size="small" 
                                  color={contribution.status === 'approved' ? 'success' : 'warning'}
                                />
                              </Box>
                            }
                            secondary={
                              <>
                                {contribution.note && <Typography variant="body2">{contribution.note}</Typography>}
                                <Typography variant="caption" color="text.secondary">
                                  {new Date(contribution.created_at).toLocaleString()}
                                </Typography>
                              </>
                            }
                          />
                        </ListItem>
                        {contribution.proofs?.map((proof) => (
                          <Box key={proof.id} sx={{ ml: 9, mb: 2 }}>
                            <ProofCard proof={proof} />
                          </Box>
                        ))}
                        <Divider component="li" />
                      </React.Fragment>
                    ))}
                  </List>
                ) : (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography color="text.secondary">No contributions yet</Typography>
                    {challenge.is_participating && (
                      <Button 
                        variant="outlined" 
                        startIcon={<AddIcon />}
                        onClick={() => setContributionDialogOpen(true)}
                        sx={{ mt: 2 }}
                      >
                        Add Your First Contribution
                      </Button>
                    )}
                  </Box>
                )}
              </Box>
            )}
            
            {tab === 1 && (
              <PendingReviewsList challengeId={id} />
            )}
          </CardContent>
        </Card>

        {/* Leave Challenge Button */}
        {challenge.is_participating && !challenge.is_creator && (
          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Button 
              color="error" 
              variant="text"
              onClick={handleLeaveChallenge}
            >
              Leave Challenge
            </Button>
          </Box>
        )}

        {/* Add Contribution Dialog */}
        <Dialog 
          open={contributionDialogOpen} 
          onClose={() => setContributionDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Log Progress</DialogTitle>
          <DialogContent>
            <Stack spacing={3} sx={{ mt: 1 }}>
              <TextField
                label={`Value (${challenge.unit || 'units'})`}
                type="number"
                value={contributionValue}
                onChange={(e) => setContributionValue(e.target.value)}
                fullWidth
                inputProps={{ min: 0, step: 0.1 }}
              />
              
              <TextField
                label="Note (optional)"
                value={contributionNote}
                onChange={(e) => setContributionNote(e.target.value)}
                fullWidth
                multiline
                rows={2}
                placeholder="Add details about your progress..."
              />
              
              {challenge.required_proof_types?.includes('PHOTO') && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    <CameraIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
                    Photo Proof Required
                  </Typography>
                  <PhotoUpload
                    onFileSelect={setProofFile}
                    preview={proofFile ? URL.createObjectURL(proofFile) : null}
                  />
                </Box>
              )}
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setContributionDialogOpen(false)}>
              Cancel
            </Button>
            <Button 
              variant="contained" 
              onClick={handleAddContribution}
              disabled={submitting || !contributionValue}
            >
              {submitting ? 'Submitting...' : 'Submit'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Layout>
  );
};

export default ChallengeDetail;
