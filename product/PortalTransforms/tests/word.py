from rigging import transformer

import os
from stat import ST_MTIME


## BIG BAD FUNCTIONAL TEST OF OOo Word Conversion
## The interfaces work, but are not quite what we need
## I might have to back fill a chain from source/dest graphing

file = "/tmp/word.doc"

class curry:
    def __init__(self, func, *fixed_args):
        self.func = func
        self.fixed_args = fixed_args

    def __call__(self, *variable_args):
        return apply(self.func, self.fixed_args +
          variable_args)

data = open("/tmp/word.doc", "r").read()

data = transformer.convert("WordToHtml", data, filename="word.doc")
print data.getData()
