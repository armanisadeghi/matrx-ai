"""Shared conftest for translation tests."""

import os

import pytest
from dotenv import load_dotenv

# Load .env file for test credentials
load_dotenv()


def pytest_configure(config):
    config.addinivalue_line("markers", "db: tests requiring database connection")
