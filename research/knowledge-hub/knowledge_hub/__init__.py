"""Knowledge Hub scaffold package."""

from .aitp_service import AITPService
from .hub import KnowledgeHub
from ._version import __version__

__all__ = ["KnowledgeHub", "AITPService", "__version__"]
