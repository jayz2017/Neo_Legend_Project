from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from neo_legend.main import app
from neo_legend.registry import build_default_registry


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def registry():
    return build_default_registry()
