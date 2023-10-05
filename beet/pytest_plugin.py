from pathlib import Path
from pprint import pformat

from _pytest.assertion.util import assertrepr_compare

from beet import (
    DataPack,
    File,
    Namespace,
    NamespaceContainer,
    OverlayContainer,
    Pack,
    ResourcePack,
)
from beet.library.test_utils import ignore_name

try:
    from pytest_insta import Fmt
except ImportError:
    pass
else:

    class FmtResourcePack(Fmt[ResourcePack]):
        extension = ".resource_pack"

        def load(self, path: Path) -> ResourcePack:
            return ignore_name(ResourcePack(path=path))

        def dump(self, path: Path, value: ResourcePack):
            value.save(path=path, overwrite=True)

    class FmtDataPack(Fmt[DataPack]):
        extension = ".data_pack"

        def load(self, path: Path) -> DataPack:
            return ignore_name(DataPack(path=path))

        def dump(self, path: Path, value: DataPack):
            value.save(path=path, overwrite=True)


def pytest_assertrepr_compare(config, op, left, right):
    if type(left) != type(right) or op != "==":
        return

    explanation = []

    if isinstance(left, Pack):
        if left.name != right.name:
            if diff := assertrepr_compare(config, op, left.name, right.name):
                explanation += ["", "Differing attribute 'name':"] + diff[1:]
        if left.extra != right.extra:
            explanation += generate_explanation(config, left.extra, right.extra, "file")
        if dict(left) != dict(right):
            explanation += generate_explanation(config, left, right, "namespace")
        if left.overlays != right.overlays:
            explanation += generate_explanation(
                config, left.overlays, right.overlays, "overlay"
            )
    elif isinstance(left, Namespace):
        if left.extra != right.extra:
            explanation += generate_explanation(config, left.extra, right.extra, "file")
        if dict(left) != dict(right):
            explanation += generate_explanation(config, left, right, "container")
    elif isinstance(left, NamespaceContainer):
        explanation += generate_explanation(config, left, right, "file")
    elif isinstance(left, File):
        if diff := config.hook.pytest_assertrepr_compare(
            config=config,
            op="==",
            left=left.ensure_deserialized(),
            right=right.ensure_deserialized(),
        ):
            return diff[0]
    elif isinstance(left, OverlayContainer):
        explanation += generate_explanation(config, left, right, "pack")

    if explanation and (diff := assertrepr_compare(config, op, left, right)):
        return [diff[0]] + explanation


def plural(name, count):
    return name + bool(count - 1) * "s"


def generate_explanation(config, left, right, item_name):
    verbose = config.getoption("verbose")

    left_keys = set(k for k, v in left.items() if v)
    right_keys = set(k for k, v in right.items() if v)

    common = left_keys & right_keys
    same = {key for key in common if left[key] == right[key]}
    diff = common - same
    extra_left = left_keys - right_keys
    extra_right = right_keys - left_keys

    yield ""

    if same and verbose < 2:
        count = len(same)
        yield f"Omitting {count} identical {plural(item_name, count)}, use -vv to show"
    elif same:
        count = len(same)
        yield f"Matching {plural(item_name, count)}:"
        yield from pformat(list(same)).splitlines()

    if diff:
        count = len(diff)
        yield f"Differing {plural(item_name, count)}:"
        yield from pformat(list(diff)).splitlines()

    if extra_left:
        count = len(extra_left)
        yield f"Left contains {count} more {plural(item_name, count)}:"
        yield from pformat({k: left[k] for k in extra_left}).splitlines()

    if extra_right:
        count = len(extra_right)
        yield f"Right contains {count} more {plural(item_name, count)}:"
        yield from pformat({k: right[k] for k in extra_right}).splitlines()

    if not diff:
        return

    if verbose < 1:
        yield ""
        yield "Use -v to get the full diff"
        return

    for k in diff:
        yield ""
        yield f"Drill down into differing {item_name} {k!r}:"

        if result := config.hook.pytest_assertrepr_compare(
            config=config,
            op="==",
            left=left[k],
            right=right[k],
        ):
            summary, *explanation = result[0]
            yield f"  assert " + summary
            for line in explanation:
                yield "  " + line
        else:
            yield f"  assert {left[k]!r} == {right[k]!r}"
