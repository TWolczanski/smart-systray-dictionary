from PyQt5.QtCore import QObject
import json

class SettingsController(QObject):
    def __init__(self, settings_model, repetition_model):
        super().__init__()
        self.settings_model = settings_model
        self.repetition_model = repetition_model
    
    def change_settings(self, quiz_time, quiz_interval):
        try:
            config = ""
            with open("./config/config.json", "r") as f:
                config = json.loads(f.read())
            with open("./config/config.json", "w") as f:
                if quiz_time != "":
                    config["quizTime"] = int(quiz_time)
                    self.repetition_model.quiz_time = int(quiz_time)
                if quiz_interval != "":
                    config["quizInterval"] = int(quiz_interval)
                    self.repetition_model.quiz_interval = int(quiz_interval)
                f.write(json.dumps(config))
        except Exception as e:
            self.settings_model.error = str(e)
        finally:
            self.settings_model.settings_changed.emit()