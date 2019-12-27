# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
#                     Mayoro DIAGNE <mayoro@nexedi.com>
#                     Guy Osvald <guy@nexedi.com>
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

import StringIO
from hashlib import md5
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.ERP5Type import ERP5TypeInformation
from Products.ERP5Form.Form import ERP5Form
from Products.ERP5Form.PDFForm import PDFForm
from Products.ERP5Form.ScribusParser import ScribusParser
from Products.ERP5Form.PDFParser import PDFParser
from OFS.DTMLDocument import DTMLDocument
from Products.ERP5Type.Utils import convertToUpperCase
from Products.ERP5Type.Core.ActionInformation import CacheableAction

def getPropertiesCSSDict(parsed_scribus
                      , page_gap
                      , image_width
                      , image_height
                      , scribus_width
                      , scribus_height
                      , space_between_pages
                      , portal_preferences):
  """
  recover all CSS data relative to the current page_object (field)
  and save these information in the output dict
  """
  #image_width = 800
  scaling_factor = min(float(image_width)/scribus_width,
                       float(image_height)/scribus_height)
  properties_css_dict = {}
  properties_css_dict['head'] = {}
  properties_css_dict['standard'] = {}
  properties_css_dict['error'] = {}
  properties_css_dict['err_d'] = {}
  pages = range(len(parsed_scribus))
  for page in pages:
    page_content =  parsed_scribus[page]
    page_id = "page_%s" % page
    properties_css_page = {}
    properties_css_pagediv = {}
    properties_page = {}
    #properties_css_page['position'] = 'relative'
    # creating image class for background
    properties_css_background = {}
    # making background id
    background_id =  page_id + '_background'
    # making page div id
    pagediv_id =  page_id + ' div'
    #getting properties
    properties_css_background['position'] = 'absolute'
    #creating corresponding page group to form
    if page == 0:
       # margin-top = 0 (first page)
      properties_css_page['margin-top'] = "%spx" % (0)
    else:
      properties_css_page['margin-top'] = "%spx" % (40)

    properties_css_page['margin']  = "0 auto 20px 0"
    properties_css_page['border-color'] = "#CCCCCC"
    properties_css_page['border-'] = "dotted none none"
    properties_css_page['border-'] = "1px 0pt 0pt"
    properties_css_page['border'] = "1px solid #999999"

    properties_css_pagediv['background'] = "transparent"
    properties_css_pagediv['border'] = "0"

    # set width and height on page block
    properties_css_page['width'] = str (image_width) + 'px'
    properties_css_page['height'] = str (image_height) + 'px'
    properties_page['actual_width'] = scribus_width
    properties_page['actual_height'] = scribus_height
    properties_css_background['height'] = str(image_height) + 'px'
    properties_css_background['width'] = str (image_width) + 'px'
    # adding properties dict to global dicts
    properties_css_dict['head'][page_id] = properties_css_page
    properties_css_dict['head'][background_id] = properties_css_background
    properties_css_dict['head'][pagediv_id] = properties_css_pagediv
    for field_name, properties_field in page_content:
      properties_field['position_y'] = \
          str(float(properties_field['position_y']) - \
          (scribus_height + page_gap)* page)
      # Processing object for CSS data
      # declaring dict containing all css data
      # _stand for general display
      field_dict = {}
      properties_css_object_stand = {}
      # _error when an error occurs
      properties_css_object_error = {}
      # _err_d to diplay the text error
      properties_css_object_err_d = {}
      #defining global properties
      properties_css_object_stand['position'] = 'absolute'
      properties_css_object_error['position'] = 'absolute'
      properties_css_object_err_d['position'] = 'absolute'
      properties_css_object_stand['padding'] = '0px'
      properties_css_object_error['padding'] = '0px'
      properties_css_object_err_d['padding'] = '0px'
      # getting field height
      properties_css_object_stand['height'] = \
          str(scaling_factor * float(properties_field['size_y'])) + 'px'
      properties_css_object_error['height'] = \
          str(scaling_factor * float(properties_field['size_y'])) + 'px'

      # Use default font-size 12px for harmonization
      properties_css_object_stand['font-size'] = '12px'
      properties_css_object_error['font-size'] = '12px'

      properties_css_object_err_d['margin-left'] = str(image_width +
          space_between_pages ) + 'px'
      properties_css_object_err_d['white-space'] = 'nowrap'
      properties_css_object_stand['margin-top'] = \
        str((scaling_factor *float(properties_field['position_y']))) + 'px'
      properties_css_object_error['margin-top'] = \
        str((scaling_factor *float(properties_field['position_y']))) + 'px'
      properties_css_object_err_d['margin-top'] = \
        str((scaling_factor *float(properties_field['position_y']))) + 'px'
      # adding special text_color for text error
      properties_css_object_err_d['color'] = 'rgb(255,0,0)'
      # then getting additional properties
      if properties_field['required'] ==1:
        # field is required: using special color
        # color is specified as light-blue when standard
        # color = 'green' when error
        properties_css_object_stand['background'] = 'rgb(236,245,220)'
        properties_css_object_error['background'] = 'rgb(128,128,255)'
      elif properties_field['type'] != 'TextAreaField':
        properties_css_object_stand['background'] = '#F5F5DC'
        properties_css_object_error['background'] = 'rgb(255,64,64)' #Previously,
                                            #B9D9D4 - should become a parameter
      else:
        properties_css_object_stand['background'] = '#F5F5DC' # Previously,
                                            #B9D9D4 - should become a parameter
        properties_css_object_error['background'] = 'rgb(255,64,64)'

      # add completed properties (in our case only the class rendering the text
      # beside an error) to the return dict
      properties_css_dict['err_d'][field_name] = properties_css_object_err_d
      # the following variable take the number of field to render for this object
      field_nb = 1
      # now processing special rendering
      if properties_field['rendering']=='single':
        # single rendering (like StringField, TextArea, etc.).
        # Do not need any special treatment
        properties_css_object_stand['width'] = \
          str(scaling_factor * float(properties_field['size_x'])) + 'px'
        properties_css_object_error['width'] = \
          str(scaling_factor * float(properties_field['size_x'])) + 'px'
        properties_css_object_stand['margin-left'] = \
          str((scaling_factor * float(properties_field['position_x']))) + 'px'
        properties_css_object_error['margin-left'] = \
          str((scaling_factor * float(properties_field['position_x']))) + 'px'
        field_id = field_name + '_class'
        # adding all these properties to the global dicts
        properties_css_dict['standard'][field_id] = properties_css_object_stand
        properties_css_dict['error'][field_id] = properties_css_object_error
      else:
        sub_field_dict = {}
        field_dict = {}
        if properties_field['type'] == 'RelationStringField':
          # rendering a relationStringField, based on two input areas
          # processing rendering of the two input fields. for that
          # each has to be evaluated and the values will be saved in
          # a dict
          # uptading number of fields to render
          field_nb = 2
          #field_1 = field_name + '_class_1'
          # processing main StringField
          field_dict[1] = {}
          field_dict[1]['width'] = \
              str(scaling_factor*(float(properties_field['size_x']) / 2)) + 'px'
          field_dict[1]['margin-left'] = \
              str(scaling_factor*float(properties_field['position_x'])) + 'px'
          # processing secondary input picture
          field_dict[2] = {}
          field_dict[2]['width'] = \
              str(scaling_factor(float(properties_field['size_x']) /2)) + 'px'
          field_dict[2]['margin-left'] = \
                str(scaling_factor(float(properties_field['size_x']) /2  +\
                float(properties_field['position_x']))) + 'px'
        elif properties_field['type'] == 'DateTimeField':
          # rendering DateTimeField, composed at least of three input
          # areas, and their order can be changed
          # getting the number of fields to render and their size unit
          field_nb = 3
          width_part = int((float(properties_field['size_x']) / 4))
          # defining global field rendering (for Date), ignoring for the moment
          # the whole part about the time
          # this following field refere to no existing field, it's use only
          # when editable property is unchecked (there is only one field
          # without _class_N but just _class, so, the 3 existing CSS selector
          # can't be applied, that the reason for this new one)
          field_dict[0] = {}
          field_dict[0]['width'] = \
              str(scaling_factor*float(width_part*(field_nb+1))) + 'px'
          field_dict[0]['margin-left'] = \
              str(scaling_factor *float(properties_field['position_x'])) + 'px'

          date_order = portal_preferences.getPreferredDateOrder()
          if  date_order is not None and date_order != '':
            preferred_date_order = date_order
          else:
            preferred_date_order = 'ymd'
          if preferred_date_order in \
                ['day/month/year', 'dmy', 'dmY', 'month/day/year', 'mdy', 'mdY']:
            # specified input order. must be dd/mm/yyyy or mm/dd/yyyy (year is
            # the last field).
            # processing first field
            field_dict[1] = {}
            field_dict[1]['width'] = str(scaling_factor*float(width_part)) + \
                'px'
            field_dict[1]['margin-left'] = \
                str(scaling_factor *float(properties_field['position_x'])) + 'px'
            # processing second field
            field_dict[2] = {}
            field_dict[2]['width'] = str(scaling_factor*float(width_part)) + \
                'px'
            field_dict[2]['margin-left'] = \
                str(scaling_factor *(float(properties_field['position_x']) + \
                width_part)) + 'px'
            # processing last field
            field_dict[3] = {}
            field_dict[3]['width'] = str(scaling_factor*float(width_part*2)) + \
                'px'
            field_dict[3]['margin-left'] = \
                str(scaling_factor *(float(properties_field['position_x']) + \
                width_part*2)) + 'px'
          else:
            # all other cases, including default one (year/month/day)
            width_part = int(int(properties_field['size_x']) / 4)
            # processing year field
            field_dict[1] = {}
            field_dict[1]['width'] = str(scaling_factor*float(width_part *2)) +\
                'px'
            field_dict[1]['margin-left'] = \
                str(scaling_factor *float(properties_field['position_x'])) + 'px'
            # processing second field (two digits only)
            field_dict[2] = {}
            field_dict[2]['width'] = str(scaling_factor*float(width_part)) + \
                'px'
            field_dict[2]['margin-left'] = \
              str(scaling_factor *(float(properties_field['position_x']) + \
              width_part*2)) + 'px'
            # processing day field
            field_dict[3] = {}
            field_dict[3]['width'] = str(scaling_factor*float(width_part)) + \
                'px'
            field_dict[3]['margin-left'] = \
              str(scaling_factor *(float(properties_field['position_x']) + \
              width_part*3)) + 'px'

        field_nb_range = field_nb + 1
        field_range = range(field_nb_range)
        for iterator in field_range:
          # iterator take the field_id according to the field_nb
          # ie (0..field_nb)
          #iterator = it + 1
          if iterator == 0:
            class_name = field_name + '_class'
          else:
            class_name = field_name + '_class_' + str(iterator)
          # managing standard class properties
          properties_css_dict['standard'][class_name] = {}
          for prop_id in properties_css_object_stand.keys():
            # saving global class properties into final dict
            properties_css_dict['standard'][class_name][prop_id] = \
                properties_css_object_stand[prop_id]
          for prop_id in field_dict[iterator].keys():
            # then adding special field properties (usually width and position_x)
            properties_css_dict['standard'][class_name][prop_id] = \
                field_dict[iterator][prop_id]
          # managing class error properties
          properties_css_dict['error'][class_name] = {}
          for prop_id in properties_css_object_error.keys():
            properties_css_dict['error'][class_name][prop_id] = \
                properties_css_object_error[prop_id]
          for prop_id in field_dict[iterator].keys():
            properties_css_dict['error'][class_name][prop_id] = \
                field_dict[iterator][prop_id]

  properties_css_page = {}
  properties_css_page['position'] = 'relative'
  properties_css_page['margin-top'] = "%spx" % str(space_between_pages)
  properties_css_dict['head']['page_end'] = properties_css_page
  return properties_css_dict

