"""
Tests for TaskMeMemo Voice-to-Challenge feature.
"""
import json
from datetime import timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from challenges.models import Challenge, VoiceMemo
from challenges.voice_service import VoiceMemoService
from rewards.models import CreditWallet

User = get_user_model()


def create_test_challenge(user, **kwargs):
    """Helper to create a test challenge with required fields."""
    defaults = {
        'creator': user,
        'title': 'Test Challenge',
        'challenge_type': 'todo',
        'target_value': 1,
        'start_date': timezone.now(),
        'end_date': timezone.now() + timedelta(days=7),
    }
    defaults.update(kwargs)
    return Challenge.objects.create(**defaults)


class VoiceMemoModelTest(TestCase):
    """Test VoiceMemo model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_voice_memo(self):
        """Test creating a voice memo."""
        audio_file = SimpleUploadedFile(
            'test.webm', 
            b'fake audio data', 
            content_type='audio/webm'
        )
        memo = VoiceMemo.objects.create(
            user=self.user,
            audio_file=audio_file,
            duration_seconds=30.0
        )
        
        self.assertEqual(memo.status, 'pending')
        self.assertEqual(memo.transcription, '')  # Default is empty string
        self.assertEqual(memo.parsed_data, {})  # Default is empty dict
    
    def test_voice_memo_status_transitions(self):
        """Test status workflow."""
        audio_file = SimpleUploadedFile(
            'test.webm', 
            b'fake audio data', 
            content_type='audio/webm'
        )
        memo = VoiceMemo.objects.create(
            user=self.user,
            audio_file=audio_file,
        )
        
        # Simulate status progression
        memo.status = 'transcribing'
        memo.save()
        self.assertEqual(memo.status, 'transcribing')
        
        memo.status = 'transcribed'
        memo.transcription = 'Ich will 30 Tage keinen Alkohol trinken'
        memo.save()
        self.assertEqual(memo.transcription, 'Ich will 30 Tage keinen Alkohol trinken')
        
        memo.status = 'parsing'
        memo.save()
        
        memo.status = 'parsed'
        memo.parsed_data = {'title': 'Kein Alkohol', 'challenge_type': 'streak'}
        memo.ai_confidence = 0.85
        memo.save()
        self.assertEqual(memo.ai_confidence, 0.85)
    
    def test_voice_memo_linked_challenge(self):
        """Test linking memo to created challenge."""
        audio_file = SimpleUploadedFile(
            'test.webm', 
            b'fake audio data', 
            content_type='audio/webm'
        )
        memo = VoiceMemo.objects.create(
            user=self.user,
            audio_file=audio_file,
            status='parsed',
            parsed_data={'title': 'Test', 'challenge_type': 'todo'}
        )
        
        challenge = create_test_challenge(self.user)
        
        memo.created_challenge = challenge
        memo.status = 'challenge_created'
        memo.save()
        
        self.assertEqual(memo.created_challenge, challenge)
        self.assertEqual(memo.status, 'challenge_created')


class VoiceMemoServiceTest(TestCase):
    """Test VoiceMemoService."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.service = VoiceMemoService()
    
    @patch('challenges.voice_service.OpenAI')
    def test_parse_challenge_from_text(self, mock_openai_class):
        """Test GPT parsing of transcribed text."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            'title': '10000 Schritte täglich',
            'description': 'Jeden Tag 10000 Schritte laufen',
            'challenge_type': 'quantified',
            'target_value': 10000,
            'unit': 'Schritte',
            'duration_days': 30,
            'proof_type': 'SELF',
            'confidence': 0.92
        })
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch.object(self.service, 'client', mock_client):
            result = self.service.parse_challenge_from_text(
                'Ich will täglich 10000 Schritte laufen'
            )
        
        self.assertEqual(result['challenge_type'], 'quantified')
        self.assertEqual(result['target_value'], 10000)
        self.assertGreater(result['confidence'], 0.9)
    
    def test_create_challenge_from_memo(self):
        """Test creating challenge from parsed memo."""
        # Create wallet with credits
        CreditWallet.objects.create(user=self.user, balance=500)
        
        audio_file = SimpleUploadedFile(
            'test.webm', 
            b'fake audio data',
            content_type='audio/webm'
        )
        memo = VoiceMemo.objects.create(
            user=self.user,
            audio_file=audio_file,
            status='parsed',
            transcription='Ich will 30 Tage keinen Alkohol trinken',
            parsed_data={
                'title': 'Kein Alkohol Challenge',
                'description': '30 Tage ohne Alkohol',
                'challenge_type': 'streak',
                'target_value': 30,
                'unit': 'Tage',
                'duration_days': 30,
                'proof_type': 'SELF',
                'confidence': 0.88
            },
            ai_confidence=0.88
        )
        
        # Create challenge - pass user and memo
        challenge = self.service.create_challenge_from_memo(
            memo=memo,
            user=self.user
        )
        
        self.assertIsNotNone(challenge)
        self.assertEqual(challenge.title, 'Kein Alkohol Challenge')
        self.assertEqual(challenge.challenge_type, 'streak')
        self.assertEqual(challenge.creator, self.user)
        
        # Check memo is updated
        memo.refresh_from_db()
        self.assertEqual(memo.status, 'challenge_created')
        self.assertEqual(memo.created_challenge, challenge)


class VoiceMemoAPITest(APITestCase):
    """Test Voice Memo API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create wallet with credits
        CreditWallet.objects.create(user=self.user, balance=500)
    
    def test_upload_voice_memo(self):
        """Test uploading a voice memo."""
        audio_file = SimpleUploadedFile(
            'recording.webm',
            b'fake audio data',
            content_type='audio/webm'
        )
        
        response = self.client.post(
            '/api/voice-memos/',
            {'audio_file': audio_file, 'duration_seconds': 15.5},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'pending')
        self.assertIn('id', response.data)
    
    def test_list_voice_memos(self):
        """Test listing user's voice memos."""
        VoiceMemo.objects.create(
            user=self.user,
            audio_file=SimpleUploadedFile('test1.webm', b'audio', content_type='audio/webm'),
            status='pending'
        )
        VoiceMemo.objects.create(
            user=self.user,
            audio_file=SimpleUploadedFile('test2.webm', b'audio', content_type='audio/webm'),
            status='parsed'
        )
        
        response = self.client.get('/api/voice-memos/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # May return results array or paginated
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2)
    
    @patch('challenges.voice_service.voice_memo_service')
    def test_process_voice_memo(self, mock_service):
        """Test processing a voice memo."""
        memo = VoiceMemo.objects.create(
            user=self.user,
            audio_file=SimpleUploadedFile('test.webm', b'audio', content_type='audio/webm'),
            status='pending'
        )
        
        # Mock the service methods
        mock_service.is_available.return_value = True
        
        def mock_process(m):
            """Simulate processing by updating memo and returning result."""
            m.status = 'parsed'
            m.transcription = 'Test transcription'
            m.parsed_data = {'title': 'Test Challenge', 'challenge_type': 'todo', 'confidence': 0.8}
            m.ai_confidence = 0.8
            m.save()
            return {'status': 'parsed'}
        
        mock_service.process_memo.side_effect = mock_process
        
        response = self.client.post(f'/api/voice-memos/{memo.id}/process/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('transcription', response.data)
        self.assertIn('parsed_data', response.data)
    
    @patch('challenges.voice_service.voice_memo_service')
    def test_create_challenge_from_memo(self, mock_service):
        """Test creating challenge from processed memo."""
        memo = VoiceMemo.objects.create(
            user=self.user,
            audio_file=SimpleUploadedFile('test.webm', b'audio', content_type='audio/webm'),
            status='parsed',
            parsed_data={'title': 'Test', 'challenge_type': 'todo'}
        )
        
        mock_challenge = create_test_challenge(self.user)
        mock_service.create_challenge_from_memo.return_value = mock_challenge
        
        response = self.client.post(f'/api/voice-memos/{memo.id}/create_challenge/')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('challenge', response.data)
    
    def test_dismiss_voice_memo(self):
        """Test dismissing a voice memo."""
        memo = VoiceMemo.objects.create(
            user=self.user,
            audio_file=SimpleUploadedFile('test.webm', b'audio', content_type='audio/webm'),
            status='parsed'
        )
        
        response = self.client.post(f'/api/voice-memos/{memo.id}/dismiss/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        memo.refresh_from_db()
        self.assertEqual(memo.status, 'dismissed')
    
    def test_delete_voice_memo(self):
        """Test deleting a voice memo."""
        memo = VoiceMemo.objects.create(
            user=self.user,
            audio_file=SimpleUploadedFile('test.webm', b'audio', content_type='audio/webm'),
            status='pending'
        )
        memo_id = memo.id
        
        response = self.client.delete(f'/api/voice-memos/{memo_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(VoiceMemo.objects.filter(id=memo_id).exists())
    
    def test_cannot_access_other_user_memo(self):
        """Test that users cannot access other users' memos."""
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='pass123'
        )
        
        memo = VoiceMemo.objects.create(
            user=other_user,
            audio_file=SimpleUploadedFile('test.webm', b'audio', content_type='audio/webm'),
            status='pending'
        )
        
        response = self.client.get(f'/api/voice-memos/{memo.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class VoiceMemoSecurityTest(APITestCase):
    """Security tests for voice memo endpoints."""
    
    def test_upload_requires_authentication(self):
        """Test that upload requires authentication."""
        audio_file = SimpleUploadedFile(
            'recording.webm',
            b'fake audio data',
            content_type='audio/webm'
        )
        
        response = self.client.post(
            '/api/voice-memos/',
            {'audio_file': audio_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_file_type_validation(self):
        """Test that only audio files are accepted."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        # Try to upload a non-audio file
        fake_file = SimpleUploadedFile(
            'malicious.exe',
            b'not audio',
            content_type='application/x-msdownload'
        )
        
        response = self.client.post(
            '/api/voice-memos/',
            {'audio_file': fake_file},
            format='multipart'
        )
        
        # Should be rejected
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE])
