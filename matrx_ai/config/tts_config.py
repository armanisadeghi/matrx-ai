from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


# ============================================================================
# TTSSpeaker — single speaker entry for multi-speaker TTS (Google only)
# ============================================================================


@dataclass
class TTSSpeaker:
    name: str
    voice: str

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> TTSSpeaker:
        return cls(name=data["name"], voice=data["voice"])

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "voice": self.voice}


# ============================================================================
# TTSVoiceConfig — unified voice configuration for all providers
#
# Three modes — determined by which field is populated:
#
#   Single-speaker:  voice is a non-empty string, speakers/dialogue_turns empty.
#                    Works with Google, OpenAI, Groq, xAI, ElevenLabs.
#
#   Multi-speaker:   voice is None, speakers has 2+ TTSSpeaker entries.
#                    Google only. Non-Google providers collapse to speakers[0].
#
#   Dialogue:        dialogue_turns has 1+ DialogueTurn entries (text+voice_id).
#                    ElevenLabs text_to_dialogue only. Each turn carries its
#                    own voice_id — no global voice config needed.
#
# Provider translation: to_google(), to_openai(), to_groq(), to_xai(),
# to_elevenlabs(). Each method enforces its own constraints.
# ============================================================================


@dataclass
class TTSVoiceConfig:
    voice: str | None = None
    speakers: list[TTSSpeaker] = field(default_factory=list)
    # ElevenLabs dialogue turns — each turn carries its own voice_id inline.
    # When set, this config is in "dialogue" mode and to_elevenlabs() is the
    # authoritative translation path. Other provider methods are not applicable.
    dialogue_turns: list[DialogueTurn] = field(default_factory=list)

    # ------------------------------------------------------------------ #
    # Construction                                                         #
    # ------------------------------------------------------------------ #

    @classmethod
    def from_config(cls, settings: Any) -> TTSVoiceConfig | None:
        raw = getattr(settings, "tts_voice", None)
        if raw is None:
            return None

        if isinstance(raw, str):
            if not raw.strip():
                return None
            return cls(voice=raw)

        if isinstance(raw, list):
            if not raw:
                return None

            first = raw[0]
            if not isinstance(first, dict):
                return None

            # Detect ElevenLabs dialogue turns: dicts with "voice_id" (not "voice"/"name")
            if "voice_id" in first:
                turns = [DialogueTurn.from_dict(t) for t in raw]
                return cls(dialogue_turns=turns)

            if len(raw) == 1:
                voice_name = first.get("voice")
                return cls(voice=voice_name)

            return cls(speakers=[TTSSpeaker.from_dict(s) for s in raw])

        return None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TTSVoiceConfig:
        return cls(
            voice=data.get("voice"),
            speakers=[TTSSpeaker.from_dict(s) for s in data.get("speakers", [])],
            dialogue_turns=[DialogueTurn.from_dict(t) for t in data.get("dialogue_turns", [])],
        )

    # ------------------------------------------------------------------ #
    # Properties                                                           #
    # ------------------------------------------------------------------ #

    @property
    def is_multi_speaker(self) -> bool:
        return len(self.speakers) > 1

    @property
    def is_dialogue(self) -> bool:
        """True when this config carries ElevenLabs dialogue turns."""
        return bool(self.dialogue_turns)

    @property
    def is_configured(self) -> bool:
        return bool(self.voice) or bool(self.speakers) or bool(self.dialogue_turns)

    def _primary_voice(self) -> str | None:
        if self.voice:
            return self.voice
        if self.speakers:
            return self.speakers[0].voice
        return None

    def strip_speaker_labels(self, text: str) -> str:
        """Remove speaker labels from transcript text for single-speaker providers.

        Handles any label format where a known speaker name appears at the start
        of a line followed by a colon and optional whitespace — regardless of
        script or language.  Only strips labels for names defined in self.speakers.

        Called by non-Google providers when collapsing a multi-speaker config to
        a single voice, so the model doesn't read out "Alex:" as part of the text.

        Examples:
            "Alex: Hello.\nSarah: Hi!"  →  "Hello.\nHi!"
            "الکس: سلام\nسارا: خوبم"   →  "سلام\nخوبم"
        """
        if not self.speakers:
            return text

        import re

        names = [re.escape(s.name) for s in self.speakers]
        pattern = re.compile(
            r"^(?:" + "|".join(names) + r")\s*:\s*",
            re.MULTILINE,
        )
        return pattern.sub("", text)

    # ------------------------------------------------------------------ #
    # Validation                                                           #
    # ------------------------------------------------------------------ #

    def validate_speaker_names(self, google_contents: list[dict[str, Any]]) -> None:
        if not self.is_multi_speaker:
            return

        full_text = ""
        for content in google_contents:
            if content.get("role") == "user":
                for part in content.get("parts", []):
                    if isinstance(part, dict):
                        text = part.get("text") or ""
                    else:
                        text = getattr(part, "text", None) or ""
                    full_text += text

        missing = [s.name for s in self.speakers if s.name and s.name not in full_text]
        if missing:
            configured = [s.name for s in self.speakers]
            raise ValueError(
                f"[Google TTS] Speaker name mismatch: {missing} not found in message text. "
                f"All configured speakers {configured} must appear as exact labels in the "
                f"transcript (e.g. 'Alex: ...'). Names are case-sensitive and must match "
                f"exactly, including non-Latin scripts."
            )

    # ------------------------------------------------------------------ #
    # Provider translation — Google                                        #
    # ------------------------------------------------------------------ #

    def to_google(self, google_contents: list[dict[str, Any]]) -> Any:
        from google.genai import types

        if not self.is_configured:
            return None

        if self.is_multi_speaker:
            self.validate_speaker_names(google_contents)
            return types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=[
                        types.SpeakerVoiceConfig(
                            speaker=s.name,
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=s.voice
                                )
                            ),
                        )
                        for s in self.speakers
                    ]
                )
            )

        return types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=self.voice)
            )
        )

    # ------------------------------------------------------------------ #
    # Provider translation — OpenAI                                        #
    # Multi-speaker is not supported; collapses to primary voice.          #
    # ------------------------------------------------------------------ #

    def to_openai(self) -> dict[str, str]:
        _, resolved_voice = OpenAITTSRegistry.resolve(voice=self._primary_voice())
        return {"voice": resolved_voice}

    def to_openai_model_and_voice(self, model: str | None = None) -> tuple[str, str]:
        return OpenAITTSRegistry.resolve(model=model, voice=self._primary_voice())

    # ------------------------------------------------------------------ #
    # Provider translation — Groq                                          #
    # Multi-speaker is not supported; collapses to primary voice.          #
    # ------------------------------------------------------------------ #

    def to_groq(self) -> dict[str, str]:
        _, resolved_voice = GroqTTSRegistry.resolve(voice=self._primary_voice())
        return {"voice": resolved_voice}

    def to_groq_model_and_voice(self, model: str | None = None) -> tuple[str, str]:
        return GroqTTSRegistry.resolve(model=model, voice=self._primary_voice())

    # ------------------------------------------------------------------ #
    # Provider translation — xAI                                           #
    # Multi-speaker is not supported; collapses to primary voice.          #
    # xAI TTS has no model parameter — single endpoint.                    #
    # ------------------------------------------------------------------ #

    def to_xai(self) -> dict[str, str]:
        resolved_voice = XAITTSRegistry.resolve_voice(self._primary_voice())
        return {"voice": resolved_voice}

    # ------------------------------------------------------------------ #
    # Provider translation — ElevenLabs                                   #
    # Dialogue mode: returns batched turns for text_to_dialogue API.      #
    # Single-speaker mode: wraps the single text+voice_id as one turn.    #
    # Multi-speaker (Google-style) is not applicable; raises clearly.     #
    # ------------------------------------------------------------------ #

    def to_elevenlabs(self, text: str | None = None, model: str | None = None) -> tuple[list[list[dict[str, str]]], str]:
        """Translate to ElevenLabs batched dialogue inputs.

        Returns:
            batches: list of batches, each batch is a list of
                     {"text": ..., "voice_id": ...} dicts ready for the SDK.
            model:   resolved model string (e.g. "eleven_v3").
        """
        resolved_model = ElevenLabsDialogueRegistry.resolve_model(model)

        if self.is_dialogue:
            batches = ElevenLabsDialogueRegistry.batch_turns(self.dialogue_turns)
            return [[t.to_elevenlabs_input() for t in batch] for batch in batches], resolved_model

        if self.speakers:
            raise ValueError(
                "TTSVoiceConfig is in Google multi-speaker mode (name→voice mapping). "
                "ElevenLabs requires turns with inline voice_id. "
                "Pass tts_voice as a list of {text, voice_id} dicts instead."
            )

        # Single-speaker: wrap the provided text as one turn
        if not text:
            raise ValueError("ElevenLabs single-speaker TTS requires text input.")
        voice_id = self.voice or ""
        if not voice_id:
            raise ValueError("ElevenLabs TTS requires a voice_id.")
        turn = DialogueTurn(text=text, voice_id=voice_id)
        batches = ElevenLabsDialogueRegistry.batch_turns([turn])
        return [[t.to_elevenlabs_input() for t in batch] for batch in batches], resolved_model

    # ------------------------------------------------------------------ #
    # Serialisation                                                        #
    # ------------------------------------------------------------------ #

    def to_storage_dict(self) -> dict[str, Any]:
        return {
            "voice": self.voice,
            "speakers": [s.to_dict() for s in self.speakers],
            "dialogue_turns": [t.to_dict() for t in self.dialogue_turns],
        }


