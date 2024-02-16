"""Plugin for setting up a merge policy that merges model overrides."""

__all__ = [
    "ModelMergingOptions",
    "ModelOverridesMergePolicy",
    "model_merging",
    "merge_model_overrides",
]


from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, Sequence, Tuple, Union

from beet import Context, Model, PluginOptions, ResourcePack
from beet.core.utils import JsonDict


class ModelMergingOptions(PluginOptions):
    predicate_order: Sequence[str] = ()


def beet_default(ctx: Context):
    ctx.require(model_merging)


def model_merging(
    arg: Union[Context, ResourcePack],
    *,
    predicate_order: Sequence[str] = (),
):
    if isinstance(arg, Context):
        pack = arg.assets
        opts = arg.validate("model_merging", ModelMergingOptions)
        if not predicate_order:
            predicate_order = opts.predicate_order
    else:
        pack = arg

    pack.merge_policy.extend_namespace(
        Model, ModelOverridesMergePolicy(predicate_order)
    )


@dataclass
class ModelOverridesMergePolicy:
    predicate_order: Sequence[str] = ()

    def __call__(
        self,
        pack: ResourcePack,
        path: str,
        current: Model,
        conflict: Model,
    ) -> bool:
        return merge_model_overrides(current, conflict, self.predicate_order)


def merge_model_overrides(
    current: Model, conflict: Model, predicate_order: Sequence[str] = ()
) -> bool:
    merged = deepcopy(conflict.data)

    overrides = current.data.get("overrides", [])
    other_overrides = merged.pop("overrides", [])
    concatenated_overrides = overrides + other_overrides

    predicate_cases = list(predicate_order)
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
