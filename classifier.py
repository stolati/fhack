from sklearn.naive_bayes import MultinomialNB
from tokenizer import tokenize
from lexer import get_lexer
from feature_extraction import extract_features
import csv
import pickle

fieldnames_array_path = 'fieldnames.pkl'

def learn(feature_set_file_path, labels_file_path):
    training_set = [];
    labels = [];

    feature_set_csv = open(feature_set_file_path)
    feature_set_csv_reader = csv.reader(feature_set_csv)

    for row in feature_set_csv_reader:
        set = []
        for item in row:
            if item == "":
                set.append(0)
            else:
                set.append(int(item))
        training_set.append(set)

    labels_csv = open(labels_file_path)
    labels_csv_reader = csv.reader(labels_csv)

    for row in labels_csv_reader:
        for item in row:
            if len(item):
                labels.append(int(item))

    classifier = MultinomialNB().fit(training_set, labels)
#    classifier = None
    return classifier

def classify(classifier, file_path):
    features = extract_features(file_path)
    fieldnames = pickle.load(open(fieldnames_array_path,'r'))
    features_arr = []
    for field in fieldnames:
        if field in features:
            features_arr.append(features[field])
        else:
            features_arr.append(0)
    
    prediction = classifier.predict([features_arr])

    return prediction
