import new, os

from Acquisition import aq_parent
from my2to3.trace import apply_fixers, patch_imports, tracing_functions
from Products.PageTemplates.ZRPythonExpr import PythonExpr
from Products.PythonScripts.PythonScript import _marker, PythonScript, PythonScriptTracebackSupplement
from RestrictedPython import compile_restricted_eval

from . import PatchClass


erp5_products_path = os.path.join(os.path.dirname(__file__), '..', '..')
erp5_products = ['Products.' + p for p in os.listdir(erp5_products_path)
                 if os.path.isdir(os.path.join(erp5_products_path, p))]


# Apply "trace" fixers on the fly
if os.environ.get("MY2TO3_ACTION") == "trace":
  def is_whitelisted(fullname, path):
    return any(fullname.startswith(p) for p in erp5_products)

  # Apply "trace" fixers on the fly, when importing modules
  patch_imports(is_whitelisted)

  # Apply "trace" fixers on the fly, on PythonScript bodies
  # Note: The modifications are not saved (unless it is done explicitly, e.g.
  # the user saves manually).
  class _(PatchClass(PythonScript)):
    ___setstate__ = PythonScript.__setstate__
    def __setstate__(self, state):
      self.___setstate__(state)

      if '_body' in state:
        # Note that self.___setstate__ is called unconditionally a first time,
        # before. The reason is:
        #   We need the file path (i.e. self.get_filepath()). This information
        #   is contained in state['_filepath'], but it is not always the case.
        #   Calling ___setstate__ before makes this information available.
        new_body = apply_fixers(state['_body'], self.get_filepath())
        if new_body != state['_body']:
          state['_body'] = new_body
          # This time, it's called to update the body.
          self.___setstate__(state)
          self._compile()

    # Add new "builtins" which the script can access
    def _exec(self, bound_names, args, kw):
        """Call a Python Script

        Calling a Python Script is an actual function invocation.
        """
        # Retrieve the value from the cache.
        keyset = None
        if self.ZCacheable_isCachingEnabled():
            # Prepare a cache key.
            keyset = kw.copy()
            asgns = self.getBindingAssignments()
            name_context = asgns.getAssignedName('name_context', None)
            if name_context:
                keyset[name_context] = aq_parent(self).getPhysicalPath()
            name_subpath = asgns.getAssignedName('name_subpath', None)
            if name_subpath:
                keyset[name_subpath] = self._getTraverseSubpath()
            # Note: perhaps we should cache based on name_ns also.
            keyset['*'] = args
            result = self.ZCacheable_get(keywords=keyset, default=_marker)
            if result is not _marker:
                # Got a cached value.
                return result

        #__traceback_info__ = bound_names, args, kw, self.func_defaults

        ft = self._v_ft
        if ft is None:
            __traceback_supplement__ = (
                PythonScriptTracebackSupplement, self)
            raise RuntimeError, '%s %s has errors.' % (self.meta_type, self.id)

        fcode, g, fadefs = ft
        g = g.copy()
        if bound_names is not None:
            g.update(bound_names)
        g['__traceback_supplement__'] = (
            PythonScriptTracebackSupplement, self, -1)
        g['__file__'] = getattr(self, '_filepath', None) or self.get_filepath()
        # <patch>
        g.update({f.__name__: f for f in tracing_functions})
        # </patch>
        f = new.function(fcode, g, None, fadefs)

        try:
            result = f(*args, **kw)
        except SystemExit:
            raise ValueError('SystemExit cannot be raised within a PythonScript')

        if keyset is not None:
            # Store the result in the cache.
            self.ZCacheable_set(result, keywords=keyset)
        return result

  # Apply "trace" fixers on the fly, on TALES PythonExpr
  class __(PatchClass(PythonExpr)):
    def __init__(self, name, expr, engine):
        self.text = self.expr = text = expr.strip().replace('\n', ' ')

        # Unicode expression are not handled properly by RestrictedPython
        # We convert the expression to UTF-8 (ajung)
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        code, err, warn, use = compile_restricted_eval(text,
                                                       self.__class__.__name__)
        if err:
            raise engine.getCompilerError()('Python expression error:\n%s' %
                                            '\n'.join(err))
        # <patch>
        # `compile_restricted_eval` is called a first time before (the original
        # code), mainly to handle errors related to the content of `text`. If it
        # succeeds, we know that `text` contains valid code, on which we can
        # safely apply fixers.
        # XXX: "'PythonExpr:' + text" is used as the name for now. Let's try to
        # find something better.
        code, err, warn, use = compile_restricted_eval(
            apply_fixers(text, 'PythonExpr:' + text),
            self.__class__.__name__)
        # </patch>
        self._varnames = use.keys()
        self._code = code

  # Add new "builtins" which the script can access
  PythonExpr._globals.update({f.__name__: f for f in tracing_functions})
