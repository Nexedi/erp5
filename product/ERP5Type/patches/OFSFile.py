from App.special_dtml import DTMLFile
from OFS.Image import File
from Products.ERP5Type import _dtmldir


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
