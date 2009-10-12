# -*- coding: utf-8 -*-

MAX_LAUNCH = 100

class OpenOffice:

  # Private methods
  def _getAvailableOpenOfficeInstancePort(self):
    """
      This method starts a collection of
      headless OpenOffice in bacground and attaches
      them to the server process. Each time
      a headless Openoffice is returned, a counter
      is incremented. After MAX_LAUNCH times,
      the server is closed and recreated.

      The method returns a port number
    """

  def _getCommand(self, param):
    """
    """
    return "/usr/bin/openoffice.convert %s"

  # Introspection API Implementation
  def getSourceFormatItemList(self):
    """
      Return the list of supported input format
      (format, name)
    """
    port = self._getAvailableOpenOfficeInstancePort()

  def getDestinationFormatItemList(self):
    """
      Return the list of supported output format
      (format, name)
    """
    port = self._getAvailableOpenOfficeInstancePort()

  # Conversion API Implementation
  def convertFile(self, file, source_format, destination_format):
    """
    """
    # XXX - just call a command line (python script)
    #  which does all the work
    port = self._getAvailableOpenOfficeInstancePort()
    input, output = popen(self._getCommand('--convert'), file)

  def getFileMetadataItemList(self, file, source_format):
    """
    """
    # XXX - just call a command line (python script)
    #  which does all the work
    port = self._getAvailableOpenOfficeInstancePort()
    input, output = popen(self._getCommand('--metadata'), file)

  def updateFileMetadata(self, file, source_format, **kw):
    """
    """
    # XXX - just call a command line (python script)
    #  which does all the work
    port = self._getAvailableOpenOfficeInstancePort()
    input, output = popen(self._getCommand('--update'), file)
