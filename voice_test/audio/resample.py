"""PCM sample rate conversion using numpy linear interpolation."""

import numpy as np


def resample(pcm: bytes, from_rate: int, to_rate: int) -> bytes:
    """Resample PCM16 mono audio from one sample rate to another.

    Returns the input unchanged if rates match.
    """
    if from_rate == to_rate:
        return pcm

    samples = np.frombuffer(pcm, dtype=np.int16).astype(np.float32)
    ratio = to_rate / from_rate
    new_length = int(len(samples) * ratio)
    if new_length == 0:
        return b""

    old_indices = np.linspace(0, len(samples) - 1, new_length)
    resampled = np.interp(old_indices, np.arange(len(samples)), samples)
    return resampled.astype(np.int16).tobytes()
