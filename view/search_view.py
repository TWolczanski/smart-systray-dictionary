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
        
        word_font = QtGui.QFont()
        word_font.setFamily("Arial")
        word_font.setPointSize(30)
        word_font.setBold(True)
        
        part_of_speech_font = QtGui.QFont()
        part_of_speech_font.setFamily("Arial")
        part_of_speech_font.setPointSize(12)
        part_of_speech_font.setItalic(True)
        
        word_label = QLabel(self.model.word)
        word_label.setFont(word_font)
        self.results_layout.addWidget(word_label)
        
        in_polish = QLabel("IN POLISH")
        in_polish.setFont(font)
        self.results_layout.addWidget(in_polish)
        
        for meaning in self.model.polish_meanings:
            layout = QVBoxLayout()
            part_of_speech = QLabel(meaning["partOfSpeech"])
            part_of_speech.setFont(part_of_speech_font)
            layout.addWidget(part_of_speech)
            for d in meaning["definitions"]:
                pm = PolishMeaning(d["definition"], d["sentences"])
                layout.addWidget(pm)
            self.results_layout.addLayout(layout)
            layout.setSpacing(30)
        
        # for meaning in self.model.english_meanings:
        #     label = QLabel(meaning["definitions"][0]["definition"])
        #     label.setWordWrap(True)
        #     self.results_layout.addWidget(label)
        #     self.meanings.append(label)
        
        self.search_count += 1

class PolishMeaning(QWidget):
    def __init__(self, definition, sentences):
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.top_layout = QHBoxLayout()
        self.bottom_layout = QVBoxLayout()
        
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        
        definition_font = QtGui.QFont()
        definition_font.setFamily("Arial")
        definition_font.setPointSize(12)
        definition_font.setBold(True)
        
        definition_label = QLabel(definition)
        definition_label.setFont(definition_font)
        definition_label.setStyleSheet("padding-left: 5px")
        button = QPushButton("+")
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.top_layout.addWidget(definition_label)
        self.top_layout.addWidget(button)
        
        for sentence in sentences:
            s = QLabel("• " + sentence)
            s.setFont(font)
            s.setStyleSheet("padding-left: 20px")
            self.bottom_layout.addWidget(s)
        self.bottom_layout.setSpacing(18)
        
        self.main_layout.addLayout(self.top_layout)
        self.main_layout.addLayout(self.bottom_layout)
        self.main_layout.setSpacing(25)
        self.setLayout(self.main_layout)
        # self.setStyleSheet(".PolishMeaning { padding: 20px }")