# ============================================================================
# OpenAITTSRegistry — voice/model resolution for OpenAI TTS
# ============================================================================


class OpenAITTSRegistry:
    # gpt-4o-mini-tts supports 13 voices
    _GPT4O_MINI_TTS_VOICES: frozenset[str] = frozenset({
        "alloy", "ash", "ballad", "coral", "echo",
        "fable", "nova", "onyx", "sage", "shimmer",
        "verse", "marin", "cedar",
    })
    # tts-1 and tts-1-hd share a 9-voice subset
    _TTS1_VOICES: frozenset[str] = frozenset({
        "alloy", "ash", "coral", "echo", "fable",
        "onyx", "nova", "sage", "shimmer",
    })
    _VOICES_BY_MODEL: dict[str, frozenset[str]] = {
        "gpt-4o-mini-tts": _GPT4O_MINI_TTS_VOICES,
        "tts-1":           _TTS1_VOICES,
        "tts-1-hd":        _TTS1_VOICES,
    }
    VALID_MODELS: frozenset[str] = frozenset(_VOICES_BY_MODEL.keys())
    DEFAULT_MODEL: str = "gpt-4o-mini-tts"
    DEFAULT_VOICE: str = "coral"

    @classmethod
    def resolve_model(cls, model: Optional[str] = None) -> str:
        if model and model.strip().lower() in cls.VALID_MODELS:
            return model.strip().lower()
        return cls.DEFAULT_MODEL

    @classmethod
    def resolve_voice(cls, voice: Optional[str] = None, model: Optional[str] = None) -> str:
        resolved_model = cls.resolve_model(model)
        valid = cls._VOICES_BY_MODEL[resolved_model]
        if voice:
            normalised = voice.strip().lower()
            if normalised in valid:
                return normalised
        return cls.DEFAULT_VOICE

    @classmethod
    def resolve(cls, model: Optional[str] = None, voice: Optional[str] = None) -> tuple[str, str]:
        resolved_model = cls.resolve_model(model)
        resolved_voice = cls.resolve_voice(voice, resolved_model)
        return resolved_model, resolved_voice

    @classmethod
    def is_valid_voice(cls, voice: str, model: Optional[str] = None) -> bool:
        normalised = voice.strip().lower()
        if model:
            m = cls.resolve_model(model)
            return normalised in cls._VOICES_BY_MODEL[m]
        return any(normalised in v for v in cls._VOICES_BY_MODEL.values())

    @classmethod
    def voices_for_model(cls, model: Optional[str] = None) -> list[str]:
        m = cls.resolve_model(model)
        return sorted(cls._VOICES_BY_MODEL[m])


