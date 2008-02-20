def getPropertySheetAttributeList(name):
  from Products.ERP5Type import PropertySheet
  class_ = PropertySheet.__dict__.get(name, None)
  result = []
  for i in getattr(class_, '_properties', ()):
    if 'acquired_property_id' in i:
      continue
    # we want to get only normal property.
    result.append(i['id'])
  return result


def getActionTitleListFromAllActionProvider(portal):
  result = {}
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

  for action in provider.listActions():
      result[action.title] = None
  return result.keys()


from StringIO import StringIO
from TAL.HTMLTALParser import HTMLTALParser
def findStaticTranslationText(page_template):
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

  parser = HTMLTALParser()
  parser.parseString(page_template._text)
  iterate(parser.gen.program, 'insertTranslation', addText)
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
