
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
from Products.ERP5.Document.File import File
from Products.ERP5Type.XMLObject import XMLObject
# to overwrite WebDAV methods
from Products.CMFDefault.File import File as CMFFile

import mimetypes, re
from DateTime import DateTime
mimetypes.init()


rs=[]
rs.append(re.compile('<HEAD>.*</HEAD>',re.DOTALL|re.MULTILINE|re.IGNORECASE))
rs.append(re.compile('<!DOCTYPE[^>]*>'))
rs.append(re.compile('<.?(HTML|BODY)[^>]*>',re.DOTALL|re.MULTILINE|re.IGNORECASE))

def stripHtml(txt):
  for r in rs:
    txt=r.sub('',txt)
  return txt


class CachingMixin:
  # time of generation of various formats
  cached_time={}
  # generated files (cache)
  cached_data={}
  # mime types for cached formats XXX to be refactored
  cached_mime={}

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.ModifyPortalContent,'clearCache')
  def clearCache(self):
    """
    Clear cache (invoked by interaction workflow upon file upload
    needed here to overwrite class attribute with instance attrs
    """
    self.cached_time={}
    self.cached_data={}
    self.cached_mime={}

  security.declareProtected(Permissions.View,'hasFileCache')
  def hasFileCache(self,format):
    """
    Checks whether we have a version in this format
    """
    return self.cached_data.has_key(format)

  def getCacheTime(self,format):
    """
    Checks when if ever was the file produced
    """
    return self.cached_time.get(format,0)

  def cacheUpdate(self,format):
      self.cached_time[format]=DateTime()

  def cacheSet(self,format,mime=None,data=None):
    if mime is not None:
      self.cached_mime[format]=mime
    if data is not None:
      self.cached_data[format]=data
      self.cacheUpdate(format)
    self._p_changed=1

  def cacheGet(self,format):
    '''
    we could be much cooler here - pass testing and updating methods to this function
    so that it does it all by itself; this'd eliminate the need for cacheSet public method
    '''
    return self.cached_mime.get(format,''),self.cached_data.get(format,'')

  security.declareProtected(Permissions.View,'getCacheInfo')
  def getCacheInfo(self):
    """
    Get cache details as string (for debugging)
    """
    s='CACHE INFO:<br/><table><tr><td>format</td><td>size</td><td>time</td><td>is changed</td></tr>'
    #self.log('getCacheInfo',self.cached_time)
    #self.log('getCacheInfo',self.cached_data)
    for f in self.cached_time.keys():
      t=self.cached_time[f]
      data=self.cached_data.get(f)
      if data:
        if isinstance(data,str):
          ln=len(data)
        else:
          ln=0
          while data is not None:
            ln+=len(data.data)
            data=data.next
      else:
        ln='no data!!!'
      s+='<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (f,str(ln),str(t),'-')
    s+='</table>'
    return s

