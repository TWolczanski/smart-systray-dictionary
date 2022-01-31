from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QErrorMessage, QTabWidget, QDesktopWidget, QMessageBox

class RepetitionView(QWidget):
    def __init__(self, model, controller):
        super().__init__()
        self.model = model
        self.controller = controller
        
        self.countdown = QTimer(self)
        self.countdown.timeout.connect(lambda: self.update_timer())
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        top_layout = QHBoxLayout()
        
        self.question = QLabel("test")
        top_layout.addWidget(self.question)
        self.time_left = QLabel()
        top_layout.addWidget(self.time_left)
        self.main_layout.addLayout(top_layout)
        
        self.setLayout(self.main_layout)
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.X11BypassWindowManagerHint)
        
        self.resize(250, 150)
        fg = self.frameGeometry()
        top_right_point = QDesktopWidget().availableGeometry().topRight()
        fg.moveTopRight(top_right_point)
        x = fg.topLeft().x() - 40
        y = fg.topLeft().y() + 40
        self.move(x, y)
        
        self.model.quiz_created.connect(lambda: self.on_quiz_created())
    
    def update_timer(self):
        self.count -= 1
        self.time_left.setText(str(self.count))
        if self.count <= 0:
            self.countdown.stop()
            self.close()
    
    def on_quiz_created(self):
        self.count = self.model.quiz_time
        self.time_left.setText(str(self.count))
        self.show()
        self.countdown.start(1000)