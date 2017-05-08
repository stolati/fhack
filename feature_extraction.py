import pickle
import io
from abc import ABCMeta, abstractmethod
from io import BytesIO, StringIO

from colorama import Fore, Style
from lxml import etree

from collections import defaultdict
from lexer import get_lexer
from question_formatters import TerminalFormatter

common_word_path = 'common_words.pkl'


def extract_features(current_idx, tokens, price_order, receipt_length):
    features = {}

    current_token = tokens[current_idx]

    features[current_token.type] = 1
    features["document_position"] = current_token.lexpos / receipt_length
    features["order_largest_to_smallest"] = price_order
    
    closest_tokens = 3
    features.update(
            ("closest_before_{}".format(t.type), idx)
            for idx, t in enumerate(tokens[current_idx - closest_tokens:current_idx], 1))
    features.update(
            ("closest_after_{}".format(t.type), idx)
            for idx, t in enumerate(reversed(tokens[current_idx + 1:current_idx + closest_tokens + 1]), 1))

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
            price = int(lexer.lexmatch.group("money_amount").translate(str.maketrans("", "", ",.")))
            if lexer.lexmatch.group("negative_sign"):
                price = -price

            prices.append((idx, price))

        tokens.append(token)
    
    prices.sort(key=lambda elt: elt[1])

    for price_order, (token_index, amount) in enumerate(prices):
        ret.append((tokens[token_index],
            extract_features(token_index, tokens, price_order, receipt_length)))

    return ret

class Receipt(object):
    def __init__(self, path):
        self.path = path

        with self.open() as receipt_file:
            self.text = receipt_file.read()

        self.lexer = get_lexer()
        self.lexer.input(self.text)

        self.tokens = []
        for token in self.lexer:
            # .lexpos refers to the lexer's *current* position, not the token's.
            token.position = token.lexpos
            self.tokens.append(token)

    def open(self):
        return open(self.path)


    def format(self, out_stream, highlighted_tokens, formatter=None):
        if formatter is None:
            formatter = TerminalFormatter()

        with self.open() as in_stream:
            formatter.format(in_stream, out_stream, highlighted_tokens)
                

    @property
    def prices(self):
        if not hasattr(self, "_prices"):
            self._prices = [t for t in self.tokens if t.type == "MONEY_AMOUNT"]

        return self._prices
            
    def get_prices(receipt):
        lexer = get_lexer()

        lexer.input(receipt)
        receipt_length = len(lexer.lexdata)

        return [t for t in lexer if t.type == "MONEY_AMOUNT"]
        ret = []
        tokens = []
        prices = []

        for idx, token in enumerate(lexer):
            if token.type == "MONEY_AMOUNT":
                price = int(lexer.lexmatch.group("money_amount").translate(str.maketrans("", "", ",.")))
                if lexer.lexmatch.group("negative_sign"):
                    price = -price

                prices.append((idx, price))

            tokens.append(token)
        
        prices.sort(key=lambda elt: elt[1])

        for price_order, (token_index, amount) in enumerate(prices):
            ret.append((tokens[token_index],
                extract_features(token_index, tokens, price_order, receipt_length)))

        return ret