class DMSFile(XMLObject,File):
  """
  Special base class, different from File only in that it can contain things 
  (like Role Definition, for example)
  will be merged with File when WebDAV issues are solved
  """
  # CMF Type Definition
  meta_type = 'ERP5 DMS File'
  portal_type = 'DMS File'
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
                    )


  # make sure to call the right edit methods
  _edit=File._edit
  edit=File.edit

  searchable_attrs=('title','description','id','reference','version',
      'short_title','keywords','subject','source_reference','source_project_title')

  ### Content indexing methods
  security.declareProtected(Permissions.View, 'getSearchableText')
  def getSearchableText(self, md=None):
    """
    Used by the catalog for basic full text indexing
    """
    searchable_text = ' '.join(map(lambda x: self.getProperty(x) or ' ',self.searchable_attrs))
    return searchable_text

  security.declarePrivate('_unpackData')
  def _unpackData(self,data):
    """
    Unpack Pdata into string
    """
    if isinstance(data,str):
      return data
    else:
      data_list=[]
      while data is not None:
        data_list.append(data.data)
        data=data.next
      return ''.join(data_list)

  SearchableText=getSearchableText

  security.declareProtected(Permissions.ModifyPortalContent, 'guessMimeType')
  def guessMimeType(self,fname=''):
    '''get mime type from file name'''
    if fname=='':fname=self.getOriginalFilename()
    if fname:
      content_type,enc=mimetypes.guess_type(fname)
      if content_type is not None:
        self.content_type=content_type
    return content_type

  security.declareProtected(Permissions.ModifyPortalContent, 'setPropertiesFromFilename')
  def setPropertiesFromFilename(self,fname):
    rx_parse=re.compile(self.portal_preferences.getPreferredDmsFilenameRegexp())
    if rx_parse is None:
      self.setReference(fname)
      return
    m=rx_parse.match(fname)
    if m is None:
      self.setReference(fname)
      return
    for k,v in m.groupdict().items():
      self.setProperty(k,v)

  security.declareProtected(Permissions.View, 'getWikiSuccessorReferenceList')
  def getWikiSuccessorReferenceList(self):
    '''
    find references in text_content, return matches
    with this we can then find objects
    '''
    if self.getTextContent() is None:
      return []
    rx_search=re.compile(self.portal_preferences.getPreferredDmsReferenceRegexp())
    try:
      res=rx_search.finditer(self.getTextContent())
    except AttributeError:
      return []
    res=[(r.group(),r.groupdict()) for r in res]
    return res

  security.declareProtected(Permissions.View, 'getWikiSuccessorValueList')
  def getWikiSuccessorValueList(self):
    '''
    getWikiSuccessorValueList - the way to find objects is on 
    implementation level
    '''
    lst=[]
    for ref in self.getWikiSuccessorReferenceList():
      res=self.DMS_findDocument(ref)
      if len(res)>0:
        lst.append(res[0].getObject())
    return lst
    #def cached_getWikiSuccessorValueList():
      #lst=[]
      #for ref in self.getWikiSuccessorReferenceList():
        #res=self.DMS_findDocument(ref)
        #if len(res)>0:
          #lst.append(res[0].getObject())
      #return lst
    #cached_getWikiSuccessorValueList = CachingMethod(cached_getWikiSuccessorValueList,
        #id='DMSFile_getWikiSuccessorValueList')
    #return cached_getWikiSuccessorValueList()

  security.declareProtected(Permissions.View, 'getWikiPredecessorValueList')
  def getWikiPredecessorValueList(self):
    '''
    it is mostly implementation level - depends on what parameters we use to identify
    document, and on how a doc must reference me to be my predecessor (reference only,
    or with a language, etc
    '''
    lst=self.DMS_findPredecessors()
    lst=[r.getObject() for r in lst]
    di=dict.fromkeys(lst) # make it unique
    ref=self.getReference()
    return [o for o in di.keys() if o.getReference()!=ref] # every object has its own reference in SearchableText
    #def cached_getWikiPredecessorValueList():
      #lst=self.DMS_findPredecessors()
      #lst=[r.getObject() for r in lst]
      #di=dict.fromkeys(lst) # make it unique
      #ref=self.getReference()
      #return [o for o in di.keys() if o.getReference()!=ref] # every object has its own reference in SearchableText
    #cached_getWikiPredecessorValueList=CachingMethod(cached_getWikiPredecessorValueList,
        #id='DMSFile_getWikiPredecessorValueList')
    #return cached_getWikiPredecessorValueList()

  security.declareProtected(Permissions.View,'getContributorList')
  def getContributorList(self):
    '''
    override
    '''
    return (self.getContributorRelatedTitleList() or [])+(self.getContributorNameList() or [])
  
  getContributorsList=getContributorList
  getContributorTitleList=getContributorList

  security.declarePrivate('setContributorList')
  def setContributorList(self,*args,**kwargs):
    '''
    just in case
    '''
    pass
  setContributorsList=setContributorList

  # BG copied from File in case
  index_html = CMFFile.index_html
  PUT = CMFFile.PUT
  security.declareProtected('FTP access', 'manage_FTPget', 'manage_FTPstat', 'manage_FTPlist')
  manage_FTPget = CMFFile.manage_FTPget
  manage_FTPlist = CMFFile.manage_FTPlist
  manage_FTPstat = CMFFile.manage_FTPstat


# vim: syntax=python shiftwidth=2 

