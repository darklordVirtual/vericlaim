# SPDX-License-Identifier: Apache-2.0
"""vericlaim — a Claim-Oriented Programming gate.

Verify that every claim a project makes about itself is backed by a committed
artifact, and that documentation never drifts from the single source of truth.
Design by Contract for the whole project, enforced in CI. Zero third-party
dependencies (Python 3.11+).
"""
from .config import Config, load_config
from .gate import run
from .register import load_register

# SINGLE SOURCE OF TRUTH for the version. pyproject.toml reads it via
# [tool.hatch.version]; CITATION.cff and the README are held to it by
# tests/test_version_consistency.py and CLAIM-META-001. Bump here, nowhere else.
__version__ = "0.4.0"
__all__ = ["Config", "load_config", "run", "load_register", "__version__"]
