"""Shared conftest for translation tests."""

import os

import pytest
from dotenv import load_dotenv

from matrx_ai.db import _setup

# Load .env file for test credentials
load_dotenv()
_setup()


def pytest_configure(config):
    config.addinivalue_line("markers", "db: tests requiring database connection")
