from __future__ import unicode_literals
import json
import sys
from threading import RLock
import logging
import inspect

logger = logging.getLogger("erp5.extension.Jedi")

import os
import jedi
import zope.dottedname.resolve
import time

last_reload_time = time.time()

# increase default cache duration
# XXX I'm really not sure this is needed, jedi seems fast enough.
jedi.settings.call_signatures_validity = 30

# monkey patch to disable buggy sys.path addition based on buildout.
# rdiff-backup seem to trigger a bug, but it's generally super slow and not correct for us.
try:
  # in jedi 0.15.1 it's here
  from jedi.evaluate import sys_path as jedi_inference_sys_path  # pylint: disable=import-error
except ImportError:
  # but it's beeing moved. Next release will be here
  # https://github.com/davidhalter/jedi/commit/3b4f2924648eafb9660caac9030b20beb50a83bb
  from jedi.inference import sys_path as jedi_inference_sys_path  # pylint: disable=import-error
_ = jedi_inference_sys_path.discover_buildout_paths  # make sure it's here


def dont_discover_buildout_paths(*args, **kw):
  return set()


jedi_inference_sys_path.discover_buildout_paths = dont_discover_buildout_paths
from jedi.api import project as jedi_api_project
jedi_api_project.discover_buildout_paths = dont_discover_buildout_paths

try:
  # for local types annotations in this component
  from erp5.portal_type import ERP5Site  # pylint: disable=unused-import
except ImportError:
  pass


def executeJediXXX(callback, context, arguments):
  from jedi.evaluate.base_context import ContextSet

  # XXX function for relaodability
  def call():
    return callback(context, arguments=arguments)

  from jedi.evaluate.context.instance import TreeInstance
  from jedi.evaluate.gradual.typing import InstanceWrapper
  from jedi.evaluate.lazy_context import LazyKnownContexts
  from jedi.evaluate.base_context import ContextSet, NO_CONTEXTS

  def makeFilterFunc(class_from_portal_type, arguments):
    def filter_func(val):
      if isinstance(val, TreeInstance) and val.tree_node.type == 'classdef':
        logger.info(
            "classdef cool => %s == %s",
            val.tree_node.name.value,
            class_from_portal_type)
        return val.tree_node.name.value == class_from_portal_type
      if isinstance(val, LazyKnownContexts) and filter_func(val.infer()):
        return True
      if isinstance(val, ContextSet):
        return val.filter(filter_func) != NO_CONTEXTS
      if isinstance(val, InstanceWrapper): 
        for wrapped in val.iterate():
          if filter_func(wrapped):
            return True
        annotation_classes = val.gather_annotation_classes()
        #import pdb; pdb.set_trace()
        return val.gather_annotation_classes().filter(filter_func)
        
        # XXX
        if str(val).count('<LazyGenericClass:') == 1:
          logger.info(
              "I don't know ... %s because %s in %s",
              "{}@".format(class_from_portal_type) in str(val),
              "{}@".format(class_from_portal_type),
              val)
          return "{}@".format(class_from_portal_type) in str(val)
      logger.info("not found in %s", val)
      return False

    return filter_func

  # methods returning portal types
  if context.is_function():
    # and 1 or context.get_function_execution(
    #).function_context.name.string_name == 'newContent':
    if not arguments.argument_node:
      return call()  # no portal_type, we'll use what's defined in the stub

    # look for a "portal_type=" argument
    for arg_name, arg_value in arguments.unpack():
      if arg_name == 'portal_type':
        try:
          portal_type = iter(arg_value.infer()).next().get_safe_value()
        except Exception:
          logger.exception("error infering")
          continue
        if not isinstance(portal_type, str):
          continue
        logger.info(
            'ahah portal_type based method with portal type=%s ...',
            portal_type)
        # XXX this is really horrible
        original = call()
        filtered = original.filter(
            makeFilterFunc(portal_type.replace(' ', ''), arguments))
        #original._set = frozenset(
        #    {x for x in original._set if class_from_portal_type in str(x)})
        logger.info(
            'portal_type based method, returning\n   %s instead of\n   %s',
            filtered,
            original)
        return filtered

  # methods returning List of portal types
  # methods returning List of Brain of portal types
  return call()


