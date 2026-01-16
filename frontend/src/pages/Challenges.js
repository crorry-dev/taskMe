import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Tabs,
  Tab,
  Skeleton,
  Alert,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import Layout from '../components/Layout';
import { ChallengeList } from '../components/ChallengeComponents';
import CreateChallengeDialog from '../components/CreateChallengeDialog';
import { challengeService } from '../services/apiService';

const ChallengesPage = () => {
  const [tab, setTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [challenges, setChallenges] = useState([]);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  const tabs = [
    { label: 'My Challenges', filter: 'my' },
    { label: 'Discover', filter: 'public' },
    { label: 'Active', filter: 'active' },
    { label: 'Completed', filter: 'completed' },
  ];

  useEffect(() => {
    loadChallenges();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab]);

  const loadChallenges = async () => {
    setLoading(true);
    try {
      let response;
      switch (tabs[tab].filter) {
        case 'my':
          response = await challengeService.getMyChallenges();
          break;
        case 'public':
          response = await challengeService.list({ visibility: 'public' });
          break;
        case 'active':
          response = await challengeService.list({ status: 'active' });
          break;
        case 'completed':
          response = await challengeService.list({ status: 'completed' });
          break;
        default:
          response = await challengeService.list();
      }
      setChallenges(response.data.results || response.data || []);
      setError(null);
    } catch (err) {
      console.error('Failed to load challenges:', err);
      setError('Failed to load challenges');
    } finally {
      setLoading(false);
    }
  };

  const handleJoin = async (challenge) => {
    try {
      await challengeService.join(challenge.id);
      loadChallenges();
    } catch (err) {
      console.error('Failed to join challenge:', err);
      setError('Failed to join challenge');
    }
  };

  const handleCreate = async (data) => {
    await challengeService.create(data);
    loadChallenges();
  };

  return (
    <Layout>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Challenges
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Compete, track progress, and achieve your goals
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
          size="large"
        >
          New Challenge
        </Button>
      </Box>

      {/* Tabs */}
      <Tabs
        value={tab}
        onChange={(e, v) => setTab(v)}
        sx={{ mb: 4, borderBottom: 1, borderColor: 'divider' }}
      >
        {tabs.map((t, i) => (
          <Tab key={t.filter} label={t.label} />
        ))}
      </Tabs>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Content */}
      {loading ? (
        <Box 
          sx={{ 
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' },
            gap: 3,
          }}
        >
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} variant="rounded" height={280} />
          ))}
        </Box>
      ) : (
        <ChallengeList 
          challenges={challenges} 
          onJoin={handleJoin}
          emptyMessage={
            tab === 0 
              ? "You haven't created or joined any challenges yet" 
              : "No challenges found"
          }
        />
      )}

      {/* Create Dialog */}
      <CreateChallengeDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        onSubmit={handleCreate}
      />
    </Layout>
  );
};

export default ChallengesPage;
