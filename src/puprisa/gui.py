import sys
from importlib.resources import files
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from puprisa.app_context import ApplicationContext

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(files("puprisa.ui.resources").joinpath("icon.svg"))))
    ctx = ApplicationContext()
    main_win = ctx.create_main_window()
    main_win.show()
    return app.exec()