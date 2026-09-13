from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / "backend" / ".env.local")


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes"}


@dataclass(frozen=True)
class Settings:
    """Small environment-only configuration surface; secrets never enter source."""

    # A test-only override keeps automated checks isolated from a running local app.
    data_dir: Path = Path(os.getenv("GDI_DATA_DIR", str(ROOT / "data" / "runtime")))
    chat_enabled: bool = _bool("CHAT_ENABLED")
    admin_token: str = os.getenv("ADMIN_TOKEN", "")
    allowed_origins: tuple[str, ...] = tuple(
        value.strip() for value in os.getenv(
            "ALLOWED_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173"
        ).split(",") if value.strip()
    )
    default_model: str = os.getenv("DEFAULT_MODEL", "gpt-5-nano")
    reasoning_model: str = os.getenv("REASONING_MODEL", "gpt-5-mini")
    per_run_budget_usd: float = float(os.getenv("PER_RUN_BUDGET_USD", "0"))
    input_usd_per_million: float = float(os.getenv("MODEL_INPUT_USD_PER_1M", "0"))
    output_usd_per_million: float = float(os.getenv("MODEL_OUTPUT_USD_PER_1M", "0"))
    vector_store_id: str = os.getenv("OPENAI_VECTOR_STORE_ID", "")
    max_input_tokens: int = int(os.getenv("MAX_INPUT_TOKENS", "12000"))
    max_output_tokens: int = int(os.getenv("MAX_OUTPUT_TOKENS", "4000"))
    sandbox_mode: str = os.getenv("SANDBOX_MODE", "disabled")

    @property
    def openai_ready(self) -> bool:
        value = os.getenv("OPENAI_API_KEY", "")
        return value.startswith("sk-") and len(value) > 20

    @property
    def sandbox_ready(self) -> bool:
        # Fail closed until a verified OpenAI-hosted or isolated provider is configured.
        return self.sandbox_mode == "openai_hosted"


settings = Settings()
