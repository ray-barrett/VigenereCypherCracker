from frequencyAnalysis import FrequencyAnalysis
from vigenereCipher import VigenereCipher
from detectEnglish import DetectEnglish
from collections import defaultdict

import itertools
import re


class VigenereCipherCracker(object):
    """docstring for VigenereCipherCracker"""

    __alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    # The maximum number of the most frequent letters to
    __MAX_FREQ_LETTERS = 3
    __MAX_KEY_LENGTH = 6

    def __init__(self, alphabet=__alphabet, max_key_len=__MAX_KEY_LENGTH):
        super(VigenereCipherCracker, self).__init__()
        self.alphabet = alphabet.upper()
        # self.nonletter_regex = re.compile('[^%s]' % self.alphabet)
        self.nonletter_regex = re.compile('[^A-Z]')
        self.max_key_len = max_key_len

    def getRepeatedSubstringDistances(self, message):
        message = self.nonletter_regex.sub('', message.upper())
        msg_len = len(message)

        # Compile a list of seqLen-letter sequences found in the message.
        seqSpacings = {}  # keys are sequences, values are list of int spacings
        for seqLen in range(3, 6):
            for seqStart in range(msg_len - seqLen):
                # Determine what the sequence is, and store it in seq
                seq = message[seqStart:seqStart + seqLen]

                # Look for this sequence in the rest of the message
                for i in range(seqStart + seqLen, msg_len - seqLen):
                    if message[i:i + seqLen] == seq:
                        # Found a repeated sequence.
                        if seq not in seqSpacings:
                            seqSpacings[seq] = []  # initialize blank list

                        # Append the spacing distance between the repeated
                        # sequence and the original sequence.
                        seqSpacings[seq].append(i - seqStart)
        return seqSpacings

    def getUsefulFactors(self, n):
        if n < 2:
            return []

        all_facs = set(reduce(list.__add__,
                              ([i, n // i] for i in range(1, int(n ** 0.5) + 1)
                               if n % i == 0)))
        return [fac for fac in all_facs if fac > 2]

    def getMostCommonFactors(self, seq_factors):
        factor_count = defaultdict(int)
        for seq in seq_factors:
            for factor in seq_factors[seq]:
                factor_count[factor] += 1

        #  {factor: frequency}
        return dict(factor_count)

    def getKeyLens(self, dists):
        dist_factors = defaultdict(list)

        for seq in dists:
            for dist in dists[seq]:
                dist_factors[seq].extend(self.getUsefulFactors(dist))

        most_common = self.getMostCommonFactors(dist_factors)

        return sorted(most_common.items(), key=lambda x: x[1], reverse=True)

    def getCharacterLists(self, factor, message):
        message = self.nonletter_regex.sub('', message.upper())
        # If the factor is 4 and the string is 'this is a test string':
        # Remove the non alphabet characters:
        # - string becomes 'thisisateststring'
        # the lists are
        # 0 - ['t', 'i' ,'e', 't', 'g']
        # 1 - ['h', 's' ,'s', 'r']
        # 2 - ['i', 'a' ,'t', 'i']
        # 3 - ['s', 't' ,'s', 'n']
        char_lists = {}
        for i in xrange(factor):
            nth_letters = []
            for n in xrange(len(message)):
                if (n - i) % factor == 0:
                    nth_letters.append(message[n])
            char_lists[i] = nth_letters

        return char_lists

    def freqAnalysis(self, char_lists):
        scores = defaultdict(list)
        for i in char_lists:
            for char in self.alphabet:
                decrypted_msg = VigenereCipher().decrypt(char, char_lists[i])
                scores[i].append((
                    char,
                    FrequencyAnalysis().frequencyMatchScore(decrypted_msg)))
            # Sort and take only the 4 with the highest score
            scores[i] = sorted(scores[i],
                               key=lambda x: x[1],
                               reverse=True)[:self.__MAX_FREQ_LETTERS]
        return scores

    # def generatePassword(self, letters):
    #     for

    def decode_cipher(self, message):
        # Step 1: Find recurring sequences >= len three chars and their
        #         distances
        # Set(int) - Distances between substring occurrences
        seq_distances = self.getRepeatedSubstringDistances(message)

        # Step 2: Find factors
        # The factors that appear the most are the most likely candidates
        # for password length
        # [int] - Most likely lengths
        likely_key_lens = self.getKeyLens(seq_distances)

        # Step 3:For each chosen factor:
        for key_length, _ in likely_key_lens:
            if key_length > self.max_key_len:
                continue
            # Step 3.1: get the list of characters every character in range 0-
            #           factor
            char_lists = self.getCharacterLists(key_length, message)
            # print char_lists

            # Step 3.2: Frequency analysis!!!
            # For each list of characters we need to analyse for each character
            # in our alphabet. Using the frequency analysis we check to see
            # which character most closely resembles the 'real world' frequency
            # Using this method we'll find the most likely candidates for each
            # index of the password.
            likely_letters = self.freqAnalysis(char_lists)

            for i in likely_letters:
                print "Possible letters for letter %d of the key: " % (i + 1),
                for score in likely_letters[i]:
                    print'%s' % score[0],
                print

            # Step 3.3: Brute Force (Somewhat intelligent due to previous
            #           steps)
            # Step 3.3.1: Generate password strings
            # Example:
            #     Password has length (factor) of 4
            #     Possible letters (based upon analysis) are:
            #     0 - ['c','x', 'y']
            #     1 - ['a','k']
            #     2 - ['j']
            #     3 - ['f', 'm']
            #     There are 12 (3 * 2 * 1 * 2) different passwords that it can
            #     be (assuming we've done everything right). Much better than
            #     the 456976 (26 * 26 * 26 * 26) that a regular brute force
            #     attack would try.
            for indexes in itertools.product(range(self.__MAX_FREQ_LETTERS),
                                             repeat=key_length):
                # print indexes
                possible_key = ''
                for i in xrange(key_length):
                    possible_key += likely_letters[i][indexes[i]][0]
                # print 'Attempting with key: %s' % possible_key

                # Step 3.3.2: Decode string using password. Check to see if is
                # readable English. Return message if it is.
                decrypted_msg = VigenereCipher().decrypt(possible_key, message)
                if DetectEnglish().isEnglish(decrypted_msg, wordPercentage=60):
                    print possible_key
                    return decrypted_msg

        return None


def main():
    cipher_string = """
        Adiz Avtzqeci Tmzubb wsa m Pmilqev halpqavtakuoi, lgouqdaf,
        kdmktsvmztsl, izr xoexghzr kkusitaaf. Vz wsa twbhdg ubalmmzhdad
        qz hce vmhsgohuqbo ox kaakulmd gxiwvos, krgdurdny i rcmmstugvtawz
        ca tzm ocicwxfg jf "stscmilpy" oid "uwydptsbuci" wabt hce Lcdwig
        eiovdnw. Bgfdny qe kddwtk qjnkqpsmev ba pz tzm roohwz at xoexghzr
        kkusicw izr vrlqrwxist uboedtuuznum. Pimifo Icmlv Emf DI, Lcdwig owdyzd
        xwd hce Ywhsmnemzh Xovm mby Cqxtsm Supacg (GUKE) oo Bdmfqclwg Bomk,
        Tzuhvif'a ocyetzqofifo ositjm. Rcm a lqys ce oie vzav wr Vpt 8, lpq
        gzclqab mekxabnittq tjr Ymdavn fihog cjgbhvnstkgds. Zm psqikmp o iuejqf
        jf lmoviiicqg aoj jdsvkavs Uzreiz qdpzmdg, dnutgrdny bts helpar jf lpq
        pjmtm, mb zlwkffjmwktoiiuix avczqzs ohsb ocplv nuby swbfwigk naf ohw
        Mzwbms umqcifm. Mtoej bts raj pq kjrcmp oo tzm Zooigvmz Khqauqvl
        Dincmalwdm, rhwzq vz cjmmhzd gvq ca tzm rwmsl lqgdgfa rcm a kbafzd-
        hzaumae kaakulmd, hce SKQ. Wi 1948 Tmzubb jgqzsy Msf Zsrmsv'e Qjmhcfwig
        Dincmalwdm vt Eizqcekbqf Pnadqfnilg, ivzrw pq onsaafsy if bts
        yenmxckmwvf ca tzm Yoiczmehzr uwydptwze oid tmoohe avfsmekbqr dn
        eifvzmsbuqvl tqazjgq. Pq kmolm m dvpwz ab ohw ktshiuix pvsaa at
        hojxtcbefmewn, afl bfzdakfsy okkuzgalqzu xhwuuqvl jmmqoigve gpcz ie hce
        Tmxcpsgd-Lvvbgbubnkq zqoxtawz, kciup isme xqdgo otaqfqev qz hce 1960k.
        Bgfdny'a tchokmjivlabk fzsmtfsy if i ofdmavmz krgaqqptawz wi 1952, wzmz
        vjmgaqlpad iohn wwzq goidt uzgeyix wi tzm Gbdtwl Wwigvwy. Vz aukqdoev
        bdsvtemzh rilp rshadm tcmmgvqg (xhwuuqvl uiehmalqab) vs sv mzoejvmhdvw
        ba dmikwz. Hpravs rdev qz 1954, xpsl whsm tow iszkk jqtjrw pug 42id
        tqdhcdsg, rfjm ugmbddw xawnofqzu. Vn avcizsl lqhzreqzsy tzif vds vmmhc
        wsa eidcalq; vds ewfvzr svp gjmw wfvzrk jqzdenmp vds vmmhc wsa
        mqxivmzhvl. Gv 10 Esktwunsm 2009, fgtxcrifo mb Dnlmdbzt uiydviyv,
        Nfdtaat Dmiem Ywiikbqf Bojlab Wrgez avdw iz cafakuog pmjxwx ahwxcby gv
        nscadn at ohw Jdwoikp scqejvysit xwd "hce sxboglavs kvy zm ion
        tjmmhzd." Sa at Haq 2012 i bfdvsbq azmtmd'g widt ion bwnafz tzm Tcpsw
        wr Zjrva ivdcz eaigd yzmbo Tmzubb a kbmhptgzk dvrvwz wa efiohzd.
    """

    decoded_cipher = VigenereCipherCracker().decode_cipher(cipher_string)

    if decoded_cipher is not None:
        print "Decoded Message:"
        print decoded_cipher
    else:
        print "Failed to Decode Message"


if __name__ == '__main__':
    main()
