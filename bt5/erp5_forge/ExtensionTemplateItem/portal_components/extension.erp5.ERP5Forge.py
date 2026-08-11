# -*- coding: utf-8 -*-
import six
from Products.ERP5Type.Utils import str2unicode, unicode2str

try:
  from fissix.refactor import RefactoringTool, get_fixers_from_package
except ImportError: # BBB py2
  from lib2to3.refactor import RefactoringTool, get_fixers_from_package

def convertPy2ToPy3(source_code, fixer_suffix_list=()):
  try:
    fixer_names = get_fixers_from_package("fissix.fixes")
  except ImportError: # BBB py2
    fixer_names = get_fixers_from_package("lib2to3.fixes")
  if fixer_suffix_list:
    fixer_names = [e for e in fixer_names if e.rsplit('.',1)[-1] in fixer_suffix_list]
  rt = RefactoringTool(fixer_names)
  tree = rt.refactor_string(
    str2unicode(source_code + ('' if source_code.endswith('\n') else '\n')),
    name="<string>",
  )
  return unicode2str(six.text_type(tree))
