import logging

from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream
from antlr4.tree.Tree import ParseTreeWalker

from arena.lql.LQLLexer import LQLLexer
from arena.lql.LQLListener import LQLListener
from arena.lql.LQLParser import LQLParser


logger = logging.getLogger(__name__)


class Interface:

    def __init__(self, name: str):
        self.name = name
        self.methods = []
        self.lql_query = ''


class MethodSignature:

    def __init__(self, name: str, constructor: bool):
        self.name = name
        self.inputNames = []
        self.inputs = []
        self.outputNames = []
        self.outputs = []
        self.constructor = constructor


class LQLParseResult:

    def __init__(self, interface: Interface):
        self.interface = interface
        self.filters = []


class LqlListener(LQLListener):
    """
    Listener to construct Interface from parse tree
    """

    def __init__(self):
        self.parse_result = None

    def enterInterfaceSpec(self, ctx:LQLParser.InterfaceSpecContext):
        if ctx.simpletype() is not None:
            self.parse_result = LQLParseResult(Interface(ctx.simpletype().getText()))

        if ctx.qualifiedtype() is not None:
            self.parse_result = LQLParseResult(Interface(ctx.qualifiedtype().getText()))


    def enterMethodSig(self, ctx:LQLParser.MethodSigContext):
        method_name = ctx.NAME().getText()
        method = MethodSignature(method_name, self.parse_result.interface.name == method_name)

        if ctx.inputs() is not None:
            for i in range(ctx.inputs().parameters().getChildCount()):
                in_param = ctx.inputs().parameters().getChild(i).getText()
                if not in_param == ",":
                    text = in_param
                    if "=" in text:
                        parts = text.split("=")
                        method.inputs.append(parts[1])
                        method.inputNames.append(parts[0])
                    else:
                        method.inputs.append(text)

        if ctx.outputs() is not None:
            for i in range(ctx.outputs().parameters().getChildCount()):
                in_param = ctx.outputs().parameters().getChild(i).getText()
                if not in_param == ",":
                    text = in_param
                    if "=" in text:
                        parts = text.split("=")
                        method.outputs.append(parts[1])
                        method.outputNames.append(parts[0])
                    else:
                        method.outputs.append(text)
        else:
            method.outputs.append("void")

        self.parse_result.interface.methods.append(method)


    def enterFilter(self, ctx:LQLParser.FilterContext):
        if ctx is not None:
            self.parse_result.filters.append(ctx.FILTERVALUE().getText())


def parse_lql(lql: str):
    """
    Parse LQL string into model.

    :param lql:
    :return:
    """

    lexer = LQLLexer(InputStream(lql))
    stream = CommonTokenStream(lexer)
    parser = LQLParser(stream)

    tree = parser.interfaceSpec()

    listener = LqlListener()

    walker = ParseTreeWalker()
    walker.walk(listener, tree)

    parse_result = listener.parse_result

    logger.debug(f"parsed LQL {tree.toStringTree(recog=parser)}")

    return parse_result