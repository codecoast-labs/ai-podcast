"""Provider registry."""

from voice_test.providers.openai_realtime import OpenAIRealtimeProvider
from voice_test.providers.xai_grok import XAIGrokProvider
from voice_test.providers.google_gemini import GoogleGeminiProvider
from voice_test.providers.hume_evi import HumeEVIProvider

PROVIDERS: dict[str, dict] = {
    "1": {
        "name": "OpenAI GPT Realtime 1.5",
        "key": "openai",
        "cls": OpenAIRealtimeProvider,
    },
    "2": {
        "name": "xAI Grok",
        "key": "xai",
        "cls": XAIGrokProvider,
    },
    "3": {
        "name": "Google Gemini Live",
        "key": "gemini",
        "cls": GoogleGeminiProvider,
    },
    "4": {
        "name": "Hume EVI 3",
        "key": "hume",
        "cls": HumeEVIProvider,
    },
}
