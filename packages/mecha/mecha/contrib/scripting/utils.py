__all__ = [
    "ScriptingQuoteHelper",
]


from dataclasses import dataclass, field
from typing import Dict

from mecha.utils import QuoteHelperWithUnicode


@dataclass
class ScriptingQuoteHelper(QuoteHelperWithUnicode):
    """Quote helper used for scripting."""

    escape_sequences: Dict[str, str] = field(
        default_factory=lambda: {
            r"\\": "\\",
            r"\f": "\f",
            r"\n": "\n",
            r"\r": "\r",
            r"\t": "\t",
        }
    )
