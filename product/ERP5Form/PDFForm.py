##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jerome PERRIN <jerome@nexedi.com>
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

from OFS.Image import File
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.ERP5Type import PropertySheet, Permissions
from Products.PageTemplates.Expressions import getEngine, SafeMapping

from urllib import quote
from Products.ERP5Type.Globals import InitializeClass, PersistentMapping, DTMLFile
from AccessControl import ClassSecurityInfo
from AccessControl.SecurityInfo import allow_class

from zLOG import LOG, PROBLEM, WARNING
import types
import popen2
import os
import urllib
import cStringIO
from tempfile import mktemp

try:
  from webdav.Lockable import ResourceLockedError
  SUPPORTS_WEBDAV_LOCKS = 1
except ImportError:
  SUPPORTS_WEBDAV_LOCKS = 0

PDFTK_EXECUTABLE = "pdftk"

class PDFTk:
  """A class to wrapp calls to pdftk executable, found at
    http://www.accesspdf.com/pdftk/
  """
  def catPages(self, pdfFile, cat_option) :
    """ limit to a specific range of pages, like pdftk's cat option"""
    return self._getOutput(
      PDFTK_EXECUTABLE+
      " - cat %s output - "%cat_option, pdfFile)

  def dumpDataFields(self, pdfFile) :
    """ returns the output of pdftk dump_data_fields as dict """
    return self._parseDumpDataFields(self.dumpDataFieldsTxt(pdfFile))

  def fillFormWithDict(self, pdfFile, values) :
    """ fill the form with values in """
    return self.fillFormWithFDF(pdfFile, self._createFdf(pdfFile, values))

  def fillFormWithFDF(self, pdfFile, fdfFile) :
    """ fill the form of pdfFile with the FDF data fdfFile """
    pdfFormFileName = mktemp(suffix=".pdf")
    fdfFormFileName = mktemp(suffix=".fdf")

    if hasattr(pdfFile, "read") :
      pdfFile = pdfFile.read()
    tmpPdfFile = open(pdfFormFileName, "wb")
    tmpPdfFile.write(pdfFile)
    tmpPdfFile.close()

    if hasattr(fdfFile, "read") :
      fdfFile = fdfFile.read()
    tmpFdfFile = open(fdfFormFileName, "wb")
    tmpFdfFile.write(fdfFile)
    tmpFdfFile.close()

    out = self._getOutput(
          PDFTK_EXECUTABLE+
          " %s fill_form %s output - flatten "%(
          pdfFormFileName, fdfFormFileName))
    os.remove(fdfFormFileName)
    os.remove(pdfFormFileName)
    return out

  def dumpDataFieldsTxt(self, pdfFile) :
    """ returns the output of pdftk dump_data_fields as text,
      pdf file is either the file object or its content"""
    return self._getOutput(
            PDFTK_EXECUTABLE+" - dump_data_fields", pdfFile,
            assert_not_empty=0)

  def _parseDumpDataFields(self, data_fields_dump) :
    """ parses the output of pdftk X.pdf dump_data_fields and
        returns a sequence of dicts [{key = value}] """
    fields = []
    for txtfield in data_fields_dump.split("---") :
      field = {}
      for line in txtfield.splitlines() :
        if line.strip() == "" :
          continue
        splits = line.split(":", 1)
        if len(splits) == 2 :
          field[splits[0]] = splits[1].strip()
      if field != {} :
        fields += [field]
    return fields

  def _getOutput(self, command, input=None, assert_not_empty=1) :
    """ returns the output of command with sending input through command's
    input stream (if input parameter is given) """
    stdout, stdin = popen2.popen2(command)
    if input:
      if hasattr(input, "read") :
        input = input.read()
      try :
        stdin.write(input)
      except IOError, e:
        raise IOError, str(e) + " ( make sure "\
          "%s exists and is in your $PATH )"%PDFTK_EXECUTABLE
    stdin.close()
    ret = stdout.read()
    stdout.close()
    if assert_not_empty and len(ret) == 0 :
      raise IOError, "Got no output from external program, make sure"\
                   " %s exists and is in your $PATH"%PDFTK_EXECUTABLE
    return ret

  def _escapeString(self, value) :
    if value is None :
      return ''
    #Convert value to string
    #See PDF Reference v1.7 - 3.8.1 String Types
    if isinstance(value, unicode):
      string = '\xfe\xff' + value.encode('utf-16BE')
    else:
      string = '\xfe\xff' + unicode(str(value), 'utf-8').encode('utf-16BE')
    escaped  = ''
    for c in string :
      if (ord(c) == 0x28 or # open paren
          ord(c) == 0x29 or # close paren
          ord(c) == 0x5c):  # backslash
        escaped += '\\' + c
      elif ord(c) < 32 or 126 < ord(c):
        escaped += "\\%03o" % ord(c)
      else:
        escaped += c
    return escaped

  def _createFdf(self, pdfFile, values, pdfFormUrl=None) :
    """ create an fdf document with the dict values """
    fields = self.dumpDataFields(pdfFile)
    fdf = "%FDF-1.2\x0d%\xe2\xe3\xcf\xd3\x0d\x0a"
    fdf += "1 0 obj\x0d<< \x0d/FDF << /Fields [ "
    for field in fields:
      # if the field is a check box
      if field.get('FieldType') == 'Button' and  \
         field.get('FieldStateOption') in ('Yes','Off'):
        # if the check box is check
        fdf += "<< /Ft /%s\n/V /%s\n/T(%s)>> \x0d" % (
            'Btn',
            values.get(field.get('FieldName')) and 'Yes' or 'Off',
            self._escapeString(field.get('FieldName')))
      # if the field is a Input Button
      # ... but this is not working yet
      # so there is a Warning
      elif field.get('FieldType') == 'Button' and  \
           field.get('FieldStateOption') is None:
        LOG("Field " + field.get('FieldName'),
             WARNING,
             "can't be returned in PDF file")
      else:
        fdf += "<</V (%s) /T (%s) /ClrF 2 /ClrFf 1 >> \x0d" % (
           self._escapeString(values.get(field.get('FieldName'))),
           self._escapeString(field.get('FieldName')))

    fdf += "] \x0d"

    # the PDF form filename or URL, if any
    if pdfFormUrl not in ("", None) :
      fdf += "/F ("+self._escapeString(pdfFormUrl)+") \x0d"

    fdf += ">> \x0d>> \x0dendobj\x0d"
    fdf += "trailer\x0d<<\x0d/Root 1 0 R \x0d\x0d>>\x0d%%EOF\x0d\x0a"
    return fdf