def makeERP5Plugin():
  logger.info('making erp5 plugin')

  from jedi.evaluate.base_context import ContextSet
  from jedi.parser_utils import get_cached_code_lines
  from StringIO import StringIO

  class JediERP5Plugin(object):
    _cache = {}

    def _getPortalObject(self):  # XXX needed ?
      # type: () -> ERP5Site
      from Products.ERP5.ERP5Site import getSite
      from Products.ERP5Type.Globals import get_request
      from ZPublisher.BaseRequest import RequestContainer
      request = get_request()
      assert request
      return getSite().__of__(RequestContainer(REQUEST=request))

    def execute(self, callback):
      """Handle dynamic methods accepting portal_type= arguments
      """
      logger.info("JediERP5Plugin registering execute")

      def wrapper(context, arguments):
        from erp5.component.extension.Jedi import executeJediXXX as _execute
        return _execute(callback, context, arguments)

        def call():
          return callback(context, arguments=arguments)

        # methods returning portal types
        if context.is_function():
          # and 1 or context.get_function_execution(
          #).function_context.name.string_name == 'newContent':
          if not arguments.argument_node:
            return call(
            )  # no portal_type, we'll use what's defined in the stub

          # look for a "portal_type=" argument
          for arg_name, arg_value in arguments.unpack():
            if arg_name == 'portal_type':
              try:
                portal_type = iter(arg_value.infer()).next().get_safe_value()
              except Exception:
                logger.exception("error infering")
                continue
              if not isinstance(portal_type, str):
                continue
              logger.info(
                  'ahah portal_type based method with portal type=%s ...',
                  portal_type)
              # XXX this is really horrible
              class_from_portal_type = portal_type.replace(' ', '') + '@'
              original = call()
              if 0:
                filtered = ContextSet.from_sets({s for s in original})
              import pdb
              pdb.set_trace()
              original._set = frozenset({
                  x for x in original._set if class_from_portal_type in str(x)
              })
              logger.info(
                  'portal_type based method, returning\n   %s instead of\n   %s',
                  original,
                  call())
              #import pdb; pdb.set_trace()
              return original

        # methods returning List of portal types
        # methods returning List of Brain of portal types
        return call()

      return wrapper

    def not_used_import_module(self, callback):  # TODO: remove, not used
      """
      Handle ERP5 dynamic modules import.
      """
      from jedi.evaluate.context import ModuleContext, StubModuleContext
      logger.info("JediERP5Plugin registering import_module")

      def wrapper(evaluator, import_names, module_context, *args, **kwargs):
        if len(import_names) > 1 and import_names[:2] in (
            ('erp5', 'portal_type'), ('erp5', 'accessor_holder'),
            ('erp5', 'skins_tool'), ('erp5', 'component')):
          try:
            if 1:
              erp5_code = '''   
from . import portal_type
from . import skins_tool
from . import accessor_holder
from . import component
                  '''
              portal = self._getPortalObject()

              module_to_component_portal_type_mapping = {
                  'test': 'Test Component',
                  'document': 'Document Component',
                  'extension': 'Extension Component',
                  'tool': 'Tool Component',
                  'module': 'Module Component',
                  'interface': 'Interface Component',
              }
              if import_names == ('erp5', 'portal_type'):
                source_code = self._cache.get('portal_type')
                if not source_code:
                  source_code = portal.portal_types.TypesTool_getStub()
                  self._cache['portal_type'] = source_code
                source_path = "erp5/portal_type.pyi"
              elif import_names == ('erp5', 'accessor_holder'):
                source_code = self._cache.get('accessor_holder')
                if not source_code:
                  source_code = portal.portal_types.PropertySheetTool_getStub()
                  self._cache['accessor_holder'] = source_code
                source_path = "erp5/accessor_holder.pyi"
              elif import_names == ('erp5', 'skins_tool'):
                source_code = self._cache.get('skins_tool')
                if not source_code:
                  source_code = portal.portal_skins.SkinsTool_getStub()
                  self._cache['skins_tool'] = source_code
                source_path = "erp5/skins_tool.pyi"
              elif import_names[1] in ('portal_types',
                                       'accessor_holder',
                                       'skins_tool'):
                # fallback
                return callback(
                    evaluator, import_names, module_context, *args, **kwargs)
              else:  # if import_name[-1] == 'component':
                dotted_name = '.'.join(import_names)
                logger.info('looking up code for %s', dotted_name)
                # we don't have source for some modules
                if dotted_name == 'erp5.component':
                  source_code = textwrap.dedent(
                      '''\
                    from . import document
                    from . import test
                    from . import extension
                    from . import tool
                    from . import interface
                    from . import module
                  ''')
                elif len(import_names) == 3 and import_names[:2] == (
                    'erp5', 'component') and import_names[
                        2] in module_to_component_portal_type_mapping:
                  line_list = []
                  for brain in portal.portal_catalog.searchResults(
                      portal_type=module_to_component_portal_type_mapping[
                          import_names[2]],
                      validation_state='validated',
                      select_dict={'reference': None}):
                    line_list.append('from . import {}'.format(brain.reference))
                  source_code = '\n'.join(line_list)
                else:
                  source_code = inspect.getsource(
                      zope.dottedname.resolve.resolve(dotted_name))
                source_path = "{}.pyi".format('/'.join(import_names))
                logger.info('got code for %s', source_path)
#                logger.error('unsupported import %s', import_names)
#                raise NotImplementedError()

#logger.info('got code for %s', source_path)
              source = StringIO(source_code)
              # XXX make this StringIO look like a jedi FileIO
              source.get_last_modified = lambda: last_reload_time  # os.path.getmtime(file_path) # TODO
              source.path = source_path
              source.get_parent_folder = lambda: None
              # TODO bug with using StringIO
              # AttributeError: StringIO instance has no attribute 'get_parent_folder'
              #   email = pers.newContent(portal_type='Email')

              module = evaluator.parse(
                  file_io=source, cache=True, use_latest_grammar=True)

              # XXX needed ?
              erp5_source = StringIO(erp5_code)
              erp5_source.path = "erp5.py"
              erp5_source.get_last_modified = lambda: 13
              erp5_module = evaluator.parse(
                  file_io=erp5_source, cache=True, use_latest_grammar=True)

              non_stub_context = ModuleContext(
                  evaluator,
                  erp5_module,
                  file_io=erp5_source,
                  string_names=None,
                  code_lines=get_cached_code_lines(
                      evaluator.latest_grammar, erp5_source.path),
                  is_package=True)
              non_stub_context.is_builtins_module = lambda: False

              parent_context = StubModuleContext(
                  ContextSet([non_stub_context]),
                  evaluator,
                  module,
                  file_io=source,
                  string_names=None,  #('erp5', 'portal_type'),
                  code_lines=get_cached_code_lines(evaluator.latest_grammar,
                                                   source.path),
                  # is_package=True
              )
              parent_context.is_builtins_module = lambda: False
              #logger.info('got context %s', parent_context)
              #import pdb; pdb.set_trace()
              return ContextSet([non_stub_context, parent_context])
          except Exception:
            logger.exception("merde")
        return callback(
            evaluator, import_names, module_context, *args, **kwargs)

      logger.info('returning %s', wrapper)
      return wrapper

  return JediERP5Plugin()


# map jedi type to the name of monaco.languages.CompletionItemKind
# This mapping and the functions below (_format_completion, _label, _detail, _sort_text )
# are copied/inspired by jedi integration in python-language-server
# https://github.com/palantir/python-language-server/blob/19b10c47988df504872a4fe07c421b0555b3127e/pyls/plugins/jedi_completion.py
# python-language-server is Copyright 2017 Palantir Technologies, Inc. and distributed under MIT License.
# https://github.com/palantir/python-language-server/blob/19b10c47988df504872a4fe07c421b0555b3127e/LICENSE

_TYPE_MAP = {
    'none': 'Value',
    'type': 'Class',
    'tuple': 'Class',
    'dict': 'Class',
    'dictionary': 'Class',
    'function': 'Function',
    'lambda': 'Function',
    'generator': 'Function',
    'class': 'Class',
    'instance': 'Reference',
    'method': 'Method',
    'builtin': 'Class',
    'builtinfunction': 'Function',
    'module': 'Module',
    'file': 'File',
    'xrange': 'Class',
    'slice': 'Class',
    'traceback': 'Class',
    'frame': 'Class',
    'buffer': 'Class',
    'dictproxy': 'Class',
    'funcdef': 'Function',
    'property': 'Property',
    'import': 'Module',
    'keyword': 'Keyword',
    'constant': 'Variable',
    'variable': 'Variable',
    'value': 'Value',
    'param': 'Variable',
    'statement': 'Keyword',
}


