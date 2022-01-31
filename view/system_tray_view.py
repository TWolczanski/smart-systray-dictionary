from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, qApp

class SystemTrayView(QSystemTrayIcon):
    def __init__(self, search_view):
        super().__init__()
        
        self.menu = QMenu()
        self.action1 = QAction("Search")
        self.action1.triggered.connect(lambda: search_view.show())
        self.action2 = QAction("Quit")
        self.action2.triggered.connect(lambda: qApp.quit())
        self.menu.addAction(self.action1)
        self.menu.addAction(self.action2)
        
        self.icon = QIcon("./asset/icon.png")
        
        self.setIcon(self.icon)
        self.setContextMenu(self.menu)