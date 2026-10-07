"""M7 WorkspaceRegistry for explicit route composition and lifecycle dispatch.

The registry is intentionally Qt-agnostic. It stores presentation surfaces as
opaque objects and owns route-listener ordering plus workspace replacement via
an injected adapter. Existing route handlers remain adapters during M7 so UI
behavior can be proven before M8 bridge retirement.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, replace
from typing import Callable, Iterable, Iterator


RouteListener = Callable[[str], None]
WorkspaceReplacer = Callable[[str, object], object | None]


@dataclass(frozen=True, slots=True)
class WorkspaceDescriptor:
    route: str
    label: str
    icon_name: str
    order: int


@dataclass(frozen=True, slots=True)
class WorkspaceBundle:
    descriptor: WorkspaceDescriptor
    workspace: object | None = None
    context: object | None = None
    inspector: object | None = None
    timeline: object | None = None

    @property
    def route(self) -> str:
        return self.descriptor.route

    @property
    def label(self) -> str:
        return self.descriptor.label

    @property
    def complete_surface_count(self) -> int:
        return sum(
            value is not None
            for value in (
                self.workspace,
                self.context,
                self.inspector,
                self.timeline,
            )
        )


@dataclass(frozen=True, slots=True)
class WorkspaceListenerRecord:
    name: str
    owner_route: str | None
    sequence: int
    callback: RouteListener


class WorkspaceRegistry:
    """Single M7 route-composition and route-dispatch owner.

    M7 deliberately preserves existing route callbacks as adapters. The
    important ownership change is that FoundationUiState has one route signal
    subscriber (this registry), while route modules register with the registry
    instead of wiring themselves directly to the signal.
    """

    def __init__(
        self,
        route_specs: Iterable[tuple[str, str, str]],
        *,
        replace_workspace: WorkspaceReplacer | None = None,
    ) -> None:
        descriptors: list[WorkspaceDescriptor] = []
        seen: set[str] = set()
        for order, raw in enumerate(route_specs):
            route, label, icon_name = (str(value) for value in raw)
            if not route or route in seen:
                raise ValueError(f"Route workspace tidak valid/duplikat: {route!r}")
            seen.add(route)
            descriptors.append(
                WorkspaceDescriptor(
                    route=route,
                    label=label,
                    icon_name=icon_name,
                    order=order,
                )
            )
        if not descriptors:
            raise ValueError("WorkspaceRegistry membutuhkan minimal satu route.")
        self._descriptors = tuple(descriptors)
        self._descriptor_map = {item.route: item for item in descriptors}
        self._bundles = {
            item.route: WorkspaceBundle(descriptor=item)
            for item in descriptors
        }
        self._replace_workspace = replace_workspace
        self._listeners: list[WorkspaceListenerRecord] = []
        self._listener_names: set[str] = set()
        self._sequence = 0
        self._current_route = descriptors[0].route

    def attach_workspace_replacer(self, replacer: WorkspaceReplacer) -> None:
        if not callable(replacer):
            raise TypeError("Workspace replacer harus callable.")
        if self._replace_workspace is not None:
            raise RuntimeError("Workspace replacer sudah dipasang.")
        self._replace_workspace = replacer

    @property
    def routes(self) -> tuple[str, ...]:
        return tuple(item.route for item in self._descriptors)

    @property
    def current_route(self) -> str:
        return self._current_route

    @property
    def registered_routes(self) -> tuple[str, ...]:
        return tuple(
            route for route in self.routes
            if self._bundles[route].workspace is not None
        )

    @property
    def listener_names(self) -> tuple[str, ...]:
        return tuple(record.name for record in self._listeners)

    def descriptor(self, route: str) -> WorkspaceDescriptor:
        key = str(route)
        try:
            return self._descriptor_map[key]
        except KeyError as exc:
            raise KeyError(f"Route workspace tidak dikenal: {key}") from exc

    def bundle(self, route: str) -> WorkspaceBundle:
        key = self.descriptor(route).route
        return self._bundles[key]

    def register_bundle(
        self,
        route: str,
        *,
        workspace: object | None = None,
        context: object | None = None,
        inspector: object | None = None,
        timeline: object | None = None,
        listener: RouteListener | None = None,
        listener_name: str = "",
        replay: bool = False,
    ) -> WorkspaceBundle:
        key = self.descriptor(route).route
        current = self._bundles[key]
        updated = replace(
            current,
            workspace=workspace if workspace is not None else current.workspace,
            context=context if context is not None else current.context,
            inspector=inspector if inspector is not None else current.inspector,
            timeline=timeline if timeline is not None else current.timeline,
        )
        if workspace is not None and workspace is not current.workspace:
            if self._replace_workspace is None:
                raise RuntimeError("Workspace replacer belum dipasang.")
            self._replace_workspace(key, workspace)
        self._bundles[key] = updated
        if listener is not None:
            self.register_listener(
                key,
                listener,
                name=listener_name or f"{key}-route",
                replay=replay,
            )
        return updated

    def register_listener(
        self,
        owner_route: str | None,
        callback: RouteListener,
        *,
        name: str,
        replay: bool = False,
    ) -> WorkspaceListenerRecord:
        if owner_route is not None:
            owner_route = self.descriptor(owner_route).route
        if not callable(callback):
            raise TypeError("Workspace route listener harus callable.")
        normalized = str(name).strip()
        if not normalized:
            raise ValueError("Nama workspace listener tidak boleh kosong.")
        if normalized in self._listener_names:
            raise ValueError(f"Workspace listener duplikat: {normalized}")
        record = WorkspaceListenerRecord(
            name=normalized,
            owner_route=owner_route,
            sequence=self._sequence,
            callback=callback,
        )
        self._sequence += 1
        self._listener_names.add(normalized)
        self._listeners.append(record)
        if replay:
            callback(self._current_route)
        return record

    def activate(self, route: str) -> str:
        key = str(route)
        if key not in self._descriptor_map:
            key = self.routes[0]
        self._current_route = key
        # Snapshot protects deterministic dispatch if a callback registers
        # another adapter while route activation is already in progress.
        for record in tuple(self._listeners):
            record.callback(key)
        return key

    def assert_complete(self) -> None:
        missing = [route for route in self.routes if self._bundles[route].workspace is None]
        if missing:
            raise RuntimeError(
                "WorkspaceRegistry belum memiliki workspace produksi untuk: "
                + ", ".join(missing)
            )


_CURRENT_WORKSPACE_REGISTRY: ContextVar[WorkspaceRegistry | None] = ContextVar(
    "full_album_maker_current_workspace_registry",
    default=None,
)


def current_workspace_registry() -> WorkspaceRegistry | None:
    return _CURRENT_WORKSPACE_REGISTRY.get()


@contextmanager
def bind_workspace_registry(
    registry: WorkspaceRegistry,
) -> Iterator[WorkspaceRegistry]:
    if not isinstance(registry, WorkspaceRegistry):
        raise TypeError("registry harus WorkspaceRegistry.")
    token = _CURRENT_WORKSPACE_REGISTRY.set(registry)
    try:
        yield registry
    finally:
        _CURRENT_WORKSPACE_REGISTRY.reset(token)


__all__ = [
    "RouteListener",
    "WorkspaceBundle",
    "WorkspaceDescriptor",
    "WorkspaceListenerRecord",
    "WorkspaceRegistry",
    "WorkspaceReplacer",
    "bind_workspace_registry",
    "current_workspace_registry",
]
