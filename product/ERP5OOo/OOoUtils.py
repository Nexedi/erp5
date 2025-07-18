# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2003-2005 Nexedi SARL and Contributors. All Rights Reserved.
#                         Kevin DELDYCKE    <kevin@nexedi.com>
#                         Guillaume MICHON  <guillaume@nexedi.com>
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

import six
from Acquisition import Implicit

from Products.PythonScripts.Utility import allow_class
from ZPublisher.HTTPRequest import FileUpload
from xml.dom import Node
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass, get_request
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED
from io import BytesIO
import random
from Products.ERP5Type import Permissions
from zLOG import LOG, INFO, DEBUG

from OFS.Image import Pdata

from lxml import etree
from lxml.etree import Element, XMLSyntaxError
from copy import deepcopy
from warnings import warn
from Products.ERP5Type.Utils import bytes2str
from Products.ERP5Type.Utils import deprecated

class CorruptedOOoFile(Exception): pass

OOo_mimeType_dict = {
  'sxw' : 'application/vnd.sun.xml.writer',
  'stw' : 'application/vnd.sun.xml.writer.template',
  'sxg' : 'application/vnd.sun.xml.writer.global',
  'sxc' : 'application/vnd.sun.xml.calc',
  'stc' : 'application/vnd.sun.xml.calc.template',
  'sxi' : 'application/vnd.sun.xml.impress',
  'sti' : 'application/vnd.sun.xml.impress.template',
  'sxd' : 'application/vnd.sun.xml.draw',
  'std' : 'application/vnd.sun.xml.draw.template',
  'sxm' : 'application/vnd.sun.xml.math',
}

