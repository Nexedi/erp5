##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from inspect import getargs
from types import MethodType
from Products.ExternalMethod.ExternalMethod import *
from Products.ERP5Type.Globals import InitializeClass
from zLOG import LOG, WARNING
from . import PatchClass
from .PythonScript import addGuard

class _(PatchClass(ExternalMethod)):

    reloadIfChanged = getFuncDefaults = getFuncCode = filepath = None

    @property
    def func_defaults(self):
        """Return a tuple of default values.
        The first value is for the "second" parameter (self is ommited)

        Example:
          componentFunction(self, form_id='', **kw)
          will have func_defaults = ('', )
        """
        return self._getFunction()[1]

    @property
    def func_code(self):
        return self._getFunction()[2]

    @property
    def func_args(self):
        """Return list of parameter names.

        Example:
          componentFunction(self, form_id='', **kw)
          will have func_args = ['self', 'form_id']
        """
        return self._getFunction()[4]

    def getFunction(self, reload=False):
        return self._getFunction(reload)[0]

    def _getFunction(self, reload=False):
        try:
            component_module = __import__(
                'erp5.component.extension.' + self._module,
                fromlist="*", level=0)
        except ImportError, e:
            if str(e) != "No module named " + self._module:
                # Fall back loudly if a component exists but is broken.
                # XXX: We used __import__ instead of
                #      erp5.component.extension.find_load_module
                #      because the latter is much slower.
                # XXX: Should we also fall back on FS if the module imports
                #      successfully but does not contain the wanted function?
                LOG("ERP5Type.dynamic", WARNING,
                    "Could not load Component module %r"
                    % ('erp5.component.extension.' + self._module),
                    error=1)
            if not reload:
                from Globals import DevelopmentMode
                if DevelopmentMode:
                    try:
                        last_read, path = self._v_fs
                    except AttributeError:
                        last_read = None
                        path = getPath('Extensions', self._module,
                                       suffixes=('', 'py', 'pyc'))
                    ts = os.stat(path)[stat.ST_MTIME]
                    if last_read != ts:
                        self._v_fs = ts, path
                        reload = True
            f = getObject(self._module, self._function, reload)
        else:
            f = getattr(component_module, self._function)
        try:
            _f = self._v_f
            if _f[0] is f:
                return _f
        except AttributeError:
            pass
        code = f.func_code
        argument_object = getargs(code)
        # reconstruct back the original names
        arg_list = argument_object.args[:]
        if argument_object.varargs:
            arg_list.append('*' + argument_object.varargs)
        if argument_object.keywords:
          arg_list.append('**' + argument_object.keywords)

        i = isinstance(f, MethodType)
        ff = f.__func__ if i else f
        has_self = len(arg_list) > i and arg_list[i] == 'self'
        i += has_self
        if i:
            code = FuncCode(ff, i)
        self._v_f = _f = (f, f.func_defaults, code, has_self, arg_list)
        return _f

    def __call__(self, *args, **kw):
        """Call an ExternalMethod

        Calling an External Method is roughly equivalent to calling
        the original actual function from Python.  Positional and
        keyword parameters can be passed as usual.  Note however that
        if first argument is 'self', and only in this case, the
        acquisition parent is passed as first positional parameter.
        """
        self.checkGuard(True)

        _f = self._getFunction()

        if _f[3]:
            return _f[0](self.aq_parent, *args, **kw)
        return _f[0](*args, **kw)

    security = ClassSecurityInfo()

addGuard(ExternalMethod, change_external_methods)

InitializeClass(ExternalMethod)
