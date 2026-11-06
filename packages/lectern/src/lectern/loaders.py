__all__ = [
    "LinkFragmentLoader",
]


from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

from .directive import Directive
from .fragment import Fragment, InvalidFragment


@dataclass
class LinkFragmentLoader:
    """Loader for validating link fragments."""

    status: Literal["enable", "ignore", "disable"] = "enable"

    def __call__(
        self,
        fragment: Fragment,
        directives: Mapping[str, Directive],
    ) -> Fragment | None:
        if fragment.url or fragment.modifier == "download":
            if self.status == "ignore":
                return None
            if self.status == "disable":
                msg = "Link fragments are disabled."
                raise InvalidFragment(msg, fragment.start_line)
        return fragment
