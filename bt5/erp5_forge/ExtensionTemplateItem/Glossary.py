def getPropertySheetList(self, portal_type):
  from Products.ERP5Type.DocumentationHelper.PortalTypeDocumentationHelper \
       import PortalTypeDocumentationHelper
  portal = self.getPortalObject()
  portal_type_uri = '%s/portal_types/%s' % (portal.getUrl(),
                                            portal_type)
  return PortalTypeDocumentationHelper(portal_type_uri).__of__(
    portal).getPropertySheetList()


def getPropertySheetAttributeList(self, name):
  from Products.ERP5Type import PropertySheet
  class_ = PropertySheet.__dict__.get(name, None)
  result = []
  for i in getattr(class_, '_properties', ()):
    if 'acquired_property_id' in i:
      continue
    # we want to get only normal property.
    result.append((i['id'], i.get('description', '')))
  for i in getattr(class_, '_categories', ()):
    try:
      result.append((i, self.getPortalObject().portal_categories[i].getDescription()))
    except KeyError:
      result.append((i, ''))
    except TypeError:
      # if category is Expression(...), TypeError raises
      pass
  return result


def getActionTitleListFromAllActionProvider(portal):
  result = []
  provider_list = []
  for provider_id in portal.portal_actions.listActionProviders():
    if provider_id in ('portal_types', 'portal_workflow'):
      continue
    provider = getattr(portal, provider_id, None)
    if provider is None:
      continue
    provider_list.append(provider)

  for typeinfo in portal.portal_types.objectValues():
    provider_list.append(typeinfo)

  for provider in provider_list:
    for action in provider.listActions():
        result.append((action.title, provider.getId()))
  return result


from StringIO import StringIO
from TAL.HTMLTALParser import HTMLTALParser
from TAL.TALParser import TALParser
from TAL.TALGenerator import TALGenerator
from TAL.DummyEngine import name_match
def findStaticTranslationText(page_template, func_name_list):
  def iterate(node, target_name, function):
    if type(node) is list:
      for i in node:
        iterate(i, target_name, function)
    elif type(node) is tuple and node:
      if node[0]==target_name:
        function(node)
      else:
        for i in node[1:]:
          iterate(i, target_name, function)

  text_dict = {}
  def addText(node):
    if len(node)!=2:
      node = (node[0], node[1:])
    program = [node]
    macros = {}
    engine = MyDummyEngine(macros)
    output = StringIO()
    interpreter = MyDummyTALInterpreter(program, macros, engine, output)
    interpreter()
    if interpreter._i18n_message_id_dict is not None:
      text_dict.update(interpreter._i18n_message_id_dict)

  def addTextFromPythonExpression(node):
    if node[0]=='insertText':
      tal_expression = node[1]
      if isinstance(tal_expression, (tuple, list)):
        tal_expression = tal_expression[0]
    elif node[0] in ('setLocal', 'setGlobal'):
      if len(node)==2:
        tal_expression = node[1][1]
      elif len(node)==3:
        tal_expression = node[2]
      else:
        return
    else:
      return
    tal_expression = tal_expression[1:-1]
    match = name_match(tal_expression)
    if match:
      type, expression = match.group(1, 2)
      if type=='python':
        # clean up expression
        expression = expression.strip()
        expression = expression.replace('\n', ' ')
        Base_getFunctionFirstArgumentValue = page_template.Base_getFunctionFirstArgumentValue
        for func_name in func_name_list:
          for message in Base_getFunctionFirstArgumentValue(func_name, expression):
            text_dict[message] = None

  if page_template.html():
    generator = TALGenerator(xml=0)
    parser = HTMLTALParser(generator)
  else:
    generator = TALGenerator(xml=1)
    parser = TALParser(generator)
  parser.parseString(page_template._text)
  iterate(parser.gen.program, 'insertTranslation', addText)
  iterate(parser.gen.program, 'insertText', addTextFromPythonExpression)
  iterate(parser.gen.program, 'setLocal', addTextFromPythonExpression)
  iterate(parser.gen.program, 'setGlobal', addTextFromPythonExpression)
  return text_dict.keys()

#
# Utility class for findStaticTranslationText
#
from TAL.TALInterpreter import TALInterpreter
from TAL.DummyEngine import DummyEngine
class MyDummyEngine(DummyEngine):

  def evaluate(self, expression):
    return None


class MyDummyTALInterpreter(TALInterpreter):

  _i18n_message_id_dict = None
  _currentTag = None

  def translate(self, msgid, default, i18ndict, obj):
    try:
      self._i18n_message_id_dict[msgid] = None
    except TypeError:
      self._i18n_message_id_dict = {msgid:None}

    return TALInterpreter.translate(self, msgid, default, i18ndict, obj)


from Products.DCWorkflow.Transitions import TransitionDefinition
def setGuard(self, guard):
  if isinstance(self, TransitionDefinition):
    self.guard = guard
  else:
    raise ValueError, "not a TransitionDefinition"
