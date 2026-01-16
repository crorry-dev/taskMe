"""
Debug Feedback Service

AI-powered analysis and implementation of user feedback.
"""
import os
import json
import subprocess
from datetime import datetime
from typing import Optional, Dict, Any, List
from django.conf import settings
from django.utils import timezone

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class DebugFeedbackService:
    """
    Service for processing debug feedback using AI.
    
    Analyzes feedback, suggests changes, and can auto-implement them.
    """
    
    def __init__(self):
        self.client = None
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            self.client = OpenAI()
        else:
            print("OpenAI API key not configured. Debug AI features disabled.")
    
    def is_available(self) -> bool:
        """Check if AI service is available."""
        return self.client is not None
    
    def analyze_feedback(self, feedback) -> Dict[str, Any]:
        """
        Analyze user feedback using AI.
        
        Returns analysis with:
        - feedback_type: bug, feature, ui_change, improvement
        - priority: low, medium, high, critical
        - summary: Brief summary
        - suggested_changes: List of file changes
        - implementation_steps: How to implement
        """
        from .models import DebugFeedback
        
        if not self.is_available():
            return {
                'status': 'error',
                'error': 'AI service not available'
            }
        
        input_text = feedback.input_text
        if not input_text:
            return {
                'status': 'error',
                'error': 'No input text to analyze'
            }
        
        # Update status
        feedback.status = 'analyzing'
        feedback.save()
        
        try:
            prompt = self._build_analysis_prompt(input_text, feedback)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Update feedback with analysis
            feedback.ai_analysis = result
            feedback.ai_suggested_changes = result.get('suggested_changes', [])
            feedback.ai_confidence = result.get('confidence', 0.5)
            feedback.feedback_type = result.get('feedback_type', 'improvement')
            feedback.priority = result.get('priority', 'medium')
            feedback.status = 'analyzed'
            feedback.analyzed_at = timezone.now()
            feedback.save()
            
            return {
                'status': 'analyzed',
                'analysis': result
            }
            
        except Exception as e:
            feedback.status = 'failed'
            feedback.ai_analysis = {'error': str(e)}
            feedback.save()
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for AI analysis."""
        return """Du bist ein erfahrener Full-Stack Entwickler für das CommitQuest Projekt.

Das Projekt verwendet:
- Frontend: React 19 + Material UI 5 + TypeScript-ähnliches JS
- Backend: Django 4.2 + Django REST Framework
- Styling: MUI Theme mit primär blauer Farbpalette

Deine Aufgabe ist es, Nutzer-Feedback zu analysieren und konkrete Code-Änderungen vorzuschlagen.

Antworte IMMER in diesem JSON-Format:
{
    "feedback_type": "bug|feature|ui_change|improvement|other",
    "priority": "low|medium|high|critical",
    "summary": "Kurze Zusammenfassung des Feedbacks",
    "understanding": "Was der Nutzer genau will",
    "suggested_changes": [
        {
            "file": "Relativer Dateipfad",
            "type": "modify|create|delete",
            "description": "Was geändert werden soll",
            "code_before": "Alter Code (wenn modify)",
            "code_after": "Neuer Code",
            "line_hint": "Ungefähre Zeilennummer oder Kontext"
        }
    ],
    "implementation_steps": ["Schritt 1", "Schritt 2"],
    "commit_message": "feat/fix/style: Beschreibung",
    "confidence": 0.85,
    "notes": "Zusätzliche Hinweise"
}

Bei UI/Design-Änderungen:
- Prüfe ob Änderungen im MUI Theme (/frontend/src/theme.js) gemacht werden sollten
- Oder in spezifischen Komponenten
- Beachte Konsistenz im Design

Bei Bugs:
- Identifiziere die wahrscheinliche Ursache
- Schlage einen Fix vor

WICHTIG: Sei präzise bei Dateipfaden und Code-Änderungen."""
    
    def _build_analysis_prompt(self, input_text: str, feedback) -> str:
        """Build the analysis prompt."""
        context = f"""
Nutzer-Feedback:
"{input_text}"

Kontext:
- Seite: {feedback.page_url or 'Unbekannt'}
- Browser: {json.dumps(feedback.browser_info) if feedback.browser_info else 'Unbekannt'}
- Zeitpunkt: {feedback.created_at}

