import compiler
import compiler.ast
import compiler.visitor


class Visitor(compiler.visitor.ASTVisitor):

  def __init__(self, func_name):
    self.func_name = func_name
    compiler.visitor.ASTVisitor.__init__(self)
    self.result = []

  def visitCallFunc(self, node, *args):
    if ((isinstance(node.node, compiler.ast.Name) and
         node.node.name==self.func_name)
        or
        (isinstance(node.node, compiler.ast.Getattr) and
         node.node.attrname==self.func_name)
        ):
      arg = node.args[0]
      value = None
      if isinstance(arg, compiler.ast.Const):
        value = arg.value
      elif isinstance(arg, compiler.ast.Add):
        value = concatenate_add_const_value(arg)
      if value is not None:
        self.result.append(value)
    for child_node in node.args:
      self.preorder(child_node, self)


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


#
# Collect translation message from products
#
import os.path
import Products.ERP5
def findMessageListFromPythonInProduct(function_name_list):
  product_dir = os.path.dirname(Products.ERP5.__path__[0])
  erp5_product_list = ('CMFActivity', 'CMFCategory',
                       'ERP5', 'ERP5Banking', 'ERP5Catalog', 'ERP5Configurator',
                       'ERP5Form', 'ERP5OOo', 'ERP5Security',
                       'ERP5SyncML', 'ERP5Type', 'ERP5Wizard', 'ERP5Workflow',
                       'HBTreeFolder2', 'MailTemplates', 'TimerService',
                       'ZMySQLDA', 'ZSQLCatalog',
                       )
  result = []
  def findStaticMessage(file_path):
    source = open(file_path).read()
    for func_name in function_name_list:
      call_func_name = '%s(' % func_name
      if call_func_name in source:
        for m in getFunctionFirstArgumentValue(func_name, source):
          result.append((m, file_path))
  def visit(arg, dirname, filename_list):
    for filename in filename_list:
      if filename.endswith('.py'):
        findStaticMessage(os.path.join(dirname, filename))
  for product_name in erp5_product_list:
    os.path.walk(os.path.join(product_dir, product_name), visit, None)
  return result
