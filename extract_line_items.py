import pickle
import re
from classifier import classify
from lexer import get_lexer

curr_dir = os.path.dirname(__file__)
data_path = os.path.join(curr_dir, 'Receipt data/data')
aldelo_path = os.path.join(data_path, 'Aldelo')
aldelo_test = os.path.join(aldelo_path, 'TEST')

common_word_path = 'common_words.pkl'
fieldnames_array_path = 'fieldnames.pkl'
classifier_path = 'classifier.pkl'

def numeral_start(string):
    numeral_start_pattern = re.compile('^[\d]+ ')
    return numeral_start_pattern.match(string)


our_classifier = pickle.load(open(classifier_path))

receipts = glob.glob(aldelo_test + '/*.txt')
line_items = []
curr_line_item = []

curr_item = ""
curr_item_num = False
curr_item_word = False
curr_item_amt = False

for receipt in receipts:
    classification = classify(our_classifier, receipt)

    if classification:
        receipt_file = open(receipt, 'r')
        lexer = get_lexer()
        lexer.input(receipt_file.read())
        while True:
            tok = lexer.token()
            if not tok:
                break
            
#            print tok.value               
            if tok.type == "NUMBER": 
                if not curr_item:
                    curr_item_num = True

                curr_item += tok.value + " "
                                        
            elif tok.type == "WORD_ITEMS":
                if curr_item_num:
                    curr_item_word = True
                    
                curr_item += tok.value + " "
            elif tok.type == "MONEY_AMOUNT":
                if curr_item_word:
                    curr_item_amt = True

                curr_item += tok.value + " "                    
            elif tok.type == "NEWLINE":                
                if curr_item_amt:                    
                    if curr_line_item:
                        line_items.append(curr_line_item)
                    
                    curr_line_item = [curr_item]
                    print curr_item
            
                elif curr_line_item and curr_item:
                    curr_line_item.append(curr_item)
                    print curr_item
                
                else:
                    if curr_line_item:
                        line_items.append(curr_line_item)
                        curr_line_item = []
                
                curr_item = ""
                
                curr_item_num = False
                curr_item_word = False    
                curr_item_amt = False      