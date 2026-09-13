from __future__ import annotations

from threading import Lock

from .settings import settings


class RuntimeState:
    """Process-local owner settings; restart resets them to environment defaults."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._chat_enabled = settings.chat_enabled

    @property
    def chat_enabled(self) -> bool:
        with self._lock:
            return self._chat_enabled

    def set_chat_enabled(self, enabled: bool) -> None:
        with self._lock:
            self._chat_enabled = enabled


runtime_state = RuntimeState()
