import sys
from Products.CMFCore.utils import ImmutableId
from zLOG import LOG, WARNING

def ImmutableId_setId(self, id):
  if id == self.getId():
      raise ValueError('The name has not been changed: %s'
                       % self.getId())
  else:
    self.id = id

ImmutableId._setId = ImmutableId_setId