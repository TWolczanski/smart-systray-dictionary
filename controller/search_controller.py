from PyQt5.QtCore import QObject
from threading import Thread
import requests
import bs4

class SearchController(QObject):
    def __init__(self, model):
        self.model = model
        
    def search(self, word):
        Thread(target=self.search_, args=[word]).start()
    
    def search_(self, word):
        self.model.word = word
        self.model.english_to_polish = []
        self.model.english_to_english = []
        
        try:
            self.search_pl(word)
        except Exception as e:
            self.model.error_pl = str(e)
        
        # fetch English definitions of the word
        # data_raw_en = requests.get("https://api.dictionaryapi.dev/api/v2/entries/en/" + word, headers={"User-Agent": "Mozilla/5.0"})
        # data_en = data_raw_en.json()
        # self.model.english_meanings = data_en[0]["meanings"]
        
        self.model.search_finished.emit()
    
    def search_pl(self, word):
        res = requests.get("https://www.diki.pl/slownik-angielskiego?q=" + word, headers={"User-Agent": "Mozilla/5.0"})
        content = res.text
        soup = bs4.BeautifulSoup(content, "html.parser")
        container = soup.select_one('a[name="en-pl"]').parent.find_next_sibling(class_="diki-results-container").select_one(".diki-results-left-column")
        
        for t1 in container.select(".dictionaryEntity"):
            meaning = {"words": [], "definitions": []}
            
            for t2 in t1.select(".hws .hw"):
                meaning["words"].append(t2.get_text(" ", strip=True))
                
            for t2 in t1.select(".foreignToNativeMeanings"):
                part_of_speech = ""
                sibling = t2.find_previous_sibling(class_="partOfSpeechSectionHeader")
                if sibling is not None:
                    child = sibling.select_one(".partOfSpeech")
                    if child is not None:
                        part_of_speech = child.get_text(strip=True)
                
                for t3 in t2.find_all(True, recursive=False):
                    d = {"definition": "", "partOfSpeech": "", "sentences": []}
                    
                    definition = ""
                    for t4 in t3.select(".hw"):
                        definition += t4.get_text(" ", strip=True) + ", "
                    if definition[-2:] == ", ":
                        definition = definition[:-2]
                        
                    sentences = []
                    for t4 in t3.select(".exampleSentence"):
                        sentences.append(t4.next.strip())
                        
                    d["definition"] = definition
                    if part_of_speech is not None:
                        d["partOfSpeech"] = part_of_speech
                    d["sentences"] = sentences
                    
                    meaning["definitions"].append(d)
            
            self.model.english_to_polish.append(meaning)