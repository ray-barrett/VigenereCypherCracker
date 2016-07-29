from collections import defaultdict


class FrequencyAnalysis(object):
    """Object for performing Frequency Analysis"""
    __englishCharFreq = {
        'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97, 'N': 6.75,
        'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25, 'L': 4.03, 'C': 2.78,
        'U': 2.76, 'M': 2.41, 'W': 2.36, 'F': 2.23, 'G': 2.02, 'Y': 1.97,
        'P': 1.93, 'B': 1.29, 'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15,
        'Q': 0.10, 'Z': 0.07}

    def __init__(self, language_frequencies=__englishCharFreq):
        super(FrequencyAnalysis, self).__init__()
        # Charasters in the alphabet in descending frequency order
        sorted_freq = sorted(language_frequencies.items(),
                             key=lambda x: x[1], reverse=True)
        # Code assumes that characters are all a single case
        self.sorted_freqs = ''.join([freq[0].upper() for freq in sorted_freq])
        self.alphabet = ''.join(sorted(language_frequencies.keys()))

    def charFrequences(self, message):
        chars = {char: 0 for char in self.alphabet}

        for char in message.upper():
            if char in self.alphabet:
                chars[char] += 1

        return chars

    def charFrequencyOrder(self, message):
        # Step 1
        char_freqs = self.charFrequences(message)

        # Step 2: Find the characters that correspond to a particular frequency
        freq_to_char = defaultdict(list)
        for char in char_freqs:
            freq_to_char[char_freqs[char]].append(char)

        # Step 3: Sort the character arrays by the order they're found in
        #         self.sorted_freqs.Convert to string for easier comparison
        for freq in freq_to_char:
            freq_to_char[freq] = ''.join(sorted(freq_to_char[freq],
                                                key=self.sorted_freqs.find,
                                                reverse=True))

        # Step 4: Convert to list of tuples, sort to have most frequent first
        freq_pairs = sorted(freq_to_char.items(),
                            key=lambda x: x[0],
                            reverse=True)

        # Step 5: Return string with all of the characters in descending
        #         frequency order
        return ''.join([freq_pair[1] for freq_pair in freq_pairs])

    def frequencyMatchScore(self, message):
        freq_order = self.charFrequencyOrder(message)

        # While there are more complex methods of finding the match score,
        # it seems that just checking if the 6 most/least frequent letters in
        # the sorted frequencies match any of the 6 most/least frequent letters
        # in the chosen alphabet then it's a reasonably accurate indication of
        # the match score.
        score = 0
        for char in self.sorted_freqs[:6]:
            if char in freq_order[:6]:
                score += 1

        for char in self.sorted_freqs[-6:]:
            if char in freq_order[-6:]:
                score += 1

        return score


if __name__ == '__main__':
    message = """
        Alan Mathison Turing was a British mathematician, logician, cryptanalyst,
        and computer scientist. He was highly influential in the development of
        computer science, providing a formalisation of the concepts of "algorithm"
        and "computation" with the Turing machine. Turing is widely considered to
        be the father of computer science and artificial intelligence. During World
        War II, Turing worked for the Government Code and Cypher School (GCCS) at
        Bletchley Park, Britain's codebreaking centre. For a time he was head of
        Hut 8, the section responsible for German naval cryptanalysis. He devised
        a number of techniques for breaking German ciphers, including the method
        of the bombe, an electromechanical machine that could find settings for
        the Enigma machine. After the war he worked at the National Physical
        Laboratory, where he created one of the first designs for a stored-program
        computer, the ACE. In 1948 Turing joined Max Newman's Computing Laboratory
        at Manchester University, where he assisted in the development of the
        Manchester computers and became interested in mathematical biology. He
        wrote a paper on the chemical basis of morphogenesis, and predicted
        oscillating chemical reactions such as the Belousov-Zhabotinsky reaction,
        which were first observed in the 1960s. Turing's homosexuality resulted
        in a criminal prosecution in 1952, when homosexual acts were still illegal
        in the United Kingdom. He accepted treatment with female hormones (chemical
        castration) as an alternative to prison. Turing died in 1954, just over two
        weeks before his 42nd birthday, from cyanide poisoning. An inquest
        determined that his death was suicide; his mother and some others believed
        his death was accidental. On 10 September 2009, following an Internet
        campaign, British Prime Minister Gordon Brown made an official public
        apology on behalf of the British government for "the appalling way he was
        treated." As of May 2012 a private member's bill was before the House of
        Lords which would grant Turing a statutory pardon if enacted."""
    print FrequencyAnalysis().charFrequencyOrder(message)
    print FrequencyAnalysis().frequencyMatchScore(message)
