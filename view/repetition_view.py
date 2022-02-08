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
        
        self.time_left = QLabel()
        top_layout.addWidget(self.time_left)
        top_layout.addStretch()
        
        self.feedback = QLabel()
        self.feedback.setWordWrap(True)
        top_layout.addWidget(self.feedback)
        main_layout.addLayout(top_layout)
        
        self.easy_quiz = EasyQuiz(self.model, self.controller)
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
        self.feedback.setText("")
        self.feedback.adjustSize()
        vbar = self.easy_quiz.verticalScrollBar()
        vbar.setValue(vbar.minimum())
        self.easy_quiz.set_question(self.model.quiz_question)
        self.easy_quiz.set_options(self.model.quiz_options)
        self.show()
        self.countdown.start(1000)
    
    def on_quiz_answer_checked(self):
        self.countdown.stop()
        self.count = 4
        self.time_left.setText(str(self.count))
        self.feedback.setText(self.model.quiz_feedback)
        self.feedback.adjustSize()
        self.easy_quiz.on_quiz_answer_checked()
        self.countdown.start(1000)


class EasyQuiz(QScrollArea):
    def __init__(self, model, controller):
        super().__init__()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.model = model
        self.controller = controller
        
        self.quiz = QWidget()
        self.setWidget(self.quiz)
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setSpacing(10)
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
        self.labels = []
        
        for i in range(4):
            option_layout = QHBoxLayout()
            option_layout.setAlignment(Qt.AlignLeft)
            
            option = QRadioButton()
            # give the button id, so it can be associated with a label
            self.options.addButton(option, i)
            option.clicked.connect(self.on_option_clicked)
            option_layout.addWidget(option)
            
            option_label = QLabel("a")
            option_label.setWordWrap(True)
            option_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            font = QtGui.QFont()
            font.setFamily("Arial")
            font.setPointSize(11)
            option_label.setFont(font)
            option_label.adjustSize()
            self.labels.append(option_label)
            option_layout.addWidget(option_label)
            
            main_layout.addLayout(option_layout)
        
        self.setStyleSheet(".EasyQuiz { border: none }")
    
    def on_option_clicked(self):
        self.controller.check_quiz_answer(self.labels[self.options.checkedId()].text())
        # for some reason range(4) causes a scroll
        for i in range(3, 0, -1):
            self.options.buttons()[i].setEnabled(False)
        for label in self.labels:
            label.setStyleSheet("color: gray")
    
    def set_question(self, question):
        self.question.setText(question)
    
    def set_options(self, options):
        for option in self.options.buttons():
            option.setEnabled(True)
        checked = self.options.checkedButton()
        if checked is not None:
            self.options.setExclusive(False)
            checked.setChecked(False)
            self.options.setExclusive(True)
        i = 0
        for label in self.labels:
            label.setText(options[i])
            label.setStyleSheet("color: black")
            label.adjustSize()
            i += 1
    
    def on_quiz_answer_checked(self):
        answer = self.labels[self.options.checkedId()].text()
        for label in self.labels:
            if label.text() in self.model.quiz_correct_answers:
                label.setStyleSheet("color: green")
            elif answer == label.text():
                label.setStyleSheet("color: red")