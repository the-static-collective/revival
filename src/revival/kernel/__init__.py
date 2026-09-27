"""Frozen kernel contracts.

New kernel generations must be added as descendants rather than silently
rewriting an existing generation.
"""

from .v1 import KERNEL_VERSION, PRIMITIVES

__all__ = ["KERNEL_VERSION", "PRIMITIVES"]
