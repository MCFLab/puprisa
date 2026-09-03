# puprisa/app_context.py
"""Application composition root."""

from puprisa.model.curve_manager import CurveManager
from puprisa.model.mask_manager import MaskManager
from puprisa.model.plot_manager import PlotManager
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
        self.plot_manager = PlotManager(
            stack_manager=self.stack_manager,
            processing_manager=self.processing_manager,
        )

        self.stack_manager.add_listener(self.roi_manager.handle_stack_event)
        self.stack_manager.add_listener(self.plot_manager.handle_stack_event)
        self.stack_manager.add_listener(self.mask_manager.handle_stack_event)
        self.processing_manager.add_listener(self.plot_manager.handle_processing_event)

    def create_main_window(self):
        from puprisa.ui.main_window import MainWindow
        return MainWindow(self)

    def create_phasor_window(self):
        from puprisa.ui.phasor_window import PhasorWindow
        return PhasorWindow(self)