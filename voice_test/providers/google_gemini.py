"""Google Gemini Live voice provider using the google-genai SDK."""

from typing import AsyncIterator

from google import genai
from google.genai import types

from voice_test.config import get_api_key
from voice_test.providers.base import AudioFormat, VoiceProvider

MODEL = "gemini-2.5-flash-native-audio-preview-12-2025"


class GoogleGeminiProvider(VoiceProvider):
    def __init__(self) -> None:
        self._session = None
        self._client = None
        self._cm = None  # context manager handle

    @property
    def input_format(self) -> AudioFormat:
        return AudioFormat(sample_rate=16000, sample_width=2, channels=1)

    @property
    def output_format(self) -> AudioFormat:
        return AudioFormat(sample_rate=24000, sample_width=2, channels=1)

    async def connect(self, system_prompt: str) -> None:
        key = get_api_key("gemini")
        self._client = genai.Client(api_key=key)

        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            system_instruction=system_prompt,
        )
        # connect() returns an async context manager — enter it manually
        self._cm = self._client.aio.live.connect(model=MODEL, config=config)
        self._session = await self._cm.__aenter__()

    async def send_audio(self, chunk: bytes) -> None:
        if self._session is None:
            return
        await self._session.send_realtime_input(
            audio=types.Blob(data=chunk, mime_type="audio/pcm;rate=16000")
        )

    async def receive_audio(self) -> AsyncIterator[bytes]:
        if self._session is None:
            return
        async for response in self._session.receive():
            sc = response.server_content
            if sc is None:
                continue
            if sc.model_turn is not None:
                for part in sc.model_turn.parts:
                    if part.inline_data and part.inline_data.data:
                        yield part.inline_data.data

    async def disconnect(self) -> None:
        if self._cm is not None:
            await self._cm.__aexit__(None, None, None)
            self._cm = None
            self._session = None
