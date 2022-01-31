from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QErrorMessage, QTabWidget, QDesktopWidget, QMessageBox

class SearchView(QWidget):
    def __init__(self, model, search_controller, db_controller):
        super().__init__()
        self.model = model
        self.search_controller = search_controller
        self.db_controller = db_controller
        
        self.main_layout = QVBoxLayout()
        self.top_layout = QHBoxLayout()
        
        self.search_bar = QLineEdit()
        self.search_btn = QPushButton("Search", clicked=lambda: self.search_controller.search(self.search_bar.text()))
        self.search_bar.returnPressed.connect(self.search_btn.click)
        self.top_layout.addWidget(self.search_bar)
        self.top_layout.addWidget(self.search_btn)
        
        self.main_layout.addLayout(self.top_layout)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)
        
        self.error = QErrorMessage()
        
        self.model.hotkey_pressed.connect(self.on_hotkey_pressed)
        self.model.search_finished.connect(self.on_search_finished)
        
    def on_hotkey_pressed(self):
        if self.isHidden():
            self.show()
        else:
            self.close()
    
    def closeEvent(self, event):
        event.accept()
        self.main_layout.removeWidget(self.tabs)
        self.tabs.deleteLater()
    
    def showEvent(self, event):
        self.search_bar.setText("")
        self.tabs = QTabWidget()
        event.accept()
        self.activateWindow()
        self.resize(800, 50)
        self.center()
    
    def center(self):
        fg = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        fg.moveCenter(center_point)
        self.move(fg.topLeft())
        
    def on_search_finished(self):
        if self.model.error_pl and self.model.error_en:
            self.error.showMessage(
                "Errors occurred while searching for definitions of the word:\n" +
                self.model.error_pl +
                "\n\n" +
                self.model.error_en
            )
            return
            
        if self.model.error_pl:
            self.error.showMessage(
                "An error occurred while searching for Polish definitions of the word:\n" +
                self.model.error_pl
            )
            
        if self.model.error_en:
            self.error.showMessage(
                "An error occurred while searching for English definitions of the word:\n" +
                self.model.error_en
            )

        self.resize(800, 900)
        
        self.main_layout.removeWidget(self.tabs)
        self.tabs.deleteLater()
        
        self.tabs = QTabWidget()
        
        search_results_pl = SearchResults(self.model.english_to_polish, "pl", self.db_controller)
        self.tabs.addTab(search_results_pl, "In Polish")
        search_results_en = SearchResults(self.model.english_to_english, "en", self.db_controller)
        self.tabs.addTab(search_results_en, "In English")
        
        self.main_layout.addWidget(self.tabs)


class SearchResults(QScrollArea):
    def __init__(self, entries, lang, db_controller):
        super().__init__()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        
        results = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(30)
        results.setLayout(layout)
        
        for entry in entries:
            e = Entry(entry["words"], entry["definitions"], lang, db_controller)
            layout.addWidget(e)
        
        self.setWidget(results)


class Entry(QWidget):
    def __init__(self, words, definitions, lang, db_controller):
        super().__init__()
        main_layout = QVBoxLayout()
        definitions_layout = QVBoxLayout()
        
        words_font = QtGui.QFont()
        words_font.setFamily("Times")
        words_font.setPointSize(32)
        words_font.setBold(True)
        
        words_label = QLabel("\n".join(words))
        words_label.setFont(words_font)
        words_label.setWordWrap(True)
        
        for d in definitions:
            pd = Meaning(d["definition"], d["partOfSpeech"], d["sentences"], words, lang, db_controller)
            definitions_layout.addWidget(pd)
        
        main_layout.addWidget(words_label)
        definitions_layout.setSpacing(24)
        main_layout.addLayout(definitions_layout)
        self.setLayout(main_layout)


class Meaning(QWidget):
    def __init__(self, definition, part_of_speech, sentences, words, lang, db_controller):
        super().__init__()
        self.words = words
        self.definition = definition
        self.lang = lang
        self.db_controller = db_controller
        
        main_layout = QVBoxLayout()
        top_layout = QVBoxLayout()
        top_layout_inner = QHBoxLayout()
        bottom_layout = QVBoxLayout()
        
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        
        definition_font = QtGui.QFont()
        definition_font.setFamily("Arial")
        definition_font.setPointSize(12)
        definition_font.setBold(True)
        
        part_of_speech_font = QtGui.QFont()
        part_of_speech_font.setFamily("Arial")
        part_of_speech_font.setPointSize(12)
        part_of_speech_font.setItalic(True)
        
        definition_label = QLabel(definition)
        definition_label.setFont(definition_font)
        definition_label.setWordWrap(True)
        
        part_of_speech_label = QLabel(part_of_speech)
        part_of_speech_label.setFont(part_of_speech_font)
        part_of_speech_label.setWordWrap(True)
        part_of_speech_label.setStyleSheet("color: gray")
        
        button = QPushButton("+")
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button.clicked.connect(lambda: self.on_button_clicked())
        
        self.db_msg = QMessageBox()
        self.db_msg.setIcon(QMessageBox.Information)
        self.db_msg.setText("Successfully added the meaning to the database")
        
        self.db_error = QMessageBox()
        self.db_error.setIcon(QMessageBox.Critical)
        self.db_error.setText("An error occurred while adding the meaning to the database")
        
        top_layout_inner.addWidget(definition_label)
        top_layout_inner.addWidget(button)
        top_layout.addLayout(top_layout_inner)
        top_layout.addWidget(part_of_speech_label)
        top_layout.setSpacing(8)
        
        for sentence in sentences:
            s = QLabel(sentence)
            s.setFont(font)
            s.setWordWrap(True)
            bottom_layout.addWidget(s)
        bottom_layout.setSpacing(18)
        
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)
        main_layout.setSpacing(18)
        self.setLayout(main_layout)
    
    def on_button_clicked(self):
        try:
            self.db_controller.add_words(self.words, self.definition, self.lang)
            self.db_msg.exec()
        except:
            self.db_error.exec()