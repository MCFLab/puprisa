# puprisa/gui.py
import sys
from PySide6.QtWidgets import QApplication
from puprisa.ui.main_window import MainWindow
from puprisa.model.stack_manager import StackManager

def main():
    app = QApplication(sys.argv)
    stack_manager = StackManager()
    win = MainWindow(stack_manager)
    win.show()
    return app.exec()