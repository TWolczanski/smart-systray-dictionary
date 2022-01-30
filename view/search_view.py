from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QErrorMessage, QTabWidget

class SearchView(QWidget):
    hotkey_pressed = pyqtSignal()
    
    def __init__(self, model, controller):
        super().__init__()
        self.model = model
        self.controller = controller
        
        self.main_layout = QVBoxLayout()
        self.top_layout = QHBoxLayout()
        
        self.search_bar = QLineEdit()
        self.search_btn = QPushButton("Search", clicked=lambda: self.controller.search(self.search_bar.text()))
        self.search_bar.returnPressed.connect(self.search_btn.click)
        self.top_layout.addWidget(self.search_bar)
        self.top_layout.addWidget(self.search_btn)
        
        self.main_layout.addLayout(self.top_layout)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)
        
        self.resize(800, 50)
        self.model.search_finished.connect(self.on_search_finished)
        self.hotkey_pressed.connect(self.on_hotkey)
        self.error = QErrorMessage()
        self.search_count = 0
        
    def on_hotkey(self):
        if self.isHidden():
            self.show()
        else:
            self.close()
        
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
            return
            
        if self.model.error_en:
            self.error.showMessage(
                "An error occurred while searching for English definitions of the word:\n" +
                self.model.error_en
            )
            return

        self.resize(800, 900)
        
        if self.search_count > 0:
            self.main_layout.removeWidget(self.tabs)
            self.tabs.deleteLater()
        
        self.tabs = QTabWidget()
        
        # polish definitions
        
        scroll_area_pl = QScrollArea()
        scroll_area_pl.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area_pl.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area_pl.setWidgetResizable(True)
        
        results_pl = QWidget()
        results_pl_layout = QVBoxLayout()
        results_pl_layout.setAlignment(Qt.AlignTop)
        results_pl_layout.setSpacing(30)
        results_pl.setLayout(results_pl_layout)
        scroll_area_pl.setWidget(results_pl)
        
        for meaning in self.model.english_to_polish:
            en2pl = EnglishToPolish(meaning["words"], meaning["definitions"])
            results_pl_layout.addWidget(en2pl)
        
        self.tabs.addTab(scroll_area_pl, "In Polish")
        
        # english definitions
        
        scroll_area_en = QScrollArea()
        scroll_area_en.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area_en.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area_en.setWidgetResizable(True)
        
        self.tabs.addTab(scroll_area_en, "In English")
        
        # for meaning in self.model.english_meanings:
        #     label = QLabel(meaning["definitions"][0]["definition"])
        #     label.setWordWrap(True)
        #     self.results_pl_layout.addWidget(label)
        #     self.meanings.append(label)
        
        self.main_layout.addWidget(self.tabs)
        self.search_count += 1


class EnglishToPolish(QWidget):
    def __init__(self, words, definitions):
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
            pd = PolishDefinition(d["definition"], d["partOfSpeech"], d["sentences"])
            definitions_layout.addWidget(pd)
        
        main_layout.addWidget(words_label)
        definitions_layout.setSpacing(24)
        main_layout.addLayout(definitions_layout)
        self.setLayout(main_layout)


class PolishDefinition(QWidget):
    def __init__(self, definition, part_of_speech, sentences):
        super().__init__()
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


class EnglishToEnglish():
    def __init__(self, word, meanings):
        pass