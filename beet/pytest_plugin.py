from pprint import pformat

from _pytest.assertion.util import assertrepr_compare

from beet import Namespace, NamespaceContainer, Pack


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
    elif isinstance(left, Namespace):
        explanation += generate_explanation(config, left, right, "container")
    elif isinstance(left, NamespaceContainer):
        explanation += generate_explanation(config, left, right, "file")

    if explanation:
        return [assertrepr_compare(config, op, left, right)[0]] + explanation


def plural(name, count):
    return name + bool(count - 1) * "s"


def generate_explanation(config, left, right, item_name):
    verbose = config.getoption("verbose")

    left_keys = set(left)
    right_keys = set(right)

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

        summary, *explanation = config.hook.pytest_assertrepr_compare(
            config=config, op="==", left=left[k], right=right[k]
        )[0]

        yield f"  assert " + summary
        for line in explanation:
            yield "  " + line
