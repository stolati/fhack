import ply.lex as lex

def get_lexer():
    tokens = (
        'EQ_SECTION_BREAK',
        'DASH_SECTION_BREAK',
        'STAR_SECTION_BREAK',
        'ESCAPES',
        'WORD_ITEMS',
        'LABELS',
        'COLON',
        'PERCENT',
        'NUMBER',
        'POUND',
        'OTHER',
        'TIME',
        'TOTAL',
        'SUBTOTAL',
        'MONEY_AMOUNT',
        'DELIMITER',
        'DATE',
        'NEWLINE',
        'TAB')

    def t_NEWLINE(t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        return t
        
    def t_TAB(t):
        r'\t+'
        return t

    def t_EQ_SECTION_BREAK(t):
        r'=+'
        return t

    def t_DASH_SECTION_BREAK(t):
        r'-+'
        return t

    def t_STAR_SECTION_BREAK(t):
        r'\*+'
        return t

    def t_DATE(t):
        r'\d+\/\d+\/\d+'
        return t

    def t_TIME(t):
        r'\d+:\d+:\d+\s+(AM|PM)'
        return t

    def t_PERCENT(t):
        r'\d+%'
        return t

    def t_LABELS(t):
        r'\*\*\* \s+ [^\*]+ \s+ \*\*\* \
        | >> \s+ [^<]+ \s+ <<'
        return t

    def t_COLON(t):
        r':'
        return t

    def t_DELIMITER(t):
        r'===+|\*\*\*+'
        return t

    def t_POUND(t):
        r'\#'
        return t

    def t_SUBTOTAL(t):
        r'(\w+ [ ])? [sS][uU][bB]\s?[tT][oO][tT][aA][lL][:]?'
        return t

    def t_TOTAL(t):
        r'[tT][oO][tT][aA][lL]'
        return t

    def t_MONEY_AMOUNT(t):
        r'\$?[0-9]+\.[0-9][0-9]'
        return t
        
    def t_NUMBER(t):
        r'\d+'
        return t

    def t_WORD_ITEMS(t):
#        r'[a-zA-Z]+([ ]\w+)*'
        r'[\x21-\x7E]+([ ][\x21-\x7E]+)*'
        return t

    def t_ESCAPES(t):
        r'([^a-zA-Z0-9\,\.\!\:\?\\\s\-\(\)]+([\S]+[^a-zA-Z0-9\,\.\!\:\?\\\s\-\(\)]+)+)+'
        return t

    # Don't put funtions after this!

    def t_OTHER(t):
        r'\S+'
        return t

    def t_error(t):
        #print(t)
        t.lexer.skip(1)

#    t_ignore = ' \t'

    return lex.lex()

l = get_lexer()