# Constructors
manage_addPDFForm = DTMLFile("dtml/PDFForm_add", globals())
def addPDFForm(self, id, title="", pdf_file=None,  REQUEST=None):
  """ Add a pdf form to folder. """
  # add actual object
  id = self._setObject(id, PDFForm(id, title, pdf_file))

  # upload content
  if pdf_file:
    self._getOb(id).manage_upload(pdf_file)
    self._getOb(id).content_type = "application/pdf"

  if REQUEST :
    u = REQUEST['URL1']
    if REQUEST['submit'] == " Add and Edit ":
      u = "%s/%s" % (u, quote(id))
    REQUEST.RESPONSE.redirect(u+'/manage_main')


class CalculatedValues :
  """This class holds a reference to calculated values, for use in TALES,
  because in PDF Form filling, there is lots of references to others cell
  values (sums ...). This class will be in TALES context under the key 'cell'

  It will make possible the use of TALES expressions like :
    cell/a95
    python: cell['a1'] + cell['a2']

  """
  security = ClassSecurityInfo()
  def __init__(self, values, key, not_founds) :
    """ 'values' are a dict of already calculated values
    'key' is the key we are evaluating
    'not_founds' is the list in which we will put not found values  """
    self.__values      = values
    self.__key         = key
    self.__not_founds  = not_founds
  def __getitem__(self, attr) :
    if not self.__values.has_key(attr) :
      self.__not_founds.append(attr)
      return 0 # We do not return None, so that cell['a1'] + cell['a2']
      # doesn't complain that NoneType doesn't support + when a1 not found
    return self.__values[attr]
  __getattr__ = __getitem__
