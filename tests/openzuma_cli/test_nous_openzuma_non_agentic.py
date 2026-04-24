"""Tests for the Nous-Openzuma-3/4 non-agentic warning detector.

Prior to this check, the warning fired on any model whose name contained
``"openzuma"`` anywhere (case-insensitive). That false-positived on unrelated
local Modelfiles such as ``openzuma-brain:qwen3-14b-ctx16k`` — a tool-capable
Qwen3 wrapper that happens to live under the "openzuma" tag namespace.

``is_nous_openzuma_non_agentic`` should only match the actual Nous Research
Openzuma-3 / Openzuma-4 chat family.
"""

from __future__ import annotations

import pytest

from openzuma_cli.model_switch import (
    _OPENZUMA_MODEL_WARNING,
    _check_openzuma_model_warning,
    is_nous_openzuma_non_agentic,
)


@pytest.mark.parametrize(
    "model_name",
    [
        "NousResearch/Openzuma-3-Llama-3.1-70B",
        "NousResearch/Openzuma-3-Llama-3.1-405B",
        "openzuma-3",
        "Openzuma-3",
        "openzuma-4",
        "openzuma-4-405b",
        "openzuma_4_70b",
        "openrouter/openzuma3:70b",
        "openrouter/nousresearch/openzuma-4-405b",
        "NousResearch/Openzuma3",
        "openzuma-3.1",
    ],
)
def test_matches_real_nous_openzuma_chat_models(model_name: str) -> None:
    assert is_nous_openzuma_non_agentic(model_name), (
        f"expected {model_name!r} to be flagged as Nous Openzuma 3/4"
    )
    assert _check_openzuma_model_warning(model_name) == _OPENZUMA_MODEL_WARNING


@pytest.mark.parametrize(
    "model_name",
    [
        # Kyle's local Modelfile — qwen3:14b under a custom tag
        "openzuma-brain:qwen3-14b-ctx16k",
        "openzuma-brain:qwen3-14b-ctx32k",
        "openzuma-honcho:qwen3-8b-ctx8k",
        # Plain unrelated models
        "qwen3:14b",
        "qwen3-coder:30b",
        "qwen2.5:14b",
        "claude-opus-4-6",
        "anthropic/claude-sonnet-4.5",
        "gpt-5",
        "openai/gpt-4o",
        "google/gemini-2.5-flash",
        "deepseek-chat",
        # Non-chat Openzuma models we don't warn about
        "openzuma-llm-2",
        "openzuma2-pro",
        "nous-openzuma-2-mistral",
        # Edge cases
        "",
        "openzuma",  # bare "openzuma" isn't the 3/4 family
        "openzuma-brain",
        "brain-openzuma-3-impostor",  # "3" not preceded by /: boundary
    ],
)
def test_does_not_match_unrelated_models(model_name: str) -> None:
    assert not is_nous_openzuma_non_agentic(model_name), (
        f"expected {model_name!r} NOT to be flagged as Nous Openzuma 3/4"
    )
    assert _check_openzuma_model_warning(model_name) == ""


def test_none_like_inputs_are_safe() -> None:
    assert is_nous_openzuma_non_agentic("") is False
    # Defensive: the helper shouldn't crash on None-ish falsy input either.
    assert _check_openzuma_model_warning("") == ""
