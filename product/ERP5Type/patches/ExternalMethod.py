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
from AccessControl import ModuleSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Acquisition import aq_parent
from Products.ERP5Type.patches.PythonScript import _guard_form, \
     _guard_manage_options, checkGuard, getGuard, manage_guardForm, \
     manage_setGuard
from zExceptions import Forbidden

if 1:
    def getFunction(self, reload=False, f=None):
        """
        Patch to get ZODB Component Extension function if available, otherwise
        fallback on filesystem Extension
        Patch2: do not use hasattr.
        """
        if f is None:
            try:
                component_module = __import__(
                    'erp5.component.extension.' + self._module,
                    fromlist=['erp5.component.extension'],
                    level=0)
            except ImportError:
                f = getObject(self._module, self._function, reload)
            else:
                f = getattr(component_module, self._function)

        ff = getattr(f, 'im_func', f)

        self._v_func_defaults  = ff.func_defaults
        self._v_func_code = FuncCode(ff,f is not ff)

        self._v_f=f

        return f

    ExternalMethod.getFunction = getFunction

    ExternalMethod_reloadIfChanged = ExternalMethod.reloadIfChanged
    def reloadIfChanged(self):
        try:
            component_module = __import__(
                'erp5.component.extension.' + self._module,
                fromlist=['erp5.component.extension'],
                level=0)
        except ImportError:
            return ExternalMethod_reloadIfChanged(self)

    ExternalMethod.reloadIfChanged = reloadIfChanged

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

        Monkey patches:
        - check guard against context, if guard exists.
        - call ZODB Component Extension, by trying first to import ZODB
          Component Extension if available, otherwise fallback on filesystem
          Extension
        - access volatile attribute safely
        - fix magic "self" argument when positional arguments get their values
          from kw.
        """
        guard = getattr(self, 'guard', None)
        if guard is not None:
            if not checkGuard(guard, aq_parent(self)):
                raise Forbidden, 'Calling %s %s is denied by Guard.' % (self.meta_type, self.id)

        import erp5.component.extension
        component_module = erp5.component.extension.find_load_module(self._module)
        if component_module is not None:
            f = getattr(component_module, self._function)
        else:
            import Globals  # for data

            filePath = self.filepath()
            if filePath==None:
                raise RuntimeError,\
                    "external method could not be called " \
                    "because it is None"

            if not os.path.exists(filePath):
                raise RuntimeError,\
                    "external method could not be called " \
                    "because the file does not exist"

            if Globals.DevelopmentMode:
                self.reloadIfChanged()

            f = None

        _v_f = getattr(self, '_v_f', None)
        if not _v_f or (f and f is not _v_f):
            f = self.getFunction(f=f)
        else:
            f = _v_f

        __traceback_info__=args, kw, self._v_func_defaults

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

    ExternalMethod.__call__ = __call__

security = ModuleSecurityInfo('Products.ExternalMethod.ExternalMethod.ExternalMethod')

ExternalMethod.manage_options += _guard_manage_options
ExternalMethod._guard_form = _guard_form

ExternalMethod.manage_guardForm = manage_guardForm
security.declareProtected(view_management_screens, 'manage_guardForm')

ExternalMethod.getGuard = getGuard

ExternalMethod.manage_setGuard = manage_setGuard
security.declareProtected(change_external_methods, 'manage_setGuard')

InitializeClass(ExternalMethod)
