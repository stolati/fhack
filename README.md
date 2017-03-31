# fhack-aug-2016

Uses PLY and Scikit Learn

Data stored in same directory as root of git repository with path structure ...

Receipt Data
  data
    (point of sale systems)
      TEST
      LEARN
        GOOD
        BAD
      (stores)
        receipts

Currently lexes Aldelo receipts with lexer defined in lexer.py.

Run get_words_from_receipt.py to build common words dictionary from all receipts.

Run index.py to create Multinomial Naive Bayes classifier, pickled in our_classifier.pkl.
index.py will also test any files in 'Receipt Data'/data/Aldelo/TEST directory.


