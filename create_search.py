import pickle
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.analysis import FancyAnalyzer
from whoosh.analysis import StemmingAnalyzer
import os, os.path
import io
import whoosh.index as index
from whoosh import writing
from whoosh.qparser import QueryParser

schema = Schema(title=ID(stored=True),
                body=TEXT(analyzer=StemmingAnalyzer()))

ix = None
if not os.path.exists("indexdir"):
    os.mkdir("indexdir")

ix = index.create_in("indexdir", schema)

writer = ix.writer()

for root, dirs, filenames in os.walk('line_item_pkls'):
    for f in filenames:
        if (f != '.DS_Store'):
            body = ""
            line_items = pickle.load(io.open('line_item_pkls/'+f, 'r', encoding='utf-8'))

            for item in line_items:
                for i in range(int(item["number"])):
                    body += item["main item"].decode('unicode-escape') + " "

            writer.add_document(title=f.decode('unicode-escape'), body=body)

writer.commit()

with ix.searcher() as searcher:
    qp = QueryParser("body", schema=ix.schema)

    print "Hello friends, what would you like to eat today?",
    terms = raw_input()

    q = qp.parse(terms.decode('unicode-escape'))
    results = searcher.search(q)

    print results[0:9]




