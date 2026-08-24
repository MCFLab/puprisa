# puprisa/model/stack_manager.py
"""Pure model for managing a collection of pump-probe stacks.

This module provides :class:`StackManager`, a Qt-free model that owns the
list of loaded stacks and exposes signals for UI synchronisation.

The class does **not** interact with any widgets.  All user-initiated
actions (open, delete, rename, colour change) are performed by the view
adapter, which calls the methods defined here and receives change
notifications via Qt signals.
"""

from pathlib import Path

from PySide6.QtCore import QObject, Signal

from puprisa.core.pps import PPS
from puprisa.utils.color_utils import PHASOR_COLORS


class StackManager(QObject):
    """Central store for all stack items.

    Each stack item is a dictionary with the following keys:

    - ``id``             : unique string identifier
    - ``pps``            : :class:`~puprisa.core.pps.PPS` instance
    - ``name``           : display name
    - ``visible``        : boolean indicating whether the stack is enabled
    - ``color``          : hex colour string used for phasor overlays

    Signals
    -------
    stackChanged(object)
        Emitted with the current stack item (dict) or ``None`` when the
        selection is cleared.
    stackVisibilityChanged(str, bool)
        Emitted with ``(stack_id, visible)`` when a stack's visibility is
        toggled.
    stackItemsChanged()
        Emitted whenever the list contents or metadata (name, colour) change.
    stackDeleted(str)
        Emitted with the deleted stack's ``id``.
    """

    stackChanged = Signal(object)
    stackVisibilityChanged = Signal(str, bool)
    stackItemsChanged = Signal()
    stackDeleted = Signal(str)

    def __init__(self):
        super().__init__()
        self.stack_items: list[dict] = []
        self.current_index = -1
        self._id_counter = 0
        self._color_index = 0

    # ------------------------------------------------------------------
    # Public API for adding / removing stacks
    # ------------------------------------------------------------------
    def add_existing_stack(self, pps: PPS, name: str | None = None) -> str:
        """Add an already-loaded :class:`PPS` object.

        Parameters
        ----------
        pps : PPS
            The stack object to add.
        name : str, optional
            Display name.  If omitted, the filename stem is used, or
            ``"Untitled"`` if no filename is set.

        Returns
        -------
        str
            The unique ID of the newly added stack.
        """
        if name is None:
            name = Path(pps.filename).stem if pps.filename else "Untitled"

        item = {
            "id": self._generate_stack_id(),
            "pps": pps,
            "name": name,
            "visible": True,
            "color": self._next_color(),
        }
        self.stack_items.append(item)
        self.current_index = len(self.stack_items) - 1
        self.stackItemsChanged.emit()
        self.stackChanged.emit(item)
        return item["id"]

    def delete_stack(self, index: int) -> bool:
        """Delete a stack by its list index.

        Parameters
        ----------
        index : int
            Index of the stack to remove.

        Returns
        -------
        bool
            ``True`` if a stack was deleted, otherwise ``False``.
        """
        if not 0 <= index < len(self.stack_items):
            return False

        stack = self.stack_items.pop(index)
        was_current = (self.current_index == index)

        if was_current:
            self.current_index = min(index, len(self.stack_items) - 1)
        elif self.current_index > index:
            self.current_index -= 1

        self.stackDeleted.emit(stack["id"])
        self.stackItemsChanged.emit()

        if was_current:
            if 0 <= self.current_index < len(self.stack_items):
                self.stackChanged.emit(self.stack_items[self.current_index])
            else:
                self.stackChanged.emit(None)
        return True

    def rename_stack(self, index: int, new_name: str) -> bool:
        """Rename a stack.

        Parameters
        ----------
        index : int
            Index of the stack.
        new_name : str
            New display name.  Leading/trailing whitespace is stripped.

        Returns
        -------
        bool
            ``True`` if the rename succeeded, ``False`` otherwise.
        """
        if not 0 <= index < len(self.stack_items):
            return False

        new_name = new_name.strip()
        if not new_name:
            return False

        self.stack_items[index]["name"] = new_name
        self.stackItemsChanged.emit()
        return True

    def set_stack_color(self, stack_id: str, color_hex: str) -> bool:
        """Change the colour associated with a stack.

        Parameters
        ----------
        stack_id : str
            ID of the stack.
        color_hex : str
            New hex colour string (e.g. ``"#ff0000"``).

        Returns
        -------
        bool
            ``True`` if the stack was found and the colour updated.
        """
        stack = self.get_item_by_id(stack_id)
        if stack is None:
            return False

        stack["color"] = color_hex
        self.stackItemsChanged.emit()
        return True

    # ------------------------------------------------------------------
    # Query API
    # ------------------------------------------------------------------
    def switch_stack(self, index: int) -> None:
        """Switch the current stack by index.

        Emits ``stackChanged`` with the selected item, or ``None`` if the
        index is out of range.
        """
        if 0 <= index < len(self.stack_items):
            self.current_index = index
            self.stackChanged.emit(self.stack_items[index])
        else:
            self.current_index = -1
            self.stackChanged.emit(None)

    def set_stack_visible(self, stack_id: str, visible: bool) -> None:
        """Set the visibility of a stack.

        Parameters
        ----------
        stack_id : str
            ID of the stack.
        visible : bool
            Desired visibility state.
        """
        stack = self.get_item_by_id(stack_id)
        if stack is None:
            return
        if stack["visible"] != visible:
            stack["visible"] = visible
            self.stackVisibilityChanged.emit(stack_id, visible)

    def get_current_item(self) -> dict | None:
        """Return the currently selected stack item, or ``None``."""
        if 0 <= self.current_index < len(self.stack_items):
            return self.stack_items[self.current_index]
        return None

    def get_current_pps(self) -> PPS | None:
        """Return the :class:`PPS` object of the current stack, or ``None``."""
        item = self.get_current_item()
        return item["pps"] if item else None

    def get_item_by_id(self, stack_id: str) -> dict | None:
        """Return a stack item by its unique ID, or ``None``."""
        return next((s for s in self.stack_items if s["id"] == stack_id), None)

    def get_all_items(self) -> list[dict]:
        """Return a copy of the internal stack list."""
        return list(self.stack_items)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _generate_stack_id(self) -> str:
        """Create a unique stack ID."""
        existing = {s["id"] for s in self.stack_items}
        while True:
            self._id_counter += 1
            candidate = f"stack_{self._id_counter}"
            if candidate not in existing:
                return candidate

    def _next_color(self) -> str:
        """Return the next colour from the phasor palette."""
        color = PHASOR_COLORS[self._color_index % len(PHASOR_COLORS)]
        self._color_index += 1
        return color