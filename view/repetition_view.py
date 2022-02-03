from functools import partial
from json.tool import main
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QErrorMessage, QTabWidget, QDesktopWidget, QMessageBox, QRadioButton, QButtonGroup

class RepetitionView(QWidget):
    def __init__(self, model, controller):
        super().__init__()
        self.model = model
        self.controller = controller
        
        self.countdown = QTimer(self)
        self.countdown.timeout.connect(lambda: self.update_timer())
        
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        top_layout = QHBoxLayout()
        
        self.feedback = QLabel()
        top_layout.addWidget(self.feedback)
        self.time_left = QLabel()
        top_layout.addWidget(self.time_left)
        main_layout.addLayout(top_layout)
        
        self.easy_quiz = EasyQuiz(self.controller)
        main_layout.addWidget(self.easy_quiz)
        
        self.setLayout(main_layout)
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.X11BypassWindowManagerHint)
        
        self.resize(250, 150)
        fg = self.frameGeometry()
        top_right_point = QDesktopWidget().availableGeometry().topRight()
        fg.moveTopRight(top_right_point)
        x = fg.topLeft().x() - 40
        y = fg.topLeft().y() + 40
        self.move(x, y)
        
        self.model.quiz_created.connect(self.on_quiz_created)
        self.model.quiz_answer_checked.connect(self.on_quiz_answer_checked)
    
    def update_timer(self):
        self.count -= 1
        self.time_left.setText(str(self.count))
        if self.count <= 0:
            self.countdown.stop()
            self.close()
    
    def on_quiz_created(self):
        self.count = self.model.quiz_time
        self.time_left.setText(str(self.count))
        self.easy_quiz.set_question(self.model.quiz_question)
        self.easy_quiz.set_options(self.model.quiz_options)
        self.show()
        self.countdown.start(1000)
    
    def on_quiz_answer_checked(self):
        self.countdown.stop()
        self.count = 4
        self.time_left.setText(str(self.count))
        self.countdown.start(1000)


class EasyQuiz(QScrollArea):
    def __init__(self, controller):
        super().__init__()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.controller = controller
        
        self.quiz = QWidget()
        self.setWidget(self.quiz)
        main_layout = QVBoxLayout()
        self.quiz.setLayout(main_layout)
        
        self.question = QLabel()
        self.question.setWordWrap(True)
        question_font = QtGui.QFont()
        question_font.setFamily("Times")
        question_font.setPointSize(16)
        question_font.setBold(True)
        self.question.setFont(question_font)
        main_layout.addWidget(self.question)
        
        self.options = QButtonGroup()
        for i in range(4):
            option = QRadioButton()
            option.clicked.connect(self.on_option_clicked)
            main_layout.addWidget(option)
            self.options.addButton(option)
        
        self.setStyleSheet(".EasyQuiz { border: none }")
    
    def on_option_clicked(self):
        self.controller.check_quiz_answer(self.options.checkedButton().text())
        for option in self.options.buttons():
            option.setEnabled(False)
    
    def set_question(self, question):
        self.question.setText(question)
    
    def set_options(self, options):
        i = 0
        for option in self.options.buttons():
            option.setEnabled(True)
            option.setText(options[i])
            i += 1
        checked = self.options.checkedButton()
        if checked is not None:
            self.options.setExclusive(False)
            checked.setChecked(False)
            self.options.setExclusive(True)