class OOoBuilder(Implicit):
  """
  Tool that allows to reinject new files in a ZODB OOo document.
  """
  __allow_access_to_unprotected_subobjects__ = 1

  def __init__(self, document):
    zip_io = BytesIO()
    if hasattr(document, 'data') :
      if isinstance(document.data, Pdata):
        # Handle image included in the style
        dat = document.data
        while dat is not None:
          zip_io.write(dat.data)
          dat = dat.next
      else:
        # Default behaviour
        zip_io.write(document.data)
    else:
      zip_io.write(document)

    self._content = {}  # type: dict[str, bytes]
    self._compression_type = {}  # type: dict[str, int]

    zip_io.seek(0)
    with ZipFile(zip_io, mode='r') as zf:
      for zinfo in zf.infolist():
        self._content[zinfo.filename] = zf.read(zinfo.filename)
        self._compression_type[zinfo.filename] = zinfo.compress_type

    self._image_count = 0
    self._manifest_additions_list = []

  def replace(self, filename, stream):
    """
    Replaces the content of filename by stream in the archive.
    Creates a new file if filename was not already there.
    """
    if isinstance(stream, six.text_type):
      stream = stream.encode('utf-8')
    self._content[filename] = stream

  def extract(self, filename):
    """
    Extracts a file from the archive
    """
    return self._content[filename]

  def getNameList(self):
    return list(self._content.keys())

  def getMimeType(self):
    return bytes2str(self.extract('mimetype'))

  def prepareContentXml(self, ooo_xml_file_id):
    """
      extracts content.xml text and prepare it :
        - add tal namespace
        - indent the xml
    """
    content_xml = bytes2str(self.extract(ooo_xml_file_id))
    content_doc = etree.XML(content_xml)
    root = content_doc.getroottree().getroot()
    #Declare zope namespaces
    NSMAP = {'tal': 'http://xml.zope.org/namespaces/tal',
             'i18n': 'http://xml.zope.org/namespaces/i18n',
             'metal': 'http://xml.zope.org/namespaces/metal'}
    NSMAP.update(root.nsmap)
    new_root = Element(root.tag, nsmap=NSMAP)
    new_root.attrib.update(dict(root.attrib))
    new_root.attrib.update({'{%s}attributes' % NSMAP.get('tal'): 'dummy python:request.RESPONSE.setHeader(\'Content-Type\', \'text/html;; charset=utf-8\')'})
    for child in root.getchildren():
      new_root.append(deepcopy(child))
    return etree.tostring(new_root, encoding='utf-8', xml_declaration=True,
                          pretty_print=True)


  def addFileEntry(self, full_path, media_type, content=None):
      """ Add a file entry to the manifest and possibly is content """
      self.addManifest(full_path, media_type)
      if content:
          self.replace(full_path, content)

  def addManifest(self, full_path, media_type):
    """ Add a path to the manifest """
    li = '<manifest:file-entry manifest:media-type="%s" manifest:full-path="%s"/>'%(media_type, full_path)
    self._manifest_additions_list.append(li)

  def _update_manifest(self):
    MANIFEST_FILENAME = 'META-INF/manifest.xml'
    meta_infos = bytes2str(self.extract(MANIFEST_FILENAME))
    # prevent some duplicates
    for meta_line in meta_infos.split('\n'):
        for new_meta_line in list(self._manifest_additions_list):
            if meta_line.strip() == new_meta_line:
                self._manifest_additions_list.remove(new_meta_line)

    # add the new lines
    self._manifest_additions_list.append('</manifest:manifest>')
    meta_infos = meta_infos.replace( self._manifest_additions_list[-1], '\n'.join(self._manifest_additions_list) )
    self.replace(MANIFEST_FILENAME, meta_infos)
    self._manifest_additions_list = []

  def addImage(self, image, format='png', content_type=None):
    """
    Add an image to the current document and return its id
    """
    count = self._image_count
    self._image_count += 1
    name = "Pictures/%s.%s" % (count, format)
    if not content_type:
      import mimetypes
      warn('content_type argument must be passed explicitely', FutureWarning)
      content_type = mimetypes.guess_type(name)[0]
    self.addManifest(name, content_type)
    self.replace(name, image)
    is_legacy = ('oasis.opendocument' not in self.getMimeType())
    return "%s%s" % (is_legacy and '#' or '', name,)

  def _build_zipfile(self):
    # type: () -> io.BytesIO
    if self._manifest_additions_list:
      self._update_manifest()
    new_io = BytesIO()

    with ZipFile(new_io, mode='w', compression=ZIP_DEFLATED, allowZip64=True) as zf:
      # Write `mimetype` first, uncompressed, with no comment or extra
      # spec recommends this for file magic discovery.
      zf.writestr('mimetype', self._content['mimetype'], ZIP_STORED)
      for filename, content in six.iteritems(self._content):
        if filename != 'mimetype':
          zf.writestr(filename, content, self._compression_type.get(filename))

    new_io.seek(0)
    return new_io

  def render(self, name='', extension='sxw', source=False):
    """
    returns the OOo document
    """
    if name and not(source):
      request = get_request()
      request.response.setHeader('Content-Disposition',
                              'attachment; filename=%s.%s' % (name, extension))

    return self._build_zipfile().read()


allow_class(OOoBuilder)

