"""OpenAI GPT Realtime voice provider."""

from __future__ import annotations

import base64
import json
from typing import AsyncIterator

import websockets

from voice_test.config import get_api_key
from voice_test.providers.base import AudioFormat, VoiceProvider

WS_URL = "wss://api.openai.com/v1/realtime?model=gpt-realtime-1.5"


class OpenAIRealtimeProvider(VoiceProvider):
    def __init__(self) -> None:
        self._ws: websockets.WebSocketClientProtocol | None = None

    @property
    def input_format(self) -> AudioFormat:
        return AudioFormat(sample_rate=24000, sample_width=2, channels=1)

    @property
    def output_format(self) -> AudioFormat:
        return AudioFormat(sample_rate=24000, sample_width=2, channels=1)

    async def connect(self, system_prompt: str) -> None:
        key = get_api_key("openai")
        self._ws = await websockets.connect(
            WS_URL,
            additional_headers={
                "Authorization": f"Bearer {key}",
                "OpenAI-Beta": "realtime=v1",
            },
        )
        # Configure session
        await self._ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": system_prompt,
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "turn_detection": {"type": "server_vad"},
            },
        }))

    async def send_audio(self, chunk: bytes) -> None:
        if self._ws is None:
            return
        await self._ws.send(json.dumps({
            "type": "input_audio_buffer.append",
            "audio": base64.b64encode(chunk).decode(),
        }))

    async def receive_audio(self) -> AsyncIterator[bytes]:
        if self._ws is None:
            return
        async for raw in self._ws:
            msg = json.loads(raw)
            if msg.get("type") == "response.audio.delta":
                audio_b64 = msg.get("delta", "")
                if audio_b64:
                    yield base64.b64decode(audio_b64)
            elif msg.get("type") == "error":
                print(f"  [openai] Error: {msg.get('error', {}).get('message', msg)}")

    async def disconnect(self) -> None:
        if self._ws is not None:
            await self._ws.close()
            self._ws = None
