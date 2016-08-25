from __future__ import division
from math import log, exp
from operator import mul
from collections import Counter
import os
import pickle
import detectlanguage
from config import API_KEY
from textblob import TextBlob
import langid
import logging
import json
from pos import pos
from neg import neg
from pos2 import pos2
from neg2 import neg2


detectlanguage.configuration.api_key = API_KEY

class MyDict(dict):
    def __getitem__(self, key):
        if key in self:
            return self.get(key)
        return 0


features = set()
totals = [3321176, 3320100]
totals2 = [3321176, 3320100]
delchars = ''.join(c for c in map(chr, range(128)) if not c.isalnum())

# CDATA_FILE = "countdata.pickle"
FDATA_FILE = "reduceddata.pickle"
FDATA_FILE2 = "reduceddata2.pickle"  # for browser data analysis


def negate_sequence(text):
    """
    Detects negations and transforms negated words into "not_" form.
    """
    negation = False
    delims = "?.,!:;"
    result = []
    words = text.split()
    prev = None
    pprev = None
    for word in words:
        # stripped = word.strip(delchars)
        stripped = word.strip(delims).lower()
        negated = "not_" + stripped if negation else stripped
        result.append(negated)
        if prev:
            bigram = prev + " " + negated
            result.append(bigram)
            if pprev:
                trigram = pprev + " " + bigram
                result.append(trigram)
            pprev = prev
        prev = negated

        if any(neg in word for neg in ["not", "n't", "no"]):
            negation = not negation

        if any(c in word for c in delims):
            negation = False

    return result

def classify2(text):
    """
    For classification from pretrained data
    """
    words = set(word for word in negate_sequence(text) if word in pos or word in neg)
    if (len(words) == 0): return True, 0
    # Probability that word occurs in pos documents
    # for word in words:
    #     print "p: ", word, ": ", pos[word]
    #     print "n: ", word, ": ", neg[word]
    # print words
    pos_prob = sum(log((pos[word] + 1) / (2 * totals[0])) for word in words)
    neg_prob = sum(log((neg[word] + 1) / (2 * totals[1])) for word in words)
    return (pos_prob > neg_prob, abs(pos_prob - neg_prob))


def classify3(text):
    """
    For classification from pretrained data
    """
    words = set(word for word in negate_sequence(text) if word in pos2 or word in neg2)
    logging.debug(' words len = ' + str(len(words)))
    if (len(words) == 0): return True, 0
    # Probability that word occurs in pos documents
    pos_prob = sum(log((pos2[word] + 1) / (2 * totals[0])) for word in words)
    neg_prob = sum(log((neg2[word] + 1) / (2 * totals[1])) for word in words)
    return (pos_prob > neg_prob, abs(pos_prob - neg_prob))

def classify_demo(text):
    words = set(word for word in negate_sequence(text) if word in pos or word in neg)
    if (len(words) == 0): 
        print "No features to compare on"
        return True

    pprob, nprob = 0, 0
    for word in words:
        pp = log((pos[word] + 1) / (2 * totals[0]))
        np = log((neg[word] + 1) / (2 * totals[1]))
        print "%15s %.9f %.9f" % (word, exp(pp), exp(np))
        pprob += pp
        nprob += np

    print ("Positive" if pprob > nprob else "Negative"), "log-diff = %.9f" % abs(pprob - nprob)

def feature_selection_trials():
    """
    Select top k features. Vary k and plot data
    """
    # global pos, neg, totals, features
    # global pos2, neg2, totals2
    # retrain = False
    #
    # if not retrain and os.path.isfile(FDATA_FILE):
    #     pos, neg, totals = pickle.load(open(FDATA_FILE))
    #     pos2, neg2, totals2 = pickle.load(open(FDATA_FILE2))
    return

def lang_detect_level1(lang, gs):
    lang_id = TextBlob(lang).detect_language()  # lang_id = en
    if lang_id == 'hi':
        lang_id = 'rd'
    return {'language_id': lang_id, 'language': gs.get_languages()[lang_id]}

def lang_detect_level2(lang, gs):
    lang_id = detectlanguage.detect(lang)
    # e.g [{'isReliable': True, 'confidence': 12.04, 'language': 'es'}]
    if lang_id[0]['language'] == 'hi':
        lang_id[0]['language'] = 'rd'
    return {'language_id': lang_id[0]['language'], 'language': gs.get_languages()[lang_id[0]['language']]}

def lang_detect_level3(lang, gs):
    # langid service, source code = https://github.com/saffsd/langid.py
    res = langid.classify(lang)
    if res[0] == 'hi':
        res[0] = 'rd'
    return {'language_id': res[0], 'language': gs.get_languages()[res[0]]}

if __name__ == '__main__':
    feature_selection_trials()

def setup():
    feature_selection_trials()
