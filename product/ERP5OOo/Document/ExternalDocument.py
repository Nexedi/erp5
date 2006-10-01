
##############################################################################
#
# Copyright (c) 2002-2006 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5OOo.Document.DMSFile import DMSFile

import mimetypes, re, urllib
from htmlentitydefs import name2codepoint
from DateTime import DateTime


class SpiderException(Exception):

  def __init__(self,code, msg):
    msg="%i: %s" % (code, msg)
    Exception.__init__(self,msg)

class Opener(urllib.FancyURLopener):

  def http_error_default(self, url, fp, code, msg, headers):
    raise SpiderException(code, msg)

class ExternalDocument(DMSFile):
  """
  caching sources from outside
  This is basically an abstract class
  classes deriving from it should overwrite method _processData (this
  is the one that does something with character data obtained from source)
  Spidering method supports http, ftp and file protocols, and possibly many others
  """
  # CMF Type Definition
  meta_type = 'ERP5 External Document'
  portal_type = 'External Document'
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Version
                    , PropertySheet.Reference
                    , PropertySheet.DMSFile
                    , PropertySheet.Document
                    , PropertySheet.Url
                    , PropertySheet.ExternalDocument
                    )

  protocols=(('Web page','http'),('FTP site','ftp'),('Local file','file'),)

  searchable_attrs=DMSFile.searchable_attrs+('text_content',)

  security.declareProtected(Permissions.View, 'getProtocolList')
  def getProtocolList(self):
    """
    """
    return [x[1] for x in self.protocols]

  security.declareProtected(Permissions.View, 'getProtocolItemList')
  def getProtocolItemList(self):
    """
    """
    return self.protocols

  security.declarePrivate(Permissions.View, '_spiderSource')
  def _spiderSource(self):
    """
    FancyURLopener can open various protocols
    """
    op=Opener()
    f=op.open(self.getQualifiedUrl())
    s=f.read()
    return s

  security.declarePrivate('_processData')
  def _processData(self,s):
    raise Exception('this should be implemented in subclass')

  security.declareProtected(Permissions.ModifyPortalContent,'resetTopObject')
  def resetTopObject(self):
    '''
    abstract function for maintaining interface
    call before beginning recursive spidering
    used mostly in web pages
    '''
    pass

  security.declareProtected(Permissions.View, 'getProtocolItemList')
  def spiderSource(self):
    """
    spiders external datasource
    sets status message
    returned value tells us if it succeeded or failed
    """
    try:
      s=self._spiderSource()
    except Exception,e:
      self.log(e,level=1)
      self.setStatusMessage("Tried on %s: %s" % (self._time(),str(e)))
      return False
    chars=len(s)
    if chars==0:
      self.setStatusMessage("Tried on %s: got empty string" % self._time())
      return False
    try:
      s=self._processData(s)
    except Exception,e:
      self.log(e,level=1)
      self.setStatusMessage("Spidered on %s, %i chars, but could not process; reason: %s" % (self._time(), chars, str(e)))
      return False
    self.setTextContent(s)
    self.setStatusMessage("Spidered on %s, %i chars, recorded %i chars" % (self._time(), chars, len(s)))
    return True

  security.declareProtected(Permissions.View, 'getProtocolItemList')
  def getQualifiedUrl(self):
    """
    this should be in the Url, not here
    otherwise why does the url have a property 'url_protocol'?
    """
    return (self.getUrlProtocol() or '')+'://'+(self.getUrlString() or '')

  def _time(self):
    return DateTime().strftime('%Y/%m/%d %H:%M:%S')


# vim: syntax=python shiftwidth=2 

