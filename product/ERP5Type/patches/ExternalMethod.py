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
from Products.ExternalMethod.ExternalMethod import *
from Products.ERP5Type.Globals import InitializeClass
from zLOG import LOG, WARNING
from . import PatchClass
from .PythonScript import addGuard

class _(PatchClass(ExternalMethod)):

    reloadIfChanged = getFuncDefaults = getFuncCode = filepath = None

    @property
    def func_defaults(self):
        return self.getFunction()[1]

    @property
    def func_code(self):
        return self.getFunction()[2]

    def getFunction(self, reload=False):
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
        ff = getattr(f, 'im_func', f)
        self._v_f = _f = f, ff.func_defaults, FuncCode(ff, f is not ff)
        return _f

    def __call__(self, *args, **kw):
        """Call an ExternalMethod

        Calling an External Method is roughly equivalent to calling
        the original actual function from Python.  Positional and
        keyword parameters can be passed as usual.  Note however that
        unlike the case of a normal Python method, the "self" argument
        must be passed explicitly.  An exception to this rule is made
        if:

        - The supplied number of arguments is one less than the
          required number of arguments, and

        - The name of the function\'s first argument is 'self'.

        In this case, the URL parent of the object is supplied as the
        first argument.
        """
        self.checkGuard(True)

        _f = self.getFunction()
        f = _f[0]

        __traceback_info__ = args, kw, _f[1]

        # XXX: We'd like to use inspect.getcallargs instead of try..except.
        #      However, for the same reason as we use getargs instead of
        #      getargspec, we need something that works for any callable
        #      providing func_code & func_default (not only functions).
        try: return f(*args, **kw)
        except TypeError, v:
            tb=sys.exc_info()[2]
            try:
                func_args, func_varargs, _ = getargs(f.func_code)
                by_kw = set(kw)
                if f.func_defaults:
                    by_kw.update(func_args[-len(f.func_defaults):])
                if func_args[0] == 'self' and 'self' not in kw and (
                        func_varargs or len(set(func_args[len(args):]
                            ).difference(by_kw)) == 1):
                    return f(self.aq_parent.this(), *args, **kw)

                raise TypeError, v, tb
            finally: tb=None

    security = ClassSecurityInfo()

addGuard(ExternalMethod, change_external_methods)

InitializeClass(ExternalMethod)