# ============================================================================
# GroqTTSRegistry — voice/model resolution for Groq Orpheus TTS
# ============================================================================


class GroqTTSRegistry:
    _ENGLISH_VOICES: frozenset[str] = frozenset({
        "autumn", "diana", "hannah",
        "austin", "daniel", "troy",
    })
    _ARABIC_SAUDI_VOICES: frozenset[str] = frozenset({
        "lulwa", "noura",
        "fahad", "sultan",
    })
    _VOICES_BY_MODEL: dict[str, frozenset[str]] = {
        "canopylabs/orpheus-v1-english":   _ENGLISH_VOICES,
        "canopylabs/orpheus-arabic-saudi": _ARABIC_SAUDI_VOICES,
    }
    _SUPPORTS_VOCAL_DIRECTIONS: frozenset[str] = frozenset({
        "canopylabs/orpheus-v1-english",
    })
    VALID_MODELS: frozenset[str] = frozenset(_VOICES_BY_MODEL.keys())
    SUPPORTED_FORMATS: frozenset[str] = frozenset({"wav"})
    MAX_INPUT_LENGTH: int = 200
    DEFAULT_MODEL: str = "canopylabs/orpheus-v1-english"
    _DEFAULT_VOICE_BY_MODEL: dict[str, str] = {
        "canopylabs/orpheus-v1-english":   "troy",
        "canopylabs/orpheus-arabic-saudi": "fahad",
    }

    @classmethod
    def resolve_model(cls, model: Optional[str] = None) -> str:
        if model and model.strip().lower() in cls.VALID_MODELS:
            return model.strip().lower()
        return cls.DEFAULT_MODEL

    @classmethod
    def resolve_voice(cls, voice: Optional[str] = None, model: Optional[str] = None) -> str:
        resolved_model = cls.resolve_model(model)
        valid = cls._VOICES_BY_MODEL[resolved_model]
        if voice:
            normalised = voice.strip().lower()
            if normalised in valid:
                return normalised
        return cls._DEFAULT_VOICE_BY_MODEL[resolved_model]

    @classmethod
    def resolve(cls, model: Optional[str] = None, voice: Optional[str] = None) -> tuple[str, str]:
        resolved_model = cls.resolve_model(model)
        resolved_voice = cls.resolve_voice(voice, resolved_model)
        return resolved_model, resolved_voice

    @classmethod
    def resolve_format(cls, response_format: Optional[str] = None) -> str:
        if response_format and response_format.strip().lower() in cls.SUPPORTED_FORMATS:
            return response_format.strip().lower()
        return "wav"

    @classmethod
    def is_valid_voice(cls, voice: str, model: Optional[str] = None) -> bool:
        normalised = voice.strip().lower()
        if model:
            m = cls.resolve_model(model)
            return normalised in cls._VOICES_BY_MODEL[m]
        return any(normalised in v for v in cls._VOICES_BY_MODEL.values())

    @classmethod
    def voices_for_model(cls, model: Optional[str] = None) -> list[str]:
        m = cls.resolve_model(model)
        return sorted(cls._VOICES_BY_MODEL[m])

    @classmethod
    def supports_vocal_directions(cls, model: Optional[str] = None) -> bool:
        m = cls.resolve_model(model)
        return m in cls._SUPPORTS_VOCAL_DIRECTIONS

    @classmethod
    def validate_input_length(cls, text: str) -> str:
        if len(text) > cls.MAX_INPUT_LENGTH:
            return text[:cls.MAX_INPUT_LENGTH]
        return text


