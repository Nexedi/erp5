# -*- coding: utf-8 -*-

class Converter:
  """
    Converter classes implement document conversion
    from a given format to another format.

    ARCHITECTURE: because most document processing
    software, and potentially libraries, are unstable,
    do not always support multithreading and may lead
    to memory leaks, the recommend approach to create 
    a Converter is to simply execute a command with
    popenX in a separate process and return the result.
  """

  # Introspection API Implementation
  def getSourceFormatItemList(self):
    """
      Return the list of supported input format
      (format, name)
    """
    raise NotImplementedError

  def getDestinationFormatItemList(self):
    """
      Return the list of supported output format
      (format, name)
    """
    raise NotImplementedError

  # Conversion API Implementation
  def convertFile(self, file, source_format, destination_format):
    """
    """
    raise NotImplementedError

  def getFileMetadataItemList(self, file, source_format):
    """
    """
    raise NotImplementedError

  def updateFileMetadata(self, file, source_format, **kw):
    """
    """
    raise NotImplementedError
