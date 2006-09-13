
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
from Products.ERP5Type.Cache import CachingMethod
#from Products.ERP5.Document.Url import Url
from Products.ERP5OOo.Document.DMSFile import DMSFile, stripHtml

import mimetypes, re, urllib
from htmlentitydefs import name2codepoint
from DateTime import DateTime

# XXX refactor - html processing functions should go outside

rx=[]
rx.append(re.compile('<!--.*?-->',re.DOTALL|re.MULTILINE)) # clear comments (sometimes JavaScript code in comments contains > chars)
rx.append(re.compile('<[^>]*?>',re.DOTALL|re.MULTILINE)) # clear tags
rx.append(re.compile('\s+')) # compress multiple spaces

def clearHtml(s):
  for r in rx:
    s=r.sub(" ",s)
  return s

class SpiderException(Exception):

  def __init__(self,code, msg):
    msg="%i: %s" % (code, msg)
    Exception.__init__(self,msg)

class Opener(urllib.FancyURLopener):

  def http_error_default(self, url, fp, code, msg, headers):
    raise SpiderException(code, msg)

tgtencoding='utf-8'
encodings=['iso-8859-2','iso-8859-15','windows-1250']
rx_charset=re.compile('<meta.*charset="?([\w\d\-]*)',re.DOTALL|re.MULTILINE|re.IGNORECASE)

def recode(s):
  """
  maybe it can be useful system-wide
  """
  _encodings=encodings[:] # local copy
  _encodings.insert(0,tgtencoding) # if not declared or declared wrongly, we try
  m=rx_charset.search(s)
  if m and len(m.groups())>0:
    enc=m.groups()[0].lower()
    if enc==tgtencoding:
      return s
    if enc in _encodings:
      _encodings.remove(enc)
    _encodings.insert(0,enc) # we'll start from what we've found
  for enc in _encodings:
    try:
      return s.decode(enc).encode('utf-8')
    except UnicodeDecodeError, LookupError:
      pass
  raise CanNotDecode('sorry')

def _convertEntities(txt,rx,mapper=None):
    def repl(code):
        if mapper:
            code=mapper.get(code)
        if code is None:
            return ''
        return unichr(int(code)).encode(tgtencoding)
    res=re.split(rx,txt)
    res[1::2]=map(repl,res[1::2]) # Isn't it beautiful? :)
    return ''.join(res)

rx_chars=re.compile('&#(\d{3});')
rx_ents=re.compile('&(\w{1,6});')

def convertEntities(txt):
    txt=_convertEntities(txt,rx_chars)
    txt=_convertEntities(txt,rx_ents, name2codepoint)
    return txt

class ExternalDocument(DMSFile):
  """
  caching sources from outside
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

  protocols=(('Web page','http'),)

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

  security.declareProtected(Permissions.View, 'getProtocolItemList')
  def spiderSource(self):
    """
    Spidering policy questions:
    - refreshing: how often
    - what to do if site not accessible - erate text_content or keep it?
    Shall we delegate these questions to preferences?
    Or use portal_alarms?
    """
    op=Opener()
    try:
      f=op.open(self.getQualifiedUrl())
    except (IOError, SpiderException),e:
      self.setStatusMessage("Tried on %s: %s" % (self._time(),str(e)))
      return False
    s=f.read()
    chars=len(s)
    if chars==0:
      self.setStatusMessage("Tried on %s: got empty string" % self._time())
      return False
    # here we check encoding and convert to UTF8
    try:
      s=recode(s)
    except CanNotDecode:
      self.setStatusMessage("Spidered on %s, %i chars, but could not decode" % (self._time(), chars))
      return False
    s=stripHtml(s) # remove headers, doctype and the like
    s=clearHtml(s) # remove tags
    s=convertEntities(s) # convert charrefs and named entities
    self.setTextContent(s)
    self.setStatusMessage("Spidered on %s, %i chars" % (self._time(), chars))
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

