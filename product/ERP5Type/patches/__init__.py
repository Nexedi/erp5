import six
class PatchClass(tuple):
    """Helper to easily monkey-patch many attributes of an object

    >>> class Foo(object):
    ...     def f(self):
    ...         return 1
    ...
    >>> class _(PatchClass(Foo)):
    ...     _f = Foo.f
    ...     def f(self):
    ...         return - self._f()
    ...
    >>> Foo().f()
    -1
    """
    def __new__(cls, *args):
        if len(args) == 1:
            return tuple.__new__(cls, args)
        _, ((cls,),), d = args
        for k, v in six.iteritems(d):
          if k != "__module__":
            if getattr(v, "im_class", None) is cls and v.__self__ is None:
              v = v.__func__
            setattr(cls, k, v)