def _label(definition):
  if definition.type in ('function', 'method') and hasattr(definition,
                                                           'params'):
    params = ', '.join([param.name for param in definition.params])
    return '{}({})'.format(definition.name, params)
  return definition.name


def _detail(definition):
  try:
    return definition.parent().full_name or ''
  except AttributeError:
    return definition.full_name or ''


def _sort_text(definition):
  """ Ensure builtins appear at the bottom.
  Description is of format <type>: <module>.<item>
  """
  # If its 'hidden', put it next last
  prefix = 'z{}' if definition.name.startswith('_') else 'a{}'
  return prefix.format(definition.name)


def _format_docstring(docstring):
  return docstring


def _format_completion(d):
  completion = {
      'label': _label(d),
      '_kind': _TYPE_MAP.get(d.type),
      'detail': _detail(d),
      'documentation': _format_docstring(d.docstring()),
      'sortText': _sort_text(d),
      'insertText': d.name
  }
  return completion


def _guessType(name, context_type=None):
  """guess the type of python script parameters based on naming conventions.

  """
  name = name.split('=')[
      0]  # support also assigned names ( like REQUEST=None in params)
  if name == 'context' and context_type:
    return context_type
  if name in (
      'context',
      'container',):
    return 'ERP5Site'
  if name == 'script':
    return 'Products.PythonScripts.PythonScript'
  if name == 'REQUEST':
    return 'ZPublisher.HTTPRequest.HTTPRequest'
  if name == 'RESPONSE':
    return 'ZPublisher.HTTPRequest.HTTPResponse'
  return 'str'  # assume string by default


# Jedi is not thread safe
import Products.ERP5Type.Utils
jedi_lock = getattr(Products.ERP5Type.Utils, 'jedi_lock', None)
if jedi_lock is None:
  logger.critical("There was no lock, making a new one")
  jedi_lock = Products.ERP5Type.Utils.jedi_lock = RLock()
logger.info("Jedi locking with %s (%s)", jedi_lock, id(jedi_lock))


def ERP5Site_getPythonSourceCodeCompletionList(self, data, REQUEST=None):
  """Complete source code with jedi.
  """
  portal = self.getPortalObject()
  logger.debug('jedi get lock %s (%s)', jedi_lock, id(jedi_lock))
  with jedi_lock:

    # register our erp5 plugin
    from jedi.plugins import plugin_manager
    if not getattr(plugin_manager, '_erp5_plugin_registered', None):
      plugin_manager.register(makeERP5Plugin())
      plugin_manager._erp5_plugin_registered = True

    if isinstance(data, basestring):
      data = json.loads(data)

    # data contains the code, the bound names and the script params. From this
    # we reconstruct a function that can be checked
    def indent(text):
      return ''.join(("  " + line) for line in text.splitlines(True))

    script_name = data.get('script_name', 'unknown.py')  #  TODO name
    is_python_script = 'bound_names' in data

    if is_python_script:
      signature_parts = data['bound_names']
      if data['params']:
        signature_parts += [data['params']]
      signature = ", ".join(signature_parts)

      # guess type of `context`
      context_type = None
      if '_' in script_name:
        context_type = script_name.split('_')[0]

        if context_type not in [ti.replace(' ', '')
                                for ti in portal.portal_types.objectIds()] + [
                                    'ERP5Site',]:
          logger.warning(
              "context_type %s has no portal type, using ERP5Site",
              context_type)
          context_type = None

      imports = "from erp5.portal_type import {}; import Products.ERP5Type.Core.Folder; import ZPublisher.HTTPRequest; import Products.PythonScripts".format(
          context_type or 'ERP5Site')
      type_annotation = "  #  type: ({}) -> None".format(
          ', '.join(
              [_guessType(part, context_type) for part in signature_parts]))
      body = "%s\ndef %s(%s):\n%s\n%s" % (
          imports,
          script_name,
          signature,
          type_annotation,
          indent(data['code']) or "  pass")
      data['position']['line'] = data['position'][
          'line'] + 3  # imports, fonction header + type annotation line
      data['position'][
          'column'] = data['position']['column'] + 2  # "  " from indent(text)
    else:
      body = data['code']

    logger.debug("jedi getting completions for %s ...", script_name)
    start = time.time()
    script = jedi.Script(
        body,
        data['position']['line'],
        data['position']['column'] - 1,
        script_name,
        sys_path=['/tmp/ahaha/'] + list(sys.path),
    )

    completions = [_format_completion(c) for c in script.completions()]
    logger.info(
        "jedi got %d completions in %.2fs",
        len(completions), (time.time() - start))

    if REQUEST is not None:
      REQUEST.RESPONSE.setHeader('content-type', 'application/json')
    return json.dumps(completions)


import textwrap


def safe_python_identifier(name):
  # type: (str) -> str
  """Format this name as a python idenfier.

  For example "Person Module" becomes "PersonModule"
  """
  return name.replace(" ", "")


def safe_docstring(docstring):
  # type: (str) -> str
  """Formats a docstring to include in generated stub.
  """
  if not docstring:
    return '...'
  return "'''{}'''".format(docstring.replace("'''", r"\'\'\'"))


from Products.ERP5Type.Accessor import Constant
from Products.ERP5Type.Accessor import WorkflowState
from Products.ERP5Type.Base import WorkflowMethod
from Products.ERP5Type.ERP5Type import ERP5TypeInformation  #  pylint: disable=unused-import
from Products.PythonScripts.PythonScript import PythonScript  #  pylint: disable=unused-import

from collections import namedtuple, defaultdict


def SkinsTool_getClassSet(self):
  portal = self.getPortalObject()
  class_set = set([])
  # TODO: sort by default skin selection and use  the ones registered in skin selections
  for skin_folder in portal.portal_skins.objectValues():
    for script in skin_folder.objectValues(spec=('Script (Python)',
                                                 'External Method')):
      if not '_' in script.getId():
        logger.debug('Skipping wrongly named script %s', script.getId())
        continue
      type_ = script.getId().split('_')[0]
      class_set.add(type_)
  return class_set


