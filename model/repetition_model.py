from PyQt5.QtCore import QObject, pyqtSignal
import json

class RepetitionModel(QObject):
    quiz_created = pyqtSignal()
    quiz_answer_checked = pyqtSignal()
    
    quiz_level = 1
    quiz_question = ""
    quiz_options = []
    quiz_feedback = ""
    quiz_correct_answers = []
    
    def __init__(self):
        super().__init__()
        # read the quiz time and quiz interval from the config file
        with open("./config/config.json", "r") as f:
            config = json.loads(f.read())
            self.quiz_time = config["quizTime"]
            self.quiz_interval = config["quizInterval"]