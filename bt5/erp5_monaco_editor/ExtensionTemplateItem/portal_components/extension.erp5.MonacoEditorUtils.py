import ast
import enum
import json
import tempfile
import textwrap
import logging

logger = logging.getLogger(__name__)


class SymbolKind(enum.IntEnum):
  File = 0
  Module = 1
  Namespace = 2
  Package = 3
  Class = 4
  Method = 5
  Property = 6
  Field = 7
  Constructor = 8
  Enum = 9
  Interface = 10
  Function = 11
  Variable = 12
  Constant = 13
  String = 14
  Number = 15
  Boolean = 16
  Array = 17
  Object = 18
  Key = 19
  Null = 20
  EnumMember = 21
  Struct = 22
  Event = 23
  Operator = 24
  TypeParameter = 25


def ERP5Site_getPythonCodeSymbolList(self, data, REQUEST=None):
  """Get symbols from python code
  """
  data = json.loads(data)
  symbols = []

  class Visitor(ast.NodeVisitor):
    def addSymbol(self, symbol, current_symbol):
      if current_symbol:
        current_symbol['children'].append(symbol)
      else:
        symbols.append(symbol)

    def visit_Module(self, node):
      self.visitChildren(node, None)

    def visitChildren(self, node, current_symbol):
      for child in node.body:
        if isinstance(child, ast.FunctionDef):
          self.visitDef(child, current_symbol)
        if isinstance(child, ast.ClassDef):
          self.visitClassDef(child, current_symbol)

    def visitDef(self, node, current_symbol):
      def_symbol = self.getSymbol(
        node,
        SymbolKind.Method if (
          current_symbol is not None
          and current_symbol['kind'] == SymbolKind.Class) else
        SymbolKind.Function,
      )
      self.addSymbol(def_symbol, current_symbol)
      self.visitChildren(node, def_symbol)

    def visitClassDef(self, node, current_symbol):
      class_symbol = self.getSymbol(node, SymbolKind.Class)
      self.addSymbol(class_symbol, current_symbol)
      self.visitChildren(node, class_symbol)

    def getSymbol(self, node, kind):
      endLineNumber, endColumn = self.getEndPosition(node)
      sym = {
        "kind": int(kind),
        "name": node.name,
        "tags": [],
        "range": {
          "startColumn": node.col_offset,
          "startLineNumber": node.lineno,
          "endColumn": endColumn,
          "endLineNumber": endLineNumber,
        },
        "children": [],
      }
      sym['selectionRange'] = sym['range']
      return sym

    def getEndPosition(self, node):
      if not hasattr(node, "body") or len(node.body) == 0:
        return (node.lineno, node.col_offset)
      return self.getEndPosition(node.body[-1])

  try:
    tree = ast.parse(data['code'].encode('utf-8'))
  except SyntaxError:
    pass
  else:
    visitor = Visitor()
    visitor.visit(tree)
  if REQUEST:
    REQUEST.RESPONSE.setHeader('content-type', 'application/json')
  return json.dumps(symbols)


def ERP5Site_formatPythonSourceCode(self, data, REQUEST=None):
  from yapf.yapflib import yapf_api
  if isinstance(data, basestring):
    data = json.loads(data)
  try:
    extra = {}
    if data['range']:
      extra['lines'] = (
        (data['range']['startLineNumber'], data['range']['endLineNumber']), )
    with tempfile.NamedTemporaryFile(mode='w', suffix='.style.yapf') as f:
      f.write(
        textwrap.dedent(
          '''
          [style]
          based_on_style = pep8
          indent_width = 2
          continuation_indent_width = 2
          split_before_expression_after_opening_paren = true
          split_before_first_argument = true
          split_before_arithmetic_operator = true
          '''))
      f.flush()
      formatted_code, changed = yapf_api.FormatCode(
        data['code'], style_config=f.name, **extra)
  except SyntaxError as e:
    logger.exception("Error in source code")
    return json.dumps(dict(error=True, error_line=e.lineno))

  if REQUEST is not None:
    REQUEST.RESPONSE.setHeader('content-type', 'application/json')
  return json.dumps(dict(formatted_code=formatted_code, changed=changed))
