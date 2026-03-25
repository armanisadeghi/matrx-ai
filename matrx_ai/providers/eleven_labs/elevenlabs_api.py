from __future__ import annotations

import asyncio

from matrx_utils import vcprint

from matrx_ai.config import (
    AudioContent,
    TokenUsage,
    UnifiedConfig,
    UnifiedMessage,
    UnifiedResponse,
)
from matrx_ai.media.media_persistence import save_media
from matrx_ai.context.emitter_protocol import Emitter

from .client import get_elevenlabs_client


class ElevenLabsChat:
    """ElevenLabs TTS endpoint — supports both dialogue (multi-voice) and
    single-speaker modes via the text_to_dialogue API."""

    endpoint_name: str = "[ELEVENLABS CHAT]"

    def __init__(self) -> None:
        self.client = get_elevenlabs_client()

    async def execute(
        self,
        unified_config: UnifiedConfig,
        api_class: str,
        debug: bool = False,
    ) -> UnifiedResponse:
        from matrx_ai.context.app_context import get_app_context

        emitter: Emitter = get_app_context().emitter
        matrx_model_name = unified_config.model

        vcprint(f"[ElevenLabs Chat] executing api_class={api_class}", color="blue")

        return await self._execute_tts(unified_config, emitter, matrx_model_name)

    async def _execute_tts(
        self,
        unified_config: UnifiedConfig,
        emitter: Emitter,
        matrx_model_name: str,
    ) -> UnifiedResponse:
        from matrx_ai.config.tts_config import ElevenLabsDialogueRegistry

        tts = unified_config.tts_voice_config
        if not tts or not tts.is_configured:
            raise ValueError(
                "[ElevenLabs TTS] No tts_voice configured. "
                "Pass tts_voice as a list of {text, voice_id} dicts for dialogue mode, "
                "or a string voice_id for single-speaker mode."
            )

        audio_format = (unified_config.audio_format or "mp3").lower()
        # ElevenLabs output_format uses a compound string like "mp3_44100_128"
        valid_codecs = {"mp3", "wav", "pcm", "ulaw"}
        codec = audio_format if audio_format in valid_codecs else "mp3"
        mime_map = {"mp3": "audio/mpeg", "wav": "audio/wav", "pcm": "audio/pcm", "ulaw": "audio/basic"}
        mime_type = mime_map.get(codec, "audio/mpeg")

        # Resolve dialogue inputs — dialogue mode uses inline voice_ids;
        # single-speaker mode extracts text from messages and wraps it.
        if tts.is_dialogue:
            batched_inputs, model = tts.to_elevenlabs(model=unified_config.model)
        else:
            text_parts: list[str] = []
            for msg in unified_config.messages:
                if hasattr(msg, "content"):
                    for c in msg.content:
                        if hasattr(c, "text") and c.text:
                            text_parts.append(c.text)
            input_text = " ".join(text_parts).strip() or "."
            input_text = tts.strip_speaker_labels(input_text)
            batched_inputs, model = tts.to_elevenlabs(text=input_text, model=unified_config.model)

        vcprint(
            f"[ElevenLabs TTS] model={model} batches={len(batched_inputs)} "
            f"turns={sum(len(b) for b in batched_inputs)} codec={codec}",
            color="blue",
        )

        await emitter.send_status_update(
            status="processing",
            system_message=f"Generating audio ({sum(len(b) for b in batched_inputs)} dialogue turns)...",
            user_message="Generating audio...",
        )

        # ElevenLabs SDK is synchronous — run each batch in a thread executor
        # so the event loop stays free for heartbeats and status events.
        all_audio_bytes = b""
        for i, batch in enumerate(batched_inputs):
            batch_num = i + 1
            total_batches = len(batched_inputs)
            char_count = sum(len(t["text"]) for t in batch)
            vcprint(
                f"[ElevenLabs TTS] Requesting batch {batch_num}/{total_batches} ({char_count} chars)",
                color="cyan",
            )
            if total_batches > 1:
                await emitter.send_status_update(
                    status="processing",
                    system_message=f"Processing batch {batch_num}/{total_batches}...",
                    user_message=f"Generating audio part {batch_num} of {total_batches}...",
                )

            def _run_batch(b: list[dict]) -> bytes:
                audio_stream = self.client.text_to_dialogue.stream(
                    inputs=b, model_id=model
                )
                return b"".join(chunk for chunk in audio_stream if isinstance(chunk, bytes))

            batch_bytes = await asyncio.get_event_loop().run_in_executor(None, _run_batch, batch)
            all_audio_bytes += batch_bytes
            vcprint(f"[ElevenLabs TTS] Batch {batch_num} complete: {len(batch_bytes)} bytes", color="cyan")

        await emitter.send_status_update(
            status="processing",
            system_message=f"Audio received ({len(all_audio_bytes):,} bytes). Saving...",
            user_message="Audio received. Saving...",
        )

        url = save_media(content=all_audio_bytes, mime_type=mime_type, audio_format=codec)
        vcprint(f"[ElevenLabs TTS] Saved: {url}", color="green")

        audio_content = AudioContent(url=url, mime_type=mime_type)
        msg = UnifiedMessage(role="assistant", content=[audio_content])

        usage = TokenUsage(
            input_tokens=0,
            output_tokens=0,
            matrx_model_name=matrx_model_name,
            provider_model_name=model,
            api="elevenlabs",
        )

        unified_response = UnifiedResponse(messages=[msg], usage=usage)

        await emitter.send_data({"type": "audio_output", "url": url, "mime_type": mime_type})
        await asyncio.sleep(0)

        return unified_response
