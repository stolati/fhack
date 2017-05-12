#!/usr/bin/python3

from __future__ import absolute_import, print_function, division, unicode_literals

import os
import sys
from glob import glob

from dataset import PriceDataSet, ReceiptDataSet
from question import SkipInput
from receipt import Receipt
from util import mkdir_p

def label_for_datasets(path, datasets, force=False):
    processed = os.path.join(os.path.dirname(path), ".{}.processed".format(os.path.basename(path)))

    if os.path.exists(processed) and not force:
        return

    receipt = Receipt(path)

    try:
        for dataset in datasets:
            # Stop processing if an earlier labeler requests it
            if not dataset.ingest(receipt):
                break

    except SkipInput:
        print("Skipping!")

    # touch the touchfile
    open(processed, "w").close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Must specify one or more receipts/directories!")
        sys.exit(1)

    datasets = [ReceiptDataSet(sys.argv[1]), PriceDataSet(sys.argv[1])]

    if os.path.basename(sys.argv[0]) == "regenerate":
        for dataset in datasets:
            dataset.regenerate_features()

    else:
        for path in sys.argv[2:]:
            if os.path.isdir(path):
                for receipt_path in glob("{}/*.receipt".format(path)):
                    print("Processing {}...".format(receipt_path))
                    label_for_datasets(receipt_path, datasets)

            else:
                print("Processing {}...".format(path))
                label_for_datasets(path, datasets)
