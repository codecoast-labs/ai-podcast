"""Session orchestrator: wires provider + audio pipeline."""

import asyncio

from voice_test.audio.capture import MicCapture, DEVICE_SAMPLE_RATE
from voice_test.audio.playback import Speaker
from voice_test.audio.resample import resample
from voice_test.providers.base import VoiceProvider


async def run_session(provider: VoiceProvider, system_prompt: str) -> None:
    """Run a full voice session: mic → provider → speaker.

    Blocks until cancelled (Ctrl+C).
    """
    loop = asyncio.get_event_loop()
    mic = MicCapture(loop=loop)
    speaker = Speaker()

    await provider.connect(system_prompt)
    print("  Connected. Session active — speak into your mic.")
    print("  Press Ctrl+C to end.\n")

    mic.start()
    speaker.start()

    async def capture_and_send() -> None:
        """Read mic chunks, resample to provider input rate, and send."""
        in_rate = provider.input_format.sample_rate
        while True:
            chunk = await mic.queue.get()
            resampled = resample(chunk, DEVICE_SAMPLE_RATE, in_rate)
            await provider.send_audio(resampled)

    async def receive_and_enqueue() -> None:
        """Receive audio from provider, resample to device rate, and enqueue for playback."""
        out_rate = provider.output_format.sample_rate
        # Loop because some providers (Gemini) end their iterator after each turn
        while True:
            async for chunk in provider.receive_audio():
                resampled = resample(chunk, out_rate, DEVICE_SAMPLE_RATE)
                await speaker.queue.put(resampled)
            await asyncio.sleep(0.05)

    tasks = [
        asyncio.create_task(capture_and_send()),
        asyncio.create_task(receive_and_enqueue()),
        asyncio.create_task(speaker.play_loop()),
    ]

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        pass
    finally:
        for t in tasks:
            t.cancel()
        # Wait for tasks to finish cancellation
        await asyncio.gather(*tasks, return_exceptions=True)
        mic.stop()
        speaker.stop()
        await provider.disconnect()
        print("\n  Session ended.")
