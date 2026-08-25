import sys
from PySide6.QtWidgets import QApplication
from puprisa.app_context import ApplicationContext

def main():
    app = QApplication(sys.argv)
    ctx = ApplicationContext()
    main_win = ctx.create_main_window()
    main_win.show()
    return app.exec()