import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stepper,
  Step,
  StepLabel,
  Typography,
  Chip,
  Stack,
  Alert,
  IconButton,
} from '@mui/material';
import {
  Close as CloseIcon,
  Flag as FlagIcon,
} from '@mui/icons-material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

const challengeTypes = [
  { value: 'todo', label: 'One-time Todo', description: 'Complete a single task', icon: '✓' },
  { value: 'streak', label: 'Streak/Habit', description: 'Build a daily habit', icon: '🔥' },
  { value: 'quantified', label: 'Quantified Goal', description: 'Track a measurable target', icon: '📊' },
  { value: 'duel', label: 'Duel', description: 'Challenge a friend', icon: '⚔️' },
  { value: 'team', label: 'Team Challenge', description: 'Compete as a team', icon: '👥' },
];

const proofTypes = [
  { value: 'SELF', label: 'Self Confirmation', description: 'Honor system' },
  { value: 'PHOTO', label: 'Photo Proof', description: 'Upload a photo' },
  { value: 'PEER', label: 'Peer Verification', description: 'Others confirm' },
  { value: 'DOCUMENT', label: 'Document', description: 'Upload proof document' },
];

const steps = ['Type', 'Details', 'Rules', 'Review'];

const CreateChallengeDialog = ({ open, onClose, onSubmit }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const [formData, setFormData] = useState({
    challenge_type: 'todo',
    title: '',
    description: '',
    goal: '',
    target_value: 1,
    unit: '',
    start_date: new Date(),
    end_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 1 week from now
    visibility: 'private',
    required_proof_types: ['SELF'],
    min_peer_approvals: 1,
    reward_points: 50,
    max_participants: null,
  });

  const handleChange = (field) => (event) => {
    setFormData({ ...formData, [field]: event.target.value });
  };

  const handleProofTypeToggle = (proofType) => {
    const current = formData.required_proof_types;
    if (current.includes(proofType)) {
      setFormData({ 
        ...formData, 
        required_proof_types: current.filter(t => t !== proofType) 
      });
    } else {
      setFormData({ 
        ...formData, 
        required_proof_types: [...current, proofType] 
      });
    }
  };

  const handleNext = () => {
    if (activeStep === 0 && !formData.challenge_type) {
      setError('Please select a challenge type');
      return;
    }
    if (activeStep === 1 && (!formData.title || !formData.goal)) {
      setError('Please fill in all required fields');
      return;
    }
    setError('');
    setActiveStep((prev) => prev + 1);
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    
    try {
      await onSubmit(formData);
      onClose();
      // Reset form
      setActiveStep(0);
      setFormData({
        challenge_type: 'todo',
        title: '',
        description: '',
        goal: '',
        target_value: 1,
        unit: '',
        start_date: new Date(),
        end_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
        visibility: 'private',
        required_proof_types: ['SELF'],
        min_peer_approvals: 1,
        reward_points: 50,
        max_participants: null,
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create challenge');
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0: // Type Selection
        return (
          <Box sx={{ py: 2 }}>
            <Typography variant="h6" gutterBottom>
              What type of challenge?
            </Typography>
            <Stack spacing={1.5}>
              {challengeTypes.map((type) => (
                <Box
                  key={type.value}
                  onClick={() => setFormData({ ...formData, challenge_type: type.value })}
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    border: '2px solid',
                    borderColor: formData.challenge_type === type.value 
                      ? 'primary.main' 
                      : 'grey.200',
                    backgroundColor: formData.challenge_type === type.value 
                      ? 'primary.50' 
                      : 'transparent',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 2,
                    '&:hover': {
                      borderColor: 'primary.light',
                    },
                  }}
                >
                  <Box sx={{ fontSize: 32 }}>{type.icon}</Box>
                  <Box>
                    <Typography variant="subtitle1" fontWeight={600}>
                      {type.label}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {type.description}
                    </Typography>
                  </Box>
                </Box>
              ))}
            </Stack>
          </Box>
        );

      case 1: // Details
        return (
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <Box sx={{ py: 2 }}>
              <Typography variant="h6" gutterBottom>
                Challenge Details
              </Typography>
              
              <TextField
                fullWidth
                label="Title"
                value={formData.title}
                onChange={handleChange('title')}
                margin="normal"
                required
                placeholder="e.g., Run 5km every day"
              />
              
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={handleChange('description')}
                margin="normal"
                multiline
                rows={3}
                placeholder="Describe your challenge..."
              />
              
              <TextField
                fullWidth
                label="Goal"
                value={formData.goal}
                onChange={handleChange('goal')}
                margin="normal"
                required
                placeholder="What needs to be achieved?"
              />
              
              <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                <TextField
                  label="Target Value"
                  type="number"
                  value={formData.target_value}
                  onChange={handleChange('target_value')}
                  sx={{ flex: 1 }}
                  inputProps={{ min: 1 }}
                />
                <TextField
                  label="Unit"
                  value={formData.unit}
                  onChange={handleChange('unit')}
                  sx={{ flex: 1 }}
                  placeholder="e.g., km, reps, days"
                />
              </Box>
              
              <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                <DateTimePicker
                  label="Start Date"
                  value={formData.start_date}
                  onChange={(date) => setFormData({ ...formData, start_date: date })}
                  sx={{ flex: 1 }}
                />
                <DateTimePicker
                  label="End Date"
                  value={formData.end_date}
                  onChange={(date) => setFormData({ ...formData, end_date: date })}
                  sx={{ flex: 1 }}
                />
              </Box>
            </Box>
          </LocalizationProvider>
        );

      case 2: // Rules
        return (
          <Box sx={{ py: 2 }}>
            <Typography variant="h6" gutterBottom>
              Challenge Rules
            </Typography>
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Visibility</InputLabel>
              <Select
                value={formData.visibility}
                label="Visibility"
                onChange={handleChange('visibility')}
              >
                <MenuItem value="private">Private (Only you)</MenuItem>
                <MenuItem value="invite">Invite Only</MenuItem>
                <MenuItem value="team">Team Only</MenuItem>
                <MenuItem value="public">Public</MenuItem>
              </Select>
            </FormControl>
            
            <Typography variant="subtitle2" sx={{ mt: 3, mb: 1 }}>
              Required Proof Types
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              {proofTypes.map((proof) => (
                <Chip
                  key={proof.value}
                  label={proof.label}
                  onClick={() => handleProofTypeToggle(proof.value)}
                  color={formData.required_proof_types.includes(proof.value) ? 'primary' : 'default'}
                  variant={formData.required_proof_types.includes(proof.value) ? 'filled' : 'outlined'}
                  sx={{ mb: 1 }}
                />
              ))}
            </Stack>
            
            {formData.required_proof_types.includes('PEER') && (
              <TextField
                fullWidth
                label="Minimum Peer Approvals"
                type="number"
                value={formData.min_peer_approvals}
                onChange={handleChange('min_peer_approvals')}
                margin="normal"
                inputProps={{ min: 1, max: 10 }}
              />
            )}
            
            <TextField
              fullWidth
              label="Reward XP"
              type="number"
              value={formData.reward_points}
              onChange={handleChange('reward_points')}
              margin="normal"
              inputProps={{ min: 0, max: 1000 }}
              helperText="XP awarded upon completion"
            />
          </Box>
        );

      case 3: // Review
        const selectedType = challengeTypes.find(t => t.value === formData.challenge_type);
        return (
          <Box sx={{ py: 2 }}>
            <Typography variant="h6" gutterBottom>
              Review Your Challenge
            </Typography>
            
            <Box 
              sx={{ 
                p: 3, 
                borderRadius: 2, 
                backgroundColor: 'grey.50',
                mb: 2,
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <Box sx={{ fontSize: 40 }}>{selectedType?.icon}</Box>
                <Box>
                  <Typography variant="h5" fontWeight={600}>
                    {formData.title}
                  </Typography>
                  <Chip label={selectedType?.label} size="small" color="primary" />
                </Box>
              </Box>
              
              <Typography variant="body1" paragraph>
                {formData.description || 'No description'}
              </Typography>
              
              <Typography variant="subtitle2" color="text.secondary">
                Goal: {formData.goal}
              </Typography>
              <Typography variant="subtitle2" color="text.secondary">
                Target: {formData.target_value} {formData.unit}
              </Typography>
              <Typography variant="subtitle2" color="text.secondary">
                Duration: {formData.start_date?.toLocaleDateString()} - {formData.end_date?.toLocaleDateString()}
              </Typography>
              <Typography variant="subtitle2" color="text.secondary">
                Proof: {formData.required_proof_types.join(', ')}
              </Typography>
              <Typography variant="subtitle2" color="text.secondary">
                Reward: {formData.reward_points} XP
              </Typography>
            </Box>
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="sm" 
      fullWidth
      PaperProps={{ sx: { borderRadius: 3 } }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <FlagIcon color="primary" />
            <Typography variant="h6" fontWeight={600}>
              Create Challenge
            </Typography>
          </Box>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent dividers>
        <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {renderStepContent(activeStep)}
      </DialogContent>
      
      <DialogActions sx={{ p: 2, gap: 1 }}>
        {activeStep > 0 && (
          <Button onClick={handleBack}>
            Back
          </Button>
        )}
        <Box sx={{ flex: 1 }} />
        {activeStep < steps.length - 1 ? (
          <Button variant="contained" onClick={handleNext}>
            Next
          </Button>
        ) : (
          <Button 
            variant="contained" 
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? 'Creating...' : 'Create Challenge'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default CreateChallengeDialog;
