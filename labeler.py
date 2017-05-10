#!/usr/bin/python3

import os
import sys

from dataset import PriceDataSet
from receipt import Receipt
from util import mkdir_p

def label_for_datasets(path, datasets, force=False):
    processed = os.path.join(os.path.dirname(inpath), ".{}.processed".format(os.path.basename(inpath)))

    if os.path.exists(processed) and not force:
        return

    receipt = Receipt(path)

    if force or any(d.ingested(path) for d in datasets):
        receipt = Receipt(path)
        receipt.format(sys.stdout)

        for dataset in datasets:
            dataset.ingest(receipt)

    # touch the touchfile
    open(processed, "w").close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Must specify one or more receipts/directories!")
        sys.exit(1)

    datasets = [PriceDataSet(sys.argv[1])]

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