allow_class(CalculatedValues)


class CircularReferencyError(ValueError):
  """A circular reference is found trying to evaluate cell TALES."""


class EmptyERP5PdfFormError(Exception):
  """Error thrown when you try to display an empty Pdf. """
allow_class(EmptyERP5PdfFormError)



class PDFForm(File):
  """This class allows to fill PDF Form with TALES expressions,
    using a TALES expression for each cell.

  TODO:
    * cache compiled TALES
    * set _v_errors when setting invalid TALES (setCellTALES can raise, but
      not doEditCells)

  OBSOLETE : Not used any more. Such functionalities could be done with more
  modern tools
  """

  meta_type = "ERP5 PDF Form"
  icon = "www/PDFForm.png"

  # Those 2 are ugly names, but we keep compatibility
  # the page range we want to print (a TALES expr)
  __page_range__ = ''
  # the method to format values (a TALES expr)
  __format_method__ = ''

  # Declarative Security
  security = ClassSecurityInfo()

  # Declarative properties
  _properties = File._properties + (
      {'id' : 'download_url', 'type' : 'lines', 'mode' : 'w' },
      {'id' : 'business_template_include_content',
              'type' : 'boolean', 'mode' : 'w' },
  )
  download_url = ()
  business_template_include_content = 1

  # Constructors
  constructors =   (manage_addPDFForm, addPDFForm)

  manage_options =  ( (
        {'label':'Edit Cell TALES', 'action':'manage_cells'},
        {'label':'Display Cell Names', 'action':'showCellNames'},
        {'label':'Test PDF generation', 'action':'generatePDF'},
        {'label':'View original', 'action':'viewOriginal'},
        {'label':'Download PDF content from URL', 'action':'downloadPdfContent'},
      ) +
      filter(lambda option:option['label'] != "View", File.manage_options)
  )

  def __init__ (self, id, title='', pdf_file=''):
    # holds information about all cells, even those not related to this form
    self.all_cells = PersistentMapping()
    # holds the cells related to this pdf form
    self.cells = PersistentMapping()

    # File constructor will set the file content
    File.__init__(self, id, title, pdf_file)

  security.declareProtected(Permissions.ManagePortal, 'manage_upload')
  def manage_upload(self, file=None, REQUEST=None) :
    """ Zope calls this when the content of the enclosed file changes.
    The 'cells' attribute is updated, but already defined cells are not
    erased, they are saved in the 'all_cells' attribute so if the pdf
    file is reverted, you do not loose the cells definitions.
    """
    if not file or not hasattr(file, "read") :
      raise ValueError ("The pdf form file should not be empty")

    file.seek(0) # file is always valid here
    values = PDFTk().dumpDataFields(file)
    self.cells = {}
    for v in values :
      if v["FieldType"] not in ("Button", "Choice")\
                    or not int(v["FieldFlags"]) & 65536:
        k = v["FieldName"]
        if not self.all_cells.has_key(k) :
          self.cells[k] = ""
        else :
          self.cells[k] = self.all_cells[k]
    self.all_cells.update(self.cells)
    file.seek(0)
    File.manage_upload(self, file, REQUEST)
    if REQUEST:
      message = "Saved changes."
      return self.manage_main(self, REQUEST, manage_tabs_message=message)

  security.declareProtected(Permissions.ViewManagementScreens, 'manage_cells')
  manage_cells = PageTemplateFile('www/PDFForm_manageCells',
                                   globals(), __name__='manage_cells')

  security.declareProtected(Permissions.View, 'manage_FTPget')
  def manage_FTPget(self, REQUEST=None, RESPONSE=None) :
    """ get this pdf form via webDAV/FTP, it returns an XML
    representation of all the fields, then the pdf itself."""
    from xml.dom.minidom import getDOMImplementation
    impl = getDOMImplementation()
    newdoc = impl.createDocument(None, "pdfform", None)
    top_element = newdoc.documentElement
    cells = newdoc.createElement('cells')
    pdfform_cell_list = self.cells.keys()
    pdfform_cell_list.sort()
    for cell in pdfform_cell_list :
      cell_node = newdoc.createElement('cell')
      cell_node.setAttribute('name', cell)
      tales = newdoc.createTextNode(self.cells[cell])
      cell_node.appendChild(tales)
      cells.appendChild(cell_node)

    top_element.appendChild(cells)
    pdf_data = newdoc.createElement('pdf_data')
    pdf_content = newdoc.createTextNode(str(self.data))
    pdf_data.appendChild(pdf_content)
    top_element.appendChild(pdf_data)
    content = newdoc.toprettyxml('  ')
    if RESPONSE :
      RESPONSE.setHeader('Content-Type', 'application/x-erp5-pdfform')
      RESPONSE.setHeader('Content-Length', len(content))
    return content
  manage_DAVget = manage_FTPget

  security.declareProtected(Permissions.ManagePortal, 'PUT')
  def PUT(self, REQUEST, RESPONSE):
    """(does not) Handle HTTP PUT requests."""
    RESPONSE.setStatus(501)
    return RESPONSE
  manage_FTPput = PUT

  security.declareProtected(Permissions.View, 'hasPdfContent')
  def hasPdfContent(self) :
    """Return true if there is an enclosed PDF in this PDF Form."""
    return self.data is not None and len(self.data) > 0

  security.declareProtected(Permissions.ManagePortal, 'downloadPdfContent')
  def downloadPdfContent(self, REQUEST=None) :
    """Download the pdf content from one of `download_url` URL """
    for url in self.getProperty('download_url') :
      try :
        response = urllib.urlopen(url)
      except IOError, e :
        LOG("PDFForm", WARNING, "Unable to download from %s" % url, e)
        continue
      if response.headers.getheader('Content-Type') != 'application/pdf':
        LOG("PDFForm", WARNING, "%s is not application/pdf" % url)
        continue
      self.manage_upload(cStringIO.StringIO(response.read()))
      self.content_type = 'application/pdf'
      if REQUEST is not None :
        return REQUEST.RESPONSE.redirect(
              "%s/manage_main?manage_tabs_message=Content+Downloaded"
              % self.absolute_url())
      return
    raise ValueError, "Unable to download from any url from the "\
                      "`download_url` property."

  security.declareProtected(Permissions.ManagePortal,
                           'deletePdfContent')
  def deletePdfContent(self) :
    """Reset the pdf content. """
    assert self.getProperty('download_url'), "Download URL must be set"\
        " to delete content from PDF Form '%s'" % self.getId()
    self.data = None

  security.declareProtected(Permissions.View, 'viewOriginal')
  def viewOriginal(self, REQUEST=None, RESPONSE=None, *args, **kwargs) :
    """ publish original pdf """
    pdf = File.index_html(self, REQUEST, RESPONSE, *args, **kwargs)
    RESPONSE.setHeader('Content-Type', 'application/pdf')
    RESPONSE.setHeader('Content-Disposition', 'inline;filename="%s.pdf"'
        % (self.title_or_id()))
    return pdf

  security.declareProtected(Permissions.View, 'showCellNames')
  def showCellNames(self, REQUEST=None, RESPONSE=None, *args, **kwargs) :
    """ generates a pdf with fields filled-in by their names,
     usefull to fill in settings.
    """
    values = {}
    for cell in self.cells.keys() :
      values[cell] = cell
    pdf = PDFTk().fillFormWithDict(str(self.data), values)
    if RESPONSE :
      RESPONSE.setHeader('Content-Type', 'application/pdf')
      RESPONSE.setHeader('Content-Length', len(pdf))
      RESPONSE.setHeader('Content-Disposition',
                         'inline;filename="%s.template.pdf"' % (
                              self.title_or_id()))
    return pdf

  security.declareProtected(Permissions.ManagePortal, 'doEditCells')
  def doEditCells(self, REQUEST, RESPONSE=None):
    """ This is the action to the 'Edit Cell TALES' tab. """
    if SUPPORTS_WEBDAV_LOCKS and self.wl_isLocked():
      raise ResourceLockedError, "File is locked via WebDAV"

    for k, v in self.cells.items() :
      self.setCellTALES(k, REQUEST.get(str(k), v))
    self.__format_method__ = REQUEST.get("__format_method__")
    self.__page_range__ = REQUEST.get("__page_range__")

    if RESPONSE:
      return self.manage_cells(manage_tabs_message="Saved changes.")

  security.declareProtected(Permissions.View, 'generatePDF')
  def generatePDF(self, REQUEST=None, RESPONSE=None, *args, **kwargs) :
    """ generates the PDF with form filled in """
    if not self.hasPdfContent() :
      raise EmptyERP5PdfFormError, 'Pdf content must be downloaded first'
    values = self.calculateCellValues(REQUEST, *args, **kwargs)
    context = { 'here' : self.aq_parent,
                'context' : self.aq_parent,
                'request' : REQUEST }
    if self.__format_method__:
      compiled_tales = getEngine().compile(self.__format_method__)
      format_method = getEngine().getContext(context).evaluate(compiled_tales)
      # try to support both method name and method object
      if not callable(format_method) :
        format_method = self.restrictedTraverse(format_method)
      if callable(format_method) :
        for k, v in values.items() :
          values[k] = format_method(v, cell_name=k)
      else :
        LOG("PDFForm", PROBLEM,
            'format method (%r) is not callable' % format_method)
    data = str(self.data)
    pdftk = PDFTk()
    pdf =pdftk.fillFormWithDict(data, values)
    if self.__page_range__:
      compiled_tales = getEngine().compile(self.__page_range__)
      page_range = getEngine().getContext(context).evaluate(compiled_tales)
      if page_range :
        pdf = pdftk.catPages(pdf, page_range)
    if RESPONSE :
      RESPONSE.setHeader('Content-Type', 'application/pdf')
      RESPONSE.setHeader('Content-Length', len(pdf))
      RESPONSE.setHeader('Content-Disposition', 'inline;filename="%s.pdf"'
            % (self.title_or_id()))
    return pdf
  index_html = generatePDF
  __call__ = generatePDF

  security.declareProtected(Permissions.View, 'calculateCellValues')
  def calculateCellValues(self, REQUEST=None, *args, **kwargs) :
    """ returns a dict of cell values """
    # values to be returned
    values = {}
    # list of values that need to be reevaluated (i.e. they depend on the
    # value of a cell that was not already evaluated when evaluating them )
    uncalculated_values = []
    # cleanup kw arguments, not to pass `cell` twice to evaluateCell
    if 'cell' in kwargs:
      del kwargs['cell']

    for cell_name in self.cells.keys() :
      not_founds = []
      value = self.evaluateCell(cell_name, REQUEST = REQUEST,
              cell = SafeMapping(CalculatedValues(
                              values, cell_name, not_founds)), **kwargs)
      if len(not_founds) != 0 :
        uncalculated_values.append(cell_name)
      else :
        values[cell_name] = value
    # now we iterate on the list of uncalculated values, trying
    # to evaluate them again, if an iteration doesn't decrement
    # the length of this list, there are some circular references
    # and we cannot continue.
    while 1 :
      uncalculated_values_len = len(uncalculated_values)
      if uncalculated_values_len == 0 :
        return values
      for cell_name in uncalculated_values :
        not_founds = []
        value = self.evaluateCell(cell_name, REQUEST = REQUEST,
                cell = SafeMapping(CalculatedValues(
                                values, cell_name, not_founds)), **kwargs)
        if len(not_founds) == 0 :
          uncalculated_values.remove(cell_name)
          values[cell_name] = value
      if len(uncalculated_values) == uncalculated_values_len :
        raise CircularReferencyError("Unable to evaluate cells: %r"
                                       % (uncalculated_values, ))

  security.declareProtected(Permissions.View, 'getCellNames')
  def getCellNames(self, REQUEST=None) :
    """ returns a list of cell names """
    names = self.cells.keys()
    names.sort()
    return names

  security.declareProtected(Permissions.ManagePortal, 'deleteCell')
  def deleteCell(self, cell_name):
    """ Delete a cell.
    As setCellTALES add the cell if it is not present, we must have a
    way to remove cells created by mistake. """
    del self.all_cells[cell_name]
    del self.cells[cell_name]

  security.declareProtected(Permissions.ManagePortal, 'setCellTALES')
  def setCellTALES(self, cell_name, TALES):
    """ changes the TALES expression that will be used to evaluate
    cell value """
    if type(TALES) != types.StringType :
      LOG("PDFForm", PROBLEM,
         'TALES is not a string for cell "%s", it is = "%s"'
          %(cell_name, `TALES`))
      raise ValueError, 'TALES must be a string'
    self.all_cells[str(cell_name)] = self.cells[str(cell_name)] = TALES
    # invalidate for persistence
    self.all_cells = self.all_cells

  security.declareProtected(Permissions.View, 'getCellTALES')
  def getCellTALES(self, cell_name):
    """ returns the TALES expression associated with this cell """
    return self.cells[str(cell_name)]

  security.declareProtected(Permissions.View, 'evaluateCell')
  def evaluateCell(self, cell_name, REQUEST=None, **kwargs):
    """ evaluate the TALES expression for this cell """
    cell_name = str(cell_name)
    # we don't pass empty strings in TALES engine
    # (and this also raises the KeyError for non existant cells)
    if not self.cells[cell_name] :
      return None
    context = { 'here' : self.aq_parent,
                'context' : self.aq_parent,
                'cell_name' : cell_name,
                'request' : REQUEST }
    context.update (kwargs)
    __traceback_info__ = 'Evaluating cell "%s"' % cell_name
    compiled_tales = getEngine().compile(self.cells[cell_name])
    value = getEngine().getContext(context).evaluate(compiled_tales)
    return value

  security.declareProtected(Permissions.ManagePortal, 'setAllCellTALES')
  def setAllCellTALES(self, new_cells) :
    """ set all cell values from a dict containing { name: TALES } """
    for cell_name, cell_TALES in new_cells.items() :
      self.setCellTALES(cell_name, cell_TALES)

  security.declareProtected(Permissions.View, 'getFormatMethodTALES')
  def getFormatMethodTALES(self):
    """ returns the TALES expression for the format method attribute """
    return self.__format_method__

  security.declareProtected(Permissions.ManagePortal, 'setFormatMethodTALES')
  def setFormatMethodTALES(self, TALES):
    """ sets TALES expression for the format method attribute """
    self.__format_method__ = str(TALES)

  security.declareProtected(Permissions.View, 'getPageRangeTALES')
  def getPageRangeTALES(self):
    """ returns the TALES expression for the page range attribute """
    return self.__page_range__

  security.declareProtected(Permissions.ManagePortal, 'setPageRangeTALES')
  def setPageRangeTALES(self, TALES):
    """ sets TALES expression for the page range attribute """
    self.__page_range__ = str(TALES)

InitializeClass(PDFForm)

