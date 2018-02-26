#!/usr/bin/env python
#
# Copyright (c) 2013 Pavol Rusnak
# Copyright (c) 2017 mruddy
# Copyright (c) 2018 bill-walker
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

# To the author of the pull request that I am expecting: sorry for not waiting.

import binascii
import bisect
import hashlib
import hmac
import itertools
import os
import sys
import unicodedata


class ConfigurationError(Exception):
    pass


# From <http://tinyurl.com/p54ocsk>
def binary_search(a, x, lo=0, hi=None):                # can't use a to specify default for hi
    hi = hi if hi is not None else len(a)              # hi defaults to len(a)
    pos = bisect.bisect_left(a, x, lo, hi)             # find insertion position
    return (pos if pos != hi and a[pos] == x else -1)  # don't walk off the end


class Mnemonic(object):
    def __init__(self, language):
        self.radix = 257
        with open('%s/%s-adjectives.txt' % (self._get_directory(), "english"), 'r') as f:
            self.wordlistAdjectives = [w.strip().decode('utf8') if sys.version < '3' else w.strip() for w in f.readlines()]
        if len(self.wordlistAdjectives) != self.radix:
            raise ConfigurationError('Wordlist should contain %d words, but it contains %d words.' % (self.radix, len(self.wordlistAdjectives)))
        self.radix = 257
        with open('%s/%s-animals.txt' % (self._get_directory(), "english"), 'r') as f:
            self.wordlistAnimals = [w.strip().decode('utf8') if sys.version < '3' else w.strip() for w in f.readlines()]
        if len(self.wordlistAnimals) != self.radix:
            raise ConfigurationError('Wordlist should contain %d words, but it contains %d words.' % (self.radix, len(self.wordlistAnimals)))

    @classmethod
    def _get_directory(cls):
        return os.path.join(os.path.dirname(__file__), 'wordlists')

    @classmethod
    def normalize_string(cls, txt):
        if isinstance(txt, str if sys.version < '3' else bytes):
            utxt = txt.decode('utf8')
        elif isinstance(txt, unicode if sys.version < '3' else str):
            utxt = txt
        else:
            raise TypeError("String value expected")

        return unicodedata.normalize('NFKD', utxt)

    # Adapted from <http://tinyurl.com/oxmn476>
    def to_entropy(self, words):
        if not isinstance(words, list):
            words = words.split(' ')
        if len(words) not in [18, 21, 24, 27, 30, 33]:
            raise ValueError('Number of words must be one of the following: [18, 21, 24, 27, 30, 33], but it is not (%d).' % len(words))
            print ("incorrect number of words")
        # Look up all the words in the list and construct the
        # concatenation of the original entropy and the checksum.
        concatLenBits = len(words) * 8
        paddingLengthBits = 0
        concatBits = [False] * concatLenBits
        wordindex = 0
        use_binary_search = False
        for word in words:
            # Find the words index in the wordlist
            if (wordindex + 1) % 3 == 0:
                ndx = binary_search(self.wordlistAnimals, word) if use_binary_search else self.wordlistAnimals.index(word)
            else:
                ndx = binary_search(self.wordlistAdjectives, word) if use_binary_search else self.wordlistAdjectives.index(word)
            if ndx < 0:
                raise LookupError('Unable to find "%s" in word list.' % word)
            if ndx == 256:
                paddingLengthBits += 8
            # Set the next 8 bits to the value of the index.
            for ii in range(8):
                if ndx < 256:
                    concatBits[(wordindex * 8) + ii] = (ndx & (1 << (7 - ii))) != 0
            wordindex += 1
        checksumLengthBits = 16
        entropyLengthBits = concatLenBits - checksumLengthBits - paddingLengthBits
        # Extract original entropy as bytes.
        entropy = bytearray(entropyLengthBits // 8)
        for ii in range(len(entropy)):
            for jj in range(8):
                if concatBits[(ii * 8) + jj]:
                    entropy[ii] |= 1 << (7 - jj)
        # Take the digest of the entropy.
        hashBytes = hashlib.sha256(entropy).digest()
        if sys.version < '3':
            hashBits = list(itertools.chain.from_iterable(([ord(c) & (1 << (7 - i)) != 0 for i in range(8)] for c in hashBytes)))
        else:
            hashBits = list(itertools.chain.from_iterable(([c & (1 << (7 - i)) != 0 for i in range(8)] for c in hashBytes)))
        # Check all the checksum bits.
        for i in range(checksumLengthBits):
            if concatBits[entropyLengthBits + i] != hashBits[i]:
                raise ValueError('Failed checksum.')
                print ("failed checksum")
        return entropy

    def to_mnemonic(self, data):
        if len(data) not in [16, 20, 24, 28, 32]:
            raise ValueError('Data length should be one of the following: [16, 20, 24, 28, 32], but it is not (%d).' % len(data))
            print ("incorrect number of words")
        h = hashlib.sha256(data).hexdigest()
        b = bin(int(binascii.hexlify(data), 16))[2:].zfill(len(data) * 8) + \
            bin(int(h, 16))[2:].zfill(256)[:16]
        result = []
        for i in range(len(b) // 8):
            idx = int(b[i * 8:(i + 1) * 8], 2)
            if (i + 1) % 3 == 0:
                result.append(self.wordlistAnimals[idx])
            else:
                result.append(self.wordlistAdjectives[idx])
        if (len(b) // 8) % 3 == 1:
            result.append(self.wordlistAdjectives[256])
        if (len(b) // 8) % 3 != 0:
            result.append(self.wordlistAnimals[256])
        result_phrase = ' '.join(result)
        return result_phrase


def main():
    import binascii
    import sys
    if len(sys.argv) > 1:
        print"Do not enter secrets as command line arguments: they are stored in your bash logs. Just run the program and type or paste your words, then hit enter"
    else:
        data = sys.stdin.readline().strip()
        m = Mnemonic('english')
        print""

        if ' ' in data:
            print(binascii.hexlify(m.to_entropy(data)))
            if binascii.hexlify(m.to_entropy(data)) != binascii.hexlify(m.to_entropy(m.to_mnemonic(binascii.unhexlify(binascii.hexlify(m.to_entropy(data)))))):
                print""
                print"Self-test failed, do not use"
        else:
            data = binascii.unhexlify(data)
            print(m.to_mnemonic(data))
            if m.to_mnemonic(data) != m.to_mnemonic(binascii.unhexlify(binascii.hexlify(m.to_entropy(m.to_mnemonic(data))))):
                print""
                print"Self-test failed, do not use"
        print""


if __name__ == '__main__':
    main()
