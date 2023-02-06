from App.special_dtml import DTMLFile
from OFS.Image import File
from Products.ERP5Type import IS_ZOPE4, _dtmldir


def _setData(self, data):
  """
  Originally from Document class. Added because it is used by
  BusinessTemplate on OFS.Image.{File,Image} instances
  """
  # update_data use len(data) when size is None, which breaks this method.
  # define size = 0 will prevent len be use and keep the consistency of
  # getData() and setData()
  if data is None:
    size = 0
  else:
    data, size = self._read_data(data)
  # We call this method to make sure size is set and caches reset
  self.update_data(data, size=size)
File._setData = _setData

if not IS_ZOPE4:
  from OFS.SimpleItem import Item
  # Patch for displaying textearea in full window instead of
  # remembering a quantity of lines to display in a cookie
  manage_editForm = DTMLFile("fileEdit", _dtmldir)
  manage_editForm._setName('manage_editForm')
  File.manage_editForm = manage_editForm
  File.manage = manage_editForm
  File.manage_main = manage_editForm
  File.manage_editDocument = manage_editForm
  File.manage_editForm = manage_editForm

  # restore __repr__ after persistent > 4.4
  # https://github.com/zopefoundation/Zope/issues/379
  File.__repr__ = Item.__repr__
