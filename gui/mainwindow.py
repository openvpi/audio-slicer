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

        self.ui.progressBar.setMinimum(0)
        self.ui.progressBar.setMaximum(100)
        self.ui.progressBar.setValue(0)

        # State variables
        self.workers:list[QThread] = []
        self.workCount = 0
        self.workFinished = 0
        self.processing = False

        self.setWindowTitle("Audio Slicer")

    def _q_browse_output_dir(self):
        path = QFileDialog.getExistingDirectory(
            self, "Browse Output Directory", ".")
        if path != "":
            self.ui.lineEditOutputDir.setText(QDir.toNativeSeparators(path))

    def _q_add_audio_files(self):
        if self.processing:
            self.warningProcessNotFinished()
            return

        paths, _ = QFileDialog.getOpenFileNames(
            self, 'Select Audio Files', ".", 'Wave Files(*.wav)')
        for path in paths:
            item = QListWidgetItem()
            item.setText(QFileInfo(path).fileName())
            # Save full path at custom role
            item.setData(Qt.ItemDataRole.UserRole+1, path)
            self.ui.listWidgetTaskList.addItem(item)

    def _q_clear_audio_list(self):
        if self.processing:
            self.warningProcessNotFinished()
            return

        self.ui.listWidgetTaskList.clear()

    def _q_about(self):
        QMessageBox.information(self, "About", "OpenVPI Team")

    def _q_start(self):
        if self.processing:
            self.warningProcessNotFinished()
            return

        item_count = self.ui.listWidgetTaskList.count()

        if item_count == 0:
            return

        self.ui.progressBar.setMaximum(item_count)
        self.ui.progressBar.setValue(0)
        self.ui.pushButtonStart.setText('Slicing...')
        self.ui.pushButtonStart.setEnabled(False)
        self.ui.pushButtonAddFiles.setEnabled(False)
        self.ui.listWidgetTaskList.setEnabled(False)
        self.ui.pushButtonClearList.setEnabled(False)
        self.ui.lineEditThreshold.setEnabled(False)
        self.ui.lineEditMinLen.setEnabled(False)
        self.ui.lineEditWinLarge.setEnabled(False)
        self.ui.lineEditWinSmall.setEnabled(False)
        self.ui.lineEditMaxSilence.setEnabled(False)
        self.ui.lineEditOutputDir.setEnabled(False)
        self.ui.pushButtonBrowse.setEnabled(False)

        class WorkThread(QThread):
            def __init__(self, filename: str, window: MainWindow):
                super().__init__()

                self.filename = filename
                self.win = window

            def run(self):
                audio, sr = librosa.load(self.filename, sr=None)
                slicer = Slicer(
                    sr=sr,
                    db_threshold=float(self.win.ui.lineEditThreshold.text()),
                    min_length=int(self.win.ui.lineEditMinLen.text()),
                    win_l=int(self.win.ui.lineEditWinLarge.text()),
                    win_s=int(self.win.ui.lineEditWinSmall.text()),
                    max_silence_kept=int(self.win.ui.lineEditMaxSilence.text())
                )
                chunks = slicer.slice(audio)
                out_dir = self.win.ui.lineEditOutputDir.text()
                if out_dir == '':
                    out_dir = os.path.dirname(os.path.abspath(self.filename))
                for i, chunk in enumerate(chunks):
                    path = os.path.join(out_dir, f'%s_%d.wav' % (os.path.basename(self.filename)
                                                                 .rsplit('.', maxsplit=1)[0], i))
                    soundfile.write(path, chunk, sr)

        self.workCount = item_count
        self.workFinished = 0
        self.processing = True

        for i in range(0, item_count):
            item = self.ui.listWidgetTaskList.item(i)
            path = item.data(Qt.ItemDataRole.UserRole+1)  # Get full path

            worker = WorkThread(path, self)
            worker.finished.connect(self._q_threadFinished)
            worker.start()

            self.workers.append(worker)  # Collect in case of auto deletion

    def _q_threadFinished(self):
        self.workFinished += 1
        self.ui.progressBar.setValue(self.workFinished)

        if self.workFinished == self.workCount:
            # Join all workers
            for worker in self.workers:
                worker.wait()
            self.workers.clear()
            self.processing = False

            self.ui.pushButtonStart.setText('Start')
            self.ui.pushButtonStart.setEnabled(True)
            self.ui.pushButtonAddFiles.setEnabled(True)
            self.ui.listWidgetTaskList.setEnabled(True)
            self.ui.pushButtonClearList.setEnabled(True)
            self.ui.lineEditThreshold.setEnabled(True)
            self.ui.lineEditMinLen.setEnabled(True)
            self.ui.lineEditWinLarge.setEnabled(True)
            self.ui.lineEditWinSmall.setEnabled(True)
            self.ui.lineEditMaxSilence.setEnabled(True)
            self.ui.lineEditOutputDir.setEnabled(True)
            self.ui.pushButtonBrowse.setEnabled(True)
            QMessageBox.information(
                self, QApplication.applicationName(), "Slicing complete!")

    def warningProcessNotFinished(self):
        QMessageBox.warning(self, QApplication.applicationName(),
                            "Please wait for slicing to complete!")

    def closeEvent(self, event):
        if self.processing:
            self.warningProcessNotFinished()
            event.ignore()