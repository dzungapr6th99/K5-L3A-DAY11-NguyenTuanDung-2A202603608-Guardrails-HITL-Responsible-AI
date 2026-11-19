"""Provider routing must not accidentally send local requests to a cloud API."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from core import config
from agents.red_advance_nemo import _model_entry


def test_local_routes_and_nemo_use_same_endpoint(monkeypatch):
    monkeypatch.setenv("BLUE_TEAM_PROVIDER", "ollama")
    monkeypatch.setenv("RED_TEAM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://jetson:11434/")
    monkeypatch.setenv("LAB_OLLAMA_MODEL", "lfm3:1.7b")
    monkeypatch.setenv("OLLAMA_RED_MODEL", "red-test")
    assert config.get_blue_model() == "lfm3:1.7b"
    assert config.get_red_model() == "red-test"
    assert config.red_uses_openai_sdk()
    assert config.blue_client_kwargs() == config.red_openai_client_kwargs()
    assert config.blue_client_kwargs()["base_url"] == "http://jetson:11434/v1"
    entry = _model_entry("ollama", "red-test")
    assert entry["parameters"] == {**config.red_openai_client_kwargs(), "reasoning_effort": "none"}
    assert entry["model"] == "red-test"


def test_cloud_blue_keeps_required_model(monkeypatch):
    monkeypatch.setenv("BLUE_TEAM_PROVIDER", "openrouter")
    monkeypatch.setenv("LAB_OLLAMA_MODEL", "other-model")
    assert config.get_blue_model() == "liquid/lfm-3-1.7b:free"
    assert "openrouter.ai" in config.blue_client_kwargs()["base_url"]


def test_unknown_provider_is_rejected(monkeypatch):
    monkeypatch.setenv("RED_TEAM_PROVIDER", "olama")
    with pytest.raises(ValueError):
        config.get_red_provider()
