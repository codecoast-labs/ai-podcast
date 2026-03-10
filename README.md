# Voice API Tester

CLI tool to test real-time conversational AI voice APIs side-by-side. Speak into your mic and hear responses from different providers through your speakers.

## Supported Providers

| # | Provider | Model | Audio Format |
|---|----------|-------|--------------|
| 1 | OpenAI GPT Realtime 1.5 | `gpt-realtime-1.5` | 24 kHz PCM16 mono |
| 2 | xAI Grok | Realtime API | 24 kHz PCM16 mono |
| 3 | Google Gemini Live | `gemini-2.5-flash-native-audio-preview` | 16 kHz in / 24 kHz out |
| 4 | Hume EVI 3 | EVI 3 (Claude Sonnet backend) | 24 kHz in / 48 kHz out |

## Setup

Requires Python 3.10+ and a working microphone/speaker.

```bash
pip install -e .
```

Copy the example env file and add your API keys:

```bash
cp .env.example .env
```

```
OPENAI_API_KEY=sk-...
XAI_API_KEY=xai-...
GOOGLE_API_KEY=AI...
HUME_API_KEY=...
```

You only need keys for the providers you want to test.

## Usage

```bash
voice-test
```

This opens an interactive menu:

```
  Voice API Tester
  ================

  Select a provider:
    1. OpenAI GPT Realtime 1.5
    2. xAI Grok
    3. Google Gemini Live
    4. Hume EVI 3
```

1. Pick a provider (1-4)
2. Enter a system prompt or press Enter for the default
3. Speak into your mic — the AI responds through your speakers
4. Press `Ctrl+C` to end the session

After each session you can start another or quit.

## Architecture

```
voice_test/
├── cli.py              # Menu, provider selection, session loop
├── config.py           # API key loading from .env
├── session.py          # Orchestrator: mic → provider → speaker
├── audio/
│   ├── capture.py      # Mic input via sounddevice (48 kHz)
│   ├── playback.py     # Speaker output via sounddevice (48 kHz)
│   └── resample.py     # Sample rate conversion between device and provider
└── providers/
    ├── base.py             # VoiceProvider ABC + AudioFormat
    ├── openai_realtime.py  # OpenAI Realtime API (WebSocket)
    ├── xai_grok.py         # xAI Grok Realtime API (WebSocket)
    ├── google_gemini.py    # Google Gemini Live (google-genai SDK)
    └── hume_evi.py         # Hume EVI 3 (hume SDK)
```

All providers implement the `VoiceProvider` interface (`connect`, `send_audio`, `receive_audio`, `disconnect`). The session orchestrator handles resampling between the device's 48 kHz rate and each provider's expected format.
