# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                     Mayoro DIAGNE <mayoro@nexedi.com>
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
import commands
import re
import random
from AccessControl import ClassSecurityInfo
from tempfile import NamedTemporaryFile

PDFTK_EXECUTABLE = "pdftk"

class PDFParser:
  """
    PDF parser API provide methods wich allow to manipulate a pdf file allowing
    to convert pages as images
  """
  security = ClassSecurityInfo()

  def __init__(self, pdf_file_descriptor):
    """
    initialise self.data with pdf_file_descriptor if string's
    The __init__ function can take either a filename, an open file object
    or the content of the file
    Initialise  self.width self.height and self.pages (page count)
    """
    self.width = None
    self.height  = None
    self.pages = None

    if pdf_file_descriptor is None:
      raise ValueError, "No PDF file provided, please choose a pdf form "


    if type(pdf_file_descriptor) == 'str':
      self.data = pdf_file_descriptor
    elif hasattr(pdf_file_descriptor, "read"):
      pdf_file_descriptor.seek(0)
      self.data = pdf_file_descriptor.read()
      pdf_file_descriptor.close()
    else:
      source = open(pdf_file_descriptor, "rb")
      source.seek(0)
      self.data = source.read()
      source.close()

    # opening new file on HDD to save PDF content
    temp_pdf_file = NamedTemporaryFile(mode= "w+b")
    temp_pdf_name = temp_pdf_file.name
    # going to the begining of the input file
    # saving content
    temp_pdf = open(temp_pdf_name,'w')
    # saving content
    temp_pdf.write(self.data)
    temp_pdf.close()
    command_output = commands.getstatusoutput('pdfinfo %s' % \
        temp_pdf_name)
    if command_output[0] != 0:
        raise ValueError, 'Error: convert command failed with the following'\
                          'error message : \n%s' % command_output[1]

    # get the pdf page size
    rawstr = r'''
        Page\ssize:        #begining of the instersting line
        \s*                #some spaces
        (\S+)\sx\s(\S+)    #the matching pattern : width and height in pts'''
    compile_obj = re.compile(rawstr, re.MULTILINE | re.VERBOSE)
    match_obj = re.search(compile_obj, command_output[1])
    width, height = match_obj.groups()

    # get the pdf page_count
    rawstr = r'''
        Pages:        #begining of the instersting line
        \s*                #some spaces
        (\S+)    #the matching pattern : width and height in pts'''
    compile_obj = re.compile(rawstr, re.MULTILINE | re.VERBOSE)
    match_obj = re.search(compile_obj, command_output[1])
    page_count = match_obj.groups()[0]
    attributes = {}
    self.width = int(round(float(width)))
    self.height = int(round(float(height)))
    self.pages = int(page_count)

  def getData(self):
    """
    Return the content of the pdf file
    """
    return self.data

  security.declarePublic('getPageCount')
  def getPageCount(self):
    """
    Return the page count of the pdf file
    """
    #self.getContentInformation()['Pages']
    return  self.pages

  security.declarePublic('getPageWidth')
  def getPageWidth(self):
    """
    Return the width of the pdf file
    """
    return  self.width

  security.declarePublic('getPageHeight')
  def getPageHeight(self):
    """
    Return the page count of the pdf file
    """
    return  self.height

  security.declarePublic('getPageImage')
  def getPageImage(self, page, format, resolution, quality):
    """
    Return a temporary Image object containing the pape page of the pdf file
    width, height: attributes in pixel (px)
    format: jpg, png, etc...
    resolution: resolution of produced image for exemple 600
    quality: quality of produced image for exemple 200 raisonable quality
    more hight is quality more time it takes to be gererated
    """
    temp_pdf_document_name = "tmp%s.pdf" %  str(random.random()).split('.')[-1]
    temp_pdf_document = self.newContent(temp_object=True,
      portal_type='PDF Document', id=temp_pdf_document_name)
    temp_pdf_document.setData(self.getData())
    display = 'xlarge'
    mime, image_data = temp_pdf_document.convert(format = format,
                                                 frame = page,
                                                 resolution = resolution,
                                                 quality = quality,
                                                 display = display)
    page_image = None
    if image_data is not None:
      page_image = self.newContent(temp_object=True, portal_type='Image',
        id="page_%s" % page)
      page_image.setData(page_image)
    return page_image


  def getFlattenedPDF(self):
    """
     Return a flattened PDF. It's use to merge an input PDF's interactive
     form fields with the PDF's pages
    """
    temp_input_file = NamedTemporaryFile(mode= "w+b")
    temp_input_name = temp_input_file.name
    temp_input = open(temp_input_name,'w')
    temp_input.write(self.getData())
    temp_input.close()
    temp_output_file = NamedTemporaryFile(mode= "w+b")
    temp_output_name = temp_output_file.name
    command_output = commands.getstatusoutput('pdftk %s output %s flatten'\
                      % (temp_input_name, temp_output_name))
    if command_output[0] != 0:
      raise IOError, "pdftk failed with the following error %s"\
                      % command_output[1]
    temp_output = open(temp_output_name,'rb')
    temp_output.seek(0)
    datas = temp_output.read()
    temp_output.close()
    return datas



