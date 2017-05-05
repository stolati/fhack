import pickle
import io

from lxml import etree

from collections import defaultdict
from lexer import get_lexer

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

class Formatter(meta=ABCMeta):

    @abstractmethod
    def format(self, in_stream, out_stream, highlighted_tokens):
        pass

    @abstractmethod
    def format_highlighted(self, in_stream, out_stream, token, token_idx):
        pass

    def format_receipt(self, in_stream, out_stream, highlighted_tokens):
        for ii in range(len(highlighted_tokens)):
            token = highlighted_tokens[ii]

            out_stream.write(in_stream.read(token.position - receipt_f.tell()))

            self.format_highlighted(in_stream, out_stream, token, ii)

        out_stream.write(in_stream.read())



class TerminalFormatter(Formatter):
    def format_highlighted(self, in_stream, out_stream, token, token_idx):
        out_stream.write("".join((Fore.GREEN, "[{}]".format(token_idx, Style.RESET_ALL))))
        out_stream.write(in_stream.read(len(token.value)))


class QuestionFormFormatter(Formatter):
    XML_NS = "http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionForm.xsd"
    QUESTION_TPL = """
    <Question>
        <IsRequired>{is_required}
        <QuestionContent>
            <Text>{question_text}</Text>
        </QuestionContent>
        <AnswerSpecification>
            <SelectionAnswer>
                <MinSelectionCount>0</MinSelectionCount>
                <MaxSelectionCount>{n_selections}</MaxSelectionCount>
                <Selections>
                {selections}
                </Selections>
            </SelectionAnswer
        </AnswerSpecification>
    </Question>"""

    SELECTION_TPL = """
                    <Selection>
                        <SelectionIdentifier>{0.id}</SelectionIdentifier>
                        <SelectionText>{0.text}</SelectionText>
                    </Selection"""

    def __init__(self, title, desc, questions):
        self.questions = questions

    #override
    def format(self, in_stream, out_stream, highlighted_tokens):
        with etree.xmlfile(out_stream) as xmldoc:
            with xmldoc.element("QuestionForm", {None: self.XML_NS}) as root:
                self.write_overview(in_stream, xmldoc, highlighted_tokens)
                for question in self.questions:
                    self.write_question(in_stream, xmldoc, question)

    #override
    def format_highlighted(self, in_stream, out_stream, token, token_idx):
        out_stream.write("<b>")
        out_stream.write(in_stream.read(len(token.value)))
        out_stream.write("</b><sup><font color='green'>{}</font></sup>")
    
    def write_overview(self, in_stream, xmldoc, highlighted_tokens):
        with xmldoc.element("Overview"):
            xmldoc.write(self._make_elt("Title", self.title))
            xmldoc.write(self._make_elt("Text", self.desc))

            xmldoc.write(self._make_elt("FormattedContent"),
                    self._receipt_cdata(in_stream, highlighted_tokens))

    def write_question(self, in_stream, xmldoc, question, selections):
        with xmldoc.element("Question"):
            xmldoc.write(self._make_elt("IsRequired", "true" if question.is_required else "false"))
            with xmldoc.element("QuestionContent"):
                xmldoc.write(self._make_elt("Text", question.text))

            with xmldoc.element("AnswerSpecification"):
                with xmldoc.element("SelectionAnswer"):

        formatted = self.QUESTION_TPL.format(
                question_text=question.text,
                is_required=str(question.is_required).lower(),
                n_selections=len(question.selections),
                selections="".join(self.SELECTION_TPL.format(s) for s in question.selections))

        out_stream.write(formatted)

    def _receipt_cdata(self, in_stream, highlighted_tokens):
        ret = StringIO()
        ret.write("<p><pre>")
        self.format_receipt(in_stream, ret, highlighted_tokens)
        ret.write("</pre></p>")

        return etree.CDATA(ret.getvalue().encode("utf-8"))

    def _make_elt(self, name, text=None, attribs=None):
        ret = etree.Element(name, attribs=attribs or {})
        ret.text = text
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
