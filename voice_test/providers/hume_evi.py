"""Hume EVI 3 voice provider."""

from __future__ import annotations

import base64
from typing import AsyncIterator

from hume import AsyncHumeClient
from hume.empathic_voice.types import (
    AudioConfiguration,
    AudioInput,
    ConnectSessionSettings,
)

from voice_test.config import get_api_key
from voice_test.providers.base import AudioFormat, VoiceProvider

WAV_HEADER_SIZE = 44  # Standard WAV header to strip from audio output


class HumeEVIProvider(VoiceProvider):
    def __init__(self) -> None:
        self._client: AsyncHumeClient | None = None
        self._socket = None
        self._cm = None  # context manager handle
        self._config_id: str | None = None

    @property
    def input_format(self) -> AudioFormat:
        return AudioFormat(sample_rate=24000, sample_width=2, channels=1)

    @property
    def output_format(self) -> AudioFormat:
        # Hume outputs 48kHz WAV; we strip the header and get raw PCM
        return AudioFormat(sample_rate=48000, sample_width=2, channels=1)

    async def connect(self, system_prompt: str) -> None:
        key = get_api_key("hume")
        self._client = AsyncHumeClient(api_key=key)

        # Create an EVI config on the fly with the system prompt
        config = await self._client.empathic_voice.configs.create_config(
            evi_version="3",
            name="voice-test-session",
            prompt={"text": system_prompt},
            language_model={
                "model_provider": "ANTHROPIC",
                "model_resource": "claude-sonnet-4-20250514",
            },
        )
        self._config_id = config.id

        # connect() returns an async context manager — enter it manually
        self._cm = self._client.empathic_voice.chat.connect(
            config_id=self._config_id,
            session_settings=ConnectSessionSettings(
                audio=AudioConfiguration(
                    encoding="linear16",
                    sample_rate=24000,
                    channels=1,
                )
            ),
        )
        self._socket = await self._cm.__aenter__()

    async def send_audio(self, chunk: bytes) -> None:
        if self._socket is None:
            return
        encoded = base64.b64encode(chunk).decode("utf-8")
        await self._socket.send_publish(AudioInput(data=encoded))

    async def receive_audio(self) -> AsyncIterator[bytes]:
        if self._socket is None:
            return
        async for msg in self._socket:
            if msg.type == "audio_output":
                raw = base64.b64decode(msg.data)
                # Strip WAV header if present
                if len(raw) > WAV_HEADER_SIZE and raw[:4] == b"RIFF":
                    raw = raw[WAV_HEADER_SIZE:]
                yield raw
            elif msg.type == "user_message":
                # Log emotion data if available
                if hasattr(msg, "models") and msg.models:
                    prosody = getattr(msg.models, "prosody", None)
                    if prosody and prosody.scores:
                        scores = dict(prosody.scores)
                        top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
                        emotions = ", ".join(f"{k}: {v:.2f}" for k, v in top)
                        print(f"  [hume emotions] {emotions}")
            elif msg.type == "error":
                print(f"  [hume] Error: {getattr(msg, 'message', msg)}")

    async def disconnect(self) -> None:
        if self._cm is not None:
            try:
                await self._cm.__aexit__(None, None, None)
            except Exception:
                pass
            self._cm = None
            self._socket = None

        # Clean up the config we created
        if self._client is not None and self._config_id is not None:
            try:
                await self._client.empathic_voice.configs.delete_config(
                    id=self._config_id
                )
            except Exception:
                pass
            self._config_id = None
        self._client = None
