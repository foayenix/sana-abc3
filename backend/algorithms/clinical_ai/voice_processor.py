"""
Voice Processor
===============
Handles voice-to-text transcription for clinical notes using Whisper API.
"""

import logging
import base64
import io
from typing import Optional
from datetime import datetime

from .models import VoiceTranscriptionInput, VoiceTranscriptionResult

logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class VoiceProcessor:
    """
    Voice-to-Text Processor

    Transcribes clinical voice notes using OpenAI Whisper API.
    Optimized for medical terminology and clinical contexts.
    """

    SUPPORTED_FORMATS = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the voice processor"""
        self.api_key = api_key
        if OPENAI_AVAILABLE and api_key:
            openai.api_key = api_key

    def transcribe(self, input_data: VoiceTranscriptionInput) -> VoiceTranscriptionResult:
        """
        Transcribe audio to text

        Args:
            input_data: Audio data (URL or base64)

        Returns:
            VoiceTranscriptionResult with transcription
        """
        import time
        start_time = time.time()

        # Validate format
        if input_data.audio_format.lower() not in self.SUPPORTED_FORMATS:
            return VoiceTranscriptionResult(
                transcription=f"Error: Unsupported format '{input_data.audio_format}'",
                confidence=0.0,
                processing_time_ms=int((time.time() - start_time) * 1000),
            )

        if not OPENAI_AVAILABLE or not self.api_key:
            return VoiceTranscriptionResult(
                transcription="Voice transcription unavailable. OpenAI API key required.",
                confidence=0.0,
                processing_time_ms=int((time.time() - start_time) * 1000),
            )

        try:
            # Get audio data
            if input_data.audio_base64:
                audio_data = self._decode_base64(input_data.audio_base64)
            elif input_data.audio_url:
                audio_data = self._download_audio(input_data.audio_url)
            else:
                raise ValueError("No audio data provided")

            # Create file-like object
            audio_file = io.BytesIO(audio_data)
            audio_file.name = f"audio.{input_data.audio_format}"

            # Call Whisper API
            response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=input_data.language,
                response_format="verbose_json",
                prompt="Clinical consultation. Medical terminology: symptoms, diagnoses, herbs, supplements, treatment protocols.",
            )

            processing_time = int((time.time() - start_time) * 1000)

            return VoiceTranscriptionResult(
                transcription=response.text,
                confidence=0.95,  # Whisper doesn't provide confidence, use high default
                duration_seconds=response.duration if hasattr(response, 'duration') else 0,
                language_detected=response.language if hasattr(response, 'language') else input_data.language,
                processing_time_ms=processing_time,
            )

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return VoiceTranscriptionResult(
                transcription=f"Transcription error: {str(e)}",
                confidence=0.0,
                processing_time_ms=int((time.time() - start_time) * 1000),
            )

    def _decode_base64(self, base64_string: str) -> bytes:
        """Decode base64 audio data"""
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        return base64.b64decode(base64_string)

    def _download_audio(self, url: str) -> bytes:
        """Download audio from URL"""
        import requests
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content

    def transcribe_with_timestamps(
        self,
        input_data: VoiceTranscriptionInput
    ) -> VoiceTranscriptionResult:
        """
        Transcribe with word-level timestamps

        Useful for longer recordings where specific sections
        need to be referenced.
        """
        if not OPENAI_AVAILABLE or not self.api_key:
            return self.transcribe(input_data)

        import time
        start_time = time.time()

        try:
            if input_data.audio_base64:
                audio_data = self._decode_base64(input_data.audio_base64)
            elif input_data.audio_url:
                audio_data = self._download_audio(input_data.audio_url)
            else:
                raise ValueError("No audio data provided")

            audio_file = io.BytesIO(audio_data)
            audio_file.name = f"audio.{input_data.audio_format}"

            response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=input_data.language,
                response_format="verbose_json",
                timestamp_granularities=["word"],
            )

            # Extract timestamps
            timestamps = None
            if hasattr(response, 'words'):
                timestamps = [
                    {"word": w.word, "start": w.start, "end": w.end}
                    for w in response.words
                ]

            return VoiceTranscriptionResult(
                transcription=response.text,
                confidence=0.95,
                duration_seconds=response.duration if hasattr(response, 'duration') else 0,
                language_detected=response.language if hasattr(response, 'language') else input_data.language,
                timestamps=timestamps,
                processing_time_ms=int((time.time() - start_time) * 1000),
            )

        except Exception as e:
            logger.error(f"Timestamped transcription failed: {e}")
            return self.transcribe(input_data)  # Fall back to regular transcription
