__all__ = [
    "TreeNode",
    "generate_tree",
]


from dataclasses import dataclass
from math import ceil
from typing import Generic, Iterable, Iterator, List, TypeVar

T = TypeVar("T")


@dataclass
class TreeNode(Generic[T]):
    """Represents a node of the generated search tree."""

    parent: str
    start: int
    stop: int
    depth: int
    sibling: int
    first_sibling: bool
    last_sibling: bool
    root: str
    stack: List["TreeNode[T]"]
    items: List[T]

    def partition(self, n: int = 2) -> bool:
        """Attempt to split the current node into a given number of partitions."""
        n = max(n, 2)
        pivot = ceil(self.start + (self.stop - self.start) / (n - self.sibling))

        if pivot < self.stop:
            self.stack.append(
                TreeNode(
                    parent=self.parent,
                    start=pivot,
                    stop=self.stop,
                    depth=self.depth,
                    sibling=self.sibling + 1,
                    first_sibling=False,
                    last_sibling=pivot - self.start >= self.stop - pivot
                    and self.depth > 0,
                    root=self.root,
                    stack=self.stack,
                    items=self.items,
                )
            )
            self.stop = pivot

        if self.stop - self.start > 1:
            self.stack.append(
                TreeNode(
                    parent=self.children,
                    start=self.start,
                    stop=self.stop,
                    depth=self.depth + 1,
                    sibling=0,
                    first_sibling=True,
                    last_sibling=False,
                    root=self.root,
                    stack=self.stack,
                    items=self.items,
                )
            )
            return True

        return False

    @property
    def value(self) -> T:
        return self.items[self.start]

    @property
    def range(self) -> str:
        begin, end = self.start, self.stop - 1

        if begin == end:
            return f"{begin}"

        if self.first_sibling:
            begin = ""
        elif self.last_sibling:
            end = ""

        return f"{begin}..{end}"

    @property
    def children(self) -> str:
        return f"{self.root}/{self.start}_{self.stop - 1}"


def generate_tree(root: str, items: Iterable[T]) -> Iterator[TreeNode[T]]:
    """Depth-first traversal generating a search tree that associates each item to a leaf."""
    stack: List["TreeNode[T]"] = []
    items = list(items)

    stack.append(
        TreeNode(
            parent=root,
            start=0,
            stop=len(items),
            depth=0,
            sibling=0,
            first_sibling=False,
            last_sibling=False,
            root=root,
            stack=stack,
            items=items,
        )
    )

    while stack:
        yield stack.pop()
