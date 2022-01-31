from PyQt5.QtCore import QObject, pyqtSignal

class RepetitionModel(QObject):
    quiz_created = pyqtSignal()
    
    quiz_time = 5
    quiz_interval = 9