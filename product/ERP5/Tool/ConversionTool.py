# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from Products.CMFCore.utils import getToolByName

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions
from Products.ERP5Type.Tool.BaseTool import BaseTool

from Products.ERP5 import _dtmldir

from zLOG import LOG

class ConversionTool(BaseTool):
  """
    The ConversionTool class will provide in the future an 
    API to unify file conversion and metadata handling in ERP5.

    The first version consists of a tool which acts both as central
    point for conversion services and metadata handling services
    for all ERP5 Document classes and scripts, as well as a Web
    Service for external applications.

    The Tool calls itself, through XML-RPC protocol. A dedicated
    Zope instance can be setup for handling conversions.

    In the future, the tool will be splitted in 2 parts:
      - a Tool
      - a WSGI service

    The tool reuses the portal_web_services to connect through
    XML-RPC to the conversion server.

    ARCHITECTURE PHASE 1: all Converter classes are stored 
    in the Converter directory part of ERP5 Product. The tool
    serves both as caller and recipient, and calls itself
    through XML-RPC.

    ARCHITECTURE PHASE 2: all Converter classes are moved to
    a dedicated directory in /usr/share/oood/converter
    (or new name). The Web Service API is moved away from
    ConverterTool class and turned to a WSGI independent service

    NOTE: this class is experimental and is subject to be removed
    NOTE2: the code is only pseudo-code
  """
  id = 'portal_conversions'
  meta_type = 'ERP5 Conversion Tool'
  portal_type = 'Conversion Tool'
  allowed_types = ()

  # Declarative Security
  security = ClassSecurityInfo()

  #
  #   ZMI methods
  #
  security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
  manage_overview = DTMLFile( 'explainConversionTool', _dtmldir )

  def filtered_meta_types(self, user=None):
    # Filters the list of available meta types.
    all = SolverTool.inheritedAttribute('filtered_meta_types')(self)
    meta_types = []
    for meta_type in self.all_meta_types():
      if meta_type['name'] in self.allowed_types:
        meta_types.append(meta_type)
    return meta_types

  def tpValues(self):
    """ show the content in the left pane of the ZMI """
    return self.objectValues()

  # Internal API - called by Document classes and scripts
  def convert(self, file, source_format, destination_format, zip=False):
    """
      Returns the converted file in the given format
  
      zip parameter can be specified to return the result of conversion
      in the form of a zip archive (which may contain multiple parts). 
      This can be useful to convert a single ODF file to HMTL
      and png images.
    """
    # Just call XML-RPC
    preference_tool = getToolByName(self, 'portal_preferences')
    web_service_tool = getToolByName(self, 'portal_web_services')
    conversion_url = preference_tool.getPreferredConversionServiceUrl()
    conversion_service = web_service_tool.connect(conversion_url)
    # XXX - no exception handling - wrong
    return conversion_service.convertFile(file, source_format, destination_format)


  def getMetadataDict(self, file, source_format):
    """
      Returns a dict of metadata values for the
      document. The structure of this dict is "unpredictable"
      and follows the convention of each file.
    """
    # Just call XML-RPC
    preference_tool = getToolByName(self, 'portal_preferences')
    web_service_tool = getToolByName(self, 'portal_web_services')
    conversion_url = preference_tool.getPreferredConversionServiceUrl()
    conversion_service = web_service_tool.connect(conversion_url)
    # XXX - no exception handling - wrong
    return conversion_service.getFileMetadataItemList(file, source_format)


  def updateMetadata(self, file, source_format, **kw):
    """
      Updates the file in the given source_format 
      with provided metadata and return the resulting new file
    """
    # Just call XML-RPC
    preference_tool = getToolByName(self, 'portal_preferences')
    web_service_tool = getToolByName(self, 'portal_web_services')
    conversion_url = preference_tool.getPreferredConversionServiceUrl()
    conversion_service = web_service_tool.connect(conversion_url)
    # XXX - no exception handling - wrong
    return conversion_service.updateFileMetadata(file, source_format, **kw)


  # Web Service API - called by any application through XML-RPC
  # Will be removed in the future and moved to WSGI service
  def convertFile(self, file, source_format, destination_format, zip=False):
    """
      Returns the converted file in the given format
    """
    converter = self._findConverter(source_format, destination_format)
    return converter.convertFile(file, source_format, destination_format, zip=zip)


  def getFileMetadataItemList(self, file, source_format):
    """
      Returns a list key, value pairs representing the 
      metadata values for the document. The structure of this
      list is "unpredictable" and follows the convention of each file.
    """
    converter = self._findConverter(source_format, destination_format)
    return converter.getFileMetadataItemList(file, source_format)


  def updateFileMetadata(self, file, source_format, **kw):
    """
      Updates the file in the given source_format 
      with provided metadata and return the resulting new file
    """
    converter = self._findConverter(source_format, destination_format)
    return converter.updateFileMetadata(file, source_format, destination_format, zip=zip)

  # Private methods
  def _findConverter(self, source_format, destination_format):
    """
      Browses all converter classes, initialised the repository of
      converters and finds the appropriate class
    """