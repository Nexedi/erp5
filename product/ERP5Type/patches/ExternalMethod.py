from Products.ExternalMethod.ExternalMethod import ExternalMethod

from App.Extensions import FuncCode, getObject
def getFunction(self, reload=False, f=None):
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
  import erp5.component.extension
  try:
    f = getattr(getattr(erp5.component.extension, self._module),
                self._function)
  except AttributeError:
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