class OOoParser(Implicit):
  """
    General purpose tools to parse and handle OpenOffice v1.x documents.
  """
  __allow_access_to_unprotected_subobjects__ = 1
  def __init__(self):
    self.oo_content_dom = None
    self.oo_styles_dom  = None
    self.oo_files = {}
    self.pictures = {}
    self.filename = None

  def openFromBytes(self, bytes_content):
    return self.openFile(BytesIO(bytes_content))
  openFromString = deprecated("openFromString is deprecated, use openFromBytes instead")(openFromBytes)

  def openFile(self, file_descriptor):
    """
      Load all files in the zipped OpenOffice document
    """
    # Try to unzip the Open Office doc
    try:
      oo_unzipped = ZipFile(file_descriptor, mode="r")
    except Exception as e:
      LOG('ERP5OOo', DEBUG, 'Error in openFile', error=True)
      raise CorruptedOOoFile(e)
    # Test the integrity of the file
    if oo_unzipped.testzip() is not None:
      raise CorruptedOOoFile('Invalid zip file')

    # Get the filename
    self.filename = getattr(file_descriptor, 'filename', 'default_filename')

    # List and load the content of the zip file
    for name in oo_unzipped.namelist():
      self.oo_files[name] = oo_unzipped.read(name)
    oo_unzipped.close()

    # Get the main content and style definitions
    self.oo_content_dom = etree.XML(self.oo_files["content.xml"])
    self.oo_styles_dom  = etree.XML(self.oo_files["styles.xml"])

  def getFilename(self):
    """
      Return the name of the OpenOffice file
    """
    return self.filename

  def getContentDom(self):
    """
      Return the DOM tree of the main OpenOffice content
    """
    return self.oo_content_dom

  def getSpreadsheetsDom(self, include_embedded=False):
    """
      Return a list of DOM tree spreadsheets (optionnaly included embedded ones)
    """
    spreadsheets = []
    spreadsheets = self.getPlainSpreadsheetsDom()
    if include_embedded == True:
      spreadsheets += self.getEmbeddedSpreadsheetsDom()
    return spreadsheets

  def getSpreadsheetsMapping(self, include_embedded=False, no_empty_lines=False, normalize=True):
    """
      Return a list of table-like spreadsheets (optionnaly included embedded ones)
    """
    tables = {}
    tables = self.getPlainSpreadsheetsMapping(no_empty_lines, normalize)
    if include_embedded == True:
      embedded_tables = self.getEmbeddedSpreadsheetsMapping(no_empty_lines, normalize)
      tables = self._getTableListUnion(tables, embedded_tables)
    return tables

  def getPlainSpreadsheetsDom(self):
    """
      Retrieve every spreadsheets from the document and get they DOM tree
    """
    find_path = './/{%s}table' % self.oo_content_dom.nsmap['table']
    return self.oo_content_dom.findall(find_path)

  def getPlainSpreadsheetsMapping(self, no_empty_lines=False, normalize=True):
    """
      Return a list of plain spreadsheets from the document and transform them as table
    """
    tables = {}
    for spreadsheet in self.getPlainSpreadsheetsDom():
      new_table = self.getSpreadsheetMapping(spreadsheet, no_empty_lines, normalize)
      if new_table != None:
        tables = self._getTableListUnion(tables, new_table)
    return tables

  def getEmbeddedSpreadsheetsDom(self):
    """
      Return a list of existing embedded spreadsheets in the file as DOM tree
    """
    spreadsheets = []
    # List all embedded spreadsheets
    find_path = './/{%s}object' % self.oo_content_dom.nsmap['draw']
    emb_objects = self.oo_content_dom.findall(find_path)
    for embedded in emb_objects:
      document = embedded.get('{%s}href' % embedded.nsmap['xlink'])
      if document:
        try:
          object_content = etree.XML(self.oo_files[document[3:] + '/content.xml'])
          find_path = './/{%s}table' % self.oo_content_dom.nsmap['table']
          table_list = self.oo_content_dom.findall(find_path)
          if table_list:
            for table in table_list:
              spreadsheets.append(table)
          else: # XXX: insert the link to OLE document ?
            pass
        except XMLSyntaxError:
          pass
    return spreadsheets

  def getEmbeddedSpreadsheetsMapping(self, no_empty_lines=False, normalize=True):
    """
      Return a list of embedded spreadsheets in the document as table
    """
    tables = {}
    for spreadsheet in self.getEmbeddedSpreadsheetsDom():
      new_table = self.getSpreadsheetMapping(spreadsheet, no_empty_lines, normalize)
      if new_table != None:
        tables = self._getTableListUnion(tables, new_table)
    return tables

  def getSpreadsheetMapping(self, spreadsheet=None, no_empty_lines=False, normalize=True):
    """
      This method convert an OpenOffice spreadsheet to a simple table.
      This code is based on the oo2pt tool (http://cvs.sourceforge.net/viewcvs.py/collective/CMFReportTool/oo2pt).
    """
    if spreadsheet is None or \
      spreadsheet.tag != '{%s}table' % spreadsheet.nsmap['table']:
      return None

    table = []

    # Get the table name
    table_name = spreadsheet.get('{%s}name' % spreadsheet.nsmap["table"])

    # Scan table and store usable information
    find_path = './/{%s}table-row' % spreadsheet.nsmap['table']
    for line in spreadsheet.findall(find_path):

      # TODO : to the same as cell about abusive repeated lines

      line_group_found = line.get('{%s}number-rows-repeated' % line.nsmap["table"])
      if not line_group_found:
        lines_to_repeat = 1
      else:
        lines_to_repeat = int(line_group_found)

      for i in range(lines_to_repeat):
        table_line = []

        # Get all cells
        find_path = './/{%s}table-cell' % line.nsmap['table']
        cells = line.findall(find_path)
        cell_index_range = range(len(cells))

        for cell_index in cell_index_range:
          cell = cells[cell_index]

          # If the cell as no child, cells have no content
          # And if the cell is the last of the row, we don't need to add it to the line
          # So we can go to the next line (= exit this cells loop)
          #
          # I must do this test because sometimes the following cell group
          #   can be found in OOo documents : <table:table-cell table:number-columns-repeated='246'/>
          # This is bad because it create too much irrevelent content that slow down the process
          # So it's a good idea to break the loop in this case
          if len(cell) == 0 and cell_index == cell_index_range[-1]:
            break

          # Handle cells group
          cell_group_found = cell.get('{%s}number-columns-repeated' % cell.nsmap['table'])
          if not cell_group_found:
            cells_to_repeat = 1
          else:
            cells_to_repeat = int(cell_group_found)

          # Ungroup repeated cells
          for j in range(cells_to_repeat):
            # Get the cell content
            cell_data = None
            attribute_type_mapping = {'date': 'date-value',
                                      'time': 'time-value',
                                      'float': 'value',
                                      'percentage': 'value',
                                      'currency': 'value'}
            # Depending of odf version, value-type and value attributes can be in
            # table or office namespaces, so we use local-name.
            value_type = str(cell.xpath('string(@*[local-name()="value-type"])'))
            if value_type in attribute_type_mapping:
              xpath = '@*[local-name()="%s"]' % attribute_type_mapping[value_type]
              cell_data = str(cell.xpath(xpath)[0])
            else: # read text nodes
              # Text nodes can contain multiple <text:p> tags, one for each
              # line. There are also some tags for special entities, for
              # instance <text:s/> for a space (or using <text:s text:c="3"/>
              # for multiple spaces) <text:tab/> for a tab and <text:line-break/>
              # for new line
              text_ns = cell.nsmap['text']
              def format_node(node):
                if node.tag == '{%s}table-cell' % node.nsmap['table']:
                  return "\n".join(part for part in
                    [format_node(child) for child in node.iterchildren()]
                    if part is not None)
                elif node.tag == '{%s}p' % node.nsmap['text']:
                  part_list = [node.text]
                  part_list.extend(format_node(child)
                    for child in node.iterchildren())
                  return ''.join(part for part in part_list if part)
                elif node.tag == '{%s}s' % node.nsmap['text']:
                  count = int(node.get('{%s}c' % node.nsmap['text'], 1))
                  return ''.join(part for part in
                    [node.text, ' ' * count, node.tail] if part)
                elif node.tag == '{%s}span' % node.nsmap['text']:
                  part_list = [node.text]
                  part_list.extend(format_node(child)
                    for child in node.iterchildren())
                  part_list.append(node.tail)
                  return ''.join(part for part in part_list if part)
                elif node.tag == '{%s}tab' % node.nsmap['text']:
                  return ''.join(part for part in
                    [node.text, '\t', node.tail] if part)
                elif node.tag == '{%s}line-break' % node.nsmap['text']:
                  return ''.join(part for part in
                    [node.text, '\n', node.tail] if part)
                elif node.tag == '{%s}a' % node.nsmap['text']:
                  return ''.join(part for part in
                    [node.text, node.tail] if part)
                # we can also have table:annotation, and they are ignored
              cell_data = format_node(cell) or None

            # Add the cell to the line
            table_line.append(cell_data)

        # Delete empty lines if needed
        if no_empty_lines:
          empty_cell = 0
          for table_cell in table_line:
            if table_cell is None:
              empty_cell += 1
          if empty_cell == len(table_line):
            table_line = None

        # Add the line to the table
        if table_line is not None:
          table.append(table_line)
        else:
          # If the line is empty here, the repeated line will also be empty, so
          # no need to loop.
          break

    # Reduce the table to the minimum
    new_table = self._getReducedTable(table)

    # Get a homogenized table
    if normalize:
      table_size = self._getTableSizeDict(new_table)
      new_table = self._getNormalizedBoundsTable( table=new_table
                                                , width=table_size['width']
                                                , height=table_size['height']
                                                )
    return {table_name: new_table}

  def _getReducedTable(self, table):
    """
      Reduce the table to its minimum size
    """
    empty_lines = 0
    no_more_empty_lines = 0

    # Eliminate all empty cells at the ends of lines and columns
    # Browse the table starting from the bottom for easy empty lines count
    for line in range(len(table)-1, -1, -1):
      empty_cells = 0
      line_content = table[line]
      for cell in range(len(line_content)-1, -1, -1):
        if line_content[cell] in ('', None):
          empty_cells += 1
        else:
          break

      if (not no_more_empty_lines) and (empty_cells == len(line_content)):
        empty_lines += 1
      else:
        line_size = len(line_content) - empty_cells
        table[line] = line_content[:line_size]
        no_more_empty_lines = 1

    table_height = len(table) - empty_lines

    return table[:table_height]

  def _getTableSizeDict(self, table):
    """
      Get table dimension as dictionnary contain both height and width
    """
    return { 'width' : max(len(x) for x in table or [[]])
           , 'height': len(table)
           }

  def _getNormalizedBoundsTable(self, table, width=0, height=0):
    """
      Add necessary cells and lines to obtain given bounds
    """
    table += [[]] * (len(table) - height)
    for line in table:
      line += [None] * (len(line) - width)
    return table

  def _getTableListUnion(self, list1, list2):
    """
      Coerce two dict containing tables structures.
      We need to use this method because a OpenOffice document can hold
        several embedded spreadsheets with the same id. This explain the
        use of random suffix in such extreme case.
    """
    for list2_key in list2:
      # Generate a new table ID if needed
      new_key = list2_key
      while new_key in list1:
        new_key = list2_key + '_' + str(random.randint(1000,9999))
      list1[new_key] = list2[list2_key]
    return list1

