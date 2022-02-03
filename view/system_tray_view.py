from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, qApp

class SystemTrayView(QSystemTrayIcon):
    def __init__(self, search_view, repetition_controller):
        super().__init__()
        self.search_view = search_view
        self.repetition_controller = repetition_controller
        
        self.menu = QMenu()
        self.action1 = QAction("Search")
        self.action1.triggered.connect(lambda: self.search_view.show())
        self.action2 = QAction("Disable repetitions")
        self.action2.triggered.connect(lambda: self.on_toggle_repetitions())
        self.action3 = QAction("Quit")
        self.action3.triggered.connect(lambda: self.on_quit())
        self.menu.addAction(self.action1)
        self.menu.addAction(self.action2)
        self.menu.addAction(self.action3)
        
        self.icon = QIcon("./asset/icon.png")
        
        self.setIcon(self.icon)
        self.setContextMenu(self.menu)
    
    def on_quit(self):
        self.repetition_controller.operations.put(None)
        qApp.quit()
    
    def on_toggle_repetitions(self):
        if self.repetition_controller.repetitions_enabled:
            self.repetition_controller.repetitions_enabled = False
            self.action2.setText("Enable repetitions")
        else:
            self.repetition_controller.repetitions_enabled = True
            self.action2.setText("Disable repetitions")