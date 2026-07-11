# SPDX-License-Identifier: Apache-2.0
"""Deterministic token-bucket rate limiter — a reusable, stdlib-only building block.

A pre-verified code artifact from the VeriClaim claim library. The property that
makes it trustworthy — that available tokens never exceed the configured
capacity, no matter how much idle time elapses between requests — is registered
as a claim and proven by a committed evidence artifact; vendoring this module
carries that claim (and its caveat) with it.

The token bucket is the classic rate-limiting mechanism (RFC 2697/2698 traffic
metering, and the algorithm behind most API quota limiters). A bucket holds up
to ``capacity`` tokens and refills continuously at ``refill_per_sec`` tokens per
second. Each request costs tokens; a request is allowed only if enough tokens
are present. This lets short bursts through (up to the bucket depth) while
bounding the long-run average rate — and, crucially, the bucket never
accumulates more than ``capacity`` tokens, so a long quiet period cannot be
"banked" into an unbounded burst later.

This implementation is *time-injected*: the caller passes the current time to
every operation, so behaviour is fully deterministic and testable — there is no
hidden wall-clock read.

Public API
----------
    TokenBucket(capacity, refill_per_sec)      # construct a full bucket
    bucket.available(now_seconds) -> float     # tokens available now (refills, no consume)
    bucket.allow(now_seconds, cost=1) -> bool  # try to consume `cost` tokens
    bucket.tokens -> float                     # current stored token level (read-only)

    >>> b = TokenBucket(capacity=2, refill_per_sec=1)
    >>> b.allow(0.0), b.allow(0.0), b.allow(0.0)   # burst of 2, then empty
    (True, True, False)
    >>> b.allow(1.0)                               # 1s later, 1 token refilled
    True
"""
from __future__ import annotations


class TokenBucketError(ValueError):
    """Invalid construction or a non-monotonic / negative-cost request."""


class TokenBucket:
    """A continuously-refilling token bucket with time supplied by the caller.

    Parameters
    ----------
    capacity:
        Maximum tokens the bucket can hold (its burst size). Must be > 0.
    refill_per_sec:
        Tokens added per second of elapsed time. Must be >= 0 (0 disables
        refill: the bucket then allows at most ``capacity`` total requests).

    The bucket starts **full** (``tokens == capacity``). The clock is set on the
    first ``available``/``allow`` call; elapsed time is measured from there.
    Timestamps must be non-decreasing — a request whose ``now_seconds`` is
    earlier than the previous one raises :class:`TokenBucketError` (fail closed
    rather than silently mis-meter time going backwards).
    """

    __slots__ = ("_capacity", "_rate", "_tokens", "_last")

    def __init__(self, capacity: float, refill_per_sec: float) -> None:
        if not isinstance(capacity, (int, float)) or isinstance(capacity, bool):
            raise TokenBucketError(f"capacity must be a number, got {capacity!r}")
        if not isinstance(refill_per_sec, (int, float)) or isinstance(refill_per_sec, bool):
            raise TokenBucketError(f"refill_per_sec must be a number, got {refill_per_sec!r}")
        if capacity <= 0:
            raise TokenBucketError(f"capacity must be > 0, got {capacity!r}")
        if refill_per_sec < 0:
            raise TokenBucketError(f"refill_per_sec must be >= 0, got {refill_per_sec!r}")
        self._capacity = float(capacity)
        self._rate = float(refill_per_sec)
        self._tokens = float(capacity)  # start full
        self._last: float | None = None

    @property
    def capacity(self) -> float:
        """The bucket's maximum token level (burst size)."""
        return self._capacity

    @property
    def refill_per_sec(self) -> float:
        """Tokens added per second of elapsed time."""
        return self._rate

    @property
    def tokens(self) -> float:
        """The currently stored token level (as of the last operation)."""
        return self._tokens

    def available(self, now_seconds: float) -> float:
        """Advance the clock to *now_seconds*, refill, and return tokens available.

        Refills by ``elapsed * refill_per_sec`` since the last operation and
        clamps the result to ``capacity`` — this clamp is the safety property:
        idle time can never bank more than a full bucket. Does **not** consume
        any tokens. Raises :class:`TokenBucketError` if time moves backwards.
        """
        if not isinstance(now_seconds, (int, float)) or isinstance(now_seconds, bool):
            raise TokenBucketError(f"now_seconds must be a number, got {now_seconds!r}")
        # NaN/inf would poison _last and defeat the non-decreasing check; the
        # class advertises fail-closed time handling, so reject non-finite time.
        if now_seconds != now_seconds or now_seconds in (float("inf"), float("-inf")):
            raise TokenBucketError(f"now_seconds must be finite, got {now_seconds!r}")
        if self._last is None:
            self._last = float(now_seconds)
        elapsed = float(now_seconds) - self._last
        if elapsed < 0:
            raise TokenBucketError(
                f"timestamps must be non-decreasing: {now_seconds!r} < {self._last!r}")
        self._last = float(now_seconds)
        # The clamp is the whole point: available tokens never exceed capacity.
        self._tokens = min(self._capacity, self._tokens + elapsed * self._rate)
        return self._tokens

    def allow(self, now_seconds: float, cost: float = 1) -> bool:
        """Try to consume *cost* tokens at *now_seconds*; return whether allowed.

        Refills first (see :meth:`available`), then grants the request iff at
        least ``cost`` tokens are available, decrementing on grant. A denied
        request consumes nothing. ``cost`` must be >= 0.
        """
        if not isinstance(cost, (int, float)) or isinstance(cost, bool):
            raise TokenBucketError(f"cost must be a number, got {cost!r}")
        if cost < 0:
            raise TokenBucketError(f"cost must be >= 0, got {cost!r}")
        level = self.available(now_seconds)
        if level >= cost:
            self._tokens = level - cost
            return True
        return False
