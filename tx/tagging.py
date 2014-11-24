'''
Texata 2014 Finals Solution.
Automatic tagging algorithm.

Copyright: Konstantin Tretyakov
License: MIT
'''

from collections import Counter
import numpy as np
from sklearn.svm import LinearSVC
from sklearn.metrics import precision_score, recall_score

from tx.features import SetOfWords, FeatureVector, nvl

def find_features(wordsets, y, max_words=150):
    total_word_counts = Counter()
    tag_word_counts = Counter()
    for i, wc in enumerate(wordsets):
        total_word_counts.update(wc)
        if y[i]:
            tag_word_counts.update(wc)

    zscores = dict()
    n = sum(y)
    for w in tag_word_counts:
        p = float(total_word_counts[w])/len(y)
        zscores[w] = abs((tag_word_counts[w] - n*p)/np.sqrt(n*p*(1-p)))
    word_ranking = sorted([(-v, k) for k, v in zscores.iteritems()])
    features = [w for v, w in word_ranking if v < -6]
    if len(features) > max_words:
        features = features[0:max_words]
    features.sort()
    return features


class TaggingModel(object):
    '''
    An algorithm for tagging texts.
    Texts should be provided as a dictionary (word -> count).
    '''
    def __init__(self, tag_name, features):
        self.tag_name = tag_name
        self.fe = FeatureVector(features)
        self.clf = LinearSVC()
    
    def fit(self, X, y):
        '''X must be a matrix (i.e. with features already extracted)'''
        self.clf.fit(X, y)
    
    def predict_worddict(self, wd):
        '''Returns tag_name or None for a given worddict'''
        X = self.fe(wd)
        lbl = self.clf.predict(X)
        return self.tag_name if lbl else None


def train_tag_model(posts, tag_name):
    '''Helper function: Trains a TaggingModel and returns (model, accuracy, precision, recall)'''
    # Create X and y for the SVM:
    fe = lambda p: Counter(SET_OF_WORDS(p.all_text))
    X_wd = map(fe, posts)
    y = [tag_name in nvl(p.tags) for p in posts]
    
    # Find the informative words in X_wd
    features = find_features(X_wd, y)
    if len(features) == 0:
        return (None, 0, 0, 0)
    
    # Finally, make a matrix and train the model
    fv = FeatureVector(features)
    X = map(fv, X_wd)
    tm = TaggingModel(tag_name, features)
    tm.fit(X, y)
    y_hat = tm.clf.predict(X)
    return tm, tm.clf.score(X, y), precision_score(y, y_hat), recall_score(y, y_hat)
    