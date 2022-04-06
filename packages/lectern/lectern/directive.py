__all__ = [
    "Directive",
    "DirectiveRegistry",
    "NamespacedResourceDirective",
    "DataPackDirective",
    "ResourcePackDirective",
    "BundleFragmentMixin",
    "SkipDirective",
]


import io
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Protocol, Type
from zipfile import ZipFile

from beet import Container, DataPack, NamespaceFile, ResourcePack
from beet.core.utils import snake_case

from .fragment import Fragment


class Directive(Protocol):
    """Protocol for detecting directives."""

    def __call__(self, fragment: Fragment, assets: ResourcePack, data: DataPack):
        ...


class DirectiveRegistry(Container[str, Directive]):
    """Registry for directives."""

    resolvers: List[Callable[["DirectiveRegistry"], Any]]
    assets: ResourcePack
    data: DataPack

    def __init__(
        self,
        assets: Optional[ResourcePack] = None,
        data: Optional[DataPack] = None,
    ):
        super().__init__()
        self.resolvers = []
        self.assets = assets or ResourcePack()
        self.data = data or DataPack()

        self["data_pack"] = DataPackDirective()
        self["resource_pack"] = ResourcePackDirective()
        self["skip"] = SkipDirective()

        @self.add_resolver
        def _(self: DirectiveRegistry):
            for pack in [self.assets, self.data]:
                for file_type in pack.resolve_scope_map().values():
                    name = snake_case(file_type.__name__)
                    self[name] = NamespacedResourceDirective(file_type)

    def resolve(self) -> "DirectiveRegistry":
        """Resolve all directives in the registry."""
        for callback in self.resolvers:
            callback(self)
        return self

    def add_resolver(self, resolver: Callable[["DirectiveRegistry"], Any]):
        """Add directive resolver."""
        self.resolvers.append(resolver)

    def get_serialization_mapping(self) -> Dict[Type[NamespaceFile], str]:
        """Return the serialization mapping."""
        return {
            directive.file_type: directive_name
            for directive_name, directive in self.items()
            if isinstance(directive, NamespacedResourceDirective)
        }


@dataclass
class NamespacedResourceDirective:
    """Directive for including namespaced resources."""

    file_type: Type[NamespaceFile]

    def __call__(self, fragment: Fragment, assets: ResourcePack, data: DataPack):
        full_name = fragment.expect("full_name")
        file_instance: Any = fragment.as_file(self.file_type)

        pack = assets if self.file_type in assets.namespace_type.field_map else data
        proxy: Any = pack[self.file_type]

        if fragment.modifier == "append":
            current_file = proxy.setdefault(full_name, self.file_type(""))
            current_file.text += file_instance.text
        elif fragment.modifier == "prepend":
            current_file = proxy.setdefault(full_name, self.file_type(""))
            current_file.text = file_instance.text + current_file.text
        elif fragment.modifier == "merge":
            proxy.merge({full_name: file_instance})
        else:
            proxy[full_name] = file_instance


class BundleFragmentMixin:
    """Directive mixin that can bundle a fragment into a zipfile."""

    def bundle_pack_fragment(self, fragment: Fragment) -> ZipFile:
        """Return a zipfile containing the pack fragment."""
        relative_path = fragment.expect("relative_path")
        file_instance = fragment.as_file()

        data = io.BytesIO()
        with ZipFile(data, mode="w") as zip_file:
            file_instance.dump(zip_file, relative_path)

        data.seek(0)
        return ZipFile(data)


@dataclass
class DataPackDirective(BundleFragmentMixin):
    """Directive that loads the fragment into the data pack."""

    def __call__(self, fragment: Fragment, assets: ResourcePack, data: DataPack):
        data.load(self.bundle_pack_fragment(fragment))


@dataclass
class ResourcePackDirective(BundleFragmentMixin):
    """Directive that loads the fragment into the resource pack."""

    def __call__(self, fragment: Fragment, assets: ResourcePack, data: DataPack):
        assets.load(self.bundle_pack_fragment(fragment))


@dataclass
class SkipDirective:
    """Directive that ignores the fragment and skips to the next one."""

    def __call__(self, fragment: Fragment, assets: ResourcePack, data: DataPack):
        fragment.expect()
