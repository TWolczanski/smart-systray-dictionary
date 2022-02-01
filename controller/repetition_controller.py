from PyQt5.QtCore import QObject
from threading import Thread
import time

class RepetitionController(QObject):
    def __init__(self, model, db_controller):
        self.model = model
        self.db_controller = db_controller
        self.looper = Thread(target=self.loop, daemon=True)
        self.looper.start()
    
    def loop(self):
        while True:
            time.sleep(self.model.quiz_interval + self.model.quiz_time)
            self.create_quiz()
            self.model.quiz_created.emit()
    
    def create_quiz(self):
        meaning = self.db_controller.get_random_meaning()