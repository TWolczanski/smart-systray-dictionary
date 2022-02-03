from PyQt5.QtCore import QObject, pyqtSignal

class RepetitionModel(QObject):
    quiz_created = pyqtSignal()
    quiz_answer_checked = pyqtSignal()
    
    quiz_time = 50
    quiz_interval = 7
    quiz_level = 1
    quiz_question = ""
    quiz_options = []
    quiz_feedback = ""