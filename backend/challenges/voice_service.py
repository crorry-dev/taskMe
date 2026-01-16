"""
Voice Memo Service

Handles audio transcription via Whisper API and AI parsing
to extract challenge/task data from natural language.
"""
import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from django.conf import settings
from django.utils import timezone
from openai import OpenAI

logger = logging.getLogger(__name__)


class VoiceMemoService:
    """
    Service for processing voice memos.
    
    Flow:
    1. User uploads audio
    2. Whisper API transcribes to text
    3. GPT parses text to extract challenge/task structure
    4. User confirms/edits and creates challenge
    """
    
    def __init__(self):
        api_key = getattr(settings, 'OPENAI_API_KEY', None) or os.environ.get('OPENAI_API_KEY')
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
            logger.warning("OpenAI API key not configured. Voice memo features disabled.")
    
    def is_available(self) -> bool:
        """Check if the service is properly configured."""
        return self.client is not None
    
    def transcribe_audio(self, audio_file_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe audio file using OpenAI Whisper API.
        
        Args:
            audio_file_path: Path to the audio file
            language: Optional language hint (e.g., 'de', 'en')
            
        Returns:
            Dict with 'text', 'language', 'duration' keys
        """
        if not self.is_available():
            raise RuntimeError("OpenAI client not configured")
        
        try:
            with open(audio_file_path, 'rb') as audio_file:
                kwargs = {
                    'model': 'whisper-1',
                    'file': audio_file,
                    'response_format': 'verbose_json',
                }
                if language:
                    kwargs['language'] = language
                
                response = self.client.audio.transcriptions.create(**kwargs)
            
            return {
                'text': response.text,
                'language': getattr(response, 'language', language or 'unknown'),
                'duration': getattr(response, 'duration', None),
            }
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            raise
    
    def parse_challenge_from_text(self, text: str, user_timezone: str = 'Europe/Berlin') -> Dict[str, Any]:
        """
        Use GPT to parse natural language text into challenge structure.
        
        Args:
            text: Transcribed text from voice memo
            user_timezone: User's timezone for date calculations
            
        Returns:
            Dict with parsed challenge data
        """
        if not self.is_available():
            raise RuntimeError("OpenAI client not configured")
        
        system_prompt = """Du bist ein Assistent, der natürlichsprachliche Beschreibungen in strukturierte Challenge-Daten umwandelt.

Analysiere den Text und extrahiere:
1. challenge_type: 'todo' (einmalige Aufgabe), 'streak' (tägliche Gewohnheit), 'quantified' (Ziel mit Zahl), 'duel' (Wette/Herausforderung gegen jemanden), 'team' (Team-Challenge), 'community' (Gruppen-Ziel)
2. title: Kurzer, prägnanter Titel (max 60 Zeichen)
3. description: Ausführlichere Beschreibung
4. goal: Was erreicht werden soll
5. target_value: Zielwert (Anzahl, Tage, etc.)
6. unit: Einheit (Tage, km, Wiederholungen, €, etc.)
7. duration_days: Wie lange die Challenge dauert
8. proof_type: 'SELF' (Selbstbestätigung), 'PHOTO' (Foto-Beweis), 'PEER' (Peer-Bestätigung)
9. opponent_hint: Bei Duels, Name/Beschreibung des Gegners
10. team_hint: Bei Team-Challenges, Team-Name/Beschreibung
11. is_negative: true wenn es darum geht etwas NICHT zu tun (kein Alkohol, nicht rauchen)
12. confidence: Wie sicher du bei der Interpretation bist (0.0-1.0)

Antworte NUR mit validem JSON, keine zusätzlichen Erklärungen."""

        user_prompt = f"""Analysiere diesen Text und extrahiere Challenge-Daten:

"{text}"

Aktuelles Datum: {datetime.now().strftime('%Y-%m-%d')}
"""

        try:
            response = self.client.chat.completions.create(
                model='gpt-4o-mini',  # Cost-effective for parsing
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                response_format={'type': 'json_object'},
                max_tokens=500,
                temperature=0.3,  # Low temperature for consistent parsing
            )
            
            parsed = json.loads(response.choices[0].message.content)
            
            # Ensure required fields have defaults
            defaults = {
                'challenge_type': 'todo',
                'title': text[:60] if text else 'Neue Challenge',
                'description': text,
                'goal': '',
                'target_value': 1,
                'unit': '',
                'duration_days': 7,
                'proof_type': 'SELF',
                'opponent_hint': None,
                'team_hint': None,
                'is_negative': False,
                'confidence': 0.5,
            }
            
            for key, default_value in defaults.items():
                if key not in parsed or parsed[key] is None:
                    parsed[key] = default_value
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GPT response as JSON: {e}")
            return {
                'challenge_type': 'todo',
                'title': text[:60] if text else 'Neue Challenge',
                'description': text,
                'goal': text,
                'target_value': 1,
                'unit': '',
                'duration_days': 7,
                'proof_type': 'SELF',
                'confidence': 0.3,
                'parse_error': str(e),
            }
        except Exception as e:
            logger.error(f"GPT parsing failed: {e}")
            raise
    
    def process_memo(self, memo) -> Dict[str, Any]:
        """
        Full processing pipeline for a voice memo.
        
        Args:
            memo: VoiceMemo model instance
            
        Returns:
            Dict with status and parsed_data
        """
        from challenges.models import VoiceMemo
        
        if not self.is_available():
            memo.status = 'failed'
            memo.error_message = 'OpenAI API nicht konfiguriert'
            memo.save()
            return {'status': 'failed', 'error': memo.error_message}
        
        try:
            # Step 1: Transcribe
            memo.status = 'transcribing'
            memo.save()
            
            transcription_result = self.transcribe_audio(
                memo.audio_file.path,
                language='de'  # Default to German, could be user preference
            )
            
            memo.transcription = transcription_result['text']
            memo.language_detected = transcription_result.get('language', '')
            memo.duration_seconds = transcription_result.get('duration')
            memo.transcribed_at = timezone.now()
            memo.status = 'transcribed'
            memo.save()
            
            # Step 2: Parse with AI
            memo.status = 'parsing'
            memo.save()
            
            parsed_data = self.parse_challenge_from_text(
                memo.transcription,
                user_timezone=memo.user.timezone if hasattr(memo.user, 'timezone') else 'Europe/Berlin'
            )
            
            memo.parsed_data = parsed_data
            memo.ai_confidence = parsed_data.get('confidence', 0.5)
            memo.parsed_at = timezone.now()
            memo.status = 'parsed'
            memo.save()
            
            return {
                'status': 'parsed',
                'transcription': memo.transcription,
                'parsed_data': parsed_data,
            }
            
        except Exception as e:
            logger.error(f"Voice memo processing failed: {e}")
            memo.status = 'failed'
            memo.error_message = str(e)
            memo.save()
            return {'status': 'failed', 'error': str(e)}
    
    def create_challenge_from_memo(self, memo, user, overrides: Optional[Dict] = None):
        """
        Create a Challenge from parsed voice memo data.
        
        Args:
            memo: VoiceMemo instance with parsed_data
            user: User creating the challenge
            overrides: Optional dict to override parsed values
            
        Returns:
            Created Challenge instance
        """
        from challenges.models import Challenge, ChallengeParticipant
        from rewards.services import CreditService
        from django.utils import timezone
        from datetime import timedelta
        
        data = {**memo.parsed_data}
        if overrides:
            data.update(overrides)
        
        # Calculate dates
        duration_days = data.get('duration_days', 7)
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=duration_days)
        
        # Map parsed data to Challenge fields
        challenge = Challenge.objects.create(
            title=data.get('title', 'Neue Challenge')[:255],
            description=data.get('description', ''),
            challenge_type=data.get('challenge_type', 'todo'),
            status='active',
            visibility='private',
            goal=data.get('goal', data.get('title', ''))[:255],
            target_value=data.get('target_value', 1),
            unit=data.get('unit', '')[:50],
            required_proof_types=[data.get('proof_type', 'SELF')],
            start_date=start_date,
            end_date=end_date,
            creator=user,
        )
        
        # Add creator as participant
        ChallengeParticipant.objects.create(
            challenge=challenge,
            user=user,
            status='active'
        )
        
        # Charge credits
        try:
            CreditService.charge_for_challenge(user, challenge)
        except ValueError as e:
            # Rollback if can't afford
            challenge.delete()
            raise e
        
        # Update memo status
        memo.created_challenge = challenge
        memo.status = 'challenge_created'
        memo.save()
        
        return challenge


# Singleton instance
voice_memo_service = VoiceMemoService()
