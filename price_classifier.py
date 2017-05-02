from abc import ABCMeta, abstractmethod, abstractproperty
from sklearn.svm import SVC
from tokenizer import tokenize
from lexer import get_lexer
from feature_extraction import extract_features
import json
import pickle

fieldnames_array_path = 'fieldnames.pkl'

class Classifier(object, metaclass=ABCMeta):
    def __init__(self, datadir):
        self.datadir = datadir

    @property
    def classifier(self):
        if not hasattr(self, "_classifier"):
            self._classifier = self.make_classifier()

        return self._classifier

    @abstractmethod
    def make_classifier(self):
        pass

    @abstractmethod
    def learn(self, datadirfeature_order_file_path, *class_files):
        pass

    @abstractmethod
    def classify(self, path):
        pass


class PriceClassifier(Model):
    def make_classifier(self):
        return SVC(kernel="linear")

    def learn(datadir, samples_per_class=None):
        samples_per_class = defaultdict(lambda: -1, samples_per_class or {})

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

if __name__ == "__main__":
    
