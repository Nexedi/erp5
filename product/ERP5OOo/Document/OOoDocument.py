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

import xmlrpclib
import base64
import re
import zipfile
import cStringIO
from DateTime import DateTime

from AccessControl import ClassSecurityInfo
from OFS.Image import Pdata
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.Message import Message
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.Document.File import File, stripHtml
from Products.ERP5.Document.Document import ConversionCacheMixin
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.DCWorkflow import ValidationFailed

enc=base64.encodestring
dec=base64.decodestring

_MARKER = []


class ConversionError(Exception):pass


class OOoDocument(File, ConversionCacheMixin):
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
  snapshot = None
  oo_data = None

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Version
                    , PropertySheet.Reference
                    , PropertySheet.TextDocument
                    , PropertySheet.Document
                    )

  _properties =  (
   # XXX-JPS mime_type should be guessed is possible for the stored file
   # In any case, it should be named differently because the name
   # is too unclear. Moreover, the usefulness of this property is
   # doubtful besides download of converted file. It would be acceptable
   # for me that this property is stored as an internal property
   # or, better, in the conversion workflow attributes.
   #
   # Properties are meant for "orginal document" information,
   # not for calculated attributes.
      { 'id'          : 'mime_type',
        'description' : 'mime type of the converted OOo file stored',
        'type'        : 'string',
        'mode'        : ''},
  )

  # regexps for stripping xml from docs
  rx_strip = re.compile('<[^>]*?>', re.DOTALL|re.MULTILINE)
  rx_compr = re.compile('\s+')

  searchable_property_list = File.searchable_property_list + ('text_content', ) # XXX - good idea - should'n this be made more general ?

  def index_html(self, REQUEST, RESPONSE, format=None, force=0):
    """
      Standard function - gets converted version (from cache or new)
      sets headers and returns converted data.

      Format can be only one string (because we are OOoDocument and do not
      accept more formatting arguments).

      Force can force conversion.
    """
    self.log(format, force)
    if (not self.hasOOFile()) or force:
      self.convertToBase()
    if format is None:
      result = self.getOOFile()
      mime = self.getMimeType()
      self.log(mime)
    else:
      try:
        mime, result = self.convert(format=format, force=force)
      except ConversionError, e:
        raise # should we do something here?
    #RESPONSE.setHeader('Last-Modified', rfc1123_date(self._p_mtime)) XXX to be implemented
    RESPONSE.setHeader('Content-Type', mime)
    #RESPONSE.setHeader('Content-Length', self.size) XXX to be implemented
    RESPONSE.setHeader('Accept-Ranges', 'bytes')
    # XXX here we should find out extension for this mime type and append to filename
    RESPONSE.setBase(None)
    return result

  def _getServerCoordinate(self):
    """
      Returns OOo conversion server data from 
      preferences
    """
    pref = getToolByName(self, 'portal_preferences')
    adr = pref.getPreferredOoodocServerAddress()
    nr = pref.getPreferredOoodocServerPortNumber()
    if adr is None or nr is None:
      raise Exception('you should set conversion server coordinates in preferences')
    return adr, nr

  def _mkProxy(self):
    sp=xmlrpclib.ServerProxy('http://%s:%d' % self._getServerCoordinate(), allow_none=True)
    return sp

  def returnMessage(self, msg, code=0):
    """
      code > 0 indicates a problem
      we distinguish data return from message by checking if it is a tuple
    """
    m = Message(domain='ui', message=msg)
    return (code, m)

  security.declareProtected(Permissions.View, 'convert')
  def convertToBase(self, force=0, REQUEST=None):
    """
      Converts from the initial format to base format (ODF);
      communicates with the conversion server
      and gets converted file as well as metadata
    """
    def doConvert(force):
      if force == 0 and self.hasOOFile():
        return self.returnMessage('OOo file is up do date', 1)
      try:
        self._convertToBase()
      except xmlrpclib.Fault, e:
        return self.returnMessage('Problem: %s' % (str(e) or 'undefined'), 2)
      return self.returnMessage('converted to Open Document Format')
    msg_ob = doConvert(force)
    msg = str(msg_ob[1])
    portal_workflow = getToolByName(self, 'portal_workflow')
    portal_workflow.doActionFor(self, 'process', comment=msg)
    return msg_ob

  security.declareProtected(Permissions.AccessContentsInformation,'getTargetFormatList')
  def getTargetFormatItemList(self):
    """
      Returns a list of acceptable formats for conversion
      in the form of tuples (for listfield in ERP5Form)

      XXX - to be implemented better (with extended API to conversion server)
      XXX - what does this mean? I don't understand
    """
    # Caching method implementation
    def cached_getTargetFormatItemList(content_type):
      sp=self._mkProxy()
      allowed=sp.getAllowedTargets(content_type)
      return [[y,x] for x,y in allowed] # have to reverse tuple order

    cached_getTargetFormatItemList = CachingMethod(cached_getTargetFormatItemList,
                                        id = "OOoDocument_getTargetFormatItemList" )
    return cached_getTargetFormatItemList(self.getContentType())

  security.declareProtected(Permissions.AccessContentsInformation, 'getTargetFormatList')
  def getTargetFormatList(self):
    """
      Returns a list of acceptable formats for conversion
    """
    return map(lambda x: x[0], self.getTargetFormatItemList())

  security.declareProtected(Permissions.ModifyPortalContent, 'reset')
  def reset(self):
    """
      make the object a non-converted one, as if it was brand new
    """
    self.clearConversionCache()
    self.oo_data = None
    m = self.returnMessage('new')
    msg = str(m[1])
    portal_workflow = getToolByName(self, 'portal_workflow')
    portal_workflow.doActionFor(self, 'process', comment=msg)

  security.declareProtected(Permissions.ModifyPortalContent,'isAllowed')
  def isAllowed(self, format):
    """
      Checks if the current document can be converted
      into the specified format.
    """
    allowed = self.getTargetFormatItemList()
    if allowed is None: return False
    return (format in [x[1] for x in allowed])

  security.declareProtected(Permissions.ModifyPortalContent,'editMetadata')
  def editMetadata(self, newmeta):
    """
      Updates metadata information in the converted OOo document
      based on the values provided by the user. This is implemented
      through the invocation of the conversion server.
    """
    sp = self._mkProxy()
    kw = sp.run_setmetadata(self.getTitle(), enc(self._unpackData(self.oo_data)), newmeta)
    self.oo_data = Pdata(dec(kw['data']))
    self._setMetaData(kw['meta'])
    return True # XXX why return ? - why not?

  security.declarePrivate('_convertToBase')
  def _convertToBase(self):
    """
      Converts the original document into ODF
      by invoking the conversion server. Store the result
      on the object. Update metadata information.
    """
    sp = self._mkProxy()
    kw = sp.run_convert(self.getSourceReference(), enc(self._unpackData(self.data)))
    self.oo_data = Pdata(dec(kw['data']))
    # now we get text content 
    text_data = self.extractTextContent()
    self.setTextContent(text_data)
    self._setMetaData(kw['meta'])

  security.declareProtected(Permissions.View,'extractTextContent')
  def extractTextContent(self):
    """
      extract plain text from ooo docs - the simplest way possible, works for all ODF formats
    """
    cs = cStringIO.StringIO()
    cs.write(self._unpackData(self.oo_data))
    z = zipfile.ZipFile(cs)
    s = z.read('content.xml')
    s = self.rx_strip.sub(" ", s) # strip xml
    s = self.rx_compr.sub(" ", s) # compress multiple spaces
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
    for k,v in meta.items():
      meta[k] = v.encode('utf-8')
    self.setTitle(meta.get('title', ''))
    self.setSubject(meta.get('keywords', '').split())
    self.setDescription(meta.get('description', ''))
    #self.setLanguage(meta.get('language',''))
    if meta.get('MIMEType', False):
      self.setContentType(meta['MIMEType'])
    #self.setReference(meta.get('reference',''))

  security.declareProtected(Permissions.View, 'getOOFile')
  def getOOFile(self):
    """
      Return the converted OOo document.

      XXX - use a propertysheet for this instead. We have a type
            called data in property sheet. Look at File implementation
      XXX - doesn't seem to be there...
    """
    data = self.oo_data
    return data

  security.declareProtected(Permissions.View, 'hasOOFile')
  def hasOOFile(self):
    """
      Checks whether we have an OOo converted file
    """
    _marker = []
    if getattr(self, 'oo_data',_marker) is not _marker: # XXX - use propertysheet accessors
      return getattr(self, 'oo_data') is not None
    return False

  security.declareProtected(Permissions.View, 'hasSnapshot')
  def hasSnapshot(self):
    """
      Checks whether we have a snapshot.
    """
    _marker = []
    if getattr(self, 'snapshot', _marker) is not _marker: # XXX - use propertysheet accessors
      return getattr(self, 'snapshot') is not None
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
        return self.returnMessage('already has a snapshot', 1)
      raise ConversionError('already has a snapshot')
    # making snapshot
    # we have to figure out which pdf format to use
    tgts = [x[1] for x in self.getTargetFormatItemList() if x[1].endswith('pdf')]
    if len(tgts) > 1:
      return self.returnMessage('multiple pdf formats found - this shouldnt happen', 2)
    if len(tgts)==0:
      return self.returnMessage('no pdf format found',1)
    fmt = tgts[0]
    self.makeFile(fmt)
    self.snapshot = Pdata(self._unpackData(self.getConversion(format = fmt)[1]))
    return self.returnMessage('snapshot created')

  security.declareProtected(Permissions.View,'getSnapshot')
  def getSnapshot(self, REQUEST=None):
    """
      Returns the snapshot.
    """
    if not self.hasSnapshot():
      self.createSnapshot()
    return self.snapshot

  security.declareProtected(Permissions.ManagePortal,'deleteSnapshot')
  def deleteSnapshot(self):
    """
      Deletes the snapshot - in theory this should never be done
    """
    try:
      del(self.snapshot)
    except AttributeError:
      pass

  def getHtmlRepresentation(self):
    """
      get simplified html version to display
    """
    # we have to figure out which html format to use
    tgts = [x[1] for x in self.getTargetFormatItemList() if x[1].startswith('html')]
    if len(tgts) == 0:
      return 'no html representation available'
    fmt = tgts[0]
    fmt, data = self.convert(fmt)
    cs = cStringIO.StringIO()
    cs.write(self._unpackData(data))
    z = zipfile.ZipFile(cs)
    h = 'could not extract anything'
    for f in z.infolist():
      fn = f.filename
      if fn.endswith('html'):
        h = z.read(fn)
        break
    z.close()
    cs.close()
    return stripHtml(h)

  security.declareProtected(Permissions.View, 'convert')
  def convert(self, format, REQUEST=None, force=0):
    """
      Get file in a given format.
      Runs makeFile to make sure we have the requested version cached,
      then returns from cache.
    """
    # first check if we have base
    if not self.hasOOFile():
      self.convertToBase()
    if not self.isAllowed(format):
      if REQUEST is not None:
        return self.returnMessage('can not convert to ' + format + ' for some reason',1)
      else:
        raise ConversionError, 'can not convert to ' + format + ' for some reason'
    try:
      # make if necessary, return from cache
      self.makeFile(format, force)
      return self.getConversion(format = format)
    except ConversionError,e:
      if REQUEST is not None:
        return self.returnMessage(str(e), 2)
      raise

  security.declareProtected(Permissions.View, 'isFileChanged')
  def isFileChanged(self, format):
    """
      Checks whether the file was converted (or uploaded) after last generation of
      the target format
    """
    return not self.hasConversion(format=format)

  security.declareProtected(Permissions.ModifyPortalContent, 'makeFile')
  def makeFile(self, format, force=0, REQUEST=None, **kw):
    """
      This method implement the file conversion cache:
        * check if the format is supported
        * check date of last conversion to OOo, compare with date of last
        * if necessary, create new file and cache
        * update file generation time

      Fails silently if we have an up to date version.

      TODO:
        * support of images in html conversion (as subobjects for example)
    """
    if not self.isAllowed(format):
      errstr = '%s format is not supported' % format
      if REQUEST is not None:
        return self.returnMessage(errstr, 2)
      raise ConversionError(errstr)
    if not self.hasOOFile():
      if REQUEST is not None:
        return self.returnMessage('needs conversion', 1)
      raise ConversionError('needs conversion')
    if self.isFileChanged(format) or force:
      try:
        mime, data = self._makeFile(format)
        self.setConversion(data, mime, format = format)
        self._p_changed = 1 # XXX not sure it is necessary
      except xmlrpclib.Fault, e:
        if REQUEST is not None:
          return self.returnMessage('Problem: %s' % str(e), 2)
        else:
          raise ConversionError(str(e))
      self.updateConversion(format = format)
      if REQUEST is not None:
        return self.returnMessage('%s created' % format)
    else:
      if REQUEST is not None:
        return self.returnMessage('%s file is up to date' % format, 1)

  security.declarePrivate('_makeFile')
  def _makeFile(self,format):
    """
      Communicates with server to convert a file
    """
    # real version:
    sp = self._mkProxy()
    kw = sp.run_generate(self.getSourceReference(), enc(self._unpackData(self.oo_data)), None, format)
    return kw['mime'], Pdata(dec(kw['data']))

  # make sure to call the right edit methods
  _edit = File._edit
  edit = File.edit

  # BG copied from File in case
  security.declareProtected('FTP access', 'manage_FTPget', 'manage_FTPstat', 'manage_FTPlist')
  manage_FTPget = File.manage_FTPget
  manage_FTPlist = File.manage_FTPlist
  manage_FTPstat = File.manage_FTPstat


# vim: syntax=python shiftwidth=2 