def SkinsTool_getStubForClass(self, class_name):
  portal = self.getPortalObject()
  line_list = []
  SkinDefinition = namedtuple(
      'SkinDefinition', 'id,docstring,type_comment,skin_folder,params')
  import parso
  grammar = parso.load_grammar()
  import re
  type_coment_re = re.compile(r"\s*#\s*type:.*")
  # collect skins by type
  skin_by_type = defaultdict(list)
  # TODO: sort by default skin selection and use only the ones registered in skin selections
  for skin_folder in portal.portal_skins.objectValues():
    for script in skin_folder.objectValues(spec=('Script (Python)',
                                                 'External Method')):
      if not '_' in script.getId():
        logger.debug('Skipping wrongly named script %s', script.getId())
        continue
      type_ = script.getId().split('_')[0]
      if type_ != class_name:
        continue
      docstring = '"""External method"""'
      params = ''
      type_comment = ''
      if script.meta_type == 'Script (Python)':
        body = script.body()
        params = script.params()
        if params:
          params = ', {}'.format(params)
        icon_path = script.om_icons()[0]['path']
        icon_alt = script.om_icons()[0]['alt']
        docstring_first_line = (
            "![{icon_alt}]({portal_url}/{icon_path}) "
            "[`{script_id}`]({portal_url}/portal_skins/{skin_folder_id}/{script_id}/manage_main)\n"
        ).format(
            icon_alt=icon_alt,
            portal_url=portal.absolute_url(),
            icon_path=icon_path,
            script_id=script.getId(),
            skin_folder_id=skin_folder.getId())
        docstring = '"""{}"""'.format(docstring_first_line)
        module = grammar.parse(body)
        if next(iter(grammar.iter_errors(module)), None) is not None:
          first_leaf = module.get_first_leaf()
          type_comment = first_leaf.prefix.strip()
          if not type_coment_re.match(type_comment):
            type_comment = ''
          else:
            # make sure docstring is indented
            type_comment = '{}\n    '.format(type_comment)

          if first_leaf.type == 'string':
            original_docstring = first_leaf.value
            if original_docstring.startswith("'''"):
              docstring = "'''{}\n{}".format(
                  docstring_first_line, original_docstring[3:])
            elif original_docstring.startswith("'"):
              docstring = "'''{}\n{}''".format(
                  docstring_first_line, original_docstring[1:])
            elif original_docstring.startswith('"""'):
              docstring = '"""{}\n{}'.format(
                  docstring_first_line, original_docstring[3:])
            elif original_docstring.startswith('"'):
              docstring = '"""{}\n{}""'.format(
                  docstring_first_line, original_docstring[1:])

      skin_by_type[type_].append(
          SkinDefinition(
              script.getId(),
              docstring,
              type_comment,
              skin_folder.getId(),
              params))

  for type_, skins in skin_by_type.items():
    line_list.append(
        textwrap.dedent(
            """\
    import erp5.portal_type
    from erp5 import portal_type
     
    class {class_name}:
      {docstring}
    
    """).format(
                class_name=safe_python_identifier(type_),
                docstring=safe_docstring("Skins for {}".format(type_))))
    for skin in skins:
      skin = skin  # type: SkinDefinition
      line_list.append(
          # the comment is also here so that dedent keep indentation, because this method block needs
          # more indentation than class block
          textwrap.dedent(
              """\
      # {skin_id} in {skin_folder}
        def {skin_id}(self{params}):
          {type_comment}{docstring}
    """).format(
                  skin_id=skin.id,
                  skin_folder=skin.skin_folder,
                  params=skin.params,
                  type_comment=skin.type_comment,
                  docstring=skin.docstring))
  return "\n".join(line_list)