# ============================================================================
# GoogleTTSRegistry — voice/model resolution for Google Gemini TTS
# Only Google supports multi-speaker TTS (up to 2 speakers).
# ============================================================================


class GoogleTTSRegistry:
    _VOICE_DETAILS: dict[str, str] = {
        "zephyr":        "Bright",
        "puck":          "Upbeat",
        "charon":        "Informative",
        "kore":          "Firm",
        "fenrir":        "Excitable",
        "leda":          "Youthful",
        "orus":          "Firm",
        "aoede":         "Breezy",
        "callirrhoe":    "Easy-going",
        "autonoe":       "Bright",
        "enceladus":     "Breathy",
        "iapetus":       "Clear",
        "umbriel":       "Easy-going",
        "algieba":       "Smooth",
        "despina":       "Smooth",
        "erinome":       "Clear",
        "algenib":       "Gravelly",
        "rasalgethi":    "Informative",
        "laomedeia":     "Upbeat",
        "achernar":      "Soft",
        "alnilam":       "Firm",
        "schedar":       "Even",
        "gacrux":        "Mature",
        "pulcherrima":   "Forward",
        "achird":        "Friendly",
        "zubenelgenubi": "Casual",
        "vindemiatrix":  "Gentle",
        "sadachbia":     "Lively",
        "sadaltager":    "Knowledgeable",
        "sulafat":       "Warm",
    }
    _ALL_VOICES: frozenset[str] = frozenset(_VOICE_DETAILS.keys())
    _VOICES_BY_MODEL: dict[str, frozenset[str]] = {
        "gemini-2.5-flash-preview-tts": _ALL_VOICES,
        "gemini-2.5-pro-preview-tts":   _ALL_VOICES,
    }
    VALID_MODELS: frozenset[str] = frozenset(_VOICES_BY_MODEL.keys())
    MAX_SPEAKERS: int = 2
    DEFAULT_MODEL: str = "gemini-2.5-flash-preview-tts"
    DEFAULT_VOICE: str = "kore"

    @classmethod
    def resolve_model(cls, model: Optional[str] = None) -> str:
        if model and model.strip().lower() in cls.VALID_MODELS:
            return model.strip().lower()
        return cls.DEFAULT_MODEL

    @classmethod
    def resolve_voice(cls, voice: Optional[str] = None, model: Optional[str] = None) -> str:
        if voice:
            normalised = voice.strip().lower()
            if normalised in cls._ALL_VOICES:
                return normalised
        return cls.DEFAULT_VOICE

    @classmethod
    def resolve(cls, model: Optional[str] = None, voice: Optional[str] = None) -> tuple[str, str]:
        resolved_model = cls.resolve_model(model)
        resolved_voice = cls.resolve_voice(voice, resolved_model)
        return resolved_model, resolved_voice

    @classmethod
    def is_valid_voice(cls, voice: str, model: Optional[str] = None) -> bool:
        return voice.strip().lower() in cls._ALL_VOICES

    @classmethod
    def voices_for_model(cls, model: Optional[str] = None) -> list[str]:
        m = cls.resolve_model(model)
        return sorted(cls._VOICES_BY_MODEL[m])

    @classmethod
    def display_name(cls, voice: str) -> str:
        normalised = voice.strip().lower()
        if normalised in cls._ALL_VOICES:
            return normalised.capitalize()
        return cls.DEFAULT_VOICE.capitalize()

    @classmethod
    def voice_description(cls, voice: str) -> Optional[str]:
        return cls._VOICE_DETAILS.get(voice.strip().lower())

    @classmethod
    def voices_by_quality(cls, quality: str) -> list[str]:
        q = quality.strip().lower()
        return sorted(
            name for name, desc in cls._VOICE_DETAILS.items()
            if desc.lower() == q
        )

    @classmethod
    def validate_speakers(cls, speakers: list[dict]) -> list[dict]:
        validated = []
        for entry in speakers[:cls.MAX_SPEAKERS]:
            validated.append({
                "speaker": entry.get("speaker", f"Speaker{len(validated) + 1}"),
                "voice": cls.resolve_voice(entry.get("voice")),
            })
        return validated


