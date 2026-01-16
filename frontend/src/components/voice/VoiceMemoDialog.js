/**
 * VoiceMemoDialog Component
 * 
 * Full dialog for TaskMeMemo voice recording and challenge creation.
 */
import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Stepper,
  Step,
  StepLabel,
  CircularProgress,
  Alert,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Paper,
} from '@mui/material';
import {
  Mic,
  AutoAwesome,
  Edit,
  CheckCircle,
  Error,
} from '@mui/icons-material';
import VoiceRecorder from './VoiceRecorder';
import voiceMemoService from '../../services/voiceMemoService';
import { CostIndicator } from '../credits';
import { creditService } from '../../services';

const steps = ['Aufnehmen', 'AI Analyse', 'Bestätigen'];

const CHALLENGE_TYPE_LABELS = {
  todo: 'Todo',
  streak: 'Streak',
  quantified: 'Ziel mit Zahl',
  duel: 'Duel',
  team: 'Team Challenge',
  community: 'Community',
};

const VoiceMemoDialog = ({ open, onClose, onChallengeCreated }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Memo state
  const [memoId, setMemoId] = useState(null);
  const [transcription, setTranscription] = useState('');
  const [parsedData, setParsedData] = useState(null);
  const [editedData, setEditedData] = useState({});
  
  // Cost calculation
  const [challengeCost, setChallengeCost] = useState(null);
  const [currentBalance, setCurrentBalance] = useState(0);

  const handleRecordingComplete = async (audioBlob, duration) => {
    setLoading(true);
    setError(null);
    
    try {
      // Create file from blob
      const file = new File([audioBlob], 'recording.webm', { type: audioBlob.type });
      
      // Upload memo
      const uploadResult = await voiceMemoService.upload(file, duration);
      setMemoId(uploadResult.id);
      
      // Process (transcribe + parse)
      const processResult = await voiceMemoService.process(uploadResult.id);
      
      setTranscription(processResult.transcription);
      setParsedData(processResult.parsed_data);
      setEditedData(processResult.parsed_data);
      
      // Calculate cost
      const costResult = await creditService.calculateCost(
        processResult.parsed_data.challenge_type,
        processResult.parsed_data.proof_type
      );
      setChallengeCost(costResult);
      setCurrentBalance(costResult.current_balance);
      
      setActiveStep(2);
    } catch (err) {
      console.error('Processing failed:', err);
      setError(err.response?.data?.error || 'Verarbeitung fehlgeschlagen');
      setActiveStep(0);
    } finally {
      setLoading(false);
    }
  };

  const handleEditField = (field, value) => {
    setEditedData(prev => ({ ...prev, [field]: value }));
    
    // Recalculate cost if challenge type changes
    if (field === 'challenge_type' || field === 'proof_type') {
      creditService.calculateCost(
        field === 'challenge_type' ? value : editedData.challenge_type,
        field === 'proof_type' ? value : editedData.proof_type
      ).then(setChallengeCost);
    }
  };

  const handleCreateChallenge = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await voiceMemoService.createChallenge(memoId, editedData);
      
      if (onChallengeCreated) {
        onChallengeCreated(result.challenge);
      }
      
      handleClose();
    } catch (err) {
      console.error('Challenge creation failed:', err);
      setError(err.response?.data?.error || 'Challenge-Erstellung fehlgeschlagen');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setActiveStep(0);
    setMemoId(null);
    setTranscription('');
    setParsedData(null);
    setEditedData({});
    setChallengeCost(null);
    setError(null);
    onClose();
  };

  const handleDismiss = async () => {
    if (memoId) {
      await voiceMemoService.dismiss(memoId);
    }
    handleClose();
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: { borderRadius: 3 }
      }}
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Mic color="primary" />
        TaskMeMemo
      </DialogTitle>

      <DialogContent>
        {/* Stepper */}
        <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
          {steps.map((label, index) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Step Content */}
        {activeStep === 0 && !loading && (
          <Box>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 2, textAlign: 'center' }}>
              Sprich deine Challenge ins Mikrofon. Die AI erkennt automatisch den Typ und die Details.
            </Typography>
            <VoiceRecorder
              onRecordingComplete={handleRecordingComplete}
              onCancel={() => {}}
              maxDuration={120}
            />
            <Box sx={{ mt: 2 }}>
              <Typography variant="caption" color="text.secondary">
                Beispiele:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                <Chip size="small" label='"Ich will 30 Tage keinen Alkohol trinken"' variant="outlined" />
                <Chip size="small" label='"10.000 Schritte täglich für 2 Wochen"' variant="outlined" />
                <Chip size="small" label='"Wette: Du schaffst keine 100 Liegestütze"' variant="outlined" />
              </Box>
            </Box>
          </Box>
        )}

        {loading && (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
            <CircularProgress size={60} />
            <Typography variant="body1" sx={{ mt: 2 }}>
              {activeStep === 0 ? 'Memo wird verarbeitet...' : 'Challenge wird erstellt...'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              AI analysiert deine Aufnahme
            </Typography>
          </Box>
        )}

        {activeStep === 2 && parsedData && !loading && (
          <Box>
            {/* Transcription */}
            <Paper variant="outlined" sx={{ p: 2, mb: 3, bgcolor: 'grey.50' }}>
              <Typography variant="caption" color="text.secondary" gutterBottom>
                Transkription:
              </Typography>
              <Typography variant="body2">"{transcription}"</Typography>
            </Paper>

            {/* AI Confidence */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
              <AutoAwesome color="secondary" sx={{ fontSize: 20 }} />
              <Typography variant="body2">
                AI-Konfidenz: {Math.round((parsedData.confidence || 0) * 100)}%
              </Typography>
              {parsedData.confidence >= 0.7 ? (
                <CheckCircle color="success" sx={{ fontSize: 18 }} />
              ) : (
                <Error color="warning" sx={{ fontSize: 18 }} />
              )}
            </Box>

            {/* Editable Fields */}
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <TextField
                label="Titel"
                value={editedData.title || ''}
                onChange={(e) => handleEditField('title', e.target.value)}
                fullWidth
                size="small"
              />

              <FormControl fullWidth size="small">
                <InputLabel>Challenge-Typ</InputLabel>
                <Select
                  value={editedData.challenge_type || 'todo'}
                  onChange={(e) => handleEditField('challenge_type', e.target.value)}
                  label="Challenge-Typ"
                >
                  {Object.entries(CHALLENGE_TYPE_LABELS).map(([value, label]) => (
                    <MenuItem key={value} value={value}>{label}</MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Box sx={{ display: 'flex', gap: 2 }}>
                <TextField
                  label="Zielwert"
                  type="number"
                  value={editedData.target_value || 1}
                  onChange={(e) => handleEditField('target_value', parseInt(e.target.value))}
                  size="small"
                  sx={{ flex: 1 }}
                />
                <TextField
                  label="Einheit"
                  value={editedData.unit || ''}
                  onChange={(e) => handleEditField('unit', e.target.value)}
                  size="small"
                  placeholder="z.B. Tage, km"
                  sx={{ flex: 1 }}
                />
              </Box>

              <TextField
                label="Dauer (Tage)"
                type="number"
                value={editedData.duration_days || 7}
                onChange={(e) => handleEditField('duration_days', parseInt(e.target.value))}
                size="small"
              />

              <FormControl fullWidth size="small">
                <InputLabel>Proof-Typ</InputLabel>
                <Select
                  value={editedData.proof_type || 'SELF'}
                  onChange={(e) => handleEditField('proof_type', e.target.value)}
                  label="Proof-Typ"
                >
                  <MenuItem value="SELF">Selbstbestätigung</MenuItem>
                  <MenuItem value="PHOTO">Foto-Beweis</MenuItem>
                  <MenuItem value="PEER">Peer-Bestätigung</MenuItem>
                </Select>
              </FormControl>

              <TextField
                label="Beschreibung"
                value={editedData.description || ''}
                onChange={(e) => handleEditField('description', e.target.value)}
                multiline
                rows={2}
                fullWidth
                size="small"
              />
            </Box>

            {/* Cost */}
            {challengeCost && (
              <Box sx={{ mt: 3 }}>
                <CostIndicator
                  cost={challengeCost.total_cost}
                  currentBalance={currentBalance}
                  variant="detailed"
                  breakdown={{
                    baseCost: challengeCost.base_cost,
                    proofCost: challengeCost.proof_cost,
                  }}
                />
              </Box>
            )}
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 3 }}>
        {activeStep === 0 ? (
          <Button onClick={handleClose}>Abbrechen</Button>
        ) : (
          <>
            <Button onClick={handleDismiss} color="inherit">
              Verwerfen
            </Button>
            <Button
              variant="contained"
              onClick={handleCreateChallenge}
              disabled={loading || (challengeCost && !challengeCost.can_afford)}
              startIcon={loading ? <CircularProgress size={16} /> : <CheckCircle />}
            >
              Challenge erstellen
            </Button>
          </>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default VoiceMemoDialog;
