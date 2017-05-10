from __future__ import absolute_import, print_function, division, unicode_literals

import json
import os
import sys
from abc import ABCMeta, abstractmethod
from glob import glob
from io import StringIO

from boto.mturk.connection import MTurkConnection
from six import add_metaclass, text_type
from six.moves import input

from question import MultipleChoiceQuestion
from receipt import Receipt
from util import mkdir_p

@add_metaclass(ABCMeta)
class DataSet(object):
    LABELS_FILE = "labels.dat"
    FEATURE_DATA_FILE = "{}-{}.dat"
    FEATURE_NAME_FILE = "feature_names.dat"

    def __init__(self, name, base_path, class_names):
        self.name = name
        self.base_path = os.path.join(base_path, self.name)
        self.class_names = class_names

    @property
    def labels_path(self):
        return os.path.join(self.base_path, self.LABELS_FILE)

    @property
    def feature_names_path(self):
        return os.path.join(self.base_path, self.FEATURE_NAME_FILE)

    def feature_data_path(self, classno, name):
        return os.path.join(self.base_path,
                            self.FEATURE_DATA_FILE.format(classno, name))

    @abstractmethod
    def prompt_for_labels(self, receipt):
        pass

    def get_labeled_tokens(self, receipt, highlighted_tokens, labels):
        ret = tuple([] for c in self.class_names)

        by_position = {elt._position: elt for elt in highlighted_tokens}

        for position, label in labels.items():
            try:
                ret[label].append(by_position[position])
            except KeyError:
                ret[label].append(by_position[position-1])

        return ret

    def prompt(self, receipt, questions, highlighted_tokens=None):
        receipt.format(sys.stdout, highlighted_tokens)

        for question in questions:
            while True:
                try:
                    answer = question.answer(input(question.format()).strip())
                except ValueError as e:
                    print(text_type(e))
                else:
                    yield answer
                    break

class PriceDataSet(DataSet):
    CLASS_NAMES = [
       "unknown",
       "subtotal",
       "total",
    ]

    def __init__(self, base_path):
        super(PriceDataSet, self).__init__("prices", base_path, self.CLASS_NAMES)

    def get_questions(self, receipt):
        return [
            MultipleChoiceQuestion(
                "Which price (or prices) is the {}".format(name),
                choices=list(map(text_type, list(range(1, len(receipt.prices) + 1)))))
            for name in self.class_names[1:]
        ] 

    def prompt_for_labels(self, receipt):
        ret = tuple([] for i in self.class_names)

        answers = self.prompt(receipt, self.get_questions(receipt), receipt.prices)
        prices = dict(enumerate(receipt.prices, 1))

        for class_idx, answer in enumerate(answers, 1):
            for which in answer:
                ret[class_idx].append(prices.pop(int(which)))

        ret[0].extend(prices.values())

        return ret

    def extract_features(self, token, receipt):
        features = {}

        receipt_length = len(receipt.text)

        features[token.type] = 1
        features["document_position"] = token._position / receipt_length
        features["order_largest_to_smallest"] = (
                (len(receipt.prices) - token._price_order) / len(receipt.prices))
        
        closest_tokens = 3
        features.update(
                ("closest_before_{}".format(t.type), idx)
                for idx, t in enumerate(
                    receipt.tokens[token._index - closest_tokens:token._index], 1))
        features.update(
                ("closest_after_{}".format(t.type), idx)
                for idx, t in enumerate(reversed(
                        receipt.tokens[token._index + 1:token._index + closest_tokens + 1]), 1))

        return features

    def ingest(self, receipt, labels=None):
        mkdir_p(self.base_path)

        classes = (self.get_labeled_tokens(receipt, receipt.prices, labels)
                if labels
                else self.prompt_for_labels(receipt))

        store_labels = labels is None
        labels = labels or []

        with open(self.feature_names_path, "a+") as feature_file, \
                open(self.labels_path, "a") as labels_file:
            feature_file.seek(0)
            feature_names = set(feature_file.read().split())

            for idx, name in enumerate(self.class_names):
                with open(self.feature_data_path(idx, name), "a") as outfile:
                    for token in classes[idx]:
                        features = self.extract_features(token, receipt)

                        print(json.dumps(features), file=outfile)

                        feature_names.update(features.keys())

                        if store_labels:
                            labels.append((token.lexpos, idx))

            feature_file.seek(0)
            feature_file.truncate()
            feature_file.write("\n".join(sorted(feature_names)))

            if store_labels:
                print(json.dumps((receipt.path, labels)), file=labels_file)

    def regenerate_features(self, inpath, outpath="."):
        os.unlink(self.feature_names_path)
        for idx, name in enumerate(self.class_names):
            os.unlink(self.feature_data_path(idx, name))

        with open(self.labels_path) as labels_file:
            for line in labels_file:
                receipt_path, labels = json.loads(line)

                self.ingest(receipt_path, labels=dict(labels), force=True)
