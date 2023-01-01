import sys

from PySide6 import QtCore
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

import gui.mainwindow

if __name__ == '__main__':
    QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Audio Slicer")
    app.setApplicationDisplayName("Audio Slicer")

    font = QFont('Microsoft YaHei UI')
    font.setPixelSize(12)
    app.setFont(font)

    window = gui.mainwindow.MainWindow()
    window.show()

    sys.exit(app.exec())
