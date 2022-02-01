import sys
from PyQt5.QtWidgets import QApplication
from model.search_model import SearchModel
from model.repetition_model import RepetitionModel
from view.search_view import SearchView
from view.system_tray_view import SystemTrayView
from view.repetition_view import RepetitionView
from controller.search_controller import SearchController
from controller.db_controller import DatabaseController
from controller.repetition_controller import RepetitionController

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    search_model = SearchModel()
    repetition_model = RepetitionModel()
    
    search_controller = SearchController(search_model)
    db_controller = DatabaseController()
    repetition_controller = RepetitionController(repetition_model, db_controller)
    
    search_view = SearchView(search_model, search_controller, db_controller)
    repetition_view = RepetitionView(repetition_model, repetition_controller)
    system_tray_view = SystemTrayView(search_view)
    system_tray_view.show()
    db_controller.get_random_meaning("pl")
    
    sys.exit(app.exec())