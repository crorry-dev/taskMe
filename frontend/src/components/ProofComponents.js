import React, { useState, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Avatar,
  Chip,
  Stack,
  Alert,
  LinearProgress,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  PhotoCamera as CameraIcon,
  Delete as DeleteIcon,
  Close as CloseIcon,
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
  Pending as PendingIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';

/**
 * Photo Upload Component
 */
export const PhotoUpload = ({ 
  onUpload, 
  maxSize = 5 * 1024 * 1024, // 5MB default
  acceptedTypes = ['image/jpeg', 'image/png', 'image/webp'],
}) => {
  const [preview, setPreview] = useState(null);
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const selectedFile = event.target.files?.[0];
    if (!selectedFile) return;

    // Validate file type
    if (!acceptedTypes.includes(selectedFile.type)) {
      setError('Please upload a valid image (JPEG, PNG, or WebP)');
      return;
    }

    // Validate file size
    if (selectedFile.size > maxSize) {
      setError(`File size must be less than ${maxSize / (1024 * 1024)}MB`);
      return;
    }

    setError('');
    setFile(selectedFile);

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result);
    };
    reader.readAsDataURL(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setUploading(true);
    try {
      await onUpload(file);
      setFile(null);
      setPreview(null);
    } catch (err) {
      setError('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleRemove = () => {
    setFile(null);
    setPreview(null);
    setError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <Box>
      <input
        ref={fileInputRef}
        type="file"
        accept={acceptedTypes.join(',')}
        onChange={handleFileSelect}
        style={{ display: 'none' }}
        id="photo-upload-input"
      />

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {preview ? (
        <Box sx={{ position: 'relative' }}>
          <Box
            component="img"
            src={preview}
            alt="Preview"
            sx={{
              width: '100%',
              maxHeight: 300,
              objectFit: 'contain',
              borderRadius: 2,
              backgroundColor: 'grey.100',
            }}
          />
          <IconButton
            onClick={handleRemove}
            sx={{
              position: 'absolute',
              top: 8,
              right: 8,
              backgroundColor: 'rgba(0,0,0,0.5)',
              color: 'white',
              '&:hover': { backgroundColor: 'rgba(0,0,0,0.7)' },
            }}
          >
            <DeleteIcon />
          </IconButton>
          
          {uploading && (
            <LinearProgress sx={{ mt: 1, borderRadius: 1 }} />
          )}
          
          <Button
            fullWidth
            variant="contained"
            onClick={handleUpload}
            disabled={uploading}
            startIcon={<UploadIcon />}
            sx={{ mt: 2 }}
          >
            {uploading ? 'Uploading...' : 'Upload Proof'}
          </Button>
        </Box>
      ) : (
        <Box
          onClick={() => fileInputRef.current?.click()}
          sx={{
            border: '2px dashed',
            borderColor: 'grey.300',
            borderRadius: 2,
            p: 4,
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'all 0.2s',
            '&:hover': {
              borderColor: 'primary.main',
              backgroundColor: 'primary.50',
            },
          }}
        >
          <CameraIcon sx={{ fontSize: 48, color: 'grey.400', mb: 1 }} />
          <Typography variant="subtitle1" fontWeight={500}>
            Click to upload photo
          </Typography>
          <Typography variant="body2" color="text.secondary">
            JPEG, PNG or WebP (max {maxSize / (1024 * 1024)}MB)
          </Typography>
        </Box>
      )}
    </Box>
  );
};

/**
 * Proof Card - Displays a submitted proof
 */
export const ProofCard = ({ proof, onApprove, onReject, currentUserId }) => {
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);

  const statusConfig = {
    pending: { color: 'warning', icon: <PendingIcon />, label: 'Pending Review' },
    approved: { color: 'success', icon: <ApproveIcon />, label: 'Approved' },
    rejected: { color: 'error', icon: <RejectIcon />, label: 'Rejected' },
  };

  const status = statusConfig[proof.status] || statusConfig.pending;
  const canReview = proof.status === 'pending' && proof.user?.id !== currentUserId && onApprove;

  return (
    <>
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2 }}>
            <Avatar src={proof.user?.avatar}>
              {proof.user?.username?.[0]?.toUpperCase()}
            </Avatar>
            <Box sx={{ flex: 1 }}>
              <Typography variant="subtitle2" fontWeight={600}>
                {proof.user?.username}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {new Date(proof.submitted_at).toLocaleString()}
              </Typography>
            </Box>
            <Chip 
              icon={status.icon}
              label={status.label}
              color={status.color}
              size="small"
            />
          </Box>

          {/* Proof Image */}
          {proof.image && (
            <Box 
              sx={{ 
                position: 'relative',
                mb: 2,
                borderRadius: 2,
                overflow: 'hidden',
                cursor: 'pointer',
              }}
              onClick={() => setViewDialogOpen(true)}
            >
              <Box
                component="img"
                src={proof.image}
                alt="Proof"
                sx={{
                  width: '100%',
                  height: 200,
                  objectFit: 'cover',
                }}
              />
              <Box
                sx={{
                  position: 'absolute',
                  inset: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: 'rgba(0,0,0,0.3)',
                  opacity: 0,
                  transition: 'opacity 0.2s',
                  '&:hover': { opacity: 1 },
                }}
              >
                <ViewIcon sx={{ color: 'white', fontSize: 40 }} />
              </Box>
            </Box>
          )}

          {/* Notes */}
          {proof.notes && (
            <Typography variant="body2" color="text.secondary">
              {proof.notes}
            </Typography>
          )}

          {/* Review info */}
          {proof.status !== 'pending' && proof.reviewed_by && (
            <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
              <Typography variant="caption" color="text.secondary">
                Reviewed by {proof.reviewed_by.username} on{' '}
                {new Date(proof.reviewed_at).toLocaleDateString()}
              </Typography>
              {proof.rejection_reason && (
                <Typography variant="body2" color="error.main" sx={{ mt: 0.5 }}>
                  Reason: {proof.rejection_reason}
                </Typography>
              )}
            </Box>
          )}
        </CardContent>

        {/* Review Actions */}
        {canReview && (
          <CardActions sx={{ px: 2, pb: 2 }}>
            <Button
              variant="contained"
              color="success"
              startIcon={<ApproveIcon />}
              onClick={() => onApprove(proof.id)}
              sx={{ flex: 1 }}
            >
              Approve
            </Button>
            <Button
              variant="outlined"
              color="error"
              startIcon={<RejectIcon />}
              onClick={() => setRejectDialogOpen(true)}
              sx={{ flex: 1 }}
            >
              Reject
            </Button>
          </CardActions>
        )}
      </Card>

      {/* Full Image Dialog */}
      <Dialog 
        open={viewDialogOpen} 
        onClose={() => setViewDialogOpen(false)}
        maxWidth="md"
      >
        <Box sx={{ position: 'relative' }}>
          <IconButton
            onClick={() => setViewDialogOpen(false)}
            sx={{
              position: 'absolute',
              top: 8,
              right: 8,
              backgroundColor: 'rgba(0,0,0,0.5)',
              color: 'white',
              zIndex: 1,
              '&:hover': { backgroundColor: 'rgba(0,0,0,0.7)' },
            }}
          >
            <CloseIcon />
          </IconButton>
          <Box
            component="img"
            src={proof.image}
            alt="Proof"
            sx={{ maxWidth: '100%', display: 'block' }}
          />
        </Box>
      </Dialog>

      {/* Reject Dialog */}
      <Dialog 
        open={rejectDialogOpen} 
        onClose={() => setRejectDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Reject Proof</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Reason for rejection"
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            multiline
            rows={3}
            margin="normal"
            placeholder="Please provide a reason..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRejectDialogOpen(false)}>Cancel</Button>
          <Button 
            color="error" 
            variant="contained"
            onClick={() => {
              onReject(proof.id, rejectReason);
              setRejectDialogOpen(false);
              setRejectReason('');
            }}
          >
            Reject
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

/**
 * Pending Reviews List
 */
export const PendingReviewsList = ({ proofs, onApprove, onReject, currentUserId }) => {
  if (!proofs || proofs.length === 0) {
    return (
      <Box 
        sx={{ 
          textAlign: 'center', 
          py: 6,
          backgroundColor: 'grey.50',
          borderRadius: 2,
        }}
      >
        <ApproveIcon sx={{ fontSize: 48, color: 'grey.400', mb: 1 }} />
        <Typography variant="h6" color="text.secondary">
          No pending reviews
        </Typography>
        <Typography variant="body2" color="text.secondary">
          All caught up! Check back later.
        </Typography>
      </Box>
    );
  }

  return (
    <Box 
      sx={{ 
        display: 'grid',
        gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' },
        gap: 3,
      }}
    >
      {proofs.map((proof) => (
        <ProofCard 
          key={proof.id}
          proof={proof}
          onApprove={onApprove}
          onReject={onReject}
          currentUserId={currentUserId}
        />
      ))}
    </Box>
  );
};

export default {
  PhotoUpload,
  ProofCard,
  PendingReviewsList,
};
