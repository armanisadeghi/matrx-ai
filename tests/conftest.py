"""Root conftest — shared test initialization."""

from dotenv import load_dotenv

from matrx_ai.db import _setup

load_dotenv()
_setup()
