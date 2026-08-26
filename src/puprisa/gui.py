import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from puprisa.app_context import ApplicationContext

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(Path(__file__).parent / "ui" / "resources" / "qt.svg")))
    ctx = ApplicationContext()
    main_win = ctx.create_main_window()
    main_win.show()
    return app.exec()