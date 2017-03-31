import os
import io
import glob
import classifier
from feature_extraction import extract_features
from tokenizer import tokenize
import csv
import lexer
import pickle

curr_dir = os.path.dirname(__file__)
data_path = os.path.join(curr_dir, 'Receipt data/data')
aldelo_path = os.path.join(data_path, 'Aldelo')

training_set_path = aldelo_path + '/LEARN/training_features.csv'
labels_path = aldelo_path + '/LEARN/training_labels.csv'

common_word_path = 'common_words.pkl'
fieldnames_array_path = 'fieldnames.pkl'
classifier_path = 'classifier.pkl'


our_classifier = None

def learn_receipts():
    common_words = pickle.load(open(common_word_path, 'r'))

    fieldnames = []
    for key in common_words.keys():
        fieldnames.append(key)
    
    for token in lexer.get_lexer().lextokens_all:
        fieldnames.append(token)
        
    training_csv_file = open(training_set_path, 'w')
    training_csv_writer = csv.DictWriter(training_csv_file, fieldnames=fieldnames)
    labels_csv_file = open(labels_path, 'w')
    labels_csv_writer = csv.writer(labels_csv_file)

    good_folder = glob.glob(aldelo_path+'/LEARN/GOOD')
    bad_folder = glob.glob(aldelo_path+'/LEARN/BAD')

    start_learning(good_folder, 1, training_csv_writer, labels_csv_writer)
    start_learning(bad_folder, 0, training_csv_writer, labels_csv_writer)

    training_csv_file.close()
    labels_csv_file.close()
    
    pickle.dump(fieldnames, open(fieldnames_array_path,'wb'))
    
    

def start_learning(learn_folder, receipt_status, 
                   training_csv_writer, labels_csv_writer):
#    common_words = pickle.load(open(common_word_path, 'r'))
#
#    fieldnames = []
#    for key in common_words.keys():
#        fieldnames.append(key)
#    
#    for token in lexer.lextokens_all:
#        fieldnames.append(token)
#        
#    training_csv_file = open(training_set_path, 'a')
#    training_csv_writer = csv.DictWriter(training_csv_file, fieldnames=fieldnames)
#    labels_csv_file = open(labels_path, 'a')
#    labels_csv_writer = csv.writer(labels_csv_file)
#
#    training_csv_writer.writeheader()

    for store in learn_folder:
        receipts = glob.glob(store+'/*/*.txt')
        for receipt in receipts:
            features = extract_features(receipt)
            training_csv_writer.writerow(features)
            labels_csv_writer.writerow([receipt_status])


def test():
    print aldelo_path
    aldelo_test = os.path.join(aldelo_path,'TEST')#[A-Z]*')
    print aldelo_test
    line_item_receipts = open(os.path.join(aldelo_path,'line_item_receipts.txt'),'wb')
    non_line_item_receipts = open(os.path.join(aldelo_path, 'non_line_item_receipts.txt'),'wb')
    receipts = glob.glob(aldelo_test+'/*.txt')
    for receipt in receipts:
        result = classifier.classify(our_classifier, receipt)
        receipt_content = open(receipt).read()
        if result:
            line_item_receipts.write(receipt_content)
            line_item_receipts.write("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
        else:
            non_line_item_receipts.write(receipt_content)
            non_line_item_receipts.write("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

        print 'result ' + str(result[0]) + ' ' + receipt
        
    line_item_receipts.close()
    non_line_item_receipts.close()

learn_receipts()
our_classifier = classifier.learn(training_set_path, labels_path)
pickle.dump(our_classifier, open(classifier_path, 'wb'))
test()

