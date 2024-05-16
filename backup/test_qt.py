import sys
from multiprocessing import Pipe
from PySide6 import QtCore

from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Widgets App")
        layout = QVBoxLayout()
        self.widgets = [
            QCheckBox,
            QComboBox,
            QDateEdit,
            QDateTimeEdit,
            QDial,
            QDoubleSpinBox,
            QFontComboBox,
            QLCDNumber,
            QLabel,
            QLineEdit,
            QProgressBar,
            QPushButton,
            QRadioButton,
            QSlider,
            QSpinBox,
            QTimeEdit,
            QLineEdit,
        ]
        self.x, self.y = Pipe()
        for widget in self.widgets:
            layout.addWidget(widget())
        self.button = QPushButton("ON")
        layout.addWidget(self.button)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.button.clicked.connect(self.jsender)

    @QtCore.Slot()
    def jsender(self):
        self.x.send(100)
        r = self.y.recv()
        print(r)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()