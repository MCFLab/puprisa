# puprisa/app_context.py
"""Application composition root."""

from puprisa.model.curve_manager import CurveManager
from puprisa.model.mask_manager import MaskManager
from puprisa.model.processing_manager import ProcessingManager
from puprisa.model.roi_manager import RoiManager
from puprisa.model.stack_manager import StackEvent, StackManager

class ApplicationContext:
    def __init__(self):
        # 1. Create all managers in dependency order.
        self.stack_manager = StackManager()
        self.mask_manager = MaskManager(stack_manager=self.stack_manager)
        self.roi_manager = RoiManager(
            stack_manager=self.stack_manager,
            mask_manager=self.mask_manager,
        )
        self.curve_manager = CurveManager(
            stack_manager=self.stack_manager,
            roi_manager=self.roi_manager,
        )
        self.processing_manager = ProcessingManager(
            stack_manager=self.stack_manager,
        )

        # 2. Cross-manager wiring.
        self._connect_stack_lifecycle()

    def _connect_stack_lifecycle(self):
        def on_stack_event(event: StackEvent):
            if event.event == "removed":
                assert event.stack_id is not None
                self.roi_manager.handle_stack_deleted(event.stack_id)
            elif event.event == "visibility_changed":
                assert event.stack_id is not None and event.stack_item is not None
                self.roi_manager.handle_stack_visibility_changed(
                    event.stack_id, event.stack_item.visible
                )
        self.stack_manager.add_listener(on_stack_event)

    def create_main_window(self):
        from puprisa.ui.main_window import MainWindow
        return MainWindow(self)

    def create_phasor_window(self):
        from puprisa.ui.phasor_window import PhasorWindow
        return PhasorWindow(self)