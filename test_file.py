import os
import io
import glob
import io
from lexer import lexer

curr_dir = os.path.dirname(__file__)

data_path = os.path.join(curr_dir, 'datadump')
aldelo_path = os.path.join(data_path, 'Aldelo')

aldelo_stores = glob.glob(aldelo_path+'/[A-Z]*')

store = aldelo_stores[0]

receipts = glob.glob(store+'/*')
f = io.open(receipts[0], 'r', encoding="utf-8")
for line in f:
    print line
f.close()

f = io.open(receipts[0], 'r', encoding="utf-8")

lexer.input(f.read())