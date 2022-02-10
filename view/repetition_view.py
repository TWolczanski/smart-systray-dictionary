from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QDesktopWidget, QRadioButton, QButtonGroup, QStackedWidget

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
        
        self.close_button = QPushButton()
        self.close_button.setIcon(QtGui.QIcon("./asset/close.svg"))
        self.close_button.setStyleSheet("border: none")
        self.close_button.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.close_button.clicked.connect(self.close)
        top_layout.addWidget(self.close_button)
        top_layout.addStretch()
        
        self.info = QLabel()
        top_layout.addWidget(self.info)
        top_layout.addStretch()
        
        main_layout.addLayout(top_layout)
        
        self.quizzes = QStackedWidget()
        self.easy_quiz = EasyQuiz(self.model, self.controller, self)
        self.hard_quiz = HardQuiz(self.model, self.controller, self)
        self.quizzes.addWidget(self.easy_quiz)
        self.quizzes.addWidget(self.hard_quiz)
        main_layout.addWidget(self.quizzes)
        
        self.setLayout(main_layout)
        
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.X11BypassWindowManagerHint
        )
        
        self.resize(250, 150)
        fg = self.frameGeometry()
        top_right_point = QDesktopWidget().availableGeometry().topRight()
        fg.moveTopRight(top_right_point)
        x = fg.topLeft().x() - 40
        y = fg.topLeft().y() + 40
        self.move(x, y)
        
        self.model.quiz_created.connect(self.on_quiz_created)
        self.model.quiz_answer_checked.connect(self.on_quiz_answer_checked)
    
    def closeEvent(self, event):
        self.countdown.stop()
        event.accept()
    
    def update_timer(self):
        self.count -= 1
        self.info.setText(str(self.count))
        if self.count <= 0:
            self.close()
    
    def on_quiz_created(self):
        self.count = self.model.quiz_time
        self.info.setText(str(self.count))
        
        if self.model.quiz_level < 3:
            vbar = self.easy_quiz.verticalScrollBar()
            vbar.setValue(vbar.minimum())
            hbar = self.easy_quiz.horizontalScrollBar()
            hbar.setValue(hbar.minimum())
            self.easy_quiz.set_question(self.model.quiz_question)
            self.easy_quiz.set_options(self.model.quiz_options)
            self.quizzes.setCurrentWidget(self.easy_quiz)
        else:
            vbar = self.hard_quiz.verticalScrollBar()
            vbar.setValue(vbar.minimum())
            hbar = self.hard_quiz.horizontalScrollBar()
            hbar.setValue(hbar.minimum())
            self.hard_quiz.set_question(self.model.quiz_question)
            self.quizzes.setCurrentWidget(self.hard_quiz)
            
        self.show()
        self.countdown.start(1000)
    
    def on_quiz_answer_checked(self):
        self.countdown.stop()
        self.info.setText(self.model.quiz_feedback)
        self.info.adjustSize()
        if self.model.quiz_level < 3:
            self.easy_quiz.on_quiz_answer_checked()
        else:
            self.hard_quiz.on_quiz_answer_checked()


class EasyQuiz(QScrollArea):
    def __init__(self, model, controller, view):
        super().__init__()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWidgetResizable(True)
        self.model = model
        self.controller = controller
        self.view = view
        
        self.quiz = QWidget()
        self.setWidget(self.quiz)
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setSpacing(10)
        self.quiz.setLayout(main_layout)
        
        self.question = QLabel()
        self.question.setWordWrap(True)
        self.question.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.question_font = QtGui.QFont()
        self.question_font.setFamily("Times")
        self.question_font.setPointSize(16)
        self.question_font.setBold(True)
        self.question.setFont(self.question_font)
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
        self.view.activateWindow()
        self.controller.check_quiz_answer(self.labels[self.options.checkedId()].text())
        # for some reason range(4) causes a scroll
        for i in range(3, 0, -1):
            self.options.buttons()[i].setEnabled(False)
        for label in self.labels:
            label.setStyleSheet("color: gray")
    
    def set_question(self, question):
        if len(question) > 60:
            self.question_font.setPointSize(12)
        elif len(question) > 30:
            self.question_font.setPointSize(14)
        else:
            self.question_font.setPointSize(16)
        self.question.setFont(self.question_font)
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
                
                
class HardQuiz(QScrollArea):
    def __init__(self, model, controller, view):
        super().__init__()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWidgetResizable(True)
        self.model = model
        self.controller = controller
        self.view = view
        
        self.quiz = QWidget()
        self.setWidget(self.quiz)
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setSpacing(10)
        self.quiz.setLayout(self.main_layout)
        
        self.question = QLabel()
        self.question.setWordWrap(True)
        self.question.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.question_font = QtGui.QFont()
        self.question_font.setFamily("Times")
        self.question_font.setPointSize(16)
        self.question_font.setBold(True)
        self.question.setFont(self.question_font)
        self.main_layout.addWidget(self.question)
        
        self.button = QPushButton("Check")
        self.button.clicked.connect(self.on_button_clicked)
        
        self.answer = ClickableLineEdit()
        self.answer.clicked.connect(self.view.activateWindow)
        self.answer.returnPressed.connect(self.button.click)
        
        self.feedback = QWidget()
        self.feedback_layout = QVBoxLayout()
        self.feedback.setLayout(self.feedback_layout)
        
        self.main_layout.addWidget(self.answer)
        self.main_layout.addWidget(self.button)
        self.main_layout.addWidget(self.feedback)
        
        self.setStyleSheet(".HardQuiz { border: none }")
    
    def on_button_clicked(self):
        self.button.setEnabled(False)
        self.answer.setEnabled(False)
        self.controller.check_quiz_answer(self.answer.text())
    
    def set_question(self, question):
        if len(question) > 60:
            self.question_font.setPointSize(12)
        elif len(question) > 30:
            self.question_font.setPointSize(14)
        else:
            self.question_font.setPointSize(16)
        self.question.setFont(self.question_font)
        self.question.setText(question)
        
        self.button.setEnabled(True)
        self.answer.setEnabled(True)
        self.answer.setText("")
        
        # clear the feedback
        self.main_layout.removeWidget(self.feedback)
        self.feedback.deleteLater()
        self.feedback = QWidget()
    
    def on_quiz_answer_checked(self):
        answer = self.answer.text()
        feedback_layout = QVBoxLayout()
        self.feedback.setLayout(feedback_layout)
        self.main_layout.addWidget(self.feedback)
        
        if answer not in self.model.quiz_correct_answers:
            label = QLabel(answer)
            label.setStyleSheet("color: red")
            feedback_layout.addWidget(label)
            
        for a in self.model.quiz_correct_answers:
            label = QLabel(a)
            label.setStyleSheet("color: green")
            feedback_layout.addWidget(label)


class ClickableLineEdit(QLineEdit):
    clicked = pyqtSignal()
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)