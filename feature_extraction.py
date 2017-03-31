from lexer import get_lexer
import pickle
import io

common_word_path = 'common_words.pkl'

def extract_features(file_path):
    f = io.open(file_path, 'r', encoding='utf-8')
    lexer = get_lexer()
    lexer.input(f.read())
    
    common_words = pickle.load(open(common_word_path, 'r'))
    
    total_lines = 0

    features = {}

    while True:
        tok = lexer.token()
        if not tok:
            break;
        if tok.type not in features:
            features[tok.type] = 0
        features[tok.type] += 1
        total_lines = tok.lineno
        if tok.value in common_words:
            if tok.value not in features:
                features[tok.value] = 0
            features[tok.value] += 1
            
    f.close()

    return features
