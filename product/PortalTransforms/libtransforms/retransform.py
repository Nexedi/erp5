from Products.PortalTransforms.interfaces import itransform
import re

class retransform:
    """abstract class for regex transforms (re.sub wrapper)"""
    __implements__ = itransform

    inputs  = ('text/',)

    def __init__(self, name, *args):
        self.__name__ = name
        self.regexes = []
        for pat, repl in args:
            self.addRegex(pat, repl)

    def name(self):
        return self.__name__

    def addRegex(self, pat, repl):
        r = re.compile(pat)
        self.regexes.append((r, repl))

    def convert(self, orig, data, **kwargs):
        for r, repl in self.regexes:
            orig = r.sub(repl, orig)
        data.setData(orig)
        return data
