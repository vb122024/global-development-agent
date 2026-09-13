from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    # Short greetings are useful UX and are handled locally without a model call.
    question: str = Field(min_length=1, max_length=1000)
    countries: list[str] = Field(default_factory=list, max_length=10)
    start_year: int = Field(default=2019, ge=1960, le=2100)
    end_year: int = Field(default=2023, ge=1960, le=2100)
    mode: Literal["live"] = "live"
    session_id: str | None = Field(default=None, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")


class SettingsPatch(BaseModel):
    chat_enabled: bool


class DataRefreshRequest(BaseModel):
    countries: list[str] = Field(default_factory=list, max_length=10)
    start_year: int = Field(default=2019, ge=1960, le=2100)
    end_year: int = Field(default=2024, ge=1960, le=2100)


class DataCleanRequest(BaseModel):
    countries: list[str] = Field(default_factory=list, max_length=10)
    mode: Literal["preview", "model"] = "preview"


class Citation(BaseModel):
    source_id: str
    title: str
    url: str


class AgentHandoff(BaseModel):
    """An inspectable handoff between live specialist agents."""

    from_agent: str
    to_agent: str
    purpose: str
    tools: list[str] = Field(default_factory=list)
    status: Literal["completed", "skipped"] = "completed"


class LiveAgentAnswer(BaseModel):
    """Validated shape required from the live synthesis agent."""

    answer: str
    citations: list[Citation]
    limitations: list[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    run_id: str
    status: str
    answer: str
    citations: list[Citation]
    model: str | None = None
    estimated_cost_usd: float | None = None
    limitations: list[str] = Field(default_factory=list)
    handoffs: list[AgentHandoff] = Field(default_factory=list)
    session_id: str | None = None