allow_class(OOoParser)
allow_class(CorruptedOOoFile)

def newOOoParser(container):
  return OOoParser().__of__(container)


def _utf8_chunks(xml_string, size=8192):
  # type: (str, int) -> bytes
  yield b"""<dummy
    xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:dom="http://www.w3.org/2001/xml-events"
    xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"
    xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
    xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0"
    xmlns:math="http://www.w3.org/1998/Math/MathML"
    xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
    xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:ooo="http://openoffice.org/2004/office"
    xmlns:oooc="http://openoffice.org/2004/calc"
    xmlns:ooow="http://openoffice.org/2004/writer"
    xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
    xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:xforms="http://www.w3.org/2002/xforms"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:anim="urn:oasis:names:tc:opendocument:xmlns:animation:1.0"
    xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
  >"""
  for i in range(0, len(xml_string), size):
    yield xml_string[i:i+size].encode('utf-8')
  yield b"</dummy>"


def _get_optimized_odf_xml_from_fragment(xml_string):
  # type: (str) -> str
  parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
  for chunk in _utf8_chunks(xml_string):
    parser.feed(chunk)
  root = parser.close()

  table_number_columns_spanned = '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}number-columns-spanned'
  for cell in root.iter('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-cell'):
    if cell.get(table_number_columns_spanned) in ("0", "1"):
      cell.attrib.pop(table_number_columns_spanned, None)

  return etree.tostring(root, encoding="unicode")


_optimize_odf_xml_fragment_head_len = None


def optimize_odf_xml_fragment(xml_string):
  # type: (str) -> str
  global _optimize_odf_xml_fragment_head_len
  if _optimize_odf_xml_fragment_head_len is None:
    minimal_content_odf = _get_optimized_odf_xml_from_fragment(u"<content/>")
    # we have "{head}<content/></dummy>", we want to know the length of head
    assert minimal_content_odf.endswith("><content/></dummy>")
    _optimize_odf_xml_fragment_head_len = len(minimal_content_odf) - len("<content/></dummy>")

  optimized = _get_optimized_odf_xml_from_fragment(xml_string)
  return optimized[_optimize_odf_xml_fragment_head_len:-len("</dummy>")]
