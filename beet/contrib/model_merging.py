"""Plugin for setting up a merge policy that merges model overrides."""


__all__ = [
    "model_merging",
    "merge_model_overrides",
]


from copy import deepcopy
from typing import Dict, List, Tuple, Union

from beet import Context, Model, ResourcePack
from beet.core.utils import JsonDict


def beet_default(ctx: Context):
    ctx.require(model_merging)


def model_merging(ctx: Union[Context, ResourcePack]):
    pack = ctx.assets if isinstance(ctx, Context) else ctx
    pack.merge_policy.extend_namespace(Model, merge_model_overrides)


def merge_model_overrides(
    pack: ResourcePack,
    path: str,
    current: Model,
    conflict: Model,
) -> bool:
    merged = deepcopy(conflict.data)

    overrides = current.data.get("overrides", [])
    other_overrides = merged.pop("overrides", [])
    concatenated_overrides = overrides + other_overrides

    predicate_cases: List[str] = []
    for override in concatenated_overrides:
        for predicate in override.get("predicate", {}):
            if predicate not in predicate_cases:
                predicate_cases.append(predicate)

    override_index: Dict[Tuple[float, ...], JsonDict] = {}
    for override in concatenated_overrides:
        predicate = override.get("predicate", {})
        key = tuple(predicate.get(case, 0) for case in predicate_cases)
        override_index[key] = override

    if not merged:
        merged = current.data

    if override_index:
        merged["overrides"] = [
            override for _, override in sorted(override_index.items())
        ]

    current.data = merged

    return True