def generateCSSOutputContent(properties_css_dict):
  """
  return a string containing the whole content of the CSS output
  from properties_css_dict
  """
  form_css_content =  "/*-- special css form generated through ScribusUtils"\
      "module     --*/\n"
  form_css_content += "/*-- to have a graphic rendering with 'form_html' "\
      "page template --*/\n\n"
  form_css_content += "/* head : classes declared for general purpose */\n"
  # iterating classes in document's head
  for class_name in properties_css_dict['head'].keys():
    # getting class properties_dict
    class_properties = properties_css_dict['head'][class_name]
    # joining exerything
    output_string = "." + str(class_name) + " {" \
                    + "; ".join(["%s:%s" % (id, val) for id,
                      val in class_properties.items()]) \
                    + "}"
    # adding current line to css_content_object
    form_css_content += output_string + "\n"
  form_css_content += "\n/* standard field classes */ \n"
  # adding standard classes
  for class_name in properties_css_dict['standard'].keys():
    class_properties = properties_css_dict['standard'][class_name]
    output_string = "." + str(class_name) + " {" \
                    + "; ".join(["%s:%s" % (id, val) for id,
                      val in class_properties.items()]) \
                    + "}"
    form_css_content += output_string + "\n"
  form_css_content += "\n/* error field classes */\n"
  # adding error classes
  for class_name in properties_css_dict['error'].keys():
    class_properties = properties_css_dict['error'][class_name]
    output_string = "." + str(class_name) + "_error {" \
                    + "; ".join(["%s:%s" % (id, val) for id,
                    val in class_properties.items()]) \
                    + "}"
    form_css_content += output_string + "\n"
  form_css_content += "\n/* text_error field classes */ \n"
  # adding field error classes
  for class_name in properties_css_dict['err_d'].keys():
    class_properties = properties_css_dict['err_d'][class_name]
    output_string = "." + str(class_name) + "_error_display {" \
                    + "; ".join(["%s:%s" % (id, val) for id,
                    val in class_properties.items()]) \
                    + "}"
    form_css_content += output_string + "\n"
  # return final String
  return form_css_content


