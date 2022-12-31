import os

import librosa
import soundfile

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from slicer import Slicer

import ui_mainwindow


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = ui_mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButtonAddFiles.clicked.connect(self._q_add_audio_files)
        self.ui.pushButtonBrowse.clicked.connect(self._q_browse_output_dir)
        self.ui.pushButtonClearList.clicked.connect(self._q_clear_audio_list)
        self.ui.pushButtonAbout.clicked.connect(self._q_about)
        self.ui.pushButtonStart.clicked.connect(self._q_start)

        self.setWindowTitle("Audio Slicer")

    def _q_browse_output_dir(self):
        path = QFileDialog.getExistingDirectory(self, "Browse Output Directory", ".")
        if path != "":
            self.ui.lineEditOutputDir.setText(QDir.toNativeSeparators(path))

    def _q_add_audio_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, 'Select Audio Files', ".", 'Wave Files(*.wav)')
        for path in paths:
            self.ui.listWidgetTaskList.addItem(QListWidgetItem(QFileInfo(path).fileName()))

    def _q_clear_audio_list(self):
        self.ui.listWidgetTaskList.clear()

    def _q_about(self):
        QMessageBox.information(self, "About", "OpenVPI Team")

    def _q_start(self):
        self.ui.progressBar.setValue(0)
        tasks_count = self.ui.listWidgetTaskList.count()
        self.ui.progressBar.setMaximum(tasks_count)
        progress = 0
        for index, item in enumerate(self.ui.listWidgetTaskList.items()):
            audio, sr = librosa.load(item, sr=None)
            slicer = Slicer(
                sr=sr,
                db_threshold=self.ui.lineEditThreshold,
                min_length=self.ui.lineEditMinLen,
                win_l=self.ui.lineEditWinLarge,
                win_s=self.ui.lineEditWinSmall,
                max_silence_kept=self.ui.lineEditMaxSilence
            )
            chunks = slicer.slice(audio)
            for i, chunk in enumerate(chunks):
                out_dir = self.ui.lineEditOutputDir
                path = os.path.join(out_dir, f'%s_%d.wav' % (os.path.basename(item).rsplit('.', maxsplit=1)[0], i))
                soundfile.write(path, chunk, sr)
            progress += 1
            self.ui.progressBar.setValue(progress)
