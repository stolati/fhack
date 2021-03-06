from __future__ import absolute_import, print_function, division, unicode_literals

import io
import pickle
import re
from abc import ABCMeta, abstractmethod
from io import BytesIO, StringIO

from lxml import etree
from six import text_type

from collections import defaultdict
from lexer import get_lexer
from question import TerminalFormatter

common_word_path = 'common_words.pkl'


class Receipt(object):
    def __init__(self, path):
        self.path = path

        with self.open() as receipt_file:
            self.text = receipt_file.read()

        self.lexer = get_lexer()
        self.lexer.input(self.text)

        self.tokens = []
        for idx, token in enumerate(self.lexer):
            # .lexpos refers to the lexer's *current* position, not the token's.
            token._position = token.lexpos
            token._match = self.lexer.lexmatch
            token._index = idx

            self.tokens.append(token)

        self.by_position = {t._position: t for t in self.tokens}

    def open(self):
        return open(self.path, "rb")


    def format(self, out_stream, highlighted_tokens=None, formatter=None):
        if formatter is None:
            formatter = TerminalFormatter()

        with self.open() as in_stream:
            formatter.format(in_stream, out_stream, highlighted_tokens)

    @property
    def prices(self):
        if not hasattr(self, "_prices"):
            self._prices = [t for t in self.tokens if t.type == "MONEY_AMOUNT"]
            for token in self._prices:
                price = int(re.sub(r"[,.]", "", token._match.group("money_amount")))

                if token._match.group("negative_sign"):
                    price = -price

                token._price_in_cents = price

            for idx, token in enumerate(sorted(self._prices, key=lambda t: t._price_in_cents)):
                token._price_order = idx

        return self._prices
