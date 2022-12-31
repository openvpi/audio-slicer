import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

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