class PDFTypeInformation(ERP5TypeInformation):
  """
    EXPERIMENTAL - DO NOT USE THIS CLASS BESIDES R&D

    A Type Information class which (will) implement
    all PDF Editor related methods in a more generic
    way.
  """
  # CMF Type Definition
  meta_type = 'ERP5 PDF Type Information'
  portal_type = 'PDF Type'
  isPortalContent = 1
  isRADContent = 1

  property_sheets = ( PropertySheet.PDFType,
                      PropertySheet.Reference,
                      PropertySheet.Login,)

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.View, 'renderForm')
  def renderForm(self, context):
    """
    """
    form = self.getERP5Form()
    return form.__of__(context)()

  security.declareProtected(Permissions.View, 'renderPDFForm')
  def renderPDFForm(self, context):
    """
    """
    form = self.getPDFForm()
    return form.__of__(context)()

  security.declareProtected(Permissions.View, 'renderFormImage')
  def renderFormImage(self, REQUEST, RESPONSE, page):
    """
    """
    return self.getERP5FormImage(page).index_html(REQUEST, RESPONSE,
                                                  format='jpg')

  security.declareProtected(Permissions.View, 'renderFormCSS')
  def renderFormCSS(self):
    """
    """
    return self.getERP5FormCSS()

  def _getParsedScribusFile(self):
    """
      Returns a reusable data structure which can
      be used to generate ERP5 Form, ERP5 Form CSS,
      PDF Form, etc.
    """
    scribus_form = self.getDefaultScribusFormValue()
    if scribus_form is None:
      return

    def generateParsedScribus():
      import_scribus_file = StringIO.StringIO(scribus_form.getData())
      scribus_parser = ScribusParser(import_scribus_file)
      import_scribus_file.close()
      return scribus_parser.getERP5PropertyDict()

    generateParsedScribus = CachingMethod(generateParsedScribus,
                                        ('PDFTypeInformation_generateParsedScribus',
                                        md5(scribus_form.getData()).digest()),
                                        cache_factory='dms_cache_factory')
    return generateParsedScribus()

  def getERP5Form(self):
    """
      Returns an ERP5 Form instance (stored in RAM)
    """
    if self.getDefaultScribusFormValue() is None:
      return

    def generateERP5Form():
      form_name = "view"
      form = ERP5Form(form_name, self.getId())
      parsed_scribus = self._getParsedScribusFile()
      pages = range(len(parsed_scribus))
      #get the context for default values
      context = None
      context_parent = self.aq_parent
      if context_parent is not None:
        context = context_parent.aq_parent
      for page in pages:
        page_content =  parsed_scribus[page]
        group_id = page_id = "page_%s" % page
        if page != 0:
          group = form.add_group(group_id)
        for field_name, fields_values in page_content:
          field_id = field_name
          field_title = fields_values["title"]
          field_order = fields_values["order"]
          field_erp5_order = fields_values["nb"]
          field_type = fields_values["type"]
          field_required = fields_values["required"]
          field_editable = fields_values["editable"]
          field_rendering = fields_values["rendering"]
          field_size_x = fields_values["size_x"]
          field_size_y = fields_values["size_y"]
          field_position_x = fields_values["position_x"]
          field_position_y = fields_values["position_y"]
          old_group='left'
          # creating new field in form
          if field_type in ['ListField', 'MultiListField']:
            field = form.manage_addField(field_id,
                                field_title,
                                'ProxyField')
            field = form[field_name]
            field.values['form_id'] = 'Base_viewFieldLibrary'
            if field_type == 'ListField':
              field.values['field_id'] = 'my_list_field'
            else:
              field.values['field_id'] = 'my_multi_list_field'
            # ne pas déléguer les propriétés items et default
            field.delegated_list += ('items', 'default')
            field.manage_tales_xmlrpc({"items":
              "python: here.EGov_getCategoryChildItemListByFieldName('%s')"\
              % field_id})
            field.manage_tales_xmlrpc({"default":
              "python: here.getProperty('%s')" % field_id[3:]})
          elif field_type == 'DateTimeField':
            field = form.manage_addField(field_id,
                                field_title,
                                field_type)
            field = form[field_name]
            field.values['date_only'] = 1
            preferences = self.getPortalObject().portal_preferences
            date_order = preferences.getPreferredDateOrder()
            if  date_order is not None and date_order != '':
              field.values['input_order'] = date_order
          else:
            field = form.manage_addField(field_id,
                                field_title,
                                field_type)
          field = form[field_name]
          field.values['required'] = field_required
          field.values['editable'] = field_editable

          if page != 0:
            # move fields to destination group
            form.move_field_group(field_id,
                                  old_group,
                                  group_id)


      default_groups = ['right', 'center', 'bottom', 'hidden']
      old_group='left'
      group_id = 'page_0'
      form.rename_group(old_group, group_id)
      # remove all other groups:
      for existing_group in default_groups:
        form.remove_group(existing_group)
      # updating form settings
      # building dict containing (property, value)
      values = {}
      values['title'] = self.getId()
      values['row_length'] = 4
      values['name'] = form_name
      values['pt'] = "form_render_PDFeForm"
      values['action'] = "PDFDocument_edit"
      values['update_action'] = ""
      values['method'] = 'POST'
      values['enctype'] = 'multipart/form-data'
      values['encoding'] = "UTF-8"
      values['stored_encoding'] = 'UTF-8'
      values['unicode_mode'] = 0
      values['getBackgroundUrl'] = lambda page: \
        'portal_types/%s/renderFormImage?page=%s' % (self.getId(), page)
      values['getCSSUrl'] = lambda: 'portal_types/%s/renderFormCSS' % self.getId()
      # using the dict declared just above to set the attributes
      for key, value in values.items():
        setattr(form, key, value)
      return form
    #generateERP5Form = CachingMethod(generateERP5Form,
    #                                ('PDFTypeInformation_generateERP5Form',
    #                                md5(self.getDefaultScribusFormValue().getData()).digest()),
    #                                cache_factory='dms_cache_factory')
    return generateERP5Form().__of__(self)

  # XXX criticize Image Document
  #     (we are forced to use xlarge preference)
  def getWidth(self):
    portal_preferences = self.getPortalObject().portal_preferences
    return portal_preferences.getPreferredXlargeImageWidth()

  def getHeight(self):
    portal_preferences = self.getPortalObject().portal_preferences
    return portal_preferences.getPreferredXlargeImageHeight()


  def getERP5FormCSS(self):
    """
      Returns a CSS file containing all layout instructions
    """
    if self.getDefaultScribusFormValue() is None:
      return
    def generateERP5FormCSS():
      parsed_scribus = self._getParsedScribusFile()
      import_pdf_file = StringIO.StringIO(self.getDefaultPdfFormValue().getData())
      pdf_parser = PDFParser(import_pdf_file)
      import_scribus_file = StringIO.StringIO(self.getDefaultScribusFormValue().getData())
      scribus_parser = ScribusParser(import_scribus_file)
      page_gap = scribus_parser.getPageGap()
      scribus_width = scribus_parser.getPageWidth()
      scribus_height = scribus_parser.getPageHeight()
      space_between_pages = 20 # XXX - hardcoded
      image0 = self.getERP5FormImage(0)
      properties_css_dict=getPropertiesCSSDict(parsed_scribus,
                                              page_gap,
                                              image0.getWidth(),
                                              image0.getHeight(),
                                              scribus_width,
                                              scribus_height,
                                              space_between_pages,
                                              self.getPortalObject().portal_preferences)
      # declaring object that holds the CSS data
      css_file_name = "%s_css.css" % self.getId().replace(' ','')
      css_file_content = generateCSSOutputContent(properties_css_dict)
      css_file = DTMLDocument(css_file_content, __name__ = css_file_name)
      import_scribus_file.close()
      import_pdf_file.close()
      return css_file

    generateERP5FormCSS = CachingMethod(generateERP5FormCSS,
                                        ('PDFTypeInformation_generateERP5FormCSS',
                                        md5(self.getDefaultScribusFormValue().getData()).digest()),
                                        cache_factory='dms_cache_factory')
    self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/css')
    return generateERP5FormCSS()


  def getERP5FormImage(self, page):
    """
      Returns the background image for a given page
    """
    import_pdf_file = self.getDefaultPdfFormValue()
    #depend on preferences, best xlargeheight = 1131
    mime, image_data = import_pdf_file.convert(format = 'jpg',
                                                frame = page,
                                                resolution = self.getResolution(),
                                                quality = 600,
                                                display = 'xlarge')
    if image_data is None:
      return
    page_image = self.newContent(temp_object=True, portal_type='Image',
      id="page_%s" % page)
    page_image.setData(image_data)
    self.REQUEST.RESPONSE.setHeader('Content-Type', mime)
    return page_image

  def getPDFForm(self):
    """
      Returns an PDF Form instance (stored in RAM)
    """
    if self.getDefaultScribusFormValue() is None:
      return
    portal_type_name = self.getId().replace(' ','')
    pdf_form_name ='%s_view%sAsPdf' % (portal_type_name, portal_type_name)
    pdf_file = StringIO.StringIO(self.getDefaultPdfFormValue().getData())
    pdf_form = PDFForm(pdf_form_name, portal_type_name, pdf_file)
    pdf_form.manage_upload(pdf_file)
    import_scribus_file = StringIO.StringIO(self.getDefaultScribusFormValue().getData())
    scribus_parser = ScribusParser(import_scribus_file)
    erp5_properties = scribus_parser.getERP5PropertyDict()
    def_usePropertySheet = 0
    my_prefix = 'my_'
    prefix_len = len(my_prefix)
    pages = range(len(erp5_properties))
    for page in pages:
      page_content =  erp5_properties[page]
      for cell_name, field_dict in page_content:
      # current object is PDF Form
        if cell_name[:prefix_len] == my_prefix:
          cell_process_name_list = []
          suffix = cell_name[prefix_len:].split('_')[-1]
          # If properties field are filled in scribus, get Type form
          # global_properties. Else, guess Type by suffix id (eg: List, Date,...)
          list_field_type_list = ('ListField', 'MultiListField', 'LinesField',)
          date_field_type_list = ('DateTimeField',)
          suffix_mapping = {'List' : list_field_type_list,
                            'Date' : date_field_type_list}
          field_type = field_dict.get('erp_type', suffix_mapping.get(suffix, [''])[0])
          if def_usePropertySheet:
            # generating PropertySheet and Document, no need to use them to
            # get field data
            if field_type in list_field_type_list:
              TALES = "python: %s " % ', '.join(
              "here.get%s()" % convertToUpperCase(cell_name[prefix_len:]))
            elif field_type in date_field_type_list:
              attributes_dict = field_dict['attributes']
              # assign the property input_order
              input_order = attributes_dict['input_order']
              input_order = input_order.replace('y', 'Y')
              # make the Tales according to the cases
              date_pattern = '/'.join(['%%%s' % s for s in list(input_order)])
              if not(attributes_dict['date_only']):
                date_pattern += ' %H:%M'
              TALES = "python: here.get%s() is not None and here.get%s().strftime('%s') or ''"\
                % (convertToUpperCase(cell_name[prefix_len:]),
                  convertToUpperCase(cell_name[prefix_len:]),
                  date_pattern)
            else:
              TALES = "python: here.get%s()" %\
                                convertToUpperCase(cell_name[prefix_len:])
          else:
            if field_type in list_field_type_list:
              TALES = "python: %s" % ', '.join(
                    "here.getProperty('%s')" % cell_name[prefix_len:])
            elif field_type in date_field_type_list:
              attributes_dict = field_dict['attributes']
              # assign the property input_order
              input_order = attributes_dict['input_order']
              input_order = input_order.replace('y', 'Y')
              # make the Tales according to the cases
              date_pattern = '/'.join(['%%%s' % s for s in list(input_order)])
              if not(attributes_dict['date_only']):
                date_pattern += ' %H:%M'
              TALES = "python: here.getProperty('%s') is not None and here.getProperty('%s').strftime('%s') or ''"\
                    % (cell_name[prefix_len:],
                        cell_name[prefix_len:],
                        date_pattern)
            else:
              TALES = "python: here.getProperty('%s')" % cell_name[prefix_len:]
          pdf_form.setCellTALES(cell_name, TALES)
    import_scribus_file.close()
    pdf_file.close()
    self.REQUEST.RESPONSE.setHeader('Content-Type', 'application/pdf')
    return pdf_form


  def getCacheableActionList(self):
    portal_type_name = self.getId().replace(' ','')
    pdf_form_name ='%s_view%sAsPdf' % (portal_type_name, portal_type_name)
    action_list = ERP5TypeInformation.getCacheableActionList(self)
    if self.getPortalType() == "EGov Type":
      name = 'View'
    else:
      name = 'Document Procedure Definition'
    return list(action_list) + [
      CacheableAction(id='view',
                      name=name,
                      description='',
                      category='object_view',
                      priority=0.5,
                      icon=None,
                      action='string:${object_url}/PDFType_viewDefaultForm',
                      condition=None,
                      permission_list=['View']),
      CacheableAction(id=pdf_form_name,
                      name='PDF Form',
                      description='',
                      category='object_print',
                      priority=3.0,
                      icon=None,
                      action='string:${object_url}/PDFType_viewAsPdf',
                      condition=None,
                      permission_list=['View']),
    ]

  def getTypePropertySheetValueList(self):
    property_sheet_list = super(PDFTypeInformation,
                                self).getTypePropertySheetValueList()

    try:
      parsed_scribus_iterator = self._getParsedScribusFile().itervalues()
    except AttributeError:
      return property_sheet_list

    try:
      property_sheet = self.getPortalObject().portal_property_sheets.newContent(
        id=self.__name__.replace(' ', ''),
        portal_type='Property Sheet',
        temp_object=True)

    except AttributeError:
        return property_sheet_list

    for page_content in parsed_scribus_iterator:
      for field_name, fields_values in page_content:
        property_sheet.newContent(reference=field_name[3:],
                                  elementary_type=fields_values["data_type"],
                                  portal_type='Standard Property',
                                  temp_object=True)

    property_sheet_list.append(property_sheet)
    return property_sheet_list
