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

from Products.ExternalMethod.ExternalMethod import ExternalMethod

from App.Extensions import FuncCode, getObject
if 1:
    def getFunction(self, reload=False, f=None):
        """
        Patch to get ZODB Component Extension function if available, otherwise
        fallback on filesystem Extension
        """
        if f is None:
            import erp5.component.extension
            try:
                f = getattr(getattr(erp5.component.extension, self._module),
                            self._function)
            except AttributeError:
                f = getObject(self._module, self._function, reload)

        # From ExternalMethod.getFunction
        ff = getattr(f, 'im_func', f)
        self._v_func_defaults = ff.func_defaults
        self._v_func_code = FuncCode(ff, f is not ff)
        self._v_f = f
        return f

    ExternalMethod.getFunction = getFunction

    ExternalMethod__call__ = ExternalMethod.__call__
    def __call__(self, *args, **kw):
        """
        Patch to call ZODB Component Extension, by trying first to import ZODB
        Component Extension if available, otherwise fallback on filesystem
        Extension
        """
        try:
            f = getattr(__import__('erp5.component.extension.' + self._module,
                                   fromlist=['erp5.component.extension'],
                                   level=0),
                        self._function)

        except (ImportError, AttributeError):
            return ExternalMethod__call__(self, *args, **kw)
        else:
            _v_f = getattr(self, '_v_f', None)
            if not _v_f or f is not _v_f:
                f = self.getFunction(f=f)

            # From ExternalMethod.__call__
            __traceback_info__ = args, kw, self._v_func_defaults

            try:
                return f(*args, **kw)
            except TypeError, v:
                import sys
                tb = sys.exc_info()[2]
                try:
                    if ((self._v_func_code.co_argcount -
                         len(self._v_func_defaults or ()) - 1 == len(args)) and
                          self._v_func_code.co_varnames[0] == 'self'):
                      return f(self.aq_parent.this(), *args, **kw)

                    raise TypeError, v, tb
                finally:
                    tb = None

    ExternalMethod.__call__ = __call__
