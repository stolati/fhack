#!/usr/bin/python3

import json
import os
import sys
from glob import glob
from io import StringIO

from colorama import Fore, Style

from feature_extraction import extract_prices
from util import mkdir_p

BASE_PATH = "LABELED"
CLASSES = [
   "unknown",
   "subtotal",
]

class DataSet(object):
    LABELS_FILE = "labels.dat"
    FEATURE_DATA_FILE = "{}-{}.dat"
    FEATURE_NAME_FILE = "feature_names.dat"

    def __init__(self, base_path, classes):
        self.base_path = base_path
        self.classes = classes

    @property
    def labels_path(self):
        return os.path.join(self.base_path, self.LABELS_FILE)

    @property
    def feature_names_path(self):
        return os.path.join(self.base_path, self.FEATURE_NAME_FILE)


class DataSet(object):

    def label(self, inpath):
        receipt = Receipt(inpath)

        prices = list(receipt.prices)

        with receipt.open() as receipt_f:
            for ii in range(len(receipt.prices)):
                token = prices[ii]

                sys.stdout.write(receipt_f.read(token.position - receipt_f.tell()))
                sys.stdout.write("".join((Fore.GREEN, "[{}]".format(ii), Style.RESET_ALL)))

            sys.stdout.write(receipt_f.read())

        prompt = "Which price is the subtotal (or 'skip' to skip this receipt)? "
        which = input(prompt)
        while not which.isdigit() and not which == "skip":
            input(prompt)

        return ([], []) if which == "skip" else (prices, [prices.pop(int(which))])

    @classmethod
    def label(cls, inpath, labels=None):
        ret = tuple([] for c in self.classes)

        receipt = StringIO(open(inpath).read())
        prices = extract_prices(receipt.getvalue())

        if labels:
            prices = {elt[0].lexpos: elt for elt in prices}

            for lexpos, label in labels.items():
                try:
                    ret[label].append(prices[lexpos])
                except KeyError:
                    ret[label].append(prices[lexpos-1])

        else:
            ret = cls.manually_label(receipt, prices)

        return ret


    def label_and_record(self, inpath, outpath=".", labels=None, force=False):
        processed = os.path.join(os.path.dirname(inpath), ".{}.processed".format(os.path.basename(inpath)))

        if os.path.exists(processed) and not force:
            return

        mkdir_p(os.path.join(outpath, BASE_PATH))

        classes = label(inpath, labels=labels)

        store_labels = labels is None
        labels = labels or []

        with open(os.path.join(outpath, FEATURE_NAME_PATH), "a+") as feature_file, \
                open(os.path.join(outpath, LABELS_PATH), "a") as labels_file:
            feature_file.seek(0)
            feature_names = set(feature_file.read().split())

            for idx, name in enumerate(CLASSES):
                with open(os.path.join(outpath, FEATURE_DATA_PATH.format(idx, name)), "a") as outfile:
                    for token, features in classes[idx]:
                        json.dump(features, outfile)
                        print(file=outfile)

                        feature_names.update(features.keys())

                        if store_labels:
                            labels.append((token.lexpos, idx))

            feature_file.seek(0)
            feature_file.truncate()
            feature_file.write("\n".join(sorted(feature_names)))

            if store_labels:
                json.dump((inpath, labels), labels_file)
                print(file=labels_file)

        open(processed, "w").close()


    def regenerate_features(inpath, outpath="."):
        with open(os.path.join(inpath, LABELS_PATH)) as labels_file:
            for line in labels_file:
                receipt_path, labels = json.loads(line)

                label_and_record(receipt_path, outpath, labels=dict(labels), force=True)


    if __name__ == "__main__":
        if len(sys.argv) < 2:
            print("Must specify one or more receipts/directories!")
            sys.exit(1)

        if os.path.basename(sys.argv[0]) == "regenerate":
            regenerate_features(*sys.argv[1:3])

        else:
            for path in sys.argv[1:]:
                if os.path.isdir(path):
                    for receipt in glob("{}/*.receipt".format(path)):
                        print("Processing {}...".format(receipt))
                        label_and_record(receipt)

                else:
                    print("Processing {}...".format(path))
                    label_and_record(path)
