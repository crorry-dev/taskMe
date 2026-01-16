/**
 * VoiceRecorder Component
 * 
 * Record audio with waveform visualization for TaskMeMemo feature.
 */
import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  Box,
  IconButton,
  Typography,
  Paper,
  LinearProgress,
  Tooltip,
  Fade,
} from '@mui/material';
import {
  Mic,
  Stop,
  Delete,
  Send,
  PlayArrow,
  Pause,
} from '@mui/icons-material';

const VoiceRecorder = ({
  onRecordingComplete,
  onCancel,
  maxDuration = 120, // Max 2 minutes
  disabled = false,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [duration, setDuration] = useState(0);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [visualizerData, setVisualizerData] = useState([]);

  const mediaRecorderRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const audioRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);
  const animationRef = useRef(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopRecording();
      if (audioUrl) URL.revokeObjectURL(audioUrl);
      if (timerRef.current) clearInterval(timerRef.current);
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [audioUrl]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Setup audio context for visualization
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      analyserRef.current.fftSize = 64;

      // Setup media recorder
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/mp4'
      });

      chunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(chunksRef.current, { 
          type: mediaRecorderRef.current.mimeType 
        });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
        
        // Close audio context
        if (audioContextRef.current) {
          audioContextRef.current.close();
        }
      };

      mediaRecorderRef.current.start(100);
      setIsRecording(true);
      setDuration(0);

      // Start timer
      timerRef.current = setInterval(() => {
        setDuration(prev => {
          if (prev >= maxDuration) {
            stopRecording();
            return prev;
          }
          return prev + 1;
        });
      }, 1000);

      // Start visualization
      visualize();

    } catch (error) {
      console.error('Failed to start recording:', error);
      alert('Mikrofon-Zugriff nicht möglich. Bitte erlaube den Zugriff in deinen Browser-Einstellungen.');
    }
  };

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
        animationRef.current = null;
      }
    }
  }, [isRecording]);

  const visualize = () => {
    if (!analyserRef.current) return;

    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      if (!isRecording) return;
      
      animationRef.current = requestAnimationFrame(draw);
      analyserRef.current.getByteFrequencyData(dataArray);
      
      // Normalize to 0-1 range
      const normalized = Array.from(dataArray).map(v => v / 255);
      setVisualizerData(normalized);
    };

    draw();
  };

  const handleSubmit = () => {
    if (audioBlob && onRecordingComplete) {
      onRecordingComplete(audioBlob, duration);
    }
  };

  const handleCancel = () => {
    setAudioBlob(null);
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
      setAudioUrl(null);
    }
    setDuration(0);
    setVisualizerData([]);
    if (onCancel) onCancel();
  };

  const togglePlayback = () => {
    if (!audioRef.current) return;
    
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Paper
      elevation={0}
      sx={{
        p: 3,
        borderRadius: 3,
        border: '2px solid',
        borderColor: isRecording ? 'error.main' : 'divider',
        bgcolor: isRecording ? 'error.50' : 'background.paper',
        transition: 'all 0.3s ease',
      }}
    >
      {/* Waveform Visualizer */}
      <Box
        sx={{
          height: 60,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 0.5,
          mb: 2,
        }}
      >
        {isRecording ? (
          visualizerData.slice(0, 32).map((value, i) => (
            <Box
              key={i}
              sx={{
                width: 4,
                height: `${Math.max(4, value * 50)}px`,
                bgcolor: 'error.main',
                borderRadius: 1,
                transition: 'height 0.05s ease',
              }}
            />
          ))
        ) : audioUrl ? (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <IconButton onClick={togglePlayback} color="primary">
              {isPlaying ? <Pause /> : <PlayArrow />}
            </IconButton>
            <Typography variant="body2" color="text.secondary">
              Aufnahme anhören
            </Typography>
            <audio
              ref={audioRef}
              src={audioUrl}
              onEnded={() => setIsPlaying(false)}
              style={{ display: 'none' }}
            />
          </Box>
        ) : (
          <Typography variant="body2" color="text.secondary">
            Klicke auf das Mikrofon um aufzunehmen
          </Typography>
        )}
      </Box>

      {/* Timer / Progress */}
      <Box sx={{ mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
          <Typography variant="caption" color="text.secondary">
            {formatTime(duration)}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Max: {formatTime(maxDuration)}
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={(duration / maxDuration) * 100}
          color={isRecording ? 'error' : 'primary'}
        />
      </Box>

      {/* Controls */}
      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
        {!audioBlob ? (
          <Tooltip title={isRecording ? 'Aufnahme stoppen' : 'Aufnahme starten'}>
            <IconButton
              onClick={isRecording ? stopRecording : startRecording}
              disabled={disabled}
              sx={{
                width: 64,
                height: 64,
                bgcolor: isRecording ? 'error.main' : 'primary.main',
                color: 'white',
                '&:hover': {
                  bgcolor: isRecording ? 'error.dark' : 'primary.dark',
                },
              }}
            >
              {isRecording ? <Stop sx={{ fontSize: 32 }} /> : <Mic sx={{ fontSize: 32 }} />}
            </IconButton>
          </Tooltip>
        ) : (
          <>
            <Tooltip title="Aufnahme löschen">
              <IconButton
                onClick={handleCancel}
                color="error"
                sx={{ width: 56, height: 56 }}
              >
                <Delete />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Aufnahme senden">
              <IconButton
                onClick={handleSubmit}
                sx={{
                  width: 64,
                  height: 64,
                  bgcolor: 'success.main',
                  color: 'white',
                  '&:hover': { bgcolor: 'success.dark' },
                }}
              >
                <Send sx={{ fontSize: 28 }} />
              </IconButton>
            </Tooltip>
          </>
        )}
      </Box>

      {/* Recording indicator */}
      <Fade in={isRecording}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mt: 2, gap: 1 }}>
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              bgcolor: 'error.main',
              animation: 'pulse 1s infinite',
              '@keyframes pulse': {
                '0%': { opacity: 1 },
                '50%': { opacity: 0.4 },
                '100%': { opacity: 1 },
              },
            }}
          />
          <Typography variant="caption" color="error">
            Aufnahme läuft...
          </Typography>
        </Box>
      </Fade>
    </Paper>
  );
};

export default VoiceRecorder;
