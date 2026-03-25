from __future__ import annotations

import asyncio
import os
import traceback

from google import genai
from matrx_utils import vcprint

from matrx_ai.config import UnifiedConfig, UnifiedResponse
from matrx_ai.config.media_config import VideoContent
from matrx_ai.config.message_config import UnifiedMessage

from .translator import GoogleTranslator


class GoogleVideoGeneration:
    """
    Google Veo video generation endpoint.

    Uses client.models.generate_videos() — a completely separate API from
    generate_content.  The operation is long-polling: we submit the job, then
    poll until operation.done, then download and persist each video.
    """

    def __init__(self):
        self.client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),
            http_options={"api_version": "v1beta"},
        )
        self.translator = GoogleTranslator()

    async def execute(
        self,
        unified_config: UnifiedConfig,
        api_class: str,
        debug: bool = False,
    ) -> UnifiedResponse:
        from matrx_ai.context.app_context import get_app_context

        emitter = get_app_context().emitter

        kwargs = self.translator.to_google_video(unified_config)

        if debug:
            vcprint(kwargs, "[Google Video] generate_videos kwargs", color="blue")

        try:
            def _start_operation():
                return self.client.models.generate_videos(**kwargs)

            if emitter:
                await emitter.send_status_update(
                    status="processing",
                    system_message="Starting video generation (Veo)...",
                    user_message="Starting video generation...",
                )

            initial_operation = await asyncio.get_event_loop().run_in_executor(None, _start_operation)

            def _poll_until_done(op):
                import time
                while not op.done:
                    vcprint("[Google Video] Waiting for video... polling in 10s", color="cyan")
                    time.sleep(10)
                    op = self.client.operations.get(op)
                return op

            operation = await asyncio.get_event_loop().run_in_executor(
                None, _poll_until_done, initial_operation
            )

            result = operation.result
            if not result or not result.generated_videos:
                raise RuntimeError("Google Veo returned no generated videos.")

            from matrx_ai.media import save_media

            content: list[VideoContent] = []
            for generated_video in result.generated_videos:
                def _download(gv=generated_video) -> bytes:
                    # Returns raw bytes directly; also sets gv.video.video_bytes as side effect
                    return self.client.files.download(file=gv.video)

                video_bytes: bytes = await asyncio.get_event_loop().run_in_executor(
                    None, _download
                )

                url = save_media(content=video_bytes, mime_type="video/mp4")
                if not url or not isinstance(url, str):
                    raise RuntimeError(f"save_media returned invalid URL: {url!r}")
                vcprint(f"[Google Video] Saved to Supabase: {url}", color="green")

                vc = VideoContent(url=url, mime_type="video/mp4")
                content.append(vc)

                if emitter:
                    await emitter.send_data(
                        {"type": "video_output", "url": url, "mime_type": "video/mp4"}
                    )

            messages = [UnifiedMessage(role="assistant", content=content)]
            return UnifiedResponse(messages=messages)

        except Exception as e:
            vcprint(e, "[Google Video] Error", color="red")
            traceback.print_exc()

            from matrx_ai.providers.errors import classify_google_error
            error_info = classify_google_error(e)

            if emitter:
                await emitter.send_error(
                    error_type=error_info.error_type,
                    message=error_info.message,
                    user_message=error_info.user_message,
                )

            e.error_info = error_info
            raise