def TypeInformation_getStub(self):
  # type: (ERP5TypeInformation) -> str
  """returns a .pyi stub file for this portal type

  https://www.python.org/dev/peps/pep-0484/
  """
  portal = self.getPortalObject()

  # TODO: getParentValue
  # TODO: a class for magic things like getPortalObject ?

  @WorkflowMethod.disable
  def makeTempClass():
    # everything is allowed in portal trash so we create our
    # temp object there.
    return portal.portal_trash.newContent(
        portal_type=self.getId(), temp_object=True, id='?', title='?').__class__

  temp_class = makeTempClass()

  # mro() of temp objects is like :
  # (<class 'erp5.temp_portal_type.Temporary Person Module'>,
  #  <class 'Products.ERP5Type.mixin.temporary.TemporaryDocumentMixin'>,
  #  <class 'erp5.portal_type.Person Module'>,      <-- this is the generated class.
  #  <class 'Products.ERP5.Document.Person.Person'>,   <-- this is the source code of the "real" class,
  #                                                        extending other "real" classes
  #  ...
  temp_class = temp_class.mro()[2]
  parent_class = temp_class.mro()[1]
  parent_class_module = parent_class.__module__

  imports = set([
      'from erp5.portal_type import Type_CatalogBrain',
      'from erp5.portal_type import Type_AnyPortalTypeList',
      'from erp5.portal_type import Type_AnyPortalTypeCatalogBrainList',
      'from typing import Union, List, Optional, Any, overload, Literal, TypeVar, Generic',
      'from DateTime import DateTime.DateTime as DateTime # XXX help jedi',
  ])
  header = ""
  methods = []
  debug = ""
  method_template_template = """  {decorator}\n  def {method_name}({method_args}) -> {return_type}:\n    {docstring}"""

  methods.append(
      method_template_template.format(
          decorator='',
          method_name='getPortalType',
          method_args="self",
          return_type='Literal["{}"]'.format(self.getId()),
          # We want to be able to infer based on the portal type named returned by x.getPortalType()
          # jedi does not support Literal in this context, so add a method implementation.
          # This is not really valid for a .pyi, but jedi does not care.
          docstring="{}\n    return '{}'".format(
              safe_docstring(self.getId()), self.getId())))

  # XXX debug
  methods.append(
      method_template_template.format(
          decorator='',
          method_name='reveal_portal_tye_{}'.format(
              safe_python_identifier(self.getId())),
          method_args='self',
          return_type='',
          docstring=safe_docstring("ahaha cool :)")))

  imports.add('from erp5.portal_type import ERP5Site')
  methods.append(
      method_template_template.format(
          decorator='',
          method_name='getPortalObject',
          method_args="self",
          return_type='ERP5Site',
          docstring=safe_docstring(
              getattr(temp_class.getPortalObject, '__doc__', None) or '...')))

  # first class contain workflow and some constraints.
  for property_name in sorted(vars(temp_class)):
    if property_name[0] == '_':
      continue
    property_value = getattr(temp_class, property_name)
    if isinstance(property_value, Constant.Getter):
      # TODO: add an implementation returning the value so that jedi can infer
      methods.append(
          method_template_template.format(
              decorator='',
              method_name=safe_python_identifier(property_name),
              method_args="self",
              return_type=type(property_value.value).__name__,
              docstring=safe_docstring('TODO %s' % property_value)))
    elif isinstance(property_value,
                    (WorkflowState.TitleGetter,
                     WorkflowState.TranslatedGetter,
                     WorkflowState.TranslatedTitleGetter,
                     WorkflowState.Getter)):
      # TODO: docstring (with link to workflow)
      methods.append(
          method_template_template.format(
              decorator='',
              method_name=safe_python_identifier(property_name),
              method_args="self",
              return_type="str",
              docstring=safe_docstring('TODO %s' % property_value)))
    elif isinstance(property_value, WorkflowMethod):
      # TODO: docstring (with link to workflow)
      # TODO: also docstring for interaction methods (and maybe something clever so that if we
      # have an interaction on _setSomething the docstring of setSomething mention it).
      methods.append(
          method_template_template.format(
              decorator='',
              method_name=safe_python_identifier(property_name),
              method_args="self",
              return_type='None',
              docstring=safe_docstring('TODO %s' % property_value)))
    elif property_name.startswith(
        'serialize'
    ):  # isinstance(property_value, WorkflowState.SerializeGetter): XXX not a class..
      methods.append(
          method_template_template.format(
              decorator='',
              method_name=safe_python_identifier(property_name),
              method_args="self",
              return_type='None',
              docstring=safe_docstring(
                  getattr(property_value, '__doc__', None))))
    # TODO: generated methods for categories.
    else:
      debug += "\n  # not handled property: {} -> {} {}".format(
          property_name,
          property_value,
          getattr(property_value, '__dict__', ''))

  # for folderish contents, generate typed contentValues
  allowed_content_types = self.getTypeAllowedContentTypeList()
  allowed_content_types_classes = [
      safe_python_identifier(t) for t in allowed_content_types
  ]
  if allowed_content_types and hasattr(temp_class, 'contentValues'):
    for allowed in allowed_content_types_classes:
      imports.add('from erp5.portal_type import {}'.format(allowed))
    if len(allowed_content_types) == 1:
      subdocument_type = '{}'.format(allowed_content_types_classes[0])
    else:
      subdocument_type = 'Union[{}]'.format(
          ', '.join(allowed_content_types_classes))

    # TODO: getParentValue

    for method_name in ('contentValues', 'objectValues', 'searchFolder'):
      return_type = 'List[{}]'.format(subdocument_type)
      if method_name == 'searchFolder':
        return_type = 'List[Type_CatalogBrain[{}]]'.format(subdocument_type)
        if len(allowed_content_types) > 1:
          # not correct but it makes jedi complete well when portal_type='one'
          return_type = 'Union[{}]'.format(
              ', '.join((
                  'List[Type_CatalogBrain[{}]]'.format(t)
                  for t in allowed_content_types_classes)))
      methods.append(
          method_template_template.format(
              decorator='',
              method_name=method_name,
              method_args="self",
              return_type=return_type,
              docstring=safe_docstring(
                  getattr(getattr(temp_class, method_name), '__doc__', None))))

    methods.append(
        method_template_template.format(
            decorator='',
            method_name='newContent',
            method_args="self",  # TODO
            return_type=subdocument_type,
            docstring=safe_docstring(
                getattr(temp_class.newContent, '__doc__', None))))

    # getattr, getitem and other Zope.OFS alais returns an instance of allowed content types.
    # so that portal.person_module['1'] is a person
    for method_name in (
        '__getattr__',
        '__getitem__',
        '_getOb',
        'get',):
      methods.append(
          method_template_template.format(
              decorator='',
              method_name=method_name,
              method_args="self, attribute:str",
              return_type=subdocument_type,
              docstring='...'))

  for identity_method in (
      'getObject',
      'asContext',
      '__of__',):
    method = getattr(temp_class, identity_method, None)
    if method is not None:
      methods.append(
          method_template_template.format(
              decorator='',
              method_name=identity_method,
              method_args="self",  # TODO
              return_type=safe_python_identifier(temp_class.__name__),
              docstring=safe_docstring(getattr(method, '__doc__', None))))

  # the parent class is imported in a name that should not clash
  parent_class_alias = '{class_name}_parent_{parent_class}'.format(
      class_name=safe_python_identifier(temp_class.__name__),
      parent_class=safe_python_identifier(parent_class.__name__))
  base_classes = [parent_class_alias]
  for pc in temp_class.mro():
    if pc.__module__ == 'erp5.accessor_holder.property_sheet':
      # Fake name for property sheets
      prefixed_class_name = 'property_sheet_{}'.format(
          safe_python_identifier(pc.__name__))
      imports.add(
          'from erp5.accessor_holder import {} as {}'.format(
              safe_python_identifier(pc.__name__), prefixed_class_name))
      base_classes.append(prefixed_class_name)

    # Fake name for skins
    prefixed_class_name = 'skins_tool_{}'.format(
        safe_python_identifier(pc.__name__))
    imports.add(
        'from erp5.skins_tool import {} as {}'.format(
            safe_python_identifier(pc.__name__), prefixed_class_name))
    base_classes.append(prefixed_class_name)

  # everything can use ERP5Site_ skins
  imports.add('from erp5.skins_tool import ERP5Site as skins_tool_ERP5Site')
  base_classes.append('skins_tool_ERP5Site')

  base_classes.append(prefixed_class_name)

  class_template = textwrap.dedent(
      """\
  {header}
  {imports}
  from {parent_class_module} import {parent_class} as {parent_class_alias}
  class {class_name}({base_classes}):
    {docstring}
  {methods}
  {debug}
  """)

  docstring = textwrap.dedent(
      '''
  # {type_title_or_id}
  ---
  {type_description}

  {type_url}
  ''').format(
          type_title_or_id=self.getTitleOrId(),
          type_description=self.getDescription(),
          type_url=self.absolute_url())

  return class_template.format(
      imports="\n".join(sorted(imports)),
      header=header,
      docstring=safe_docstring(docstring),
      class_name=safe_python_identifier(temp_class.__name__),
      base_classes=', '.join(base_classes),
      parent_class=safe_python_identifier(parent_class.__name__),
      parent_class_alias=parent_class_alias,
      parent_class_module=safe_python_identifier(parent_class_module),
      methods="\n".join(methods),
      debug=debug)


