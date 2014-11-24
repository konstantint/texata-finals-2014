'''
Texata 2014 Finals Solution.
Several feature extractors for text.

Copyright: Konstantin Tretyakov
License: MIT
'''

import os, warnings, random
import numpy as np
from textblob import TextBlob
from tx.hash import winnowing_hasher

# Load default wordlist
if os.path.exists('data/informative.wordlist.txt'):
    WORDLIST = set([unicode(w, 'utf-8').strip() for w in open('data/informative.wordlist.txt')])
else:
    warnings.warn("Could not load wordlist")


# ----- Some helpers ------ #
def nvl(x):
    return x if x is not None else ''

def compose(f, g):
    "Functional helper for combining feature extractors"
    return lambda x: f(g(x))

# ----- Feature extractors ------ #
class SetOfWords(object):
    '''
    Given a string, converts it to a set of words, which only includes 'interesting' words.
    
    >>> s = SetOfWordsConverter()
    >>> s('hello, my name is John')
    set([u'john'])
    '''

    def __init__(self, wordlist=WORDLIST):
        self.words = wordlist
    def __call__(self, text):
        return set(TextBlob(text).words.lemmatize().lower()).intersection(self.words)


class RandomSummary(object):
    '''
    Extracts a random "summary" from a set of words for a given string
    This summary is suitable for use in fulltext queries for similar items.
    
    >>> wf = SetOfWords()
    >>> sf = RandomSummary()
    >>> random.seed(1)
    >>> sf(wf('linux servers tend to require administrators to configure eth0 interfaces'))
    u'administrator interface linux eth0'
    '''

    def __init__(self, max_words_per_summary=4):
        self.max_words_per_summary = max_words_per_summary
    
    def __call__(self, wordset):
        '''
        Picks random max_words_per_summary from a word set.
        '''
        words = list(wordset)
        if len(words) > self.max_words_per_summary:
            words = random.sample(words, self.max_words_per_summary)
        return (' '.join(words)).replace("'", "")


class SimHash(object):
    '''
    The simhash hashing algorithm for wordsets
    '''
    def __init__(self, feature_count=24):
        self.feature_count = feature_count
    
    def __call__(self, wordset):
        result = np.zeros(self.feature_count)
        for w in wordset:
            h = hash(w)
            for i in xrange(self.feature_count):
                if h & 1:
                    result[i] += 1
                else:
                    result[i] -= 1
                h = h >> 1
        r = 0
        for i in result:
            r = r << 1
            if i > 0:
                r += 1
        return r


class Winnowing(object):
    '''
    Essentially a convenience wrapper around the winnowing_hasher function with some word filtering added.
    '''
    
    def __init__(self, k=3, w=4, wordlist=WORDLIST):
        '''
        Parameters:
          k  - text will be processed as k-word-grams.
          w  - "window size". That many consecutive k-word-grams will be considered as a
               single winnowing window.
        '''
        self.k = k
        self.w = w
        self.words = wordlist
        
    def __call__(self, text):
        words = TextBlob(text).words.lemmatize().lower()
        # Filter away words shorter than 3 symbols
        words = filter(lambda x: len(x) >= 3 and x in self.words, words)
        
        # Compute fingerprints
        fps, wfps = winnowing_hasher(words, self.k, self.w)
        return wfps


class FeatureVector(object):
    '''
    Converts a dict(word->count) to a np.array of counts for given words.
    '''
    def __init__(self, features):
        self.features = features
    def __call__(self, worddict):
        return np.array([worddict[w] for w in self.features])    


# ----- Feature extractor singletons with default config ------ #

SET_OF_WORDS = SetOfWords()
RANDOM_SUMMARY = RandomSummary()
SIMHASH = SimHash()
WINNOWING = Winnowing()
