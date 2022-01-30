from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QErrorMessage

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
        if self.model.error:
            self.error.showMessage(self.model.error)
            return

        self.resize(800, 900)
        
        if self.search_count > 0:
            self.main_layout.removeWidget(self.scroll_area)
            self.scroll_area.deleteLater()
            # self.scroll_area.setParent(None)
            # print(self.scroll_area.children())
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        
        self.search_results = QWidget()
        self.results_layout = QVBoxLayout()
        self.results_layout.setAlignment(Qt.AlignTop)
        self.results_layout.setSpacing(30)
        self.search_results.setLayout(self.results_layout)
        self.scroll_area.setWidget(self.search_results)
        self.main_layout.addWidget(self.scroll_area)
        
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        
        in_polish = QLabel("IN POLISH")
        in_polish.setFont(font)
        self.results_layout.addWidget(in_polish)
        
        en2pl_layout = QVBoxLayout()
        
        for meaning in self.model.english_to_polish:
            en2pl = EnglishToPolish(meaning["words"], meaning["definitions"])
            en2pl_layout.addWidget(en2pl)
        
        en2pl_layout.setSpacing(30)
        self.results_layout.addLayout(en2pl_layout)
        
        # for meaning in self.model.english_meanings:
        #     label = QLabel(meaning["definitions"][0]["definition"])
        #     label.setWordWrap(True)
        #     self.results_layout.addWidget(label)
        #     self.meanings.append(label)
        
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
        top_layout = QHBoxLayout()
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
        
        part_of_speech_label = QLabel(part_of_speech)
        part_of_speech_label.setFont(part_of_speech_font)
        part_of_speech_label.setStyleSheet("color: gray")
        
        button = QPushButton("+")
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        top_layout.addWidget(definition_label)
        top_layout.addWidget(button)
        
        for sentence in sentences:
            s = QLabel("• " + sentence)
            s.setFont(font)
            s.setStyleSheet("padding-left: 15px")
            bottom_layout.addWidget(s)
        bottom_layout.setSpacing(18)
        
        main_layout.addLayout(top_layout)
        main_layout.addWidget(part_of_speech_label)
        main_layout.addLayout(bottom_layout)
        main_layout.setSpacing(14)
        self.setLayout(main_layout)