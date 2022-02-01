from PyQt5.QtCore import QObject, pyqtSignal

class SearchModel(QObject):
    hotkey_pressed = pyqtSignal()
    search_finished = pyqtSignal()
    database_operation_finished = pyqtSignal()
    
    hotkey = "<cmd>+s"
    english_to_polish = []
    english_to_english = []
    error_pl = ""
    error_en = ""
    db_error = ""