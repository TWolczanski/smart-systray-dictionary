from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, qApp

class SystemTrayView(QSystemTrayIcon):
    def __init__(self, search_view, settings_view, repetition_controller):
        super().__init__()
        self.search_view = search_view
        self.settings_view = settings_view
        self.repetition_controller = repetition_controller
        
        self.menu = QMenu()
        self.action1 = QAction("Search")
        self.action1.triggered.connect(self.search_view.show)
        self.action2 = QAction("Disable repetitions")
        self.action2.triggered.connect(self.on_toggle_repetitions)
        self.action3 = QAction("Settings")
        self.action3.triggered.connect(self.settings_view.show)
        self.action4 = QAction("Quit")
        self.action4.triggered.connect(self.on_quit)
        self.menu.addAction(self.action1)
        self.menu.addAction(self.action2)
        self.menu.addAction(self.action3)
        self.menu.addAction(self.action4)
        
        self.icon = QIcon("./asset/icon.png")
        
        self.setIcon(self.icon)
        self.setContextMenu(self.menu)
    
    def on_quit(self):
        # stop the thread performing database operations
        self.repetition_controller.operations.put(None)
        qApp.quit()
    
    def on_toggle_repetitions(self):
        if self.repetition_controller.repetitions_enabled:
            self.repetition_controller.repetitions_enabled = False
            self.action2.setText("Enable repetitions")
        else:
            self.repetition_controller.repetitions_enabled = True
            self.action2.setText("Disable repetitions")