import compiler
import compiler.ast
import compiler.visitor


class Visitor(compiler.visitor.ASTVisitor):

  def __init__(self, func_name):
    self.func_name = func_name
    compiler.visitor.ASTVisitor.__init__(self)
    self.result = []

  def visitCallFunc(self, node, *args):
    if (isinstance(node.node, compiler.ast.Name) and
        node.node.name==self.func_name):
      arg = node.args[0]
      value = None
      if isinstance(arg, compiler.ast.Const):
        value = arg.value
      elif isinstance(arg, compiler.ast.Add):
        value = concatenate_add_const_value(arg)
      if value is not None:
        self.result.append(value)


def concatenate_add_const_value(node):
  def iterate(nodes):
    if not nodes:
      return ''
    node = nodes[0]
    if isinstance(node, compiler.ast.Const):
      return node.value + iterate(nodes[1:])
    elif isinstance(node, compiler.ast.Add):
      if getattr(node, 'nodes', None):
        children_nodes = node.nodes
      else:
        children_nodes = (node.left, node.right)
      return iterate(children_nodes)+iterate(nodes[1:])
    elif isinstance(node, compiler.ast.Mod):
      # we can't handle Mod node statically.
      pass
  return iterate((node,))


def getFunctionFirstArgumentValue(func_name, source):
  ast = compiler.parse(source)
  visitor = Visitor(func_name)
  compiler.walk(ast, visitor)
  return visitor.result
