import os

import librosa
import soundfile

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from slicer import Slicer

from gui.Ui_MainWindow import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButtonAddFiles.clicked.connect(self._q_add_audio_files)
        self.ui.pushButtonBrowse.clicked.connect(self._q_browse_output_dir)
        self.ui.pushButtonClearList.clicked.connect(self._q_clear_audio_list)
        self.ui.pushButtonAbout.clicked.connect(self._q_about)
        self.ui.pushButtonStart.clicked.connect(self._q_start)

        self.setWindowTitle("Audio Slicer")


    def _q_browse_output_dir(self):
        path = QFileDialog.getExistingDirectory(
            self, "Browse Output Directory", ".")
        if path != "":
            self.ui.lineEditOutputDir.setText(QDir.toNativeSeparators(path))


    def _q_add_audio_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, 'Select Audio Files', ".", 'Wave Files(*.wav)')
        for path in paths:
            item = QListWidgetItem()
            item.setText(QFileInfo(path).fileName())
            item.setData(Qt.ItemDataRole.UserRole+1, path) # Save full path at custom role
            self.ui.listWidgetTaskList.addItem(item)


    def _q_clear_audio_list(self):
        self.ui.listWidgetTaskList.clear()


    def _q_about(self):
        QMessageBox.information(self, "About", "OpenVPI Team")


    def _q_start(self):
        item_count = self.ui.listWidgetTaskList.count()

        self.ui.progressBar.setMaximum(item_count)
        self.ui.progressBar.setValue(0)

        for i in range(0, item_count):
            item = self.ui.listWidgetTaskList.item(i)
            fullpath = item.data(Qt.ItemDataRole.UserRole+1) # Get full path
            filename = item.text()

            audio, sr = librosa.load(fullpath, sr=None)
            slicer = Slicer(
                sr=sr,
                db_threshold=float(self.ui.lineEditThreshold.text()),
                min_length=int(self.ui.lineEditMinLen.text()),
                win_l=int(self.ui.lineEditWinLarge.text()),
                win_s=int(self.ui.lineEditWinSmall.text()),
                max_silence_kept=int(self.ui.lineEditMaxSilence.text())
            )
            chunks = slicer.slice(audio)
            for i, chunk in enumerate(chunks):
                out_dir = self.ui.lineEditOutputDir.text()
                path = os.path.join(out_dir, f'%s_%d.wav' % (filename.rsplit('.', maxsplit=1)[0], i))
                soundfile.write(path, chunk, sr)

            self.ui.progressBar.setValue(i)
