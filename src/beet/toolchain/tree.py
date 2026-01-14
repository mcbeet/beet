__all__ = [
    "TreeNode",
    "TreeData",
    "generate_tree",
]


from dataclasses import dataclass
from math import ceil
from typing import Callable, Generic, Iterable, Iterator, List, Optional, Tuple, TypeVar

T = TypeVar("T")


@dataclass
class TreeData(Generic[T]):
    """Holds the static data for the search tree."""

    root: str
    stack: List["TreeNode[T]"]
    items: List[T]
    key: Optional[Callable[[T], int]]
    name: Optional[str]


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
    data: TreeData[T]

    def partition(self, n: int = 2) -> bool:
        """Attempt to split the current node into a given number of partitions."""
        n = max(n, 2)
        pivot = ceil(self.start + (self.stop - self.start) / (n - self.sibling))

        if pivot < self.stop:
            last_partition = pivot - self.start >= self.stop - pivot
            self.data.stack.append(
                TreeNode(
                    parent=self.parent,
                    start=pivot,
                    stop=self.stop,
                    depth=self.depth,
                    sibling=self.sibling + 1,
                    first_sibling=False,
                    last_sibling=last_partition and self.depth > 0,
                    data=self.data,
                )
            )
            self.stop = pivot

        if self.stop - self.start > 1:
            self.data.stack.append(
                TreeNode(
                    parent=self.children,
                    start=self.start,
                    stop=self.stop,
                    depth=self.depth + 1,
                    sibling=0,
                    first_sibling=True,
                    last_sibling=False,
                    data=self.data,
                )
            )
            return True

        return False

    @property
    def value(self) -> T:
        return self.data.items[self.start]

    @property
    def items(self) -> List[T]:
        return self.data.items[self.start : self.stop]

    @property
    def delimitters(self) -> Tuple[int, int]:
        begin, end = self.start, self.stop - 1

        if self.data.key:
            begin = self.data.key(self.data.items[begin])
            end = self.data.key(self.data.items[end])

        return begin, end

    @property
    def range(self) -> str:
        begin, end = self.delimitters

        if begin == end:
            return f"{begin}"

        if self.first_sibling:
            begin = ""
        elif self.last_sibling:
            end = ""

        return f"{begin}..{end}"

    @property
    def children(self) -> str:
        begin, end = self.delimitters
        if self.data.name:
            return f"{self.data.root}/{self.data.name}/{begin}_{end}"
        else:
            return f"{self.data.root}/{begin}_{end}"

    @property
    def root(self) -> bool:
        return self.stop - self.start == len(self.data.items)


def generate_tree(
    root: str,
    items: Iterable[T],
    key: Optional[Callable[[T], int]] = None,
    name: Optional[str] = None,
) -> Iterator[TreeNode[T]]:
    """Generate a search tree and yield nodes in a depth-first traversal."""
    data = TreeData[T](root, [], list(items), key, name)

    data.stack.append(
        TreeNode(
            parent=root,
            start=0,
            stop=len(data.items),
            depth=0,
            sibling=0,
            first_sibling=False,
            last_sibling=False,
            data=data,
        )
    )

    while data.stack:
        yield data.stack.pop()
