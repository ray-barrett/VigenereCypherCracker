import re


class DetectEnglish(object):
    """docstring for DetectEnglish"""
    def __init__(self):
        super(DetectEnglish, self).__init__()
        self.nonletter_regex = re.compile('[^A-Z \t\n]')
        with open('dictionary.txt', 'rb') as dict_file:
            self.dictionary = {word: None for word in dict_file.read().split('\n')}

    def getEnglishWordPercentage(self, message):
        message = self.nonletter_regex.sub('', message.upper())
        words = message.split()

        if not words:
            return 0

        matches = 0
        for word in words:
            if word in self.dictionary:
                matches += 1

        return float(matches) / len(words) * 100

    def isEnglish(self, message, wordPercentage=20, letterPercentage=85):
        words = self.getEnglishWordPercentage(message) >= wordPercentage
        numLetters = len(self.nonletter_regex.sub('', message.upper()))
        percentLetters = float(numLetters) / len(message) * 100
        letters = percentLetters >= letterPercentage

        return words and letters

if __name__ == '__main__':
    DetectEnglish().isEnglish('Hello there my good sir, how are you on this fine day?')
