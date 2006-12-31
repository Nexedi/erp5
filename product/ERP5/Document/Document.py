##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.WebDAVSupport import TextContent
from DateTime import DateTime

def makeSortedTuple(kw):
  items = kw.items()
  items.sort()
  return tuple(items)

class ConversionCacheMixin:
  """
    This class provides a generic API to store in the ZODB
    various converted versions of a file or of a string.

    TODO:
    * Implement ZODB BLOB
  """
  # time of generation of various formats
  _cached_time = {}
  # generated files (cache)
  _cached_data = {}
  # mime types for cached formats XXX to be refactored
  _cached_mime = {}

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.ModifyPortalContent, 'clearConversionCache')
  def clearConversionCache(self):
    """
    Clear cache (invoked by interaction workflow upon file upload
    needed here to overwrite class attribute with instance attrs
    """
    self._cached_time = {}
    self._cached_data = {}
    self._cached_mime = {}

  security.declareProtected(Permissions.View, 'hasConversion')
  def hasConversion(self, **format):
    """
      Checks whether we have a version in this format
    """
    return self._cached_data.has_key(makeSortedTuple(format))

  def getCacheTime(self, **format):
    """
      Checks when if ever was the file produced
    """
    return self._cached_time.get(makeSortedTuple(format), 0)

  def updateConversion(self, **format):
      self._cached_time[makeSortedTuple(format)] = DateTime()

  def setConversion(self, data, mime=None, **format):
    tformat = makeSortedTuple(format)
    if mime is not None:
      self._cached_mime[tformat] = mime
    if data is not None:
      self._cached_data[tformat] = data
      self.updateConversion(format = format)
    self._p_changed = 1

  def getConversion(self, **format):
    '''
    we could be much cooler here - pass testing and updating methods to this function
    so that it does it all by itself; this'd eliminate the need for cacheSet public method
    '''
    tformat = makeSortedTuple(format)
    return self._cached_mime.get(tformat, ''), self._cached_data.get(tformat, '')

  security.declareProtected(Permissions.View, 'getConversionCacheInfo')
  def getConversionCacheInfo(self):
    """
    Get cache details as string (for debugging)
    """
    s = 'CACHE INFO:<br/><table><tr><td>format</td><td>size</td><td>time</td><td>is changed</td></tr>'
    #self.log('getCacheInfo',self.cached_time)
    #self.log('getCacheInfo',self.cached_data)
    for f in self._cached_time.keys():
      t = self._cached_time[f]
      data = self._cached_data.get(f)
      if data:
        if isinstance(data, str):
          ln = len(data)
        else:
          ln = 0
          while data is not None:
            ln += len(data.data)
            data = data.next
      else:
        ln = 'no data!!!'
      s += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (f, str(ln), str(t), '-')
    s += '</table>'
    return s