from Products.ERP5Type.Core.PropertySheet import PropertySheet  #  pylint: disable=unused-import


def PropertySheetTool_getStub(self):
  print('PropertySheetTool_getStub start')
  sources = []
  for ps in self.getPortalObject().portal_property_sheets.contentValues():
    try:
      sources.append(PropertySheet_getStub(ps))
    except Exception:
      logger.exception('error generating stub for %s', ps.getId())
  print('PropertySheetTool_getStub end')
  return "\n".join(sources)


def PropertySheet_getStub(self):
  # type: (PropertySheet) -> str
  """returns a .pyi stub file for this property sheet

  https://www.python.org/dev/peps/pep-0484/
  """
  portal_categories = self.getPortalObject().portal_categories

  class_template = textwrap.dedent(
      """\
  {imports}
  class {class_name}:
    '''{property_sheet_id}

    {property_sheet_description}
    '''
  {methods}
  {debug}
  """)
  debug = ''
  methods = []
  imports = [
      'from typing import Optional, List, Any',
      'from DateTime import DateTime',
      'from erp5.portal_type import Type_CatalogBrain',
      'from erp5.portal_type import Type_AnyPortalType',
      'from erp5.portal_type import Type_AnyPortalTypeList'
  ]
  method_template_template = """  def {method_name}({method_args}) -> {return_type}:\n    {docstring}"""

  # debug
  methods.append(
      method_template_template.format(
          method_name='reveal_property_sheet_{}'.format(
              safe_python_identifier(self.getId())),
          method_args='self',
          return_type='str',
          docstring=safe_docstring("ahaha cool :)")))

  def _getPythonTypeFromPropertySheetType(prop):
    # type: (erp5.portal_type.StandardProperty) -> str
    property_sheet_type = prop.getElementaryType()
    if property_sheet_type in ('content', 'object'):
      # TODO
      return 'Any'
    mapped_type = {
        'string': 'str',
        'boolean': 'bool',
        'data': 'bytes',
          # XXX jedi does not understand DateTime dynamic name, so use "real name"
        'date': 'DateTime.DateTime',
        'int': 'int',
        'long': 'int',  # ???
        'lines': 'List[str]',
        'tokens': 'List[str]',
        'float': 'float',
        'text': 'str',
    }.get(property_sheet_type, 'Any')
    if prop.isMultivalued():
      return 'List[{}]'.format(mapped_type)
    return mapped_type

  from Products.ERP5Type.Utils import convertToUpperCase
  from Products.ERP5Type.Utils import evaluateExpressionFromString
  from Products.ERP5Type.Utils import createExpressionContext
  expression_context = createExpressionContext(self)

  for prop in self.contentValues():

    if prop.getPortalType() in ('Standard Property', 'Acquired Property'):
      docstring = safe_docstring(
          textwrap.dedent(
              """\
        [{property_sheet_title} {property_reference}]({property_url})

        {property_description}
        """).format(
                  property_description=prop.getDescription(),
                  property_sheet_title=self.getTitle(),
                  property_reference=prop.getReference(),
                  property_url=prop.absolute_url()))
      methods.append(
          method_template_template.format(
              method_name='get{}'.format(
                  convertToUpperCase(prop.getReference())),
              method_args='self',
              return_type=_getPythonTypeFromPropertySheetType(prop),
              docstring=docstring))
      if prop.getElementaryType() == 'boolean':
        methods.append(
            method_template_template.format(
                method_name='is{}'.format(
                    convertToUpperCase(prop.getReference())),
                method_args='self',
                return_type=_getPythonTypeFromPropertySheetType(prop),
                docstring=docstring))
      methods.append(
          method_template_template.format(
              method_name='set{}'.format(
                  convertToUpperCase(prop.getReference())),
              method_args='self, value:{}'.format(
                  _getPythonTypeFromPropertySheetType(prop)),
              return_type='None',
              docstring=docstring))
    elif prop.getPortalType() in ('Category Property',
                                  'Dynamic Category Property'):
      if prop.getPortalType() == 'Dynamic Category Property':
        category_id_list = evaluateExpressionFromString(
            expression_context, prop.getCategoryExpression())
      else:
        category_id_list = [prop.getReference()]

      for category in category_id_list:
        category_value = portal_categories._getOb(category, None)
        if category_value is None:
          continue

        docstring = safe_docstring(
            textwrap.dedent(
                """\
          [{property_sheet_title} {property_reference}]({property_url})

          [{category_title}]({category_url})

          {property_description}
          {category_description}
          """).format(
                    property_description=prop.getDescription(),
                    property_sheet_title=self.getTitle(),
                    property_reference=prop.getReference() or '',
                    property_url=prop.absolute_url(),
                    category_title=category_value.getTitle(),
                    category_url=category_value.absolute_url(),
                    category_description=category_value.getDescription(),
                ))

        methods.append(
            method_template_template.format(
                method_name='get{}'.format(
                    convertToUpperCase(category_value.getId())),
                method_args='self',
                return_type='str',
                docstring=docstring))
        methods.append(
            method_template_template.format(
                method_name='get{}Title'.format(
                    convertToUpperCase(category_value.getId())),
                method_args='self',
                return_type='str',
                docstring=docstring))
        methods.append(
            method_template_template.format(
                method_name='get{}TranslatedTitle'.format(
                    convertToUpperCase(category_value.getId())),
                method_args='self',
                return_type='str',
                docstring=docstring))
        methods.append(
            method_template_template.format(
                method_name='get{}Value'.format(
                    convertToUpperCase(category_value.getId())),
                method_args='self',
                return_type='Type_AnyPortalType',
                docstring=docstring))
        methods.append(
            method_template_template.format(
                method_name='get{}ValueList'.format(
                    convertToUpperCase(category_value.getId())),
                method_args='self',
                return_type='Type_AnyPortalTypeList',
                docstring=docstring))
        methods.append(
            method_template_template.format(
                method_name='set{}'.format(
                    convertToUpperCase(category_value.getId())),
                method_args='self, value: str',
                return_type='None',
                docstring=docstring))
        methods.append(
            method_template_template.format(
                method_name='set{}Value'.format(
                    convertToUpperCase(category_value.getId())),
                method_args='self, value: Base',
                return_type='None',
                docstring=docstring))
        methods.append(
            method_template_template.format(
                method_name='set{}ValueList'.format(
                    convertToUpperCase(category_value.getId())),
                method_args='self, value_list: List[Base]',
                return_type='None',
                docstring=docstring))

  return class_template.format(
      imports='\n'.join(imports),
      class_name=safe_python_identifier(self.getId()),
      property_sheet_id=self.getId(),
      property_sheet_description=self.getDescription().replace(
          "'''", r"\\'\\'\\'"),
      methods='\n'.join(methods),
      debug=debug,
  )


