from sklearn.svm import SVC
from tokenizer import tokenize
from lexer import get_lexer
from feature_extraction import extract_features
import json
import pickle

fieldnames_array_path = 'fieldnames.pkl'

def learn(feature_order_file_path, *class_files, n_samples):
    training_set = []
    labels = []

    feature_order = open(feature_order_file_path).read().split()

    for idx, class_file in enumerate(class_files):
        with open(class_file) as labeled:
            training_set.extend(
                    [item.get(feature, 0) for feature in feature_order]
                    for item in map(json.loads, labeled))

            labels.extend([idx] * (len(training_set) - len(labels)))
            
    classifier = SVC(kernel="linear").fit(training_set, labels)
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
