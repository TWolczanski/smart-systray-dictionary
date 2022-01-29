from PyQt5.QtCore import QObject, pyqtSignal

class SearchModel(QObject):
    search_finished = pyqtSignal()
    word = ""
    polish_meanings = []
    english_meanings = []
    error = ""