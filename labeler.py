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
LABELS_PATH = os.path.join(BASE_PATH, "labels.dat")
FEATURE_DATA_PATH = os.path.join(BASE_PATH, "{}:{}.dat")
FEATURE_NAME_PATH=os.path.join(BASE_PATH, "feature_names.dat")

def manually_label(receipt, prices):
    prices.sort(key=lambda elt: elt[0].lexpos)

    receipt.seek(0)
    for ii in range(len(prices)):
        token, features = prices[ii]

        sys.stdout.write(receipt.read(token.lexpos - receipt.tell()))
        sys.stdout.write("".join((Fore.GREEN, "[{}]".format(ii), Style.RESET_ALL)))

    sys.stdout.write(receipt.read())

    prompt = "Which price is the subtotal (or 'skip' to skip this receipt)? "
    which = input(prompt)
    while not which.isdigit() and not which == "skip":
        input(prompt)

    return ([], []) if which == "skip" else (prices, [prices.pop(int(which))])


def label(inpath, labels=None):
    ret = ([], [])

    receipt = StringIO(open(inpath).read())
    prices = extract_prices(receipt.getvalue())

    if labels:
        prices = {elt[0].lexpos: elt for elt in prices}

        for lexpos, label in labels.items():
            ret[label].append(prices[lexpos])

    else:
        ret = manually_label(receipt, prices)

    return ret


def label_and_record(inpath, outpath=".", labels=None, force=False):
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
