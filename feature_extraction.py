import pickle
import io

from collections import defaultdict
from lexer import get_lexer

common_word_path = 'common_words.pkl'

def extract_features(current_idx, tokens, price_order, receipt_length):
    features = {}

    current_token = tokens[current_idx]

    features[current_token.type] = 1
    features["distance_from_start"] = current_token.lexpos
    features["distance_from_end"] = receipt_length - current_token.lexpos
    features["order_largest_to_smallest"] = price_order
    
    for idx, token in enumerate(tokens):
        if token.type not in features or idx < current_idx:
            features["closest_{}".format(token.type)] = abs(current_idx - idx)

    return features

def extract_prices(receipt):
    lexer = get_lexer()

    lexer.input(receipt)
    receipt_length = len(lexer.lexdata)

    ret = []
    tokens = []
    prices = []

    for idx, token in enumerate(lexer):
        if token.type == "MONEY_AMOUNT":
            prices.append((idx, int(lexer.lexmatch.group("money_amount").replace(".", ""))))

        tokens.append(token)
    
    prices.sort(key=lambda elt: elt[1])

    for price_order, (token_index, amount) in enumerate(prices):
        ret.append((tokens[token_index],
            extract_features(token_index, tokens, price_order, receipt_length)))

    return ret
