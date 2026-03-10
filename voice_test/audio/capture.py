"""Microphone capture: sounddevice callback → asyncio.Queue."""

from __future__ import annotations

import asyncio

import numpy as np
import sounddevice as sd

DEVICE_SAMPLE_RATE = 48000
BLOCK_SIZE = 2400  # 50ms at 48kHz


class MicCapture:
    """Streams raw PCM16 mono chunks from the default mic into an asyncio queue."""

    def __init__(self, loop: asyncio.AbstractEventLoop | None = None):
        self.queue: asyncio.Queue[bytes] = asyncio.Queue()
        self._loop = loop
        self._stream: sd.InputStream | None = None

    def _callback(
        self, indata: np.ndarray, frames: int, time_info: object, status: sd.CallbackFlags
    ) -> None:
        if status:
            print(f"  [mic] {status}")
        # indata is float32 [-1, 1] → convert to int16 PCM
        pcm = (indata[:, 0] * 32767).astype(np.int16).tobytes()
        loop = self._loop or asyncio.get_event_loop()
        loop.call_soon_threadsafe(self.queue.put_nowait, pcm)

    def start(self) -> None:
        self._loop = self._loop or asyncio.get_event_loop()
        self._stream = sd.InputStream(
            samplerate=DEVICE_SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=BLOCK_SIZE,
            callback=self._callback,
        )
        self._stream.start()

    def stop(self) -> None:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
