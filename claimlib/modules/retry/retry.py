# SPDX-License-Identifier: Apache-2.0
"""Deterministic exponential backoff with full jitter — a reusable, stdlib-only
building block.

A pre-verified code artifact from the VeriClaim claim library. The property that
makes it trustworthy — that every jittered delay lands inside the un-jittered
ceiling window and that the schedule is byte-for-byte reproducible from a seed —
is registered as a claim and proven by a committed evidence artifact; vendoring
this module carries that claim (and its caveat) with it.

Full jitter (AWS Architecture Blog, "Exponential Backoff And Jitter", 2015)
replaces a fixed backoff of ``min(cap, base * 2**attempt)`` with a value drawn
uniformly from ``[0, that ceiling]``. Spreading retries across the whole window
is what actually decorrelates a thundering herd of clients. This module keeps
that spread but makes the draw **deterministic**: the "random" fraction is
derived from a SHA-256 hash of ``(seed, attempt)`` instead of a PRNG, so a given
seed always yields the same schedule — reproducible in tests, logs and across
processes — while different seeds decorrelate different clients.

Public API
----------
    backoff_ceiling(attempt, base, cap) -> float   # un-jittered window top
    jitter_fraction(seed, attempt) -> float        # deterministic value in [0,1)
    backoff_delay(attempt, base, cap, seed) -> float  # jittered delay in [0, ceiling]

    >>> round(backoff_ceiling(3, base=1.0, cap=60.0), 6)
    8.0
    >>> d = backoff_delay(3, base=1.0, cap=60.0, seed=1337)
    >>> 0.0 <= d <= backoff_ceiling(3, 1.0, 60.0)
    True
    >>> backoff_delay(3, 1.0, 60.0, 1337) == backoff_delay(3, 1.0, 60.0, 1337)
    True
"""
from __future__ import annotations

import hashlib

# Number of decimal places the returned delay is rounded to. Rounding keeps the
# schedule byte-stable when serialized (e.g. into a JSON evidence artifact)
# without perturbing the sub-microsecond scheduling behaviour.
_PRECISION = 6

# Width, in bits, of the hash slice mapped onto the [0, 1) unit interval.
_FRACTION_BITS = 64
_FRACTION_DENOM = float(1 << _FRACTION_BITS)


class RetryError(ValueError):
    """A backoff parameter is invalid (negative attempt, non-positive base/cap)."""


def backoff_ceiling(attempt: int, base: float, cap: float) -> float:
    """Un-jittered backoff ceiling for *attempt*: ``min(cap, base * 2**attempt)``.

    This is the classic capped exponential backoff (a.k.a. "exponential backoff
    and full jitter" without the jitter). *attempt* is 0-indexed: attempt 0 is
    the first retry. Raises :class:`RetryError` on a negative attempt or a
    non-positive *base*/*cap* — fail closed rather than emit a nonsensical
    schedule.
    """
    if not isinstance(attempt, int) or isinstance(attempt, bool):
        raise RetryError("attempt must be an int")
    if attempt < 0:
        raise RetryError("attempt must be >= 0")
    if base <= 0:
        raise RetryError("base must be > 0")
    if cap <= 0:
        raise RetryError("cap must be > 0")
    return float(min(cap, base * (2 ** attempt)))


def jitter_fraction(seed: int | str, attempt: int) -> float:
    """Deterministic pseudo-random fraction in ``[0, 1)`` from *(seed, attempt)*.

    Uses SHA-256 over the ASCII string ``"{seed}:{attempt}"`` and maps its top
    64 bits onto the unit interval. This is intentionally **not** the ``random``
    module: the result depends only on the two inputs, so it is identical across
    processes, platforms and Python versions, yet varies smoothly with both seed
    and attempt. Not cryptographically unpredictable — it is a reproducible
    spreading function, not a secret.
    """
    if not isinstance(attempt, int) or isinstance(attempt, bool):
        raise RetryError("attempt must be an int")
    if attempt < 0:
        raise RetryError("attempt must be >= 0")
    key = f"{seed}:{attempt}".encode("utf-8")
    digest = hashlib.sha256(key).digest()
    top = int.from_bytes(digest[: _FRACTION_BITS // 8], "big")
    return top / _FRACTION_DENOM


def backoff_delay(attempt: int, base: float, cap: float, seed: int | str) -> float:
    """Deterministic full-jitter backoff delay for *attempt*, in ``[0, ceiling]``.

    ``ceiling = backoff_ceiling(attempt, base, cap)`` and the returned delay is
    ``jitter_fraction(seed, attempt) * ceiling`` — a value drawn from the whole
    ``[0, ceiling]`` window, reproducible from *seed*. The result is rounded to
    ``_PRECISION`` decimals and clamped so it can never exceed the ceiling even
    after rounding, so the invariant ``0.0 <= delay <= ceiling`` always holds.
    """
    ceiling = backoff_ceiling(attempt, base, cap)
    frac = jitter_fraction(seed, attempt)          # in [0, 1)
    delay = round(frac * ceiling, _PRECISION)
    if delay > ceiling:                            # guard rounding at the top edge
        delay = round(ceiling, _PRECISION)
    return delay
