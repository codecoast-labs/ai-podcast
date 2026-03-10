"""Voice provider abstract base class."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator


@dataclass
class AudioFormat:
    sample_rate: int
    sample_width: int  # bytes per sample (2 = PCM16)
    channels: int


class VoiceProvider(ABC):
    """Common interface for all real-time voice API providers."""

    @property
    @abstractmethod
    def input_format(self) -> AudioFormat:
        """Audio format the provider expects for input."""

    @property
    @abstractmethod
    def output_format(self) -> AudioFormat:
        """Audio format the provider produces for output."""

    @abstractmethod
    async def connect(self, system_prompt: str) -> None:
        """Open a session with the given system prompt."""

    @abstractmethod
    async def send_audio(self, chunk: bytes) -> None:
        """Send a raw PCM audio chunk to the provider."""

    @abstractmethod
    async def receive_audio(self) -> AsyncIterator[bytes]:
        """Yield raw PCM audio chunks from the provider."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the session and clean up resources."""
