from lexer import get_lexer
import os
import io
import glob
import operator
import pickle

lexer = get_lexer()

curr_dir = os.path.dirname(__file__)
data_path = os.path.join(curr_dir, 'Receipt data/data')
aldelo_path = os.path.join(data_path, 'Aldelo')
common_words_path = 'common_words.pkl'

dict = {}

aldelo_stores = glob.glob(aldelo_path+'/*')
store_dicts = []
for store in aldelo_stores:
    store_dict = {}
    receipts = glob.glob(store+'/*.txt')
    for receipt in receipts:
        f=io.open(receipt, 'r', encoding='utf-8')

        try:
            lexer.input(f.read())
        except:
            continue

        while True:
            tok = lexer.token()
            if not tok:
                break;

            if tok.type == "WORD_ITEMS" or tok.type == "TOTAL" or tok.type == "SUBTOTAL":
                if tok.value not in dict:
                    dict[tok.value] = 0 
                if tok.value not in store_dict:
                    store_dict[tok.value] = 0
                dict[tok.value] += 1
                store_dict[tok.value] += 1
    store_dicts.append(store_dict)

dict_copy = {}

for k,v in dict.iteritems():  
    if v > 50:
        dict_copy[k] = v
#    if len(k) == 1:
#        continue
#    skip = False
#    stores = 0
#    for store_dict in store_dicts:
#        if k in store_dict:
#            stores += 1
#    if stores > 1:
#        print stores
#        print k
#        dict_copy[k] = v

#sorted_dict = sorted(dict_copy.items(), key=operator.itemgetter(1))
#common_words = {}

pickle.dump(dict_copy, open(common_words_path,'wb'))
#
