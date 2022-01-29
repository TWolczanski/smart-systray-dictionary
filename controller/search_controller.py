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
        self.model.polish_meanings = []
        self.model.english_meanings = []
        
        self.scrape_pl(word)
        # try:
        #     self.scrape_pl(word)
        # except:
        #     self.model.error = "An error occured during the search"
        
        # fetch English definitions of the word
        # data_raw_en = requests.get("https://api.dictionaryapi.dev/api/v2/entries/en/" + word, headers={"User-Agent": "Mozilla/5.0"})
        # data_en = data_raw_en.json()
        # self.model.english_meanings = data_en[0]["meanings"]
        
        self.model.search_finished.emit()
    
    def scrape_pl(self, word):
        res = requests.get("https://www.diki.pl/slownik-angielskiego?q=" + word, headers={"User-Agent": "Mozilla/5.0"})
        content = res.text
        soup = bs4.BeautifulSoup(content, "html.parser")
        container = soup.select_one('a[name="en-pl"]').parent.find_next_sibling(class_="diki-results-container").select_one(".diki-results-left-column")
        
        for t1 in container.select(".dictionaryEntity"):
            for t2 in t1.select(".partOfSpeechSectionHeader"):
                part_of_speech = t2.select_one(".partOfSpeech").text
                new_part_of_speech = True
                meaning = {}
                meaning["partOfSpeech"] = part_of_speech
                meaning["definitions"] = []
                
                for m in self.model.polish_meanings:
                    if m["partOfSpeech"] == part_of_speech:
                        new_part_of_speech = False
                        meaning = m
                
                for t3 in t2.find_next_sibling(class_="foreignToNativeMeanings").find_all(True, recursive=False):
                    definition = t3.select_one(".hw").get_text(" ", strip=True)
                    sentences = []
                    for t4 in t3.select(".exampleSentence"):
                        sentences.append(t4.next.strip())
                    meaning["definitions"].append({"definition": definition, "sentences": sentences})
                    
                if new_part_of_speech:
                    self.model.polish_meanings.append(meaning)