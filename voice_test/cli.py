"""CLI menu, provider selection, and session loop."""

from __future__ import annotations

import asyncio
import signal

from voice_test.providers import PROVIDERS

DEFAULT_PROMPT = "You are a helpful, friendly voice assistant. Keep your responses concise."


def print_menu() -> None:
    print("\n  Voice API Tester")
    print("  ================\n")
    print("  Select a provider:")
    for key, info in PROVIDERS.items():
        print(f"    {key}. {info['name']}")
    print()


def select_provider() -> dict | None:
    while True:
        choice = input("  Choice [1-4]: ").strip()
        if choice in PROVIDERS:
            return PROVIDERS[choice]
        if choice.lower() in ("q", "quit", "exit"):
            return None
        print("  Invalid choice. Enter 1-4 or 'q' to quit.")


def get_system_prompt() -> str:
    prompt = input("\n  Enter system prompt (or Enter for default):\n  > ").strip()
    return prompt if prompt else DEFAULT_PROMPT


async def _run_session(provider_info: dict, system_prompt: str) -> None:
    from voice_test.session import run_session

    provider = provider_info["cls"]()

    # Set up Ctrl+C to cancel the session task
    loop = asyncio.get_event_loop()
    task = asyncio.current_task()

    def _sigint_handler() -> None:
        if task and not task.done():
            task.cancel()

    loop.add_signal_handler(signal.SIGINT, _sigint_handler)

    try:
        print(f"\n  Connecting to {provider_info['name']}...")
        await run_session(provider, system_prompt)
    except asyncio.CancelledError:
        pass
    except RuntimeError as e:
        print(f"\n  Error: {e}")
    except Exception as e:
        print(f"\n  Unexpected error: {type(e).__name__}: {e}")
    finally:
        loop.remove_signal_handler(signal.SIGINT)


def main() -> None:
    while True:
        print_menu()
        provider_info = select_provider()
        if provider_info is None:
            print("  Goodbye.")
            break

        system_prompt = get_system_prompt()

        try:
            asyncio.run(_run_session(provider_info, system_prompt))
        except KeyboardInterrupt:
            print("\n  Session ended.")

        try:
            again = input("\n  Start another session? [y/N]: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            again = "n"

        if again != "y":
            print("  Goodbye.")
            break
