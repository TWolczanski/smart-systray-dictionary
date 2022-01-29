import sys
# import keyboard
from pynput import keyboard
from PyQt5.QtWidgets import QApplication
from model.search_model import SearchModel
from view.search_view import SearchView
from controller.search_controller import SearchController

# def for_canonical(f):
#     return lambda k: f(listener.canonical(k))

# def on_activate():
#     search_view.hotkey_pressed.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    search_model = SearchModel()
    search_controller = SearchController(search_model)
    search_view = SearchView(search_model, search_controller)
    # hotkey = keyboard.HotKey(keyboard.HotKey.parse("<cmd>+s"), on_activate=on_activate)
    # listener = keyboard.Listener(on_press=for_canonical(hotkey.press), on_release=for_canonical(hotkey.release))
    # listener.start()
    search_view.show()
    sys.exit(app.exec())