# ============================================================================
# XAITTSRegistry — voice resolution for xAI Grok TTS
# No model parameter — xAI TTS is a single endpoint.
# Only Google supports multi-speaker TTS.
# ============================================================================


class XAITTSRegistry:
    _VOICE_DETAILS: dict[str, dict[str, str]] = {
        "eve": {"tone": "Energetic, upbeat",    "description": "Default voice - engaging and enthusiastic"},
        "ara": {"tone": "Warm, friendly",        "description": "Balanced and conversational"},
        "rex": {"tone": "Confident, clear",      "description": "Professional and articulate - ideal for business"},
        "sal": {"tone": "Smooth, balanced",      "description": "Versatile voice for a wide range of contexts"},
        "leo": {"tone": "Authoritative, strong", "description": "Commanding and decisive - great for instructional content"},
    }
    _ALL_VOICES: frozenset[str] = frozenset(_VOICE_DETAILS.keys())
    _LANGUAGES: dict[str, str] = {
        "auto":  "Auto-detect",
        "en":    "English",
        "ar-eg": "Arabic (Egypt)",
        "ar-sa": "Arabic (Saudi Arabia)",
        "ar-ae": "Arabic (United Arab Emirates)",
        "bn":    "Bengali",
        "zh":    "Chinese (Simplified)",
        "fr":    "French",
        "de":    "German",
        "hi":    "Hindi",
        "id":    "Indonesian",
        "it":    "Italian",
        "ja":    "Japanese",
        "ko":    "Korean",
        "pt-br": "Portuguese (Brazil)",
        "pt-pt": "Portuguese (Portugal)",
        "ru":    "Russian",
        "es-mx": "Spanish (Mexico)",
        "es-es": "Spanish (Spain)",
        "tr":    "Turkish",
        "vi":    "Vietnamese",
    }
    VALID_LANGUAGES: frozenset[str] = frozenset(_LANGUAGES.keys())
    VALID_CODECS: frozenset[str] = frozenset({"mp3", "wav", "pcm", "mulaw", "alaw"})
    VALID_SAMPLE_RATES: frozenset[int] = frozenset({8000, 16000, 22050, 24000, 44100, 48000})
    VALID_BIT_RATES: frozenset[int] = frozenset({32000, 64000, 96000, 128000, 192000})
    MAX_TEXT_LENGTH: int = 15_000
    MODEL_SENTINEL: str = "xai-tts"
    DEFAULT_VOICE: str = "eve"
    DEFAULT_LANGUAGE: str = "en"
    DEFAULT_CODEC: str = "mp3"
    DEFAULT_SAMPLE_RATE: int = 24000
    DEFAULT_BIT_RATE: int = 128000

    @classmethod
    def resolve_voice(cls, voice: Optional[str] = None) -> str:
        if voice:
            normalised = voice.strip().lower()
            if normalised in cls._ALL_VOICES:
                return normalised
        return cls.DEFAULT_VOICE

    @classmethod
    def resolve(cls, model: Optional[str] = None, voice: Optional[str] = None) -> tuple[str, str]:
        return cls.MODEL_SENTINEL, cls.resolve_voice(voice)

    @classmethod
    def resolve_language(cls, language: Optional[str] = None) -> str:
        if language:
            normalised = language.strip().lower()
            if normalised in cls.VALID_LANGUAGES:
                return normalised
        return cls.DEFAULT_LANGUAGE

    @classmethod
    def resolve_codec(cls, codec: Optional[str] = None) -> str:
        if codec:
            normalised = codec.strip().lower()
            if normalised in cls.VALID_CODECS:
                return normalised
        return cls.DEFAULT_CODEC

    @classmethod
    def resolve_sample_rate(cls, sample_rate: Optional[int] = None) -> int:
        if sample_rate is not None and sample_rate in cls.VALID_SAMPLE_RATES:
            return sample_rate
        return cls.DEFAULT_SAMPLE_RATE

    @classmethod
    def resolve_bit_rate(cls, bit_rate: Optional[int] = None, codec: Optional[str] = None) -> Optional[int]:
        resolved_codec = cls.resolve_codec(codec)
        if resolved_codec != "mp3":
            return None
        if bit_rate is not None and bit_rate in cls.VALID_BIT_RATES:
            return bit_rate
        return cls.DEFAULT_BIT_RATE

    @classmethod
    def resolve_output_format(
        cls,
        codec: Optional[str] = None,
        sample_rate: Optional[int] = None,
        bit_rate: Optional[int] = None,
    ) -> dict:
        resolved_codec = cls.resolve_codec(codec)
        result: dict = {
            "codec": resolved_codec,
            "sample_rate": cls.resolve_sample_rate(sample_rate),
        }
        resolved_br = cls.resolve_bit_rate(bit_rate, resolved_codec)
        if resolved_br is not None:
            result["bit_rate"] = resolved_br
        return result

    @classmethod
    def is_valid_voice(cls, voice: str) -> bool:
        return voice.strip().lower() in cls._ALL_VOICES

    @classmethod
    def voices(cls) -> list[str]:
        return sorted(cls._ALL_VOICES)

    @classmethod
    def voice_description(cls, voice: str) -> Optional[dict[str, str]]:
        return cls._VOICE_DETAILS.get(voice.strip().lower())

    @classmethod
    def languages(cls) -> dict[str, str]:
        return dict(cls._LANGUAGES)

    @classmethod
    def validate_text_length(cls, text: str, truncate: bool = False) -> str:
        if len(text) <= cls.MAX_TEXT_LENGTH:
            return text
        if truncate:
            return text[:cls.MAX_TEXT_LENGTH]
        raise ValueError(
            f"Text length {len(text):,} exceeds the {cls.MAX_TEXT_LENGTH:,} "
            f"character limit. Use truncate=True or the WebSocket endpoint."
        )