from Products.ERP5.ERP5Site import ERP5Site  # pylint: disable=unused-import


def ERP5Site_getPortalStub(self):
  # type: (ERP5Site) -> str

  module_stub_template = textwrap.dedent(
      '''
      @property
      def {module_id}(self):
        from erp5.portal_type import {module_class_name}
        return {module_class_name}()
      ''')
  tool_stub_template = textwrap.dedent(
      '''
      @property
      def {tool_id}(self):
        {tool_import}
        return {tool_class}()
      ''')
  source = []
  for m in self.objectValues():
    if m.getPortalType().endswith('Module'):
      source.extend(
          module_stub_template.format(
              module_id=m.getId(),
              module_class_name=safe_python_identifier(
                  m.getPortalType())).splitlines())

    else:
      tool_class = safe_python_identifier(m.__class__.__name__)
      tool_import = 'from {} import {}'.format(
          m.__class__.__module__, tool_class)
      if m.getId() == 'portal_catalog':
        tool_class = 'ICatalogTool'  # XXX these I-prefix are stupid
        tool_import = 'from erp5.portal_type import ICatalogTool'
      elif m.getId() == 'portal_simulation':
        tool_class = 'ISimulationTool'  # XXX these I-prefix are stupid
        tool_import = 'from erp5.portal_type import ISimulationTool'

      source.extend(
          tool_stub_template.format(
              tool_id=m.getId(), tool_class=tool_class,
              tool_import=tool_import).splitlines())

      # TODO: tools with at least base categories for CategoryTool

  return textwrap.dedent(
      '''
      from Products.ERP5Site.ERP5Site import ERP5Site as ERP5Site_parent_ERP5Site
      from erp5.skins_tool import ERP5Site as skins_tool_ERP5Site
      from erp5.skins_tool import Base as skins_tool_Base
      class ERP5Site(ERP5Site_parent_ERP5Site, skins_tool_ERP5Site, skins_tool_Base):
        {}
        def getPortalObject(self):
          return self
      ''').format('\n  '.join(source))


def ERP5Site_dumpModuleCode(self, component_or_script=None):
  """Save code in filesystem for jedi to use it.

  Generate stubs for erp5.* dynamic modules and copy the in-ZODB modules
  to files.
  """
  def mkdir_p(path):
    if not os.path.exists(path):
      os.mkdir(path, 0o700)

  # this import is for type annotation, but pylint does not understand this.
  import erp5.portal_type  # pylint: disable=unused-variable

  portal = self.getPortalObject()  # type: erp5.portal_type.ERP5Site
  module_dir = '/tmp/ahaha/erp5/'  # TODO
  mkdir_p(module_dir)

  # generate erp5/__init__.py
  with open(
      os.path.join(module_dir, '__init__.py'),
      'w',) as erp5__init__f:
    for module in (
        'portal_type',
        'accessor_holder',
        'skins_tool',
        'component',):
      erp5__init__f.write('from . import {module}\n'.format(module=module))
      mkdir_p(os.path.join(module_dir, module))
      if module == 'portal_type':
        # portal types
        all_portal_type_class_names = []
        with open(
            os.path.join(
                module_dir,
                module,
                '__init__.py',),
            'w',) as module_f:
          for ti in portal.portal_types.contentValues():
            class_name = safe_python_identifier(ti.getId())
            all_portal_type_class_names.append(class_name)
            module_f.write(
                'from .{class_name} import {class_name}\n'.format(
                    class_name=class_name))
            with open(
                os.path.join(
                    module_dir,
                    module,
                    '{class_name}.pyi'.format(class_name=class_name),
                ),
                'w',
            ) as type_information_f:
              type_information_f.write(
                  ti.TypeInformation_getStub().encode('utf-8'))

          # portal type groups ( useful ? used in Simulation Tool only )
          portal_types_by_group = defaultdict(list)
          for ti_for_group in portal.portal_types.contentValues():
            for group in ti_for_group.getTypeGroupList():
              portal_types_by_group[group].append(
                  safe_python_identifier(ti_for_group.getId()))

          for group, portal_type_class_list in portal_types_by_group.items():
            group_class = 'Group_{}'.format(group)
            module_f.write(
                'from .{} import {}\n'.format(group_class, group_class))
            with open(
                os.path.join(
                    module_dir,
                    module,
                    '{}.pyi'.format(group_class),),
                'w',
            ) as group_f:
              group_f.write(
                  textwrap.dedent(
                      '''
                      {imports}
                      class {group_class}({bases}):
                        """All portal types of group {group}.
                        """
                      ''').format(
                          imports='\n'.join(
                              'from erp5.portal_type import {}'.format(
                                  portal_type_class)
                              for portal_type_class in portal_type_class_list),
                          group_class=group_class,
                          bases=', '.join(portal_type_class_list),
                          group=group))

          # tools with extra type annotations
          module_f.write('from .ICatalogTool import ICatalogTool\n')
          with open(
              os.path.join(
                  module_dir,
                  module,
                  'ICatalogTool.pyi',),
              'w',) as portal_f:
            portal_f.write(
                textwrap.dedent(
                    '''
                    from Products.ERP5Catalog.Tool.ERP5CatalogTool import ERP5CatalogTool
                    # XXX CatalogTool itself has a portal type
                    
                    from erp5.portal_type import Type_AnyPortalTypeCatalogBrainList

                    class ICatalogTool(ERP5CatalogTool):
                      def searchResults(self) -> Type_AnyPortalTypeCatalogBrainList:
                        """Search Catalog"""
                      def __call__(self) -> Type_AnyPortalTypeCatalogBrainList:
                        """Search Catalog"""

                    '''))

          module_f.write('from .ISimulationTool import ISimulationTool\n')
          with open(
              os.path.join(
                  module_dir,
                  module,
                  'ISimulationTool.pyi',),
              'w',) as portal_f:
            portal_f.write(
                textwrap.dedent(
                    '''
                    from erp5.portal_type import SimulationTool
                    from erp5.portal_type import Type_AnyPortalTypeInventoryListBrainList

                    class ISimulationTool(SimulationTool):
                      def getInventoryList() -> Type_AnyPortalTypeInventoryListBrainList:
                        ...

                    '''))

          # portal object
          module_f.write('from .ERP5Site import ERP5Site\n')
          with open(
              os.path.join(
                  module_dir,
                  module,
                  'ERP5Site.pyi',),
              'w',) as portal_f:
            portal_f.write(ERP5Site_getPortalStub(self.getPortalObject()))

          # some type helpers
          module_f.write('from .Type_CatalogBrain import Type_CatalogBrain\n')
          with open(
              os.path.join(
                  module_dir,
                  module,
                  'Type_CatalogBrain.pyi',),
              'w',) as catalog_brain_f:
            catalog_brain_f.write(
                textwrap.dedent(
                    '''
                    from typing import TypeVar, Generic
              
                    T = TypeVar('T')
                    class Type_CatalogBrain(Generic[T]):
                      id: str
                      path: str
                      def getObject(self) -> T:
                        ...
              '''))
          module_f.write(
              'from .Type_InventoryListBrain import Type_InventoryListBrain\n')
          with open(
              os.path.join(
                  module_dir,
                  module,
                  'Type_InventoryListBrain.pyi',),
              'w',
          ) as catalog_brain_f:
            catalog_brain_f.write(
                textwrap.dedent(
                    '''
                    from typing import TypeVar, Generic
                    from erp5.component.extension.InventoryBrain import InventoryListBrain
                    from DateTime import DateTime.DateTime as DateTime
                    from erp5.portal_type import Group_node
                    from erp5.portal_type import Group_resource

                    T = TypeVar('T')
                    class Type_InventoryListBrain(Generic[T], InventoryListBrain):
                      node_uid: int
                      mirror_node_uid: int
                      section_uid: int
                      mirror_section_uid: int
                      function_uid: int
                      project_uid: int
                      function_uid: int
                      funding_uid: int
                      ledger_uid: int
                      payment_request_uid: int
                      
                      node_value: Group_node
                      mirror_node_value: Group_node
                      section_value: Group_node
                      mirror_section_value: Group_node
                      resource_value: Group_resource

                      date: DateTime
                      mirror_date: DateTime

                      variation_text: str
                      sub_variation_text: str
                      simulation_state: str

                      inventory: float
                      total_price: float
                      
                      path: str
                      stock_uid: uid
                      def getObject(self) -> T:
                        ...

              '''))

          module_f.write('from typing import List, Union\n')
          module_f.write(
              'Type_AnyPortalType = Union[\n  {}]\n'.format(
                  ',\n  '.join(
                      '{}'.format(portal_type_class)
                      for portal_type_class in all_portal_type_class_names),
              ))
          module_f.write(
              'Type_AnyPortalTypeList = Union[\n  {}]\n'.format(
                  ',\n  '.join(
                      'List[{}]'.format(portal_type_class)
                      for portal_type_class in all_portal_type_class_names)))
          module_f.write(
              'Type_AnyPortalTypeCatalogBrainList = Union[\n  {}]\n'.format(
                  ',\n  '.join(
                      'List[Type_CatalogBrain[{}]]'.format(portal_type_class)
                      for portal_type_class in all_portal_type_class_names),
              ))
          module_f.write(
              'Type_AnyPortalTypeInventoryListBrainList = Union[\n  {}]\n'
              .format(
                  ',\n  '.join(
                      'List[Type_InventoryListBrain[{}]]'.format(
                          portal_type_class)
                      for portal_type_class in all_portal_type_class_names),
              ))

      elif module == 'accessor_holder':
        # TODO: real path is accessor_holder.something !?
        with open(
            os.path.join(module_dir, module, '__init__.py'),
            'w',) as accessor_holder_f:
          for ps in portal.portal_property_sheets.contentValues():
            class_name = safe_python_identifier(ps.getId())
            accessor_holder_f.write(
                'from .{class_name} import {class_name}\n'.format(
                    class_name=class_name))
            with open(
                os.path.join(
                    module_dir,
                    module,
                    '{class_name}.pyi'.format(class_name=class_name),
                ),
                'w',
            ) as property_sheet_f:
              property_sheet_f.write(ps.PropertySheet_getStub().encode('utf-8'))
      elif module == 'skins_tool':
        skins_tool = portal.portal_skins
        with open(
            os.path.join(module_dir, module, '__init__.py'),
            'w',) as skins_tool_f:
          for class_name in SkinsTool_getClassSet(skins_tool):
            skins_tool_f.write(
                'from {class_name} import {class_name}\n'.format(
                    class_name=class_name))
            with open(
                os.path.join(
                    module_dir,
                    module,
                    '{}.pyi'.format(class_name),),
                'w',
            ) as skin_f:
              skin_f.write(
                  SkinsTool_getStubForClass(
                      skins_tool,
                      class_name,).encode('utf-8'))
      elif module == 'component':
        # TODO: component versions ?
        module_to_component_portal_type_mapping = {
            'test': 'Test Component',
            'document': 'Document Component',
            'extension': 'Extension Component',
            'tool': 'Tool Component',
            'module': 'Module Component',
            'interface': 'Interface Component',
        }
        with open(
            os.path.join(module_dir, module, '__init__.py'),
            'w',) as component_module__init__f:
          for sub_module, portal_type in module_to_component_portal_type_mapping.items():
            component_module__init__f.write(
                'from . import {}\n'.format(sub_module))
            mkdir_p(os.path.join(module_dir, module, sub_module))
            with open(
                os.path.join(module_dir, module, sub_module, '__init__.py'),
                'w',
            ) as component_sub_module_init_f:
              for brain in portal.portal_catalog(
                  portal_type=portal_type, validation_state=('validated',)):
                component = brain.getObject()
                component_sub_module_init_f.write(
                    "from {component_reference} import {component_reference}\n"
                    .format(component_reference=component.getReference()))
                with open(
                    os.path.join(
                        module_dir,
                        module,
                        sub_module,
                        '{}.py'.format(component.getReference()),
                    ),
                    'w',
                ) as component_f:
                  component_f.write(component.getTextContent())  #.encode('utf-8'))
  return 'done'
