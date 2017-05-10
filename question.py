from __future__ import absolute_import, print_function, division, unicode_literals

from abc import ABCMeta, abstractmethod

from six import add_metaclass, text_type
from colorama import Fore, Style

@add_metaclass(ABCMeta)
class Formatter(object):
    @abstractmethod
    def format(self, in_stream, out_stream, highlighted_tokens=None):
        pass

    @abstractmethod
    def format_highlighted(self, in_stream, out_stream, token, token_idx):
        pass

    def format_receipt(self, in_stream, out_stream, highlighted_tokens=None):
        highlighted_tokens = highlighted_tokens or []

        for ii in range(len(highlighted_tokens)):
            token = highlighted_tokens[ii]

            out_stream.write(in_stream.read(token._position - in_stream.tell()))

            self.format_highlighted(in_stream, out_stream, token, ii + 1)

        out_stream.write(in_stream.read())



class TerminalFormatter(Formatter):
    def format(self, in_stream, out_stream, highlighted_tokens=None):
        self.format_receipt(in_stream, out_stream, highlighted_tokens)

    def format_highlighted(self, in_stream, out_stream, token, token_idx):
        out_stream.write("".join((Fore.GREEN, "[{}]".format(token_idx), Style.RESET_ALL)))
        out_stream.write(in_stream.read(len(token.value)))


class SkipInput(Exception):
    """Raised to signify that an input should be skipped"""


class Question(object):
    def __init__(self, text, choices=None, is_required=True):
        self.text = text
        self.choices = choices
        self.is_required = is_required

    def format(self):
       return "{}? ".format(self.text)

    def answer(self, answer_text):
        if answer_text == "skip":
            raise SkipInput

        if self.choices and answer_text not in self.choices:
            raise ValueError("{} not in {{{}}}".format(",".join(self.choices)))

        return answer


class BooleanQuestion(Question):
    def __init__(self, text, is_required=True, short_circuit=None):
        super(BooleanQuestion, self).__init__(text, ["yes", "no"], is_required, short_circuit)

    def format(self):
        return "{} ({})? ".format(self.text, ",".join(self.choices))

    def answer(self, answer_text):
        answer = super(BooleanQuestion, self).answer(answer_text)
        return True if self.answer == "yes" else False


class MultipleChoiceQuestion(Question):
    def answer(self, answer_text):
        if answer_text == "skip":
            raise SkipInput

        if not answer_text:
            raise ValueError("No answer provided; try again!")

        answers = set(answer_text.replace(",", " ").split())
        
        invalid = answers - set(self.choices)
        if invalid:
            raise ValueError("{} not in {{{}}}"
                    .format(",".join(invalid), ",".join(self.choices)))

        return answers


class QuestionFormFormatter(Formatter):
    XML_NS = "http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionForm.xsd"

    def __init__(self, title, desc, questions):
        self.title = title
        self.desc = desc
        self.questions = questions

    #override
    def format(self, in_stream, out_stream, highlighted_tokens=None):
        root = etree.Element("QuestionForm", nsmap={None: self.XML_NS})

        root.append(self.make_overview(in_stream, root, highlighted_tokens))
        for question in self.questions:
            root.append(self.make_question(question, highlighted_tokens))

        out_stream.write(etree.tostring(root, pretty_print=True, encoding="unicode"))

    #override
    def format_highlighted(self, in_stream, out_stream, token, token_idx):
        out_stream.write("<b>")
        out_stream.write(in_stream.read(len(token.value)))
        out_stream.write("</b><sup><font color='green'>{}</font></sup>".format(token_idx))
    
    def make_overview(self, in_stream, root, highlighted_tokens=None):
        ret = etree.Element("Overview")
        ret.append(self._make_elt("Title", self.title))
        ret.append(self._make_elt("Text", self.desc))

        ret.append(self._make_elt(
                "FormattedContent", self._receipt_cdata(in_stream, highlighted_tokens)))

        return ret

    def make_question(self, question, highlighted_tokens=None):
        ret = etree.Element("Question")

        ret.append(self._make_elt("IsRequired", "true" if question.is_required else "false"))

        ret.append(etree.Element("QuestionContent"))
        ret[-1].append(self._make_elt("Text", question.text))

        answer_spec = etree.Element("AnswerSpecification")
        selection_answer = etree.Element("SelectionAnswer")

        selections = []

        if question.choices:
            selection_answer.append(self._make_elt("StyleSuggestion", "radiobutton"))
            selections = question.choices

        elif highlighted_tokens:
            selection_answer.append(self._make_elt("StyleSuggestion", "multichooser"))
            selection_answer.append(self._make_elt("MinSelectionCount", "0"))
            selections = [(text_type(idx), t.value) for (idx, t) in enumerate(highlighted_tokens, 1)]

        else:
            raise ValueError("No choices provided for question '{}'".format(question.text))

        selection_answer.append(etree.Element("Selections"))
        for identifier, text in selections:
            selection_elt = etree.Element("Selection")
            selection_elt.append(self._make_elt("SelectionIdentifier", identifier))
            selection_elt.append(self._make_elt("Text", text))

            selection_answer[-1].append(selection_elt)

        answer_spec.append(selection_answer)
        ret.append(answer_spec)

        return ret

    def _receipt_cdata(self, in_stream, highlighted_tokens=None):
        ret = StringIO()
        ret.write("<p><pre>")
        self.format_receipt(in_stream, ret, highlighted_tokens)
        ret.write("</pre></p>")

        return etree.CDATA(ret.getvalue())

    def _make_elt(self, name, text=None, attrib=None):
        ret = etree.Element(name, attrib=attrib or {})
        ret.text = text
        return ret
