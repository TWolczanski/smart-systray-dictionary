from PyQt5.QtCore import QObject, pyqtSignal

class SearchModel(QObject):
    search_finished = pyqtSignal()
    english_to_polish = []
    english_to_english = []
    error_pl = ""
    error_en = ""