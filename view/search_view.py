from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QErrorMessage, QTabWidget, QDesktopWidget, QMessageBox

class SearchView(QWidget):
    def __init__(self, model, search_controller, repetition_controller):
        super().__init__()
        self.model = model
        self.search_controller = search_controller
        self.repetition_controller = repetition_controller
        
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
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Information)
        
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
        
        search_results_pl = SearchResults(self.model.english_to_polish)
        for entry in search_results_pl.entries:
            for meaning in entry.meanings:
                meaning.button.clicked.connect(lambda: self.on_button_clicked(entry.words, meaning.definition))
        self.tabs.addTab(search_results_pl, "In Polish")
        
        search_results_en = SearchResults(self.model.english_to_english)
        for entry in search_results_en.entries:
            for meaning in entry.meanings:
                meaning.button.clicked.connect(lambda: self.on_button_clicked(entry.words, meaning.definition))
        self.tabs.addTab(search_results_en, "In English")
        
        self.main_layout.addWidget(self.tabs)
    
    def on_button_clicked(self, words, definition):
        try:
            self.repetition_controller.add_words(words, definition)
            self.msg.setText("Successfully added the meaning to the database")
            self.msg.exec()
        except:
            self.error.showMessage("An error occured while adding the meaning to the database")


class SearchResults(QScrollArea):
    def __init__(self, entries):
        super().__init__()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        
        results = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(30)
        results.setLayout(layout)
        
        self.entries = []
        
        for entry in entries:
            e = Entry(entry["words"], entry["definitions"])
            layout.addWidget(e)
            self.entries.append(e)
        
        self.setWidget(results)


class Entry(QWidget):
    def __init__(self, words, definitions):
        super().__init__()
        self.words = words
        main_layout = QVBoxLayout()
        definitions_layout = QVBoxLayout()
        
        words_font = QtGui.QFont()
        words_font.setFamily("Times")
        words_font.setPointSize(32)
        words_font.setBold(True)
        
        words_label = QLabel("\n".join(words))
        words_label.setFont(words_font)
        words_label.setWordWrap(True)
        
        self.meanings = []
        
        for d in definitions:
            m = Meaning(d["definition"], d["partOfSpeech"], d["sentences"])
            definitions_layout.addWidget(m)
            self.meanings.append(m)
        
        main_layout.addWidget(words_label)
        definitions_layout.setSpacing(24)
        main_layout.addLayout(definitions_layout)
        self.setLayout(main_layout)


class Meaning(QWidget):
    def __init__(self, definition, part_of_speech, sentences):
        super().__init__()
        self.definition = definition
        
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
        
        self.button = QPushButton("+")
        self.button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        top_layout_inner.addWidget(definition_label)
        top_layout_inner.addWidget(self.button)
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