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

from Products.PythonScripts.Utility import allow_class
from ZPublisher.HTTPRequest import FileUpload
from xml.dom.ext.reader import PyExpat
from xml.dom import Node
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from zipfile import ZipFile
from zLOG import LOG
import imghdr



class CorruptedOOoFile(Exception): pass



class OOoParser:
  """
    General purpose tools to parse and handle OpenOffice v1.x documents.
  """


  # Declarative security
  security = ClassSecurityInfo()


  security.declarePrivate('__init__')
  def __init__(self):
    # Create the PyExpat reader
    self.reader = PyExpat.Reader()
    self.oo_content_dom = None
    self.oo_styles_dom  = None
    self.oo_files = {}
    self.pictures = {}
    self.ns = {}


  security.declarePublic('openFile')
  def openFile(self, file_raw_data):
    """
      Load all files in the zipped OpenOffice document
    """
    # Try to unzip the Open Office doc
    LOG('KevLog >>>>>>>>',0,repr(file_raw_data))
    try:
      oo_unzipped = ZipFile(file_raw_data, mode="r")
    except:
      raise CorruptedOOoFile
    # Test the integrity of the file
    if oo_unzipped.testzip() != None:
      raise CorruptedOOoFile

    # Initialize internal variables
    self.__init__()

    # List and load the content of the zip file
    for name in oo_unzipped.namelist():
      self.oo_files[name] = oo_unzipped.read(name)

    # Get the main content and style definitions
    self.oo_content_dom = self.reader.fromString(self.oo_files["content.xml"])
    self.oo_styles_dom  = self.reader.fromString(self.oo_files["styles.xml"])

    # Create a namespace table
    doc_ns = self.oo_styles_dom.getElementsByTagName("office:document-styles")
    for i in range(doc_ns[0].attributes.length):
        if doc_ns[0].attributes.item(i).nodeType == Node.ATTRIBUTE_NODE:
            name = doc_ns[0].attributes.item(i).name
            if name[:5] == "xmlns":
                self.ns[name[6:]] = doc_ns[0].attributes.item(i).value


  security.declarePublic('getPictures')
  def getPictures(self):
    """
      Return a dictionnary of all pictures in the document
    """
    if len(self.pictures) <= 0:
      for file_name in self.oo_files:
        raw_data = self.oo_files[file_name]
        pict_type = imghdr.what(None, raw_data)
        if pict_type != None:
          self.pictures[file_name] = raw_data
    return self.pictures


  security.declarePublic('getContentAsDom')
  def getContentAsDom(self):
    """
      Return the DOM tree of the main OpenOffice content
    """
    return self.oo_content_dom


  security.declarePublic('getEmbeddedSpreadsheetsAsDom')
  def getEmbeddedSpreadsheetsAsDom(self):
    """
      Return a list of existing embedded spreadsheets in the file as DOM tree
    """
    spreadsheets = []
    # List all embedded spreadsheets
    emb_objects = self.oo_content_dom.getElementsByTagName("draw:object")
    for embedded in emb_objects:
      document = embedded.getAttributeNS(self.ns["xlink"], "href")
      if document:
        try:
          object_content = self.reader.fromString(self.oo_files[document[3:] + '/content.xml'])
          if object_content.getElementsByTagName("table:table"):
            spreadsheets.append(object_content)
        except:
          pass
    return spreadsheets


  security.declarePublic('getEmbeddedSpreadsheetsAsTable')
  def getEmbeddedSpreadsheetsAsTable(self):
    """
      Return a list of existing spreadsheets in the file as table
    """
    tables = []
    for spreadsheet in self.getEmbeddedSpreadsheetsAsDom():
      new_table = self.getSpreadsheetAsTable(spreadsheet)
      if new_table != None:
        tables.append(new_table)
    return tables


  security.declarePublic('getSpreadsheetAsTable')
  def getSpreadsheetAsTable(self, spreadsheet=None):
    """
      This method convert an OpenOffice spreadsheet to a simple table.
      This code is base on the oo2pt tool (http://cvs.sourceforge.net/viewcvs.py/collective/CMFReportTool/oo2pt).
    """
    if spreadsheet == None:
      return None

    # Create the table
    for table in spreadsheet.getElementsByTagName("table:table"):
      texts = []

      # Store informations on column widths and default styles
      line_number = 0
      for col in table.getElementsByTagName("table:table-column"):
        repeated = col.getAttributeNS(self.ns["table"],"number-columns-repeated")

      # Scan table and store usable informations
      for line in table.getElementsByTagName("table:table-row"):
        repeated_lines = line.getAttributeNS(self.ns["table"], "number-rows-repeated")
        if not repeated_lines:
          repeated_lines = 1
        else:
          repeated_lines = int(repeated_lines)

        for i in range(repeated_lines):
          texts_line = {'line':[]}
          col_number=0

          for cell in line.getElementsByTagName("table:table-cell"):
            repeated_cells = cell.getAttributeNS(self.ns["table"],"number-columns-repeated")
            if not repeated_cells:
              repeated_cells = 1
            else:
              repeated_cells = int(repeated_cells)

            for j in range(repeated_cells):
              texts_cell = {'texts':[]}
              textTags = cell.getElementsByTagName("text:p")

              for text in textTags:
                for k in range(text.childNodes.length):
                  child = text.childNodes[k]
                  if child.nodeType == Node.TEXT_NODE:
                    texts_cell['texts'].append(child.nodeValue)

              texts_line['line'].append(texts_cell)
              col_number += 1

          texts.append(texts_line)
          line_number += 1

      # Reduce the table to the minimum
      text_min_bounds = self._getTableMinimalBounds(texts)
      self._setTableBounds(texts, width=text_min_bounds['width'], height=text_min_bounds['height'])

    return texts


  security.declarePrivate('_getTableMinimalBounds')
  def _getTableMinimalBounds(self, texts):
    """
      Calcul the minimum size of a text table
    """
    empty_lines = 0
    no_more_empty_lines = 0

    # Eliminate all empty cells at the ends of lines and columns
    for line in range(len(texts)-1, -1, -1):
      empty_cells = 0
      line_content = texts[line]['line']
      for cell in range(len(line_content)-1, -1, -1):
        if len(line_content[cell]['texts']) == 0:
          empty_cells += 1
        else:
          break
      if (not no_more_empty_lines) and (empty_cells == len(line_content)):
        empty_lines += 1
      else:
        line_size = len(line_content) - empty_cells
        texts[line]['line'] = line_content[:line_size]
        no_more_empty_lines = 1

    texts_size = len(texts) - empty_lines
    texts = texts[:texts_size]

    # Determine minimum bounds
    max_cols = 0
    for line in range(len(texts)):
      line_content = texts[line]['line']
      if len(line_content) > max_cols: max_cols = len(line_content)

    return { 'width':max_cols, 'height':len(texts) }


  security.declarePrivate('_setTableBounds')
  def _setTableBounds(self, texts, width=0, height=0):
    """
      Enlarge a text table to given bounds
    """
    while height > len(texts):
      texts.append( {'line':[]} )
    for line in range(height):
      while width > len(texts[line]['line']):
        texts[line]['line'].append( {'texts':[]} )



InitializeClass(OOoParser)
allow_class(OOoParser)
