import nltk
nltk.download('words')
from nltk.corpus import words
from collections import defaultdict

from collections import defaultdict

class TrieNode:
    def __init__(self):
        self.children = defaultdict(TrieNode)
        self.is_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.frequencies = nltk.FreqDist(words.words())
        for word in self.frequencies.keys():
            self.insert(word)
    
    def insert(self, word):
        current = self.root
        for char in word:
            current = current.children[char]
        current.is_word = True

    def autocomplete(self, prefix):
        current = self.root
        for char in prefix:
            if char not in current.children:
                return [] 
            current = current.children[char]

        suggestions = []
        self._traverse_suffix(current, prefix, suggestions)
        
        suggestions.sort(key=lambda x: self.frequencies[x], reverse=True)  
        return suggestions[:5] # return top 5

    
    def _traverse_suffix(self, current, prefix, suggestions):
        if current.is_word:
            suggestions.append(prefix)
        for char, node in current.children.items():
            self._traverse_suffix(node, prefix + char, suggestions)