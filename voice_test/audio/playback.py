"""Speaker playback: asyncio.Queue → sounddevice OutputStream."""

from __future__ import annotations

import asyncio

import numpy as np
import sounddevice as sd

DEVICE_SAMPLE_RATE = 48000


class Speaker:
    """Plays raw PCM16 mono chunks from an asyncio queue through the default speaker."""

    def __init__(self) -> None:
        self.queue: asyncio.Queue[bytes] = asyncio.Queue()
        self._stream: sd.OutputStream | None = None

    def start(self) -> None:
        self._stream = sd.OutputStream(
            samplerate=DEVICE_SAMPLE_RATE,
            channels=1,
            dtype="int16",
        )
        self._stream.start()

    def stop(self) -> None:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    async def play_loop(self) -> None:
        """Continuously pull chunks from the queue and write to the speaker."""
        while True:
            chunk = await self.queue.get()
            if self._stream is None:
                continue
            samples = np.frombuffer(chunk, dtype=np.int16)
            self._stream.write(samples.reshape(-1, 1))
