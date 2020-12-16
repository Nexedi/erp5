"""
The purpose of this module is to have an XML parser capable of handling >50MB files
without using too much RAM.
"""
from xml.etree.ElementTree import iterparse, Element, TreeBuilder, XMLParser
from Products.ERP5Type.mixin.matrix import INFINITE_SET

class RestrictedElement(Element):
  __allow_access_to_unprotected_subobjects__ = 1

class ChildDiscardingElement(RestrictedElement):
  """
  Ignores any children added to it.

  Useful to parse large files, so as many-children nodes actually discards
  them to free memory.
  """
  def __init__(self, tag, expected_tag_set):
    super(ChildDiscardingElement, self).__init__(tag)
    self.__expected_tag_set = expected_tag_set

  def __single(self, child):
    if not (
          isinstance(child, ChildDiscardingElement) or
          child.tag in self.__expected_tag_set
        ):
      raise ValueError('Unexpected discarded tag: %r (inside %r)' % (
        child.tag,
        self.tag,
      ))

  append = __single

  def extend(self, elements):
    for child in elements:
      self.__single(child)

  def insert(self, index, element):
    self.__single(element)

def parseStream(stream, child_discard_set, callback_dict, catchall=None):
  """
  stream (opened read stream)
    Where XML data is read from. Expects a "read" method following the
    "file" API.

  child_discard_set (anything implementing '__in__')
    Set of tags whose children should be discarded while parsing.

  callback_dict (dict)
    Dict of callables per event and tag type, to be called for these
    combinations when encountered. Expected structure is:
    {
      (event, tag): callable(element) -> None,
    }
    See xml.etree.ElementTree.iterparse for a list of possible events.

  catchall (None, callable(element) -> None)
    Callback triggered for all actually triggered events but not declared in
    callback_dict.
    If None, a ValueError exception will be raised when an element whose tag is
    present in child_discard_set receives a non-child-discarding child for
    which neither "start" nor "end" callback exist.
  """
  if catchall is None:
    catchall = lambda x: None
    callback_set = {
      y for x, y in callback_dict
      if x in ('start', 'end', None) # None is equivalent to 'end'
    }
  else:
    callback_set = INFINITE_SET
  def elementFactory(tag, attrs):
    if tag in child_discard_set:
      return ChildDiscardingElement(tag, callback_set)
    return RestrictedElement(tag, attrs)
  for event, elem in iterparse(
          stream,
          events={x for x, _ in callback_dict},
          parser=XMLParser(
            target=TreeBuilder(
              element_factory=elementFactory,
            ),
          ),
        ):
    callback_dict.get((event, elem.tag), catchall)(elem)

from AccessControl.SecurityInfo import ModuleSecurityInfo
ModuleSecurityInfo(__name__).declarePublic('parseStream')
