/**
 * VoiceMemoButton Component
 * 
 * FAB button to open the VoiceMemo dialog for quick voice-to-challenge creation.
 */
import React, { useState } from 'react';
import { Fab, Tooltip, Zoom } from '@mui/material';
import { Mic } from '@mui/icons-material';
import VoiceMemoDialog from './VoiceMemoDialog';

const VoiceMemoButton = ({ 
  onChallengeCreated,
  position = 'fixed',
  bottom = 24,
  right = 24,
  color = 'secondary',
}) => {
  const [dialogOpen, setDialogOpen] = useState(false);

  const handleChallengeCreated = (challenge) => {
    if (onChallengeCreated) {
      onChallengeCreated(challenge);
    }
  };

  return (
    <>
      <Tooltip title="Sprachaufnahme starten" placement="left">
        <Zoom in={true}>
          <Fab
            color={color}
            onClick={() => setDialogOpen(true)}
            sx={{
              position: position,
              bottom: bottom,
              right: right,
              background: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #ee5a24 0%, #ff6b6b 100%)',
              },
            }}
          >
            <Mic />
          </Fab>
        </Zoom>
      </Tooltip>

      <VoiceMemoDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onChallengeCreated={handleChallengeCreated}
      />
    </>
  );
};

export default VoiceMemoButton;
