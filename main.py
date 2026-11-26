import sys
from PyQt6.QtWidgets import QApplication
from main_window import MyWidget


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())