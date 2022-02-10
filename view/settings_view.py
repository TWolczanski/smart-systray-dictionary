from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QFormLayout, QErrorMessage, QMessageBox

class SettingsView(QWidget):
    def __init__(self, settings_model, repetition_model, controller):
        super().__init__()
        self.settings_model = settings_model
        self.repetition_model = repetition_model
        self.controller = controller
        
        self.setWindowTitle("Settings")
        
        layout = QFormLayout()
        self.setLayout(layout)
        
        self.quiz_time = QLineEdit()
        self.quiz_interval = QLineEdit()
        
        self.validator = QtGui.QIntValidator(bottom=1)
        self.quiz_time.setValidator(self.validator)
        self.quiz_interval.setValidator(self.validator)
        
        self.save = QPushButton("Save")
        self.save.clicked.connect(self.on_save)
        
        layout.addRow("Quiz duration (in seconds)", self.quiz_time)
        layout.addRow("Time interval between quizzes (in seconds)", self.quiz_interval)
        layout.addRow(self.save)
        
        self.error = QErrorMessage()
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Information)
        
        self.settings_model.settings_changed.connect(self.on_settings_changed)
    
    def showEvent(self, event):
        self.quiz_time.setText(str(self.repetition_model.quiz_time))
        self.quiz_interval.setText(str(self.repetition_model.quiz_interval))
        event.accept()
    
    def on_save(self):
        self.controller.change_settings(
            self.quiz_time.text(),
            self.quiz_interval.text()
        )
    
    def on_settings_changed(self):
        if self.settings_model.error:
            self.error.showMessage("An error occurred while saving changes")
        else:
            self.msg.setText("Settings saved")
            self.msg.exec()