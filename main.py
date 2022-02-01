import sys
from PyQt5.QtWidgets import QApplication
from model.search_model import SearchModel
from model.repetition_model import RepetitionModel
from view.search_view import SearchView
from view.system_tray_view import SystemTrayView
from view.repetition_view import RepetitionView
from controller.search_controller import SearchController
from controller.repetition_controller import RepetitionController

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    search_model = SearchModel()
    repetition_model = RepetitionModel()
    
    search_controller = SearchController(search_model)
    repetition_controller = RepetitionController(repetition_model, search_model)
    
    search_view = SearchView(search_model, search_controller, repetition_controller)
    repetition_view = RepetitionView(repetition_model, repetition_controller)
    system_tray_view = SystemTrayView(search_view, repetition_controller)
    system_tray_view.show()
    
    sys.exit(app.exec())