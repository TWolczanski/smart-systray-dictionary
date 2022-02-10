from PyQt5.QtCore import QObject, pyqtSignal

class SettingsModel(QObject):
    settings_changed = pyqtSignal()
    error = ""