# puprisa/model/stack_manager.py
"""Qt-free model for managing a collection of pump-probe stacks."""
from dataclasses import dataclass
from typing import Callable

from puprisa.core.pps import PPS
from puprisa.model.entities import StackItem
from puprisa.utils.color_utils import PHASOR_COLORS


@dataclass(frozen=True)
class StackEvent:
    """Emitted whenever stack collection or metadata changes."""

    event: str                  # "added" / "removed" / "renamed" / "reordered" /
                                # "visibility_changed" / "current_changed" / "color_changed"
    stack_id: str | None = None
    stack_item: StackItem | None = None


class StackManager:
    """Central store for all stack items. Qt-free, callback-based."""

    def __init__(self):
        self._items: list[StackItem] = []
        self._listeners: list[Callable[[StackEvent], None]] = []
        self._current_id: str | None = None
        self._id_counter: int = 0
        self._color_index: int = 0

    # ------------------------------------------------------------------
    # Listener management
    # ------------------------------------------------------------------
    def add_listener(self, callback: Callable[[StackEvent], None]) -> None:
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[StackEvent], None]) -> None:
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify(self, event: StackEvent) -> None:
        for cb in list(self._listeners):
            cb(event)

    # ------------------------------------------------------------------
    # Collection mutation
    # ------------------------------------------------------------------
    def add_stack(self, pps: PPS, name: str | None = None) -> str:
        """Add an already-loaded PPS and return its ID."""
        stack_id = self._generate_stack_id()
        item = StackItem.from_pps(
            stack_id, pps, name=name, color=self._next_color()
        )
        self._items.append(item)
        self._current_id = stack_id

        self._notify(StackEvent(event="added", stack_id=stack_id, stack_item=item))
        self._notify(StackEvent(event="current_changed", stack_id=stack_id, stack_item=item))
        return stack_id

    def delete_stack(self, stack_id: str) -> str:
        """Delete a stack by ID and return the ID of the deleted stack."""
        item = self.get_item_by_id(stack_id)
        if item is None:
            raise KeyError(f"Unknown stack_id: {stack_id!r}")
        # Find the original index of the item to be removed
        original_index = self.get_index_by_id(stack_id)
        # Remove the item from the list
        self._items.pop(original_index)
        # Check if the removed item was the current stack
        was_current = self._current_id == stack_id
        self._notify(StackEvent(event="removed", stack_id=item.id, stack_item=item))
        # If the removed item was the current stack, update the current stack
        if was_current:
            # If there are still items left, set the current stack to the next item in the list
            if self._items:
                new_index = min(original_index, len(self._items) - 1)
                self._current_id = self._items[new_index].id
            else: # If the list is now empty, set the current stack to None
                self._current_id = None
            self._notify(StackEvent(event="current_changed", stack_id=self._current_id, stack_item=self.get_current_item()))
        return item.id

    def rename_stack(self, stack_id: str, new_name: str) -> None:
        """Rename a stack by ID."""
        item = self.get_item_by_id(stack_id)
        if item is None:
            raise KeyError(f"Unknown stack_id: {stack_id!r}")
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("Stack name cannot be empty.")
        item.name = new_name
        self._notify(StackEvent(event="renamed", stack_id=item.id, stack_item=item))

    def set_stack_color(self, stack_id: str, color_hex: str) -> None:
        item = self.get_item_by_id(stack_id)
        if item is None:
            raise KeyError(f"Unknown stack_id: {stack_id!r}")
        item.color = color_hex
        self._notify(StackEvent(event="color_changed", stack_id=stack_id, stack_item=item))

    def set_stack_visible(self, stack_id: str, visible: bool) -> None:
        item = self.get_item_by_id(stack_id)
        if item is None:
            raise KeyError(f"Unknown stack_id: {stack_id!r}")
        if item.visible == visible:
            return
        item.visible = visible
        self._notify(StackEvent(event="visibility_changed", stack_id=stack_id, stack_item=item))

    def switch_stack(self, stack_id: str | None) -> None:
        """Switch the current stack to the one identified by ``stack_id``."""
        if stack_id is not None:
            item = self.get_item_by_id(stack_id)
            if item is None:
                raise KeyError(f"Unknown stack_id: {stack_id!r}")
            if self._current_id == stack_id:
                return
            self._current_id = stack_id
        else:
            self._current_id = None
            item = None
        self._notify(StackEvent(event="current_changed", stack_id=stack_id, stack_item=item))

    def reorder_stacks(self, stack_ids: list[str]) -> None:
        """Reorder stack items in place to match the given stack IDs."""
        if set(stack_ids) != {item.id for item in self._items}:
            raise ValueError("stack_ids must contain exactly the current stack IDs")
        rank = {stack_id: i for i, stack_id in enumerate(stack_ids)}
        self._items.sort(key=lambda item: rank[item.id])
        self._notify(StackEvent(event="reordered", stack_id=self._current_id, stack_item=self.get_current_item()))

    def save_stack(self, stack_id: str, path, format: str) -> None:
        """Save the stack identified by ``stack_id`` using the requested format."""
        item = self.get_item_by_id(stack_id)
        if item is None:
            raise KeyError(f"Unknown stack_id: {stack_id!r}")
        item.pps.save(path, format=format)

    def clear_all_stacks(self) -> None:
        """Remove all stacks."""
        if not self._items:
            return
        while self._items:
            item = self._items.pop()
            self._notify(StackEvent(event="removed", stack_id=item.id, stack_item=item))
        self._current_id = None
        self._notify(StackEvent(event="current_changed", stack_id=None, stack_item=None))

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------ 
    def get_current_item(self) -> StackItem | None:
        return self.get_item_by_id(self._current_id) if self._current_id is not None else None

    def get_current_pps(self) -> PPS | None:
        item = self.get_current_item()
        return item.pps if item else None

    def get_current_stack_id(self) -> str | None:
        item = self.get_current_item()
        return item.id if item else None

    def get_index_by_id(self, stack_id: str) -> int | None:
        return next((i for i, s in enumerate(self._items) if s.id == stack_id), None)
    
    def get_item_by_id(self, stack_id: str) -> StackItem | None:
        return next((s for s in self._items if s.id == stack_id), None)

    def get_all_items(self) -> list[StackItem]:
        return list(self._items)

    def get_visible_items(self) -> list[StackItem]:
        return [i for i in self._items if i.visible]

    def get_all_stack_ids(self) -> list[str]:
        return [i.id for i in self._items]

    def __len__(self) -> int:
        return len(self._items)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _generate_stack_id(self) -> str:
        existing = {i.id for i in self._items}
        while True:
            self._id_counter += 1
            candidate = f"stack_{self._id_counter}"
            if candidate not in existing:
                return candidate

    def _next_color(self) -> str:
        color = PHASOR_COLORS[self._color_index % len(PHASOR_COLORS)]
        self._color_index += 1
        return color