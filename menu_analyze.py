__author__ = 'Sierra'

from nltk import *
from nltk.corpus.reader import CategorizedPlaintextCorpusReader
import re
import random
from nltk import metrics
from nltk import precision
from nltk import recall
import collections

# Create corpus reader from categorized corpus in current directory
menureader = CategorizedPlaintextCorpusReader('./menus', r'menu.*\.txt', cat_file='../cats.txt')

# Sort specific categories into more broad general categories for higher accuracy
general_cats = {'Asian':['Asian','Chinese','Cambodian','Filipino','Indian','Japanese','Korean','Malaysian','Sushi','Thai','Vietnamese','Indonesian','Pacific-Rim','Burmese','Sri-Lankan'],
                'American':['American', 'Bar', 'Barbecue', 'Brew-Pub','Contemporary','Delicatessen', 'Diner','Fast-Food','Fusion', 'Gastropub','Pub','Seafood', 'Soups','Steakhouse','Grill','Cafe','Southwestern','International'],
                # 'Special-Diet':['Gluten-Free','Kosher','Vegan', 'Vegetarian','Healthy'],
                'French':['French', 'Wine-Bar'],
                'Latin':['Latin','Argentinean','Brazilian','Central-American','Colombian', 'Cuban','Mexican','Peruvian','Portuguese','South-American','Spanish','Venezuelan'],
                'Caribbean':['Caribbean','Jamaican'],
                'Mediterranean':['Mediterranean','Greek','Armenian'],
                'Middle-Eastern':['Middle-Eastern','Lebanese','Israeli','Afghani', 'Pakistani','Persian'],
                # 'British':['British', 'Irish','Scottish'],
                # 'German':['German','Belgian','Austrian'],
                # 'Australian':['Australian'],
                'Italian':['Italian', 'Pizza'],
                # 'European':['European','Eastern-European','Central-European','Hungarian','Polish','Russian', 'Scandinavian','Czech','Swedish', 'Swiss',  'Turkish', 'Ukrainian','Yugoslavian']
                }

# Given a value (specific cuisine), return the key (general cuisine)
def keybyvalue(dct, value):
    for k in dct:
        if value in dct[k]:
            return k
        else:
            if value == dct[k]:
                return k

# Build a list of tuples of (menu words, general category) for use in feature sets
menus = [(list(menureader.words(fileid)), keybyvalue(general_cats, category))
         for category in menureader.categories()
         if category in general_cats.keys()
         for fileid in menureader.fileids(category)]
# Shuffle the list for varied results
random.shuffle(menus)

# Set all words to lowercase and get frequency distribution only of alphabet characters, to ignore prices and other irrelevant text
all_words = FreqDist(w.lower() for w in menureader.words() if re.match(r'[A-Z,a-z]+',w))
most_common = all_words.most_common(2000)
# Use the 5000 most common words in the corpus for highest relevance
word_features = [t[0] for t in most_common]


def document_features(document):
    # Create a set of the words in each document to avoid processing duplicates
    document_words = set(document)
    features = {}
    # Build a dictionary to identify all the words contained in a document
    for word in word_features:
        features['contains({})'.format(word)] = (word in document_words)
    return features

# Feature set is a list of tuples of (document feature dictionary, category) for all menus
featuresets = [(document_features(d), c) for (d,c) in menus]
size = int(.1*len(featuresets))
# Train on the first 90%, test on the last 10%
train_set, test_set = featuresets[size:], featuresets[:size]
# Initialize Naive Bayes classifier
classifier = NaiveBayesClassifier.train(train_set)
# Show most informative features and accuracy of classifier
print(classifier.show_most_informative_features(20))
print("Accuracy: ", classify.accuracy(classifier, test_set))

classifier = NaiveBayesClassifier.train(train_set)
refsets = collections.defaultdict(set)
testsets = collections.defaultdict(set)

for i, (feats, label) in enumerate(test_set):
    refsets[label].add(i)
    observed = classifier.classify(feats)
    testsets[observed].add(i)

print ('%-15s %-15s %-15s' %('Cuisine:', 'Precision:', 'Recall:'))
for k in general_cats.keys():
    p = precision(refsets[k],testsets[k])
    if p is not None:
        p = str(round(precision(refsets[k],testsets[k]),4))
    r = recall(refsets[k],testsets[k])
    if r is not None:
        r = str(round(recall(refsets[k],testsets[k]),4))
    print ('%-15s %-15s %-15s' %(k, p, r))