class Document(XMLObject):
    """
        Document is an abstract class with all methods
        related to document management in ERP5. This includes
        searchable text, explicit relations, implicit relations,
        metadata, versions, languages, etc.

        There currently two types of Document subclasses:

        * File for binary file based documents. File
          has subclasses such as Image, OOoDocument,
          PDFDocument, etc. to implement specific conversion
          methods

        * TextDocument for text based documents. TextDocument
          has subclasses such as Wiki to implement specific
          methods

        Document classes which implement conversion should use
        the CachingMixin class so that converted values are
        stored.

        The Document class behaviour can be extended through scripts.

        * Document_discoverMetadata (DMS_ingestFile)
          finds all metadata or uses the metadata which was
          provided as parameter. Document_discoverMetadata should
          be overloaded if necessary for some classes
          (ex. TextDocument_discoverMetadata, Image_discoverMetadata)
          and should be called through a single API discoverMetadata()
          Consider using _getTypeBasedMethod for implementation

        * Document_ingestFile (Document_uploadFile)
          is called for http based ingestion and itself calls
          Document_discoverMetadata. Many parameters may be
          passed to Document_ingest through an
          online form.

        * Document_ingestEmail is called for email based
          ingestion and itself calls Document_ingestFile.
          Document_ingestEmail is in charge of parsing email
          to extract metadata before calling Document_ingestFile.

        * PUT is called for DAV/FTP based ingestion directly from the class.
          It itself calls Document_discoverMetadata.

        Custom scripts for automatic classification:

        * Document_findWikiPredecessorList finds a list of documents
          which are referencing us.
          Should this be merged with WebSite_getDocumentValue ? XXX

        * Document_findWikiSuccessor tries to find a document matching with
          a given regexp.
          Should this be merged with WebSite_getDocumentValue ? XXX

        Subcontent: documents may include subcontent (files, images, etc.)
        so that publication of rich content can be path independent.
    """

    meta_type = 'ERP5 Document'
    portal_type = 'Document'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1
    isDocument = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Version
                      , PropertySheet.Document
                      )

    # Declarative interfaces
    __implements__ = ()

    searchable_property_list = ('title', 'description', 'id', 'reference',
                                'version', 'short_title', 'keywords',
                                'subject', 'source_reference', 'source_project_title')
                                # What is keywords ?
                                # XXX-JPS This is a plural
                                # XXX-JPS subject_list would be better than subject in this case
                                # and the getSearchableText should be able to process lists
                                # Same for source_reference_list, source_project_title_list
  
    ### Content indexing methods
    security.declareProtected(Permissions.View, 'getSearchableText')
    def getSearchableText(self, md=None):
      """
      Used by the catalog for basic full text indexing.
  
      XXX-JPS - This method is nice. It should probably be moved to Base class
      searchable_property_list could become a standard class attribute.
  
      TODO (future): Make this property a per portal type property.
      """
      searchable_text = ' '.join(map(lambda x: self.getProperty(x) or ' ',self.searchable_property_list))
      return searchable_text

    # Compatibility with CMF Catalog
    SearchableText = getSearchableText # XXX-JPS - Here wa have a security issue - ask seb what to do

    security.declareProtected(Permissions.ModifyPortalContent, 'setPropertyListFromFilename')
    def setPropertyListFromFilename(self, fname):
      """
        XXX-JPS missing description
      """
      rx_src = self.portal_preferences.getPreferredDocumentFilenameRegexp()
      if rx_src:
        rx_parse = re.compile()
        if rx_parse is None:
          self.setReference(fname) # XXX-JPS please use _setReference to prevent reindexing all the time
          return
        m = rx_parse.match(fname)
        if m is None:
          self.setReference(fname) # XXX-JPS please use _setReference to prevent reindexing all the time
          return
        for k,v in m.groupdict().items():
          self.setProperty(k,v) # XXX-JPS please use _setProperty to prevent reindexing all the time
        # XXX-JPS finally call self.reindexObject()
      else:
        # If no regexp defined, we use the file name as reference
        # this is the failover behaviour
        self.setReference(fname)
  
    security.declareProtected(Permissions.View, 'getWikiSuccessorReferenceList')
    def getWikiSuccessorReferenceList(self):
      """
        find references in text_content, return matches
        with this we can then find objects
      """
      if self.getTextContent() is None:
        return []
      rx_search = re.compile(self.portal_preferences.getPreferredDocumentReferenceRegexp()) # XXX-JPS Safe ? Better error required ?
      try:
        res = rx_search.finditer(self.getTextContent())
      except AttributeError:
        return []
      res = [(r.group(),r.groupdict()) for r in res]
      return res
  
    security.declareProtected(Permissions.View, 'getWikiSuccessorValueList')
    def getWikiSuccessorValueList(self):
      """
        XXX-JPS Put a description then add notes (notes only is not enough)
        
        getWikiSuccessorValueList - the way to find objects is on 
        implementation level
      """
      # XXX results should be cached as volatile attributes
      # XXX-JPS - Please use TransactionCache in ERP5Type for this
      # TransactionCache does all the work for you
      lst = []
      for ref in self.getWikiSuccessorReferenceList():
        r = ref[1]
        res = self.Document_findWikiSuccessor(**r)
        if len(res)>0:
          lst.append(res[0].getObject())
      return lst
  
    security.declareProtected(Permissions.View, 'getWikiPredecessorValueList')
    def getWikiPredecessorValueList(self):
      """
        XXX-JPS Put a description then add notes (notes only is not enough)
        
        it is mostly implementation level - depends on what parameters we use to identify
        document, and on how a doc must reference me to be my predecessor (reference only,
        or with a language, etc
      """
      # XXX results should be cached as volatile attributes
      lst = self.Document_findWikiPredecessorList()
      lst = [r.getObject() for r in lst]
      di = dict.fromkeys(lst) # make it unique
      ref = self.getReference()
      return [o for o in di.keys() if o.getReference() != ref] # every object has its own reference in SearchableText
