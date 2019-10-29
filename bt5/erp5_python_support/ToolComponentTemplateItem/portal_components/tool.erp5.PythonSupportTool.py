
import sys
from collections import namedtuple
import logging
import json
import functools
import textwrap
import enum

from typing import Union, List, Literal, Dict, NamedTuple, TYPE_CHECKING  # pylint: disable=unused-import

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions

import jedi

logger = logging.getLogger(__name__)


def loadJson(data):
  """Load json in objects (and not dictionaries like json.loads does by default).
  """
  return json.loads(
      data, object_hook=lambda d: namedtuple('Unknown', d.keys())(*d.values())
  )


def dumpsJson(data):
  """symetric of loadJson, dumps to json, with support of simple objects.
  """
  def flatten(obj):
    if hasattr(obj, '_asdict'):  # namedtuple
      obj = obj._asdict()
    if isinstance(obj, dict):
      return {k: flatten(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
      return [flatten(x) for x in obj]
    if hasattr(obj, '__dict__'):
      obj = obj.__dict__
    return obj

  return json.dumps(flatten(data))


def json_serialized(f):
  """Transparently deserialize `data` parameter and serialize the returned value to/as json.
  """
  @functools.wraps(f)
  def wrapper(self, data):
    return dumpsJson(f(self, loadJson(data)))

  return wrapper


Position = namedtuple('Position', 'lineNumber, column')
"""Position in the editor, same as monaco, ie. indexed from 1
"""

if TYPE_CHECKING:
  import erp5.portal_type  # pylint: disable=import-error,unused-import

  # XXX "Context" is bad name
  class Context:
    code = None  # type: str

  class PythonScriptContext(Context):
    script_name = None  # type: str
    bound_names = None  # type: List[str]
    params = None  # type: str

  class CompletionContext(Context):
    position = None  # type: Position

  class PythonScriptCompletionContext(CompletionContext, PythonScriptContext):
    """completion for portal_skins's Script (Python)
    """

  CompletionKind = Union[Literal['Method'],
                          Literal['Function'],
                          Literal['Constructor'],
                          Literal['Field'],
                          Literal['Variable'],
                          Literal['Class'],
                          Literal['Struct'],
                          Literal['Interface'],
                          Literal['Module'],
                          Literal['Property'],
                          Literal['Event'],
                          Literal['Operator'],
                          Literal['Unit'],
                          Literal['Value'],
                          Literal['Constant'],
                          Literal['Enum'],
                          Literal['EnumMember'],
                          Literal['Keyword'],
                          Literal['Text'],
                          Literal['Color'],
                          Literal['File'],
                          Literal['Reference'],
                          Literal['Customcolor'],
                          Literal['Folder'],
                          Literal['TypeParameter'],
                          Literal['Snippet'],
                         ]


class CompletionKind(enum.Enum): # pylint: disable=function-redefined
  Method = 'Method'
  Function = 'Function'
  Constructor = 'Constructor'
  Field = 'Field'
  Variable = 'Variable'
  Class = 'Class'
  Struct = 'Struct'
  Interface = 'Interface'
  Module = 'Module'
  Property = 'Property'
  Event = 'Event'
  Operator = 'Operator'
  Unit = 'Unit'
  Value = 'Value'
  Constant = 'Constant'
  Enum = 'Enum'
  EnumMember = 'EnumMember'
  Keyword = 'Keyword'
  Text = 'Text'
  Color = 'Color'
  File = 'File'
  Reference = 'Reference'
  Customcolor = 'Customcolor'
  Folder = 'Folder'
  TypeParameter = 'TypeParameter'
  Snippet = 'Snippet'


# https://microsoft.github.io/monaco-editor/api/interfaces/monaco.imarkdownstring.html
class IMarkdownString(NamedTuple('IMarkdownString', (('value', str),))):
  value = None  # type: str


class CompletionItem(NamedTuple(
    'CompletionItem',
    (
        ('label', str),
        ('kind', CompletionKind),
        ('detail', str),
        ('documentation', Union[str, IMarkdownString]),
        ('sortText', str),
        ('insertText', str),
    ))):
  """A completion item represents a text snippet that is proposed to complete text that is being typed.
  
  https://microsoft.github.io/monaco-editor/api/interfaces/monaco.languages.completionitem.html
  """
  label = None  # type: str
  kind = None  # type: CompletionKind
  detail = None  # type: str
  documentation = None  # type: Union[str, IMarkdownString]
  sortText = None  # type: str
  insertText = None  # type: str


logger = logging.getLogger(__name__)



class PythonSupportTool(BaseTool):
  """Tool to support code editors.
  """
  portal_type = 'Python Support Tool'
  meta_type = 'ERP5 {}'.format(portal_type)
  id = 'portal_python_support'
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.ManagePortal)

  def _getCode(self, completion_context):
    # type: (PythonScriptCompletionContext) -> str
    return ''

  def getStubPath(self):
    """The path where stubs are generated.
    """
    return "/tmp/stubs/"

  def _convertCompletion(self, completion):
    # type: (jedi.api.classes.Completion,) -> CompletionItem
    """Convert a completion from jedi format to the format used by text editors.
    """

    # map jedi type to the name of monaco.languages.CompletionItemKind
    # This mapping and this method are copied/inspired by jedi integration in python-language-server
    # https://github.com/palantir/python-language-server/blob/19b10c47988df504872a4fe07c421b0555b3127e/pyls/plugins/jedi_completion.py
    # python-language-server is Copyright 2017 Palantir Technologies, Inc. and distributed under MIT License.
    # https://github.com/palantir/python-language-server/blob/19b10c47988df504872a4fe07c421b0555b3127e/LICENSE
    _TYPE_MAP = {
        'none': CompletionKind.Value,
        'type': CompletionKind.Class,
        'tuple': CompletionKind.Class,
        'dict': CompletionKind.Class,
        'dictionary': CompletionKind.Class,
        'function': CompletionKind.Function,
        'lambda': CompletionKind.Function,
        'generator': CompletionKind.Function,
        'class': CompletionKind.Class,
        'instance': CompletionKind.Reference,
        'method': CompletionKind.Method,
        'builtin': CompletionKind.Class,
        'builtinfunction': CompletionKind.Function,
        'module': CompletionKind.Module,
        'file': CompletionKind.File,
        'xrange': CompletionKind.Class,
        'slice': CompletionKind.Class,
        'traceback': CompletionKind.Class,
        'frame': CompletionKind.Class,
        'buffer': CompletionKind.Class,
        'dictproxy': CompletionKind.Class,
        'funcdef': CompletionKind.Function,
        'property': CompletionKind.Property,
        'import': CompletionKind.Module,
        'keyword': CompletionKind.Keyword,
        'constant': CompletionKind.Variable,
        'variable': CompletionKind.Variable,
        'value': CompletionKind.Value,
        'param': CompletionKind.Variable,
        'statement': CompletionKind.Keyword,
    }  # type: Dict[str, CompletionKind]

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

    def _format_docstring(completion):
      # type: (jedi.api.classes.Completion,) -> Union[str, IMarkdownString]
      # XXX we could check based on completion.module_path() python's stdlib tend to be rst
      # but for now, we assume everything is markdown
      return IMarkdownString(completion.docstring())

    return {
        'label': _label(completion),
        'kind': _TYPE_MAP.get(completion.type),
        'detail': _detail(completion),
        'documentation': _format_docstring(completion),
        'sortText': _sort_text(completion),
        'insertText': completion.name
    }

  @json_serialized
  def getCompletions(self, completion_context):
    # type: (Union[CompletionContext, PythonScriptCompletionContext],) -> List[CompletionItem]
    """Returns completions.
    """
    script = JediController(
        self,
        # fixPythonScriptContext not here !
        fixPythonScriptContext(completion_context, self.getPortalObject())
    ).getScript()

    return [self._convertCompletion(c) for c in script.completions()]

  @json_serialized
  def getCodeLens(self, completion_context):
    # type: (Union[CompletionContext, PythonScriptCompletionContext],) -> List[CompletionItem]
    """Returns code lens.
    """

    return []


def fixPythonScriptContext(context, portal):
  # type: (Union[CompletionContext, PythonScriptCompletionContext], erp5.portal_type.ERP5Site) -> CompletionContext
  """Normalize completion context for python scripts
  ie. make a function with params and adjust the line number.
  """
  if not getattr(context, "bound_names"):
    return context

  def _guessParameterType(name, context_type=None):
    """guess the type of python script parameters based on naming conventions.
    """
    # TODO: `state_change` arguments for workflow scripts
    name = name.split('=')[
        0]  # support also assigned names (like REQUEST=None in params)
    if name == 'context' and context_type:
      return context_type
    if name in (
        'context',
        'container',):
      return 'erp5.portal_type.ERP5Site'
    if name == 'script':
      return 'Products.PythonScripts.PythonScript.PythonScript'
    if name == 'REQUEST':
      return 'ZPublisher.HTTPRequest.HTTPRequest'
    if name == 'RESPONSE':
      return 'ZPublisher.HTTPRequest.HTTPResponse'
    return 'str'  # assume string by default

  signature_parts = context.bound_names + (
      [context.params] if context.params else []
  )

  # guess type of `context`
  context_type = None
  if '_' in context:
    context_type = context.split('_')[0]
    if context_type not in [
        ti.replace(' ', '')  # XXX "python identifier"
        for ti in portal.portal_types.objectIds()
    ] + [
        'ERP5Site',]:
      logger.debug(
          "context_type %s has no portal type, using ERP5Site", context_type
      )
      context_type = None

  type_comment = "  #  type: ({}) -> None".format(
      ', '.join(
          [_guessParameterType(part, context_type) for part in signature_parts]
      )
  )

  def indent(text):
    return ''.join(("  " + line) for line in text.splitlines(True))

  context.code = textwrap.dedent(
      '''import erp5.portal_type;
      import Products.ERP5Type.Core.Folder;
      import ZPublisher.HTTPRequest;
      import Products.PythonScripts.PythonScript
      def {script_name}({signature}):
        {type_comment}
        {body}
        pass
      '''
  ).format(
      script_name=context.script_name,
      signature=', '.join(signature_parts),
      type_comment=type_comment,
      body=indent(context.code)
  )
  context.position.lineNumber += 6  # imports, fonction header + type comment
  context.position.column += 2  # re-indentation
  return context


class JediController(object):
  """Controls jedi.
  """
  def __init__(self, tool, context):
    # type: (PythonSupportTool, CompletionContext) -> None
    if not self._isEnabled():
      self._patchBuildoutSupport()
      self._enablePlugin()
    self._sys_path = [tool.getStubPath()] + sys.path
    self._context = context

  def _isEnabled(self):
    """is our plugin already enabled ?
    """
    return False

  def _enablePlugin(self):
    """Enable our ERP5 jedi plugin.
    """
  def _patchBuildoutSupport(self):
    """Patch jedi to disable buggy buildout.cfg support.
    """
    # monkey patch to disable buggy sys.path addition based on buildout.
    # https://github.com/davidhalter/jedi/issues/1325
    # rdiff-backup also seem to trigger a bug, but it's generally super slow and not correct for us.
    try:
      # in jedi 0.15.1 it's here
      from jedi.evaluate import sys_path as jedi_inference_sys_path  # pylint: disable=import-error,unused-import,no-name-in-module
    except ImportError:
      # but it's beeing moved. Next release (0.15.2) will be here
      # https://github.com/davidhalter/jedi/commit/3b4f2924648eafb9660caac9030b20beb50a83bb
      from jedi.inference import sys_path as jedi_inference_sys_path  # pylint: disable=import-error,unused-import,no-name-in-module
    _ = jedi_inference_sys_path.discover_buildout_paths  # make sure we found it here

    def dont_discover_buildout_paths(*args, **kw):
      return set()

    jedi_inference_sys_path.discover_buildout_paths = dont_discover_buildout_paths
    from jedi.api import project as jedi_api_project
    jedi_api_project.discover_buildout_paths = dont_discover_buildout_paths

  def getScript(self):
    # type: () -> jedi.Script
    """Returns a jedi.Script for this code.
    """
    # TODO: lock ! (and not only here)
    context = self._context
    return jedi.Script(
        context.code,
        context.position.lineNumber,
        context.position.column - 1,
        context.script_name,
        self._sys_path
    )

  @staticmethod
  def jedi_execute(callback, context, arguments):
    # type: (Callable[[Any], Any], jedi.Context, Any) -> Any
    """jedi plugin `execute`
    XXX
    """
    return "jedi executed"


class PythonCodeGenerator(object):
  """Generator python code for static analysis.
  """


# make sure PythonSupportTool is first, this is needed for dynamic components.
__all__ = (
    'PythonSupportTool', 'json_serialized', 'PythonCodeGenerator', 'Position'
)
