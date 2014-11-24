'''
Texata 2014 Finals Solution.
Similarity indexing engines for the "related posts" task.

Copyright: Konstantin Tretyakov
License: MIT
'''

# ---------------------------- Fulltext searcher ------------------------------- #
from collections import Counter

class FulltextDBSearcher(object):
    '''
    Implementation of the database-based related post search algorithm.
    The algorithm is probabilistic (i.e. different invocations may produce different results)
    '''
    def __init__(self, feature_extractor, engine, iterations=10):
        self.feature_extractor = feature_extractor
        self.engine = engine
        self.iterations = iterations

    def _find_similar_posts(self, p):
        '''Summarize the post into a query and send it to the database, returning a list of ids and scores.'''
        query = """select 
                       id, 
                       ts_rank(to_tsvector('english', coalesce(title,'') || ' ' || coalesce(body,'')), plainto_tsquery('%(q)s')) as score 
                   from post
                   where 
                   to_tsvector('english', coalesce(title,'') || ' ' || coalesce(body,'')) @@ plainto_tsquery('%(q)s')
                   and id <> %(id)s
                   and title is not null
                   order by score desc
                   limit 5;
                """
        summary = self.feature_extractor(p.all_text)
        results = self.engine.execute(query % {'q': summary, 'id': p.id})
        return list(results)
    
    def __call__(self, p):
        '''The _find_similar_posts algorithm is probabilistic and returns random results each time.
        Here we run it multiple times and aggregate the results.'''
        counter = Counter()
        for i in xrange(self.iterations):
            res = self._find_similar_posts(p)
            counter.update([id for id, score in res])
        return [el for el, cnt in counter.most_common(5)]
    

# ---------------------------- SimHash ------------------------------- #
from collections import defaultdict
import numpy as np
from tx.features import SIMHASH, SET_OF_WORDS, compose

class SimHashIndexer(object):
    '''
    Simhashing-based document indexer.
    '''
    def __init__(self, hasher=compose(SIMHASH, SET_OF_WORDS), feature_count=24):
        self.ix = defaultdict(list)
        self.hasher = hasher
        self.feature_count = feature_count
    
    def add(self, text, obj):
        self.add_hash(self.hasher(text), obj)
    
    def add_hash(self, h, obj):
        self.ix[h].append(obj)
    
    def find(self, text):
        return self.find_hash(self.hasher(text))
    
    def find_hash(self, h):
        # Search in radius 2 of given hash
        candidates = list(self.ix[h])
        for i in range(self.feature_count):
            h_i = h ^ (1 << i)
            candidates.extend(self.ix[h_i])
            for j in range(i+1, self.feature_count):
                h_ij = h_i ^ (1 << j)
                candidates.extend(self.ix[h_ij])
        return candidates


# ---------------------------- TextWinnowing ------------------------------- #
from collections import defaultdict
from textblob import TextBlob
from tx.features import WINNOWING

class TextWinnowingIndexer(object):
    '''
    Text winnowing-based indexing and retrieval.
    '''

    def __init__(self, hasher=WINNOWING):
        self.hasher = hasher
        self.ix = defaultdict(set)
        
    def add(self, text, obj):
        self.add_hash(self.hasher(text), obj)
    
    def add_hash(self, h, obj):
        for fp in h:
            self.ix[fp].add(obj)
    
    def find(self, text):
        return self.find_hash(self.hasher(text))
    
    def find_hash(self, h):
        results = set()
        for fp in h:
            results.update(self.ix[fp])
        return results