# ============================================================================
# DialogueTurn — a single speaker turn for ElevenLabs text_to_dialogue
#
# Each turn carries both the text and the voice_id inline, which is how
# ElevenLabs' dialogue API works. This differs from other providers where
# voice config is global (one voice for the whole request).
# ============================================================================


@dataclass
class DialogueTurn:
    text: str
    voice_id: str

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> DialogueTurn:
        return cls(text=data["text"], voice_id=data["voice_id"])

    def to_dict(self) -> dict[str, str]:
        return {"text": self.text, "voice_id": self.voice_id}

    def to_elevenlabs_input(self) -> dict[str, str]:
        """Return the dict format the ElevenLabs SDK expects."""
        return {"text": self.text, "voice_id": self.voice_id}


# ============================================================================
# ElevenLabsDialogueRegistry — model resolution and batching for ElevenLabs
# text_to_dialogue API.
#
# The API has a 5000-char limit per request — batching is handled internally.
# Supported models: eleven_v3 (multilingual, emotion-aware, best quality),
#                   eleven_multilingual_v2 (stable, broad language support).
# ============================================================================


class ElevenLabsDialogueRegistry:
    VALID_MODELS: frozenset[str] = frozenset({
        "eleven_v3",
        "eleven_multilingual_v2",
    })
    DEFAULT_MODEL: str = "eleven_v3"
    MAX_CHARS_PER_BATCH: int = 4800  # stay safely under the 5000-char API limit
    DEFAULT_OUTPUT_FORMAT: str = "mp3_44100_128"

    # ElevenLabs supports emotion/direction tags in square brackets, e.g. [excited]
    SUPPORTS_EMOTION_TAGS: bool = True

    @classmethod
    def resolve_model(cls, model: Optional[str] = None) -> str:
        if model and model.strip().lower() in cls.VALID_MODELS:
            return model.strip().lower()
        return cls.DEFAULT_MODEL

    @classmethod
    def batch_turns(cls, turns: list[DialogueTurn]) -> list[list[DialogueTurn]]:
        """Split dialogue turns into batches whose combined text stays under MAX_CHARS_PER_BATCH."""
        batches: list[list[DialogueTurn]] = []
        current: list[DialogueTurn] = []
        current_len = 0
        for turn in turns:
            turn_len = len(turn.text)
            if current and current_len + turn_len > cls.MAX_CHARS_PER_BATCH:
                batches.append(current)
                current = []
                current_len = 0
            current.append(turn)
            current_len += turn_len
        if current:
            batches.append(current)
        return batches

    @classmethod
    def is_valid_model(cls, model: str) -> bool:
        return model.strip().lower() in cls.VALID_MODELS
