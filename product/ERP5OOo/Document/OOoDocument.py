
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
from OFS.Image import Pdata
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.Message import Message
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5.Document.File import File
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5OOo.Document.DMSFile import DMSFile
from DateTime import DateTime
import xmlrpclib, base64, re, zipfile, cStringIO
# to overwrite WebDAV methods
from Products.CMFDefault.File import File as CMFFile
from Products.CMFCore.utils import getToolByName

enc=base64.encodestring
dec=base64.decodestring

class ConvertionError(Exception):pass

#class OOoDocument(File):
class OOoDocument(DMSFile):
  """
    A file document able to convert OOo compatible files to
    any OOo supported format, to capture metadata and to
    update metadata in OOo documents.

    This class can be used:

    - to create an OOo document database with powerful indexing (r/o)
      and metadata handling (r/w) features (ex. change title in ERP5 ->
      title is changed in OOo document)

    - to massively convert MS Office documents to OOo format

    - to easily keep snapshots (in PDF and/or OOo format) of OOo documents
      generated from OOo templates

    This class may be used in the future:

    - to create editable OOo templates (ex. by adding tags in WYSIWYG mode
      and using tags to make document dynamic - ask kevin for more info)

    - to automatically sign / encrypt OOo documents based on user

    - to automatically sign / encrypt PDF generated from OOo documents based on user

    This class should not be used:

    - to store files in formats not supported by OOo

    - to stored pure images (use Image for that)

    - as a general file conversion system (use portal_transforms for that)
  """
  # CMF Type Definition
  meta_type = 'ERP5 OOo Document'
  portal_type = 'OOo Document'
  isPortalContent = 1
  isRADContent = 1

  # Global variables
  snapshot=None
  oo_data=None

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
                    , PropertySheet.DMSFile
                    , PropertySheet.OOoDocument
                    )

  # time of generation of various formats
  cached_time={}
  # generated files (cache)
  cached_data={}
  # mime types for cached formats XXX to be refactored
  cached_mime={}
  # XXX the above craves for a separate class, but I'm not sure how to handle
  # it in ZODB, so for now let it be

  # regexps for stripping xml from docs
  rx_strip=re.compile('<[^>]*?>',re.DOTALL|re.MULTILINE)
  rx_compr=re.compile('\s+')

  searchable_attrs=DMSFile.searchable_attrs+('text_content',)

  security.declareProtected(Permissions.ModifyPortalContent,'clearCache')
  def clearCache(self):
    """
    Clear cache (invoked by interaction workflow upon file upload
    needed here to overwrite class attribute with instance attrs
    """
    self.cached_time={}
    self.cached_data={}
    self.cached_mime={}

  def _getServerCoordinates(self):
    """
    Returns OOo conversion server data from 
    preferences
    """
    pref=getToolByName(self,'portal_preferences')
    adr=pref.getPreferredDmsOoodocServerAddress()
    nr=pref.getPreferredDmsOoodocServerPortNumber()
    if adr is None or nr is None:
      raise Exception('you should set conversion server coordinates in preferences')
    return adr,nr

  def _mkProxy(self):
    sp=xmlrpclib.ServerProxy('http://%s:%d' % self._getServerCoordinates(),allow_none=True)
    return sp

  def returnMessage(self,msg,code=0):
    """
    code > 0 indicates a problem
    we distinguish data return from message by checking if it is a tuple
    """
    m=Message(domain='ui',message=msg)
    return (code,m)

  security.declareProtected(Permissions.ModifyPortalContent,'convert')
  def convert(self,force=0,REQUEST=None):
    """
    Converts from the initial format to OOo format;
    communicates with the conversion server
    and gets converted file as well as metadata
    """
    if force==0 and not self.isFileUploaded():
      return self.returnMessage('OOo file is up do date',1)
    try:
      self._convert()
    except xmlrpclib.Fault,e:
      return self.returnMessage('Problem: %s' % str(e),2)
    self.setLastConvertTime(DateTime())
    return self.returnMessage('converted')

  security.declareProtected(Permissions.AccessContentsInformation,'getTargetFormatList')
  def getTargetFormatItemList(self):
    """
      Returns a list of acceptable formats for conversion
      in the form of tuples (for listfield in ERP5Form)

      XXX - to be implemented better (with extended API to conversion server)
      XXX - what does this mean? I don't understand
    """
    # Caching method implementation
    def cached_getTargetFormatItemList(mimetype):
      sp=self._mkProxy()
      allowed=sp.getAllowedTargets(mimetype)
      return [[y,x] for x,y in allowed] # have to reverse tuple order

    cached_getTargetFormatItemList = CachingMethod(cached_getTargetFormatItemList,
                                        id = "OOoDocument_getTargetFormatItemList" )

    return cached_getTargetFormatItemList(self.getMimeType())


  security.declareProtected(Permissions.AccessContentsInformation,'getTargetFormatList')
  def getTargetFormatList(self):
    """
      Returns a list of acceptable formats for conversion
    """
    return map(lambda x: x[0], self.getTargetFormatItemList())


  security.declareProtected(Permissions.ModifyPortalContent,'isAllowed')
  def isAllowed(self, format):
    """
    Checks if the current document can be converted
    into the specified format.

    """
    if not self.hasOOfile(): return False
    allowed=self.getTargetFormatItemList()
    #self.log('allowed',allowed)
    if allowed is None: return False
    return (format in [x[1] for x in allowed])

  security.declareProtected(Permissions.ModifyPortalContent,'editMetadata')
  def editMetadata(self,newmeta):
    """
    Updates metadata information in the converted OOo document
    based on the values provided by the user. This is implemented
    through the invocation of the conversion server.
    """
    #self.log('editMetadata',newmeta)
    sp=self._mkProxy()
    kw=sp.run_setmetadata(self.getTitle(),enc(self._unpackData(self.oo_data)),newmeta)
    #self.log('res editMetadata',meta)
    self.oo_data=Pdata(dec(kw['data']))
    self._setMetaData(kw['meta'])
    return True # XXX why return ? - why not?

  security.declarePrivate('_convert')
  def _convert(self):
    """
    Converts the original document into OOo document
    by invoking the conversion server. Store the result
    on the object. Update metadata information.
    """
    sp=self._mkProxy()
    #self.log('_convert',enc(self._unpackData(self.data))[:500])
    kw=sp.run_convert(self.getOriginalFilename(),enc(self._unpackData(self.data)))
    self.oo_data=Pdata(dec(kw['data']))
    # now we get text content 
    text_data=self.extractTextContent()
    self.setTextContent(text_data)
    self._setMetaData(kw['meta'])

  security.declareProtected(Permissions.View,'extractTextContent')
  def extractTextContent(self):
    """
    extract plain text from ooo docs - the simplest way possible, works for all ODF formats
    """
    cs=cStringIO.StringIO()
    cs.write(self._unpackData(self.oo_data))
    z=zipfile.ZipFile(cs)
    s=z.read('content.xml')
    s=self.rx_strip.sub(" ",s) # strip xml
    s=self.rx_compr.sub(" ",s) # compress multiple spaces
    cs.close()
    z.close()
    return s

  security.declarePrivate('_setMetaData')
  def _setMetaData(self,meta):
    """
    Sets metadata properties of the ERP5 object.

    XXX - please double check that some properties
    are not already defined in the Document class (which is used
    for Web Page in ERP5)

    XXX - it would be quite nice if the metadata structure
          could also support user fields in OOo
          (user fields are so useful actually...)
          XXX - I think it does (BG)
    """
    #self.log('meta',meta)
    for k,v in meta.items():
      meta[k]=v.encode('utf-8')
    #self.log('meta',meta)
    self.setTitle(meta.get('title',''))
    self.setSubject([meta.get('subject',''),])
    self.setKeywords(meta.get('keywords',''))
    self.setDescription(meta.get('description',''))
    self.setLanguage(meta.get('language',''))
    if meta.get('MIMEType',False):
      self.setMimeType(meta['MIMEType'])
    self.setReference(meta.get('reference',''))

  #security.declareProtected(Permissions.View,'getOOfile')
  def getOOfile(self):
    """
    Return the converted OOo document.

    XXX - use a propertysheet for this instead. We have a type
          called data in property sheet. Look at File implementation
    XXX - doesn't seem to be there...
    """
    data=self.oo_data
    return data

  security.declareProtected(Permissions.View,'hasFile')
  def hasFile(self):
    """
    Checks whether we have an initial file
    """
    print 'IS INSTANCE'
    print isinstance(self,object)
    _marker=[]
    if getattr(self,'data',_marker) is not _marker: # XXX - use propertysheet accessors
      return getattr(self,'data') is not None
    return False

  security.declareProtected(Permissions.View,'hasOOfile')
  def hasOOfile(self):
    """
    Checks whether we have an OOo converted file
    """
    _marker=[]
    if getattr(self,'oo_data',_marker) is not _marker: # XXX - use propertysheet accessors
      return getattr(self,'oo_data') is not None
    return False

  security.declareProtected(Permissions.View,'hasSnapshot')
  def hasSnapshot(self):
    """
    Checks whether we have a snapshot.
    """
    _marker=[]
    if getattr(self,'snapshot',_marker) is not _marker: # XXX - use propertysheet accessors
      return getattr(self,'snapshot') is not None
    return False

  security.declareProtected(Permissions.ModifyPortalContent,'createSnapshot')
  def createSnapshot(self,REQUEST=None):
    """
    Create a PDF snapshot

    XXX - we should not create a snapshot if some error happened at conversion
          is this checked ?
    XXX - error at conversion raises an exception, so it should be ok
    """
    if self.hasSnapshot():
      if REQUEST is not None:
        return self.returnMessage('already has a snapshot')
      raise ConvertionError('already has a snapshot')
    # making snapshot
    # we have to figure out which pdf format to use
    tgts=[x[1] for x in self.getTargetFormatItemList() if x[1].endswith('pdf')]
    if len(tgts)>1:
      return self.returnMessage('multiple pdf formats found - this shouldnt happen')
    if len(tgts)==0:
      return self.returnMessage('no pdf format found')
    fmt=tgts[0]
    self.makeFile(fmt)
    self.snapshot=Pdata(self._unpackData(self.cached_data[fmt]))  # XXX - use propertysheet accessors
    return self.returnMessage('snapshot created')

  security.declareProtected(Permissions.View,'getSnapshot')
  def getSnapshot(self,REQUEST=None):
    """
    Returns the snapshot.
    """
    '''getSnapshot'''
    if not self.hasSnapshot():
      self.createSnapshot()
    return self.snapshot # XXX - use propertysheet accessors

  security.declareProtected(Permissions.ManagePortal,'deleteSnapshot')
  def deleteSnapshot(self):
    """
    Deletes the snapshot - in theory this should never be done
    """
    try:
      del(self.snapshot)
    except AttributeError:
      pass

  security.declareProtected(Permissions.View,'getTargetFile')
  def getTargetFile(self,format,REQUEST=None):
    """
    Get (possibly generate) file in a given format
    """
    if not self.isAllowed(format):
      return self.returnMessage('can not convert to '+format+' for some reason')
    try:
      self.makeFile(format)
      return self.cached_mime[format],self.cached_data[format]
    except ConvertionError,e:
      return self.returnMessage(str(e))

  security.declareProtected(Permissions.View,'isFileUploaded')
  def isFileUploaded(self):
    """
    Checks whether the file was uploaded after the last conversion into OOo
    """
    if not self.hasOOfile():return True
    return self.getLastUploadTime() > self.getLastConvertTime()

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

  security.declareProtected(Permissions.View,'isFileChanged')
  def isFileChanged(self,format):
    """
    Checks whether the file was converted (or uploaded) after last generation of
    the target format
    """
    if self.isFileUploaded(): return True
    if not self.hasFileCache(format):return True
    return self.getLastConvertTime()>self.getCacheTime(format)

  security.declareProtected(Permissions.ModifyPortalContent,'makeFile')
  def makeFile(self,format,REQUEST=None):
    """
    This method implement the file conversion cache:
      * check if the format is supported
      * check date of last conversion to OOo, compare with date of last
      * if necessary, create new file and cache
      * update file generation time

    TODO:
      * support of images in html conversion (as subobjects for example)
    """
    if not self.isAllowed(format):
      errstr='%s format is not supported' % format
      if REQUEST is not None:
        return self.returnMessage(errstr)
      raise ConvertionError(errstr)
    if self.isFileUploaded():
      if REQUEST is not None:
        return self.returnMessage('needs conversion')
      raise ConvertionError('needs conversion')
    if self.isFileChanged(format):
      try:
        self.cached_mime[format],self.cached_data[format]=self._makeFile(format)
        self._p_changed=1 # XXX not sure it is necessary
      except xmlrpclib.Fault,e:
        if REQUEST is not None:
          return self.returnMessage('Problem: %s' % str(e))
        else:
          raise ConvertionError(str(e))
      self.cached_time[format]=DateTime()
      if REQUEST is not None:
        return self.returnMessage('%s created' % format)
    else:
      if REQUEST is not None:
        return self.returnMessage('%s file is up to date' % format)
      return ConvertionError('%s file is up to date' % format)

  security.declarePrivate('_makeFile')
  def _makeFile(self,format):
    """
    Communicates with server to convert a file
    """
    # real version:
    sp=self._mkProxy()
    kw=sp.run_generate(self.getOriginalFilename(),enc(self._unpackData(self.oo_data)),None,format)
    #self.log('_makeFile',mime)
    return kw['mime'],Pdata(dec(kw['data']))

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
      s+='<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (f,str(ln),str(t),str(self.isFileChanged(f)))
    s+='</table>'
    return s

  # make sure to call the right edit methods
  _edit=File._edit
  edit=File.edit

  # BG copied from File in case
  index_html = CMFFile.index_html
  PUT = CMFFile.PUT
  security.declareProtected('FTP access', 'manage_FTPget', 'manage_FTPstat', 'manage_FTPlist')
  manage_FTPget = CMFFile.manage_FTPget
  manage_FTPlist = CMFFile.manage_FTPlist
  manage_FTPstat = CMFFile.manage_FTPstat


# vim: syntax=python shiftwidth=2 