Analysiere dieses Feedback und schlage konkrete Code-Änderungen vor.
"""
        return context
    
    def transcribe_voice_memo(self, feedback) -> Dict[str, Any]:
        """Transcribe voice memo using Whisper."""
        if not self.is_available():
            return {'status': 'error', 'error': 'AI service not available'}
        
        if not feedback.voice_memo:
            return {'status': 'error', 'error': 'No voice memo'}
        
        try:
            audio_path = feedback.voice_memo.path
            
            with open(audio_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="de"
                )
            
            feedback.voice_transcription = transcript.text
            feedback.save()
            
            return {
                'status': 'transcribed',
                'transcription': transcript.text
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def implement_changes(self, feedback, changes: List[Dict]) -> Dict[str, Any]:
        """
        Implement suggested changes.
        
        This is a placeholder - actual implementation would need
        careful file manipulation and validation.
        """
        from .models import DebugConfig
        
        config = DebugConfig.get_config()
        
        if not config.auto_implement:
            return {
                'status': 'pending_approval',
                'message': 'Auto-implement is disabled. Changes require manual approval.'
            }
        
        implemented_files = []
        errors = []
        
        for change in changes:
            try:
                file_path = change.get('file', '')
                change_type = change.get('type', 'modify')
                
                # Security: Only allow changes in frontend/src and backend directories
                if not self._is_safe_path(file_path):
                    errors.append(f"Unsafe path: {file_path}")
                    continue
                
                # For now, just log - actual implementation would modify files
                implemented_files.append(file_path)
                
            except Exception as e:
                errors.append(f"{file_path}: {str(e)}")
        
        feedback.affected_files = implemented_files
        feedback.status = 'implemented' if not errors else 'failed'
        feedback.implemented_at = timezone.now()
        feedback.save()
        
        return {
            'status': 'implemented' if not errors else 'partial',
            'implemented': implemented_files,
            'errors': errors
        }
    
    def _is_safe_path(self, path: str) -> bool:
        """Check if path is safe for modification."""
        safe_prefixes = [
            'frontend/src/',
            'backend/',
        ]
        unsafe_patterns = [
            '..',
            'node_modules',
            '.git',
            '.env',
            'settings.py',
            'manage.py',
        ]
        
        # Check safe prefixes
        if not any(path.startswith(prefix) for prefix in safe_prefixes):
            return False
        
        # Check unsafe patterns
        if any(pattern in path for pattern in unsafe_patterns):
            return False
        
        return True
    
    def create_commit(self, feedback, message: str = None) -> Dict[str, Any]:
        """
        Create a git commit for the implemented changes.
        """
        from .models import DebugConfig
        
        config = DebugConfig.get_config()
        
        if not config.auto_commit:
            return {
                'status': 'pending',
                'message': 'Auto-commit is disabled'
            }
        
        if not feedback.affected_files:
            return {
                'status': 'error',
                'error': 'No files to commit'
            }
        
        try:
            # This would actually run git commands
            commit_message = message or feedback.ai_analysis.get(
                'commit_message',
                f"fix: Implement feedback #{feedback.id}"
            )
            
            # Placeholder - would use subprocess to run git
            # subprocess.run(['git', 'add'] + feedback.affected_files)
            # result = subprocess.run(['git', 'commit', '-m', commit_message])
            
            feedback.commit_message = commit_message
            feedback.status = 'committed'
            feedback.committed_at = timezone.now()
            # feedback.commit_hash = result...
            feedback.save()
            
            return {
                'status': 'committed',
                'message': commit_message
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def process_feedback(self, feedback) -> Dict[str, Any]:
        """
        Full pipeline: transcribe (if voice) -> analyze -> implement -> commit.
        """
        from .models import DebugConfig
        from rewards.services import CreditService
        
        config = DebugConfig.get_config()
        
        # Check credits (unless unlimited)
        if not DebugConfig.user_has_unlimited_credits(feedback.user):
            wallet = CreditService.get_or_create_wallet(feedback.user)[0]
            if wallet.balance < config.feedback_cost:
                return {
                    'status': 'error',
                    'error': 'Insufficient credits'
                }
            
            # Charge credits
            CreditService.deduct_credits(
                user=feedback.user,
                amount=config.feedback_cost,
                transaction_type='debug_feedback',
                description=f'Debug feedback #{feedback.id}'
            )
            feedback.credits_charged = True
            feedback.save()
        
        # Step 1: Transcribe if voice memo
        if feedback.voice_memo and not feedback.voice_transcription:
            result = self.transcribe_voice_memo(feedback)
            if result['status'] == 'error':
                return result
        
        # Step 2: Analyze
        result = self.analyze_feedback(feedback)
        if result['status'] == 'error':
            return result
        
        # Step 3: Implement (if auto)
        if config.auto_implement and not config.require_approval:
            changes = feedback.ai_suggested_changes
            if changes:
                result = self.implement_changes(feedback, changes)
                
                # Step 4: Commit (if auto)
                if result['status'] == 'implemented' and config.auto_commit:
                    self.create_commit(feedback)
        
        return {
            'status': feedback.status,
            'analysis': feedback.ai_analysis,
            'suggested_changes': feedback.ai_suggested_changes
        }


# Singleton instance
debug_feedback_service = DebugFeedbackService()
