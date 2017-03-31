import ply.lex as lex
from lexer import get_lexer

def tokenize(file):
    lexer = get_lexer()
    lexer.input(file.read())

    return lexer


