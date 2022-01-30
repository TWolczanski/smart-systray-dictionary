from PyQt5.QtCore import QObject, pyqtSignal

class SearchModel(QObject):
    search_finished = pyqtSignal()
    word = ""
    english_to_polish = []
    english_to_english = []
    error = ""