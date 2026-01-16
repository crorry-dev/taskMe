/**
 * DebugPanel Component
 * 
 * Floating debug/QA feedback panel for testers.
 * Allows submitting voice memos or text feedback that gets
 * analyzed by AI and automatically implemented.
 */
import React, { useState, useRef, useEffect } from 'react';
import {
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  IconButton,
  Tooltip,
  Chip,
  Alert,
  LinearProgress,
  Collapse,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Badge,
} from '@mui/material';
import {
  BugReport,
  Mic,
  MicOff,
  Send,
  Close,
  AutoAwesome,
  Code,
  ExpandMore,
  ExpandLess,
  Lightbulb,
  Palette,
  Build,
} from '@mui/icons-material';
import debugService from '../../services/debugService';
import { useAuth } from '../../contexts/AuthContext';

const FEEDBACK_TYPE_ICONS = {
  bug: <BugReport color="error" />,
  feature: <Lightbulb color="primary" />,
  ui_change: <Palette color="secondary" />,
  improvement: <Build color="action" />,
};

const STATUS_COLORS = {
  pending: 'default',
  analyzing: 'info',
  analyzed: 'primary',
  implementing: 'warning',
  implemented: 'success',
  committed: 'success',
  rejected: 'error',
  failed: 'error',
};

const DebugPanel = ({ position = 'bottom-left', externalOpen = false, onClose = null }) => {
  const { user } = useAuth();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Sync with external open state
  useEffect(() => {
    if (externalOpen) {
      setOpen(true);
    }
  }, [externalOpen]);

  // Handle close with callback
  const handleClose = () => {
    setOpen(false);
    if (onClose) onClose();
  };
  
  // Input state
  const [textInput, setTextInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  
  // Result state
  const [lastFeedback, setLastFeedback] = useState(null);
  const [showDetails, setShowDetails] = useState(false);
  
  // Recording refs
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);
  
  // Position styles
  const positionStyles = {
    'bottom-left': { bottom: 24, left: 24 },
    'bottom-right': { bottom: 24, right: 24 },
    'top-left': { top: 80, left: 24 },
    'top-right': { top: 80, right: 24 },
  };

  // Start recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];
      
      mediaRecorderRef.current.ondataavailable = (e) => {
        audioChunksRef.current.push(e.data);
      };
      
      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorderRef.current.start();
      setIsRecording(true);
      setRecordingTime(0);
      
      timerRef.current = setInterval(() => {
        setRecordingTime(t => t + 1);
      }, 1000);
      
    } catch (err) {
      setError('Mikrofon-Zugriff verweigert');
    }
  };
  
  // Stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      clearInterval(timerRef.current);
    }
  };
  
  // Clear recording
  const clearRecording = () => {
    setAudioBlob(null);
    setRecordingTime(0);
  };
  
  // Submit feedback
  const handleSubmit = async () => {
    if (!textInput.trim() && !audioBlob) {
      setError('Bitte Text eingeben oder Sprachaufnahme machen');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const data = {
        text_input: textInput,
        page_url: window.location.href,
        browser_info: debugService.getBrowserInfo(),
      };
      
      if (audioBlob) {
        data.voice_memo = new File([audioBlob], 'feedback.webm', { type: 'audio/webm' });
      }
      
      const result = await debugService.submitFeedback(data);
      
      setLastFeedback(result);
      setSuccess('Feedback gesendet! AI analysiert...');
      setTextInput('');
      setAudioBlob(null);
      
      // Show details after short delay
      setTimeout(() => {
        setShowDetails(true);
      }, 1000);
      
    } catch (err) {
      setError(err.response?.data?.error || 'Fehler beim Senden');
    } finally {
      setLoading(false);
    }
  };
  
  // Format time
  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  // Keyboard shortcut: Ctrl+Shift+D or Cmd+Shift+D to open
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
        e.preventDefault();
        setOpen(prev => !prev);
      }
    };
    
    // Also listen for custom event from navbar button
    const handleOpenEvent = () => setOpen(true);
    
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('openDebugPanel', handleOpenEvent);
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('openDebugPanel', handleOpenEvent);
    };
  }, []);

  // Only show for authenticated users
  if (!user) return null;

  return (
    <>
      {/* Floating Action Button - only show if not externally controlled */}
      {!externalOpen && (
        <Tooltip title="Debug Feedback (Ctrl+Shift+D)" placement="right">
          <Fab
            color="warning"
            onClick={() => setOpen(true)}
            sx={{
              position: 'fixed',
              ...positionStyles[position],
              zIndex: 1000,
            }}
          >
            <Badge 
              badgeContent={lastFeedback?.status === 'analyzed' ? '!' : 0} 
              color="error"
            >
              <BugReport />
            </Badge>
          </Fab>
        </Tooltip>
      )}

      {/* Feedback Dialog */}
      <Dialog
        open={open}
        onClose={handleClose}
        maxWidth="sm"
        fullWidth
        PaperProps={{ sx: { borderRadius: 3 } }}
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <BugReport color="warning" />
          Debug Feedback
          <Chip 
            label="Ctrl+Shift+D" 
            size="small" 
            sx={{ ml: 1, fontSize: 10, height: 20 }} 
          />
          <Box sx={{ flexGrow: 1 }} />
          <IconButton onClick={handleClose} size="small">
            <Close />
          </IconButton>
        </DialogTitle>

        <DialogContent>
          {/* Alerts */}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}
          {success && (
            <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
              {success}
            </Alert>
          )}

          {/* Instructions */}
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Beschreibe was geändert werden soll. Die AI analysiert dein Feedback
            und schlägt Code-Änderungen vor.
          </Typography>

          {/* Text Input */}
          <TextField
            fullWidth
            multiline
            rows={3}
            placeholder="z.B. 'Die Buttons sollten ein dunkleres Blau haben' oder 'Der Login funktioniert nicht wenn...'"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            disabled={loading}
            sx={{ mb: 2 }}
          />

          {/* Voice Recording */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Oder per Sprache:
            </Typography>
            
            {!isRecording && !audioBlob && (
              <Button
                variant="outlined"
                startIcon={<Mic />}
                onClick={startRecording}
                disabled={loading}
              >
                Aufnehmen
              </Button>
            )}
            
            {isRecording && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip
                  icon={<MicOff />}
                  label={formatTime(recordingTime)}
                  color="error"
                  onClick={stopRecording}
                />
                <Typography variant="caption" color="error">
                  Aufnahme läuft...
                </Typography>
              </Box>
            )}
            
            {audioBlob && !isRecording && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip
                  label={`Aufnahme (${formatTime(recordingTime)})`}
                  color="success"
                  onDelete={clearRecording}
                />
              </Box>
            )}
          </Box>

          {/* Loading */}
          {loading && (
            <Box sx={{ mb: 2 }}>
              <LinearProgress />
              <Typography variant="caption" color="text.secondary">
                AI analysiert Feedback...
              </Typography>
            </Box>
          )}

          {/* Last Feedback Result */}
          {lastFeedback && (
            <Box sx={{ mt: 2 }}>
              <Divider sx={{ mb: 2 }} />
              
              <Box 
                sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 1, 
                  cursor: 'pointer' 
                }}
                onClick={() => setShowDetails(!showDetails)}
              >
                <AutoAwesome color="secondary" />
                <Typography variant="subtitle2">
                  Letztes Feedback
                </Typography>
                <Chip
                  size="small"
                  label={lastFeedback.status}
                  color={STATUS_COLORS[lastFeedback.status] || 'default'}
                />
                <Box sx={{ flexGrow: 1 }} />
                {showDetails ? <ExpandLess /> : <ExpandMore />}
              </Box>

              <Collapse in={showDetails}>
                <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
                  {/* Type & Priority */}
                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <Chip
                      size="small"
                      icon={FEEDBACK_TYPE_ICONS[lastFeedback.feedback_type]}
                      label={lastFeedback.feedback_type}
                    />
                    <Chip
                      size="small"
                      label={`Priorität: ${lastFeedback.priority}`}
                      color={lastFeedback.priority === 'high' ? 'warning' : 'default'}
                    />
                    {lastFeedback.ai_confidence > 0 && (
                      <Chip
                        size="small"
                        label={`${Math.round(lastFeedback.ai_confidence * 100)}% Konfidenz`}
                      />
                    )}
                  </Box>

                  {/* AI Analysis */}
                  {lastFeedback.ai_analysis?.summary && (
                    <Typography variant="body2" sx={{ mb: 2 }}>
                      <strong>AI Analyse:</strong> {lastFeedback.ai_analysis.summary}
                    </Typography>
                  )}

                  {/* Suggested Changes */}
                  {lastFeedback.ai_suggested_changes?.length > 0 && (
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
                        Vorgeschlagene Änderungen:
                      </Typography>
                      <List dense>
                        {lastFeedback.ai_suggested_changes.map((change, i) => (
                          <ListItem key={i} sx={{ py: 0 }}>
                            <ListItemIcon sx={{ minWidth: 32 }}>
                              <Code fontSize="small" />
                            </ListItemIcon>
                            <ListItemText
                              primary={change.file}
                              secondary={change.description}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}
                </Box>
              </Collapse>
            </Box>
          )}
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Typography variant="caption" color="text.secondary" sx={{ mr: 'auto' }}>
            Kostet 1 Credit pro Feedback
          </Typography>
          <Button onClick={() => setOpen(false)}>
            Schließen
          </Button>
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={loading || (!textInput.trim() && !audioBlob)}
            startIcon={loading ? null : <Send />}
          >
            {loading ? 'Analysiere...' : 'Senden'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default DebugPanel;
