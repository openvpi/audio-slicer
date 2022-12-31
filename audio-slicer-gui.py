import sys

from PySide6 import QtCore
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

import mainwindow

if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)

    font = QFont('Microsoft YaHei UI')
    font.setPixelSize(12)
    app.setFont(font)

    window = mainwindow.MainWindow()
    window.show()

    sys.exit(app.exec())
