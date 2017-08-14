from AccessControl import ClassSecurityInfo
#
from Products.ERP5Type import Permissions, PropertySheet
#from App.special_dtml import HTMLFile
#from Products.ERP5Type.XMLObject import XMLObject
#from Products.PythonScripts.PythonScript import \
#  PythonScript as ZopePythonScript
#from Products.ERP5.mixin.expression import ExpressionMixin

from Products.ERP5.Document.PythonScript import PythonScript
from AccessControl.SecurityManagement import getSecurityManager
from Products.PythonScripts.PythonScript import PythonScriptTracebackSupplement
import new
#from Products.ERP5Type.Log import log
import sys

# securite enhacements for Cluster Data Script
# XXX: It impacts or guards, not only Cluster Data Script
# XXX: Is that good place or shall it go to product/ERP5Type/patches/Restricted.py ?
from AccessControl import (
  allow_module,
  allow_class,
  allow_type,
#  ModuleSecurityInfo,
)

allow_module('h5py')
allow_module('math')
allow_module('matplotlib.pyplot')
allow_module('numpy.random.mtrand')
allow_module('openpyxl')
from pandas.core.frame import DataFrame
allow_class(DataFrame)
DataFrame.__guarded_setitem__ = DataFrame.__setitem__.__func__
DataFrame.__guarded_delitem__ = DataFrame.__delitem__.__func__
allow_module('pandas.core.frame')
allow_module('pandas.core.groupby')
from pandas.core.groupby import DataFrameGroupBy
allow_class(DataFrameGroupBy)
allow_module('pandas.core.series')
from pandas.core.series import Series
allow_class(Series)
allow_type(type(Series.dt))
allow_module('pandas.core.strings')
from pandas.core.strings import StringMethods
allow_class(StringMethods)
allow_module('pandas.tseries.common')
allow_module('pylab')
allow_module('scipy')
allow_module('seaborn')
allow_module('sklearn')
allow_module('statsmodels')
allow_module('sympy')
allow_module('xlrd')

_marker = []

IGNORE_LOCAL_KEY_LIST = ['_print']
IGNORE_GLOBAL_KEY_LIST = [
  '_getiter_', '__metaclass__', 'context', 'sequence', '_print_', '__traceback_supplement__',
  '__file__', '_apply_', '_write_', '_getattr_', 'traverse_subpath', '__builtins__',
  'script', 'container', '_inplacevar_', '__name__', '__debug__', '_getitem_', '__package__']

class ClusterDataScript(PythonScript):
  """ Cluster Data Script for ERP5"""

  meta_type = 'ERP5 Cluster Data Script'
  portal_type = 'Cluster Data Script'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)
#
#    #View content list, Force /view, Standart option in python scripts
#    manage_options = ( XMLObject.manage_options[0],
#                       {'icon':'', 'label':'View','action':'view'}) \
#                       + ZopePythonScript.manage_options
#
   # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.PythonScript
                    # CatalogFilter property_sheet needed for bootstrapping
                    # some Python Script during ERP5 Catalog installation
                    , PropertySheet.CatalogFilter
                    )

  def _exec_with_fill(self, filler, *args, **kw):
    bindcode = getattr(self, '_v_bindcode', _marker)
    if bindcode is _marker:
      bindcode = self._prepareBindCode()

    security = getSecurityManager()
    security.addContext(self)
    try:
      if bindcode is None:
        bound_data = {}
      else:
        bound_data = []
        exec bindcode  # pylint: disable=W0122
        bound_data = bound_data[0]
      bound_data.update(filler)
      return self._exec(bound_data, (), {})
    finally:
      security.removeContext(self)

  def _exec(self, bound_names, args, kw):
    """Call a Python Script

    Calling a Python Script is an actual function invocation.
    """

    ft = self._v_ft
    if ft is None:
      __traceback_supplement__ = (  # pylint: disable=W0612
          PythonScriptTracebackSupplement, self)
      raise RuntimeError, '%s %s has errors.' % (self.meta_type, self.id)

    fcode, g, fadefs = ft  # pylint: disable=W0633
    g = g.copy()
    if bound_names is not None:
      g.update(bound_names)
    g['__traceback_supplement__'] = (
      PythonScriptTracebackSupplement, self, -1)
    g['__file__'] = getattr(self, '_filepath', None) or self.get_filepath()
    f = new.function(fcode, g, None, fadefs)

    class Executor(object):
      func_namespace = {}
      def execute(self, method, *args, **kwargs):
        def tracer(frame, event, arg):
          if event=='return':
            f_locals = frame.f_locals.copy()
            for k in IGNORE_LOCAL_KEY_LIST:
              f_locals.pop(k, None)
            f_globals = frame.f_globals.copy()
            for k in IGNORE_GLOBAL_KEY_LIST:
              f_globals.pop(k, None)
            self.func_namespace = f_locals
            self.func_namespace.update(f_globals)
        try:
          sys.setprofile(tracer)
          return method(*args, **kw)
        finally:
          sys.setprofile(None)

    executor = Executor()
    try:
      result = executor.execute(f, *args, **kw)
    except SystemExit:
      raise ValueError('SystemExit cannot be raised within a PythonScript')

    return result, executor.func_namespace