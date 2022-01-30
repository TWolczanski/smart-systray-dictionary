import sys
from PyQt5.QtWidgets import QApplication
from model.search_model import SearchModel
from view.search_view import SearchView
from controller.search_controller import SearchController
from controller.db_controller import DatabaseController

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    search_model = SearchModel()
    search_controller = SearchController(search_model)
    db_controller = DatabaseController()
    search_view = SearchView(search_model, search_controller, db_controller)
    sys.exit(app.exec())