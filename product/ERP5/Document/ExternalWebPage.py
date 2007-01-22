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
from Products.ERP5.Document.File import stripHtml
from Products.ERP5.Document.ExternalDocument import ExternalDocument, SpiderException
from Products.CMFCore.utils import getToolByName

import mimetypes, re, urllib
from htmlentitydefs import name2codepoint

rx=[]
rx.append(re.compile('<!--.*?-->',re.DOTALL|re.MULTILINE)) # clear comments (sometimes JavaScript code in comments contains > chars)
rx.append(re.compile('<[^>]*?>',re.DOTALL|re.MULTILINE)) # clear tags
rx.append(re.compile('\s+')) # compress multiple spaces

def clearHtml(s):
  for r in rx:
    s=r.sub(" ",s)
  return s


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

class ExternalWebPage(ExternalDocument):
  """
  caching sources from outside
  """
  # CMF Type Definition
  meta_type = 'ERP5 External Web Page'
  portal_type = 'External Web Page'
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
                    , PropertySheet.Document
                    , PropertySheet.TextDocument
                    , PropertySheet.Url
                    , PropertySheet.ExternalDocument
                    )

  def _findTopObject(self):
    '''
    find the top object from which the spidering begun
    we search upwards untill we find or reach portal object
    the top object is the one that is maintaining the dictionary
    I think we have to do it instead of using simple acquisition
    because we have to find a non-empty one
    '''
    ob=self
    if hasattr(self,'urldict') and len(self.urldict)>0:
      return self
    else:
      while 1:
        ob=ob.getParentValue()
        if ob==self.getPortalObject():
          return self
        if hasattr(ob,'urldict') and len(ob.urldict)>0:
          return ob

  security.declareProtected(Permissions.ModifyPortalContent,'addUrl')
  def addUrl(self,url):
    '''
    record url that has already been spidered
    '''
    self.urldict[url]=1
    self._p_changed=1

  security.declareProtected(Permissions.ModifyPortalContent,'checkUrl')
  def checkUrl(self,url):
    '''
    check if the url has already been spidered
    '''
    return self.urldict.has_key(url)

  security.declareProtected(Permissions.ModifyPortalContent,'resetTopObject')
  def resetTopObject(self):
    '''
    reset the url dictionary
    remember do it before you start recursive spidering
    '''
    self.urldict={}
    self._p_changed=1

  def _processData(self,s, inf):
    # since this is a web page, we don't want anything else
    # XXX we should find another way - like this, we end up with empty draft objects
    if (inf.getmaintype(),inf.getsubtype())!=('text','html'):
      raise SpiderException(100,'this is %s/%s' % (inf.getmaintype(),inf.getsubtype()))
    top=self._findTopObject()
    # remove current subobjects
    self.manage_delObjects([i.getId() for i in self.searchFolder(portal_type='External Web Page')])
    if self.getOptionRecursively()>0 and self.getRecursionDepth()>0:
      # first find links in text
      rx=re.compile('<a[^>]*href=[\'"](.*?)[\'"]',re.IGNORECASE)
      for ref in re.findall(rx, s):
        # eliminate anchors and specials, select internal links
        if ref.startswith('javascript') or ref.startswith('mailto'):
          continue
        ref=re.sub('#.*','',ref)
        if ref=='':continue
        #baseref='/'.join(self.getQualifiedUrl().split('/'))
        baseref=self.getQualifiedUrl()
        if not ref.startswith('http'):
          # complete relative paths
          ref=baseref+'/'+ref
        # eliminate multiple slashes
        rx=re.compile('([^:]{1})\/{2,}')
        ref=re.sub(rx,'\1/',ref)
        # create subobjects
        if ref.startswith(baseref) and not top.checkUrl(ref):
          # record my url in top object
          top.addUrl(ref)
          n=self.newContent(portal_type='External Web Page')
          # set coordinates
          n.setUrlProtocol('http')
          n.setUrlString(ref)
          n.setOptionRecursively(1)
          n.setRecursionDepth(self.getRecursionDepth()-1)
          # copy attributes
          for atr in self.portal_types[self.getPortalType()].getInstanceBaseCategoryList():
            n.setProperty(atr,self.getProperty(atr))
          n.activate(activity='SQLQueue').ExternalDocument_spiderAndSetState()
    # process self
    # here we check encoding and convert to UTF8
    try:
      s=recode(s)
    except CanNotDecode:
      msg = "Spidered on %s, %i chars, but could not decode" % (self._time(), chars)
      portal_workflow = getToolByName(self, 'portal_workflow')
      portal_workflow.doActionFor(context, 'process', comment=msg)
      return False
    s=stripHtml(s) # remove headers, doctype and the like
    s=clearHtml(s) # remove tags
    s=convertEntities(s) # convert charrefs and named entities
    return s


# vim: filetype=python syntax=python shiftwidth=2 
