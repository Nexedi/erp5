def setPortalTypeDescription(self, portal_type, description):
  self.getPortalObject().portal_types[portal_type]._updateProperty(
    'description', description)

def getPropertySheetList(self, portal_type):
  import erp5.portal_type

  return (getattr(self.getPortalObject().portal_types, portal_type).getTypePropertySheetList() +
          list(getattr(erp5.portal_type, portal_type).property_sheets))

def getPropertySheetAttributeList(self, name):
  portal = self.getPortalObject()
  try:
    property_sheet_obj = portal.portal_property_sheets[name]
  except KeyError:
    return []

  result = []
  # We don't want Acquired Property nor Category TALES Expression
  for property_obj in property_sheet_obj.contentValues(portal_type=('Category Property',
                                                                    'Standard Property')):
    reference = property_obj.getReference('')
    description = ''
    if property_obj.getPortalType() == 'Category Property':
      try:
        description = portal.portal_categories[reference].getDescription('')
      except KeyError:
        pass
    else:
      description = property_obj.getDescription('')

    result.append((reference, description))

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


from six.moves import cStringIO as StringIO
from zope.tal.htmltalparser import HTMLTALParser
from zope.tal.talparser import TALParser
from zope.tal.talgenerator import TALGenerator
from zope.tal.dummyengine import name_match
def findStaticTranslationText(page_template, func_name_list):
  def iterate(node, target_name, function):
    if isinstance(node, list):
      for i in node:
        iterate(i, target_name, function)
    elif isinstance(node, tuple) and node:
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
      type_, expression = match.group(1, 2)
      if type_=='python':
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
from zope.tal.talinterpreter import TALInterpreter
from zope.tal.dummyengine import DummyEngine
class MyDummyEngine(DummyEngine):

  def evaluate(self, expression):
    return []


class MyDummyTALInterpreter(TALInterpreter):

  _i18n_message_id_dict = None
  _currentTag = None

  def translate(self, msgid, default=None, i18ndict=None, obj=None): # pylint:disable=arguments-differ
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
    raise ValueError("not a TransitionDefinition")
