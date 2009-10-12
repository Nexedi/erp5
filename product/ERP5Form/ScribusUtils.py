##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#               Guy Oswald OBAMA <guy@nexedi.com>
#               thomas <thomas@nexedi.com>
#               Mame C.Sall <mame@nexedi.com>
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

# This code is under refactoring. This code will change in near future
# with a lot of cleanups. This is stored only for a temporary purpose.
# Do not rely on the real implementation. It is assumed that the code is
# improved and modified significantly.
# UPDATE => the code is almost refactored and supports

from Products.PythonScripts.Utility import allow_class
from ZPublisher.HTTPRequest import FileUpload
from xml.dom.ext.reader import PyExpat
from xml.dom import Node, minidom
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass, get_request
from zipfile import ZipFile, ZIP_DEFLATED
from StringIO import StringIO
from zLOG import LOG, TRACE, WARNING, ERROR, INFO
import imghdr
import random
import getopt, sys, os, re
from urllib import quote

from Products.ERP5.ERP5Site import ERP5Site
from Products.Formulator.TALESField import TALESMethod
from Products.Formulator.MethodField import Method
from Products.ERP5Type.Utils import convertToUpperCase

# defining global variables
# ANFLAG tag
# these values can be found in the Scribus document format
# (www.scribus.org.uk)
def_noScroll = '8388608'
def_noSpellCheck = '4194304'
def_editable = '262144'
def_password = '8192'
def_multiLine = '4096'
def_noExport = '4'
def_required = '2'
def_readOnly = '1'
# SCRIPT CONFIGURATION
# define if the script uses personal properties or create a
# PropertySheet and a Document model to save data.
# used in 'setPropertySheetAndDocument', 'setObjectPortalType'
# and 'setPDFForm'
def_usePropertySheet = 0


class ManageModule:
  """
  Manage the module that will contain the form
  """
  security = ClassSecurityInfo()

  security.declarePublic('setObjectNames')
  def setObjectNames(self, object_portal_type_id, object_title):
    """
    initialize object names view_pdf, view_list, etc. to be able
    to create correctly all objects in the module.
    return a dict of names.
    """
    temp_portal_type = object_portal_type_id.replace(' ','')
    object_names = {}
    real_object_names={}
    # declaring object that generate pdf output
    object_names['view_pdf'] = temp_portal_type + '_view' +\
                    temp_portal_type + 'AsPdf'
    # declaring form to list the objects of a module
    # TODO: use module portal type, not "object title + Module"
    object_names['view_list'] = object_title.replace(' ','') +\
                    'Module_view' + temp_portal_type + 'List'
    # declaring main object form
    object_names['view_id'] = temp_portal_type + '_view'
    # declaring object that holds the CSS data
    object_names['css'] = temp_portal_type + '_css.css'
    # declaring object name containing the background pictures
    object_names['page'] = temp_portal_type + '_background_'
    # return object declaration
    return object_names


  security.declarePublic('setSkinFolder')
  def setSkinFolder(self,
                    portal,
                    portal_skins_folder):
    """
    create and manage skin folder according to the skin folder
    name specified by the user (as portal_skin_folder).
    returns skin_folder, recovered from portal.portal_skins
    """
    portal_skins_folder_name = portal_skins_folder
    portal_skins = portal.portal_skins
    if not portal_skins_folder_name in portal.portal_skins.objectIds():
      # create new folder if does not exist yet
      portal_skins.manage_addFolder(portal_skins_folder_name)
    skin_folder = portal.portal_skins[portal_skins_folder_name]
    for skin_name, selection in portal_skins.getSkinPaths():
      selection = selection.split (',')
      if portal_skins_folder_name not in selection:
        new_selection = [portal_skins_folder_name,]
        new_selection.extend(selection)
        portal_skins.manage_skinLayers(skinpath = tuple(new_selection),
                                       skinname = skin_name,
                                       add_skin = 1)
    return skin_folder


  security.declarePublic('setModuleForm')
  def setModuleForm(self,
                    object_title,
                    skin_folder,
                    #portal,
                    #portal_skins_folder,
                    form_view_list,
                    module_title,
                    module_id,
                    def_lineNumberInList
                    ):
    """
    Manage ERP5 Form to handle and view the Module. then process
    the list inside this form. This procedure does not need to
    parse the scribus file as the ModuleForm is always present
    and generated the same way
    returns nothing
    """
    # the form is already existing and has been created through
    # setERP5Form. getting form object to update properties
    form_view_list_object = skin_folder[form_view_list]
    form_list_id = form_view_list_object.id
    form_list = form_view_list_object.restrictedTraverse(form_list_id)
    # defining groups for objects listing
    form_view_list_object.add_group('bottom')
    # defining module title
    title_module = '' # XXX use module title provided by user
    for word in module_title.split():
      title_module += str(word.capitalize() + ' ')
    # add listbox field to list the created objects
    id = 'listbox'
    title = title_module
    field_type = 'ListBox'
    form_view_list_object.manage_addField(id, title, field_type)
    form_view_list_object.move_field_group(['listbox'],
             form_view_list_object.group_list[0], 'bottom')

    # manage ListBox settings
    values_settings = {}
    values_settings['pt'] = "form_list"
    values_settings['action'] = "Base_doSelect"
    # set the form settings
    for key, value in values_settings.items():
      setattr(form_view_list_object, key, value)
    # manage edit property of ListBox
    listbox = getattr(form_view_list_object, id)
    listbox.manage_edit_xmlrpc(
        dict(lines=def_lineNumberInList,
             columns=[('id', 'ID'),
                      ('title', 'Title'),
                      ('description', 'Description'),
                      ('translated_simulation_state', 'State')],
             list_action='list',
             search=1,
             select=1,
             list_method=Method('searchFolder'),
             count_method=Method('countFolder'),
             selection_name='%s_selection' % module_id))


  security.declarePublic('setObjectForm')
  def setObjectForm(self,
                    skin_folder,
                    object_names,
                    option_html,
                    global_properties,
                    object_portal_type
                    ):
    """
    create and manage erp5 form to handle object, and update its
    properties (groups, values, etc.)
    return list of groups in form (used afterwards when creating
    fields).
    """
    # getting form object
    form_view_id_object = skin_folder[object_names['view_id']]
    form_id = form_view_id_object.id
    form = form_view_id_object.restrictedTraverse(form_id)
    #get the scaling factor
    # managing form groups
    default_groups = []
    if option_html !=1:
      # using default ERP5 positioning convention
      # based on 'left'/'right'/etc.
      default_groups = ['left', 'right', 'center', 'bottom', 'hidden']
    else:
      # using special page positioning convention for
      # pdf-like rendering
      for page_iterator in range(global_properties['page']):
        page_number = 'page_%s' % str(page_iterator)
        default_groups.append(page_number)
        
    # default_groups list completed, need to update the form_groups
    # rename the first group because it can't be removed
    if len(form.group_list):
      form.rename_group(form.group_list[0], default_groups[0])

    # add other groups
    for group in default_groups:
      if group not in form.group_list:
        form.add_group(group)
    form_view_id_object.rename_group('Default', default_groups[0])

    # remove all other groups:
    for existing_group in list(form.get_groups(include_empty=1)):
      if existing_group not in default_groups:
        form.remove_group(existing_group)

    # adding all other items
    for group in default_groups:
      form_view_id_object.add_group(group)
    # updating form settings
    # building dict containing (property, value)
    values = {}
    values['title'] = str(object_portal_type)
    values['row_length'] = 4
    values['name'] = object_names['view_id']
    if option_html == 1:
      # this is the name of the new form, compatible either with html_style
      # and xhtml_style.
      values['pt'] = "form_render_PDFeForm"
    else:
      values['pt'] = "form_view"
    values['action'] = "Base_edit"
    values['update_action'] = ""
    values['method'] = 'POST'
    values['enctype'] = 'multipart/form-data'
    values['encoding'] = "UTF-8"
    values['stored_encoding'] = 'UTF-8'
    values['unicode_mode'] = 0
    # using the dict declared just above to set the attributes
    for key, value in values.items():
      setattr(form, key, value)
    return (default_groups)

  security.declarePublic('setFieldsInObjectForm')
  def setFieldsInObjectForm(self,
                            skin_folder,
                            object_names,
                            default_groups,
                            global_properties,
                            option_html
                            ):
    """
    create fields in form according to the page_objects
    recovered from the scribus document file. fields are
    then moved to their corresponding group, and are given
    their properties
    """
    form_view_id_object = skin_folder[object_names['view_id']]
    # iterating field a first time to get creation order
    # based on the 'nb' value
    field_nb_dict = {}
    # this dict will handle all the information about the field_names and
    # their creation order (field_nb).

    if option_html :
      # render is PDF-like, need to take care of the page holding the field
      for field_id in global_properties['object'].keys():
        field_nb = int(global_properties['object'][field_id]['nb'])
        #field_order =  global_properties['object'][field_id]['order']
        field_order = \
         int(global_properties['object'][field_id]['order'].split('page_')[1])
        # creating sub dict if does not exist yet
        if field_order not in field_nb_dict:
          field_nb_dict[field_order] = {}
        field_nb_dict[field_order][field_nb] = field_id
      # now field_nb_dict holds all the information about the
      # fields and their creation order: just need to create
      # them.

      for field_order_id in field_nb_dict.keys():
        # iterating pages
        for field_nb in range(len(field_nb_dict[field_order_id].keys())):
          field_id = field_nb_dict[field_order_id][field_nb + 1]
          # recovering field information
          field_values = global_properties['object'][field_id]
          field_type = field_values['erp_type']
          field_title = field_values['title']
          field_order = field_values['order']
          #field_tales = field_values['tales']
          # creating new field in form
          form_view_id_object.manage_addField(field_id,
                                              field_title,
                                              field_type)
          # move fields to destination group
          form_view_id_object.move_field_group(field_id,
                                               default_groups[0],
                                               field_order)
          # recover field
          access_field = getattr(form_view_id_object, field_id)
          if field_type == 'CheckBoxField':
            test_name = field_id[3:]
            #tales = {field_id : {'default' : 'python: here.getProperty(' +\
            #    test_name + ', None)'}}

            forms = [object_names['view_id']]
            form = form_view_id_object.restrictedTraverse(forms[0])
            #for k, v in tales.items() :
            #  if hasattr(form, k) :
            #    form[k].manage_tales_xmlrpc(v)
          #if field_type == 'CheckBoxField':
          #  print "    dir(%s) > %s" % (field_id,dir(access_field))
          #  print "---manage_tales > %s \n\n" % dir(access_field.manage_tales)
          #  print "---manage_talesForm > %s \n\n" % \
          #         dir(access_field.manage_talesForm)
          #  print "---manage_talesForm__roles__ > %s\n\n " % \
          #         dir(access_field.manage_talesForm__roles__)
          #  print "---manage_tales__roles__ > %s" % \
          #         dir(access_field.manage_tales__roles__)
          #  print "--- 5 > %s" % dir(access_field.manage_tales_xmlrpc)
          #  print "--- 6 > %s" % \
          #         dir(access_field.manage_tales_xmlrpc__roles__)

    else:
      # rendering as basic ERP5 form : processing all
      # fields without taking care of their 'order'.
      for field_id in global_properties['object'].keys():
        field_nb = int(global_properties['object'][field_id]['nb'])
        if field_nb in field_nb_dict.keys():
          # field_nb is already used by another field. this can appen
          # when there are several pages in the document. In such case
          # the script find automatically the closest available value.
          LOG('ManageModule', ERROR, 
              'can not add %s to dict : %s already used by %s ' % \
              (field_id, field_nb, field_nb_dict[field_nb]))
          field_nb = field_nb + 1
          while field_nb in field_nb_dict.keys():
            # trying next value
            field_nb = field_nb + 1
        LOG('ManageModule', INFO, '  add %s to %s' % (field_id, field_nb))
        # value is available, no problem to link field_id to this field_nb
        field_nb_dict[field_nb] = field_id

      for field_nb in range(len(field_nb_dict.keys())):
        field_nb = field_nb +1
        field_id = field_nb_dict[field_nb]
        # recovering field information
        field_values = global_properties['object'][field_id]
        field_type = field_values['erp_type']
        field_title = field_values['title']
        field_order = field_values['order']
        # create field
        form_view_id_object.manage_addField(field_id,
                                            field_title,
                                            field_type)
        # move field to relative group
        form_view_id_object.move_field_group(field_id,
                                             default_groups[0],
                                             field_order)

    # field creation is complete
    form_id = form_view_id_object.id
    form = form_view_id_object.restrictedTraverse(form_id)
    # updating field properties
    # iterating fields
    for field_id in global_properties['object'].keys():
      field_attributes = getattr(form, field_id)
      #print "   %s => %s" % (field_id,field_attributes.values.keys())
      for attr_id, attr_val in \
         global_properties['object'][field_id]['attributes'].items():
        field_attributes.values[attr_id] = attr_val



  security.declarePublic('setModulePortalType')
  def setModulePortalType(self, 
                          portal_types,
                          object_portal_type_id,
                          module_portal_type,
                          object_names):
    """
    set portal_type for the module containing objects.
    returns nothing
    """
    portal_types.manage_addTypeInformation('ERP5 Type Information'
                , typeinfo_name = 'ERP5Type: ERP5 Folder'
                , id = module_portal_type)
    # getting portal_type access to be able to modify attributes
    module_portal_type_value = portal_types[module_portal_type]
    # set alowed content type
    module_portal_type_value.allowed_content_types = (object_portal_type_id,)
    module_portal_type_value.filter_content_types = 1
    # adding usefull actions (in our case the view action)
    module_portal_type_value.newContent(portal_type='Action Information',
      reference="view",
      title="View",
      action="string:${object_url}/%s" % object_names['view_list'],
      action_type="object_view")



  security.declarePublic('setObjectPortalType')
  def setObjectPortalType(self,
                          portal_types,
                          object_portal_type_id,
                          object_portal_type,
                          object_names):
    name = ''
    if def_usePropertySheet:
      # generating 'typeinfo_name' property for the new portal type.
      # if class exists, then using it, otherwize using default ERP5
      # Document type.
      name = 'ERP5Type: ERP5 ' + object_portal_type # use with PropertySheet
    else:
      name = 'ERP5Type: ERP5 Document'  # use with local properties
    portal_types.manage_addTypeInformation( 'ERP5 Type Information',
                                            typeinfo_name = name,
                                            id = object_portal_type_id)
    object_portal_type_value = portal_types[object_portal_type_id]

    # adding usefull actions (in our case the view action)
    object_portal_type_value.newContent(portal_type='Action Information',
      reference="view",
      title="View",
      action="string:${object_url}/%s" % object_names['view_id'],
      action_type="object_view")
    object_portal_type_value.newContent(portal_type='Action Information',
      reference="print",
      title="Print",
      action="string:${object_url}/%s" % object_names['view_pdf'],
      action_type="object_print",
      float_index=2.0)


  security.declarePublic('registerModule')
  def registerModule(self,
                     portal,
                     module_id,
                     module_portal_type,
                     object_portal_type,
                     module_title):
    """
    register Module inside ERP5 instance
    """
    portal.newContent( id          = str(module_id),
                       portal_type = str(module_portal_type),
                       title       = module_title)

   
class ManageFiles:
  """
  Manages PDF file, by importing the PDF document and then getting
  the TALES expressions
  """
  security = ClassSecurityInfo()



  security.declarePublic('setERP5Form')
  def setERP5Form(self,
                  factory,
                  form_name,
                  form_title):
    """
    create an ERP5 Form by using the factory
    """
    factory.addERP5Form(form_name,
                        form_title)



  security.declarePublic('setCSSFile')
  def setCSSFile(self,
                 factory,
                 form_css_id,
                 form_css_content,
                 ):
    """
    create an ERP5 DTML Document in the folder related
    to factory and save the content of the CSS string
    """
    factory.addDTMLDocument(form_css_id, "css", form_css_content)


  security.declarePublic('importFile')
  def setPDFForm(self,
                 factory,
                 skin_folder,
                 object_names,
                 object_title,
                 pdf_file,
                 global_properties
                 ):
    """
    imports PDF file as a PDFForm in ERP5 and updates its TALES
    expressions
    """
    my_prefix = 'my_'
    pdf_file.seek(0)
    factory.addPDFForm(object_names['view_pdf'], object_title, pdf_file)
    # iterating objects in skin_folder
    for c in skin_folder.objectValues():
      if c.getId() == object_names['view_pdf']:
        # current object is PDF Form
        cell_name_list = c.getCellNames()
        for cell_name in global_properties['object'].keys():
          if cell_name[:len(my_prefix)] == my_prefix:
            cell_process_name_list = []
            suffix = cell_name[len(my_prefix):].split('_')[-1]
            # If properties field are filled in scribus, get Type form
            # global_properties. Else, guess Type by suffix id (eg: List, Date,...)
            list_field_type_list = ('ListField', 'MultiListField', 'LinesField',)
            date_field_type_list = ('DateTimeField',)
            suffix_mapping = {'List' : list_field_type_list,
                              'Date' : date_field_type_list}
            field_dict = global_properties['object'][cell_name]
            field_type = field_dict.get('erp_type', suffix_mapping.get(suffix, [''])[0])
            if def_usePropertySheet:
              # generating PropertySheet and Document, no need to use them to
              # get field data
              if field_type in list_field_type_list:
                TALES = "python: %s " % ', '.join(
               "here.get%s()" % convertToUpperCase(cell_name[len(my_prefix):]))
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
                 % (convertToUpperCase(cell_name[len(my_prefix):]),
                    convertToUpperCase(cell_name[len(my_prefix):]),
                    date_pattern)
              else:
                TALES = "python: here.get%s()" %\
                                 convertToUpperCase(cell_name[len(my_prefix):])

            else:
              if field_type in list_field_type_list:
                TALES = "python: %s" % ', '.join(
                      "here.getProperty('%s')" % cell_name[len(my_prefix):])
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
                      % (cell_name[len(my_prefix):],
                         cell_name[len(my_prefix):],
                         date_pattern)
              else:
                TALES = "python: here.getProperty('%s')" % cell_name[len(my_prefix):]
            LOG('ManageFiles', INFO, '   %s > %s ' % (cell_name, TALES))
            c.setCellTALES(cell_name, TALES)

  def getPDFFile(self, file_descriptor):
    """ Get file content """
    return file_descriptor.open()

  security.declarePublic('setBackgroundPictures')
  def setBackgroundPictures(self,
                            pdf_file,
                            object_names,
                            skin_folder,
                            desired_width,
                            desired_height,
                            resolution,
                            background_format
                            ):
    """
    extract background pictures from pdf file and convert them
    in the right format (JPEG) and save them in the corresponding
    folder (skin_folder).
    to work, this procedure needs convert (from ImageMagick)
    installed on the server otherwise nothing is created.
    Temp files wich are created are deleted once the job is done.
    At the end, return the properties (size_x, size_y) the background
    images have.
    """
    import commands
    from tempfile import NamedTemporaryFile
    # opening new file on HDD to save PDF content
    temp_pdf = NamedTemporaryFile()

    # get an unused file name on HDD to save created background image content
    temp_image = NamedTemporaryFile()
    temp_image_name = temp_image.name
    temp_image.close()

    # going to the begining of the input file
    pdf_file.seek(0)
    # saving content
    temp_pdf.write(pdf_file.read())
    temp_pdf.seek(0)
     
    def makeImageList():
      background_image_list = []
      # convert add a '-N' string a the end of the file name if there is more
      # than one page in the pdf file (where N is the number of the page,
      # begining at 0)
      if os.path.exists(temp_image_name):
        # thats mean there's only one page in the pdf file
        background_image_list.append(temp_image_name)
      else:
        # in the case of multi-pages pdf file, we must find all files
        image_number = 0
        while os.path.exists(temp_image_name + '-%s' % image_number):
          background_image_list.append(temp_image_name + '-%s' % image_number)
          image_number += 1
      return background_image_list

    try:
      result = commands.getstatusoutput('convert -verbose -density %s -resize %sx%s '\
          '%s %s' % (resolution, desired_width, desired_height, temp_pdf.name,
          background_format + ':' + temp_image_name))

      # check that the command has been done succeful
      if result[0] != 0:
        LOG('ScribusUtils.setBackgroundPictures :', ERROR, 'convert command'\
            'failed with the following error message : \n%s' % result[1])

        # delete all images created in this method before raise an error
        background_image_list = makeImageList()
        for background_image in background_image_list:
          if os.path.exists(background_image):
            os.remove(background_image)

        raise ValueError, 'Error: convert command failed with the following'\
                          'error message : \n%s' % result[1]
    finally:
      temp_pdf.close()
    
    background_image_list = makeImageList()
    if not len(background_image_list):
      LOG('ScribusUtils.setBackgroundPictures :', ERROR, 'no background '\
          'image found')
      raise ValueError, 'Error: ScribusUtils.setBackgroundPictures : '\
                        'no background'

    # get the real size of the first image
    # this could be usefull if the user only defined one dimention :
    # convert command has calculate the other using proportionnality
    rawstr = r'''
        PDF\s        # The line begin with PDF 
        (\d+)x(\d+)  # old file size
        =>           # Separator between old and new size
        (\d+)x(\d+)  # The matching pattern : width and height'''
    compile_obj = re.compile(rawstr, re.MULTILINE | re.VERBOSE)
    match_obj_list = re.findall(compile_obj, result[1])
    
    # old size is not use now, and depends of the density convert parameter
    #old_size_x = match_obj_list[0][0]
    #old_size_y = match_obj_list[0][1]

    real_size_x = match_obj_list[0][2]
    real_size_y = match_obj_list[0][3]

    # add images in erp5 :
    image_number = 0
    addImageMethod = skin_folder.manage_addProduct['OFSP'].manage_addImage
    for background_image in background_image_list:
      temp_background_file = open(background_image, 'r')
      form_page_id = object_names['page'] + str(image_number)
      addImageMethod(form_page_id, temp_background_file, "background image")
      image_number += 1

    # delete all images created in this method before raise an error
    background_image_list = makeImageList()
    for background_image in background_image_list:
      # remove the file from the system
      if os.path.exists(background_image):
        os.remove(background_image)

    size_x = int(real_size_x)
    size_y = int(real_size_y)
    LOG('ScribusUtils.setBackgroundPictures :', INFO, 
        'return size : x=%s, y=%s' % (size_x, size_y))
   
    return (size_x, size_y)

  security.declarePublic('getPageAttributes')
  def getPageAttributes (self,
                         global_properties,
                         pdf_file
                        ):
    '''return the size of the original pdf file (in pts)
    This is usefull to calculate proportionnality between original size and
    desired size. That permit to place correctly the fields on the page'''
    import commands
    from tempfile import NamedTemporaryFile
    # opening new file on HDD to save PDF content
    ScribusUtilsOriginalTempPDF= NamedTemporaryFile(mode= "w+b")
    ScribusUtilsOriginaltempsPDFName = ScribusUtilsOriginalTempPDF.name

    # going to the begining of the input file

    # saving content
    temp_pdf = open(ScribusUtilsOriginaltempsPDFName,'w')
    # going to the begining of the input file
    pdf_file.seek(0)
    # saving content
    temp_pdf.write(pdf_file.read())
    temp_pdf.close()    

    
    command_output = commands.getstatusoutput('pdfinfo %s' % \
        ScribusUtilsOriginaltempsPDFName)

    if command_output[0] != 0:
        LOG('ScribusUtils.getPageAttributes :', ERROR, 'pdfinfo command'\
            'failed with the following error message : \n%s' % command_output[1])
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
    width = int(round(float(width)))
    height = int(round(float(height)))

    LOG('width_groups, height_groups', 0, '%s, %s' % (width, height))
    return (width, height)


  security.declarePublic('setPropertySheetAndDocument')
  def setPropertySheetAndDocument(self,
                                  global_properties,
                                  object_portal_type,
                                  generator,
                                  skin_folder,
                                  object_names):
    """
    recover personal properties from dict global_properties
    and save them in a propertysheet
    then create the Document related to the object.
    PropertySheetRegistry and DocumentRegistry have to be
    reinitialized after this procedure has been called.
    """
    if def_usePropertySheet:
      LOG('ManageFiles', INFO, ' object_names = %s' % object_names['view_id'])
      #property_form = getattr(skin_folder,object_names['view_id'])
      # defining file name for Property Sheet
      name_file =''
      for word in object_portal_type.split():
        name_file += word.capitalize()
      # building list containing properties
      personal_properties_list = []
      for field_id in global_properties['object'].keys():
        if field_id.startswith('my_') and not (
           field_id.startswith('my_source') or
           field_id.startswith('my_destination') or
           field_id in ('my_start_date', 'my_stop_date')):
          field_type = global_properties['object'][field_id]['data_type']
          field_default = global_properties['object'][field_id]['default']
          personal_properties = { 'id' : field_id[3:],
                                  'description' : '',
                                  'type' : field_type,
                                  'mode' : 'w'}
          ## FOLLOWING QUOTED LINES CAN BE DELETED IF NOT USES
          ## just left in case : can be usefull to create a smart
          ## script that would be able to automatically create the
          ## local properties and associate them the good type (int,
          ## string, float, date, etc.)
          #print "   (field_id,field_default_value,field_type) = \
          #   (%s,%s,%s) " % (field_id[3:], field_default, field_type)
          #property_form.manage_addProperty(field_id[3:],
          #                                 field_default,
          #                                 field_type)
          personal_properties_list.append(personal_properties)
      # the following lines create the PropertySheet and the Document for the
      # new object. Must be uncoted when such files are needed, in such case
      # you must also specify Document type to comply with class declared in 
      # the Document. For that see 'setObjectPortalType' method 
      ## generate PropertySheet
      generator.generateLocalPropertySheet(name_file, personal_properties_list)
      ## generate Document
      generator.generateLocalDocument(name_file, object_portal_type)


class ManageCSS:
  """
  Manages all CSS information to generate the css file used in the
  PDF-like rendering
  """
  security = ClassSecurityInfo()

  security.declarePublic('setInit')
  def setInit(self):
    """
    initialize various containers (dicts) used to store attributes
    in a main dict.
    returns global dict containing all the sub-dicts
    """
    # declaring dicts used to generate CSS file
    # css_dict_head contains all the 'global' class, reffering to PAGE
    properties_css_dict_head = {}
    # css_dict_standard contains all the fields classes, when no error occurs
    properties_css_dict_standard = {}
    # css_dict_error contains the same thing, but in case error occurs.
    # there background is different so that users can see where the problem
    # is on the graphic view
    properties_css_dict_error = {}
    # css_dict_err_d contains coordinates and color to display text-error
    properties_css_dict_err_d = {}
    # declaring main container for all sub_dicts
    properties_css_dict = {}
    properties_css_dict['head'] = properties_css_dict_head
    properties_css_dict['standard'] = properties_css_dict_standard
    properties_css_dict['error'] = properties_css_dict_error
    properties_css_dict['err_d'] = properties_css_dict_err_d
    # return dict
    return properties_css_dict

  security.declarePublic('setPageProperties')
  def setPageProperties(self
          ,properties_css_dict
          ,page_iterator
          ,page_id
          ,new_width
          ,new_height
          ,old_width
          ,old_height):
    """
    recover all CSS data relative to the current page and save these
    information in the output dict
    """
    # Processing current page for CSS data
    # getting properties
    properties_css_page = {}
    properties_page = {}
    properties_css_page['position'] = 'relative'
    # creating image class for background
    properties_css_background = {}
    # making background id
    background_id =  page_id + '_background'
    #getting properties
    properties_css_background['position'] = 'absolute'
    #creating corresponding page group to form
    if page_iterator == 0:
      # margin-top = 0 (first page)
      properties_css_page['margin-top'] = "0px"
      #properties_css_background['margin-top'] = \
      #   str((y_pos -10))+ 'px'
      #properties_css_background['margin-left']= \
      #   str((x_pos- 5))+   'px' 
    else:
      properties_css_page['margin-top'] = "%spx" % (40)

    # set width and height on page block
    properties_css_page['width'] = str (new_width) + 'px'
    properties_css_page['height'] = str (new_height) + 'px'

    properties_page['actual_width'] = old_width
    properties_page['actual_height'] = old_height 
    properties_css_background['height'] = str(new_height) + 'px'
    properties_css_background['width'] = str (new_width) + 'px'
    # adding properties dict to global dicts
    properties_css_dict['head'][page_id] = properties_css_page
    properties_css_dict['head'][background_id] = properties_css_background
    # return updated dict
    return (properties_css_dict, properties_page)





  security.declarePublic('setFieldProperties')
  def setFieldProperties( self
                        , properties_css_dict
                        , field
                        , page_width
                        , page_height
                        , page_iterator
                        , page_gap
                        , keep_page
                        , properties_page
                        , space_between_pages):
    """
    recover all CSS data relative to the current page_object (field)
    and save these informations in the output dict
    """
    (field_name, properties_field) = field
    LOG('ManageCSS', INFO, 
        '   => %s : %s' % (field_name, properties_field['rendering']))

    # updating field properties if necessary
    if keep_page == 1:
      # document format is 1.3.* and define object position from the top-left
      # corner of the first page, whereas the field position is expected to
      # be found from the current's page top left corner.
      # that's why Y position must be updated

      scaling_factor1 = float(page_width)/properties_page['actual_width']
      scaling_factor2 = float(page_height)/properties_page['actual_height']

      properties_field['position_y'] = \
         str(float(properties_field['position_y']) - \
         (properties_page['actual_height'] + page_gap)* page_iterator)

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
        str(scaling_factor2 * float(properties_field['size_y'])) + 'px'
    properties_css_object_error['height'] = \
        str(scaling_factor2 * float(properties_field['size_y'])) + 'px'
    # defining font-size from height - 2 (this value seems to have a good
    # rendering on Mozilla and Konqueror)
    # do not match for TextArea (as it is a multiline object)
    if properties_field['type'] != 'TextAreaField':
      if float(properties_field['size_y']) > 8.0:
        properties_css_object_stand['font-size'] = \
          str((scaling_factor2 *float(properties_field['size_y']))-5.5 ) + 'px'
        properties_css_object_error['font-size'] = \
          str((scaling_factor2 *float(properties_field['size_y']))-5.5) + 'px'
      else:
        properties_css_object_stand['font-size'] = \
          str((scaling_factor2 *float(properties_field['size_y']))-3.5 ) + 'px'
        properties_css_object_error['font-size'] = \
          str((scaling_factor2 *float(properties_field['size_y']))-3.5) + 'px'
    else:
      properties_css_object_stand['font-size'] = \
        str(12) + 'px'
      properties_css_object_error['font-size'] = \
        str(12) + 'px'
    properties_css_object_err_d['margin-left'] = str(page_width +
        space_between_pages ) + 'px'
    properties_css_object_err_d['white-space'] = 'nowrap'
    properties_css_object_stand['margin-top'] = \
      str((scaling_factor2 *float(properties_field['position_y']))) + 'px'
    properties_css_object_error['margin-top'] = \
      str((scaling_factor2 *float(properties_field['position_y']))) + 'px'
    properties_css_object_err_d['margin-top'] = \
      str((scaling_factor2 *float(properties_field['position_y']))) + 'px'
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
        str(scaling_factor1 * float(properties_field['size_x'])) + 'px'
      properties_css_object_error['width'] = \
        str(scaling_factor1 * float(properties_field['size_x'])) + 'px'
      properties_css_object_stand['margin-left'] = \
        str((scaling_factor1 * float(properties_field['position_x']))) + 'px'
      properties_css_object_error['margin-left'] = \
        str((scaling_factor1 * float(properties_field['position_x']))) + 'px'
      # in case of checkboxfield, '_class_2' is used because field is rendered
      # as two fields, the first one hidden. (supports xhtml_style)
      # UPDATE : modified because need to keep compatibility with html_style
      #if properties_field['type'] == 'CheckBoxField':
      #  field_id = field_name + '_class_2'
      #else:
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
           str(scaling_factor1*(float(properties_field['size_x']) / 2)) + 'px'
        field_dict[1]['margin-left'] = \
           str(scaling_factor1*float(properties_field['position_x'])) + 'px'

        # processing secondary input picture
        field_dict[2] = {}
        field_dict[2]['width'] = \
            str(scaling_factor1*(float(properties_field['size_x']) /2)) + 'px'
        field_dict[2]['margin-left'] = \
              str(scaling_factor1*(float(properties_field['size_x']) /2  +\
              float(properties_field['position_x']))) + 'px'
      elif properties_field['type'] == 'DateTimeField':
        # rendering DateTimeField, composed at least of three input
        # areas, and their order can be changed
        LOG('ManageCSS', INFO, '  Type DateTimeField')

        # getting the number of fields to render and their size unit
        if properties_field['date_only'] == '0':
          LOG('ManageCSS', INFO, '   Option : Not Date Only')
          field_nb = 5
          # defining counting unit for fields
          # total = 6.1 units:
          # 2 > year
          # 1 > month
          # 1 > day
          # 0.1 > space between date and time
          # 1 > hour
          # 1 > minutes
          width_part = int(float(properties_field['size_x']) / 6.1)
        else: 
          LOG('ManageCSS', INFO, '   Option : Date Only')
          field_nb = 3
          # same as before but without hours and minutes
          width_part = int((float(properties_field['size_x']) / 4))


        LOG('ManageCSS', INFO, 
            '  input_order=%s' % properties_field['input_order'])
        # defining global field rendering (for Date), ignoring for the moment
        # the whole part about the time

        # this following field refere to no existing field, it's use only 
        # when editable property is unchecked (there is only one field 
        # without _class_N but just _class, so, the 3 existing CSS selector 
        # can't be applied, that the reason for this new one)
        field_dict[0] = {}
        field_dict[0]['width'] = \
            str(scaling_factor1*float(width_part*(field_nb+1))) + 'px'
        field_dict[0]['margin-left'] = \
           str(scaling_factor1 *float(properties_field['position_x'])) + 'px'

        if properties_field['input_order'] in \
             ['day/month/year', 'dmy', 'dmY', 'month/day/year', 'mdy', 'mdY']:

          # specified input order. must be dd/mm/yyyy or mm/dd/yyyy (year is
          # the last field).
          # processing first field
          field_dict[1] = {}
          field_dict[1]['width'] = str(scaling_factor1*float(width_part)) + \
              'px'
          field_dict[1]['margin-left'] = \
             str(scaling_factor1 *float(properties_field['position_x'])) + 'px'

          # processing second field
          field_dict[2] = {}
          field_dict[2]['width'] = str(scaling_factor1*float(width_part)) + \
              'px'
          field_dict[2]['margin-left'] = \
             str(scaling_factor1 *(float(properties_field['position_x']) + \
             width_part)) + 'px'

          # processing last field
          field_dict[3] = {}
          field_dict[3]['width'] = str(scaling_factor1*float(width_part*2)) + \
              'px'
          field_dict[3]['margin-left'] = \
             str(scaling_factor1 *(float(properties_field['position_x']) + \
             width_part*2)) + 'px'
        else:
          # all other cases, including default one (year/month/day)
          width_part = int(int(properties_field['size_x']) / 4)

          # processing year field
          field_dict[1] = {}
          field_dict[1]['width'] = str(scaling_factor1*float(width_part *2)) +\
              'px'
          field_dict[1]['margin-left'] = \
             str(scaling_factor1 *float(properties_field['position_x'])) + 'px'

          # processing second field (two digits only)
          field_dict[2] = {}
          field_dict[2]['width'] = str(scaling_factor1*float(width_part)) + \
              'px'
          field_dict[2]['margin-left'] = \
            str(scaling_factor1 *(float(properties_field['position_x']) + \
            width_part*2)) + 'px'

          # processing day field
          field_dict[3] = {}
          field_dict[3]['width'] = str(scaling_factor1*float(width_part)) + \
              'px'
          field_dict[3]['margin-left'] = \
            str(scaling_factor1 *(float(properties_field['position_x']) + \
            width_part*3)) + 'px'


        # rendering time if necessary
        if properties_field['date_only'] == '0':
          # date is specified
          LOG('ManageCSS', INFO, 
              '   position_x=%s' % properties_field['position_x'])
          LOG('ManageCSS', INFO, 
              '   size_x=%s' % properties_field['size_x'])
          field_dict[4] = {}
          field_dict[4]['width'] = str(width_part) + 'px'
          field_dict[4]['margin-left'] = \
             str(int(properties_field['position_x']) +\
             int(properties_field['size_x']) - width_part*2) + 'px'

          field_dict[5] = {}
          field_dict[5]['width'] = str(width_part) + 'px'
          field_dict[5]['margin-left'] = \
             str(int(properties_field['position_x']) +\
             int(properties_field['size_x']) - width_part) + 'px'

      # number of fields to generate
      LOG('ManageCSS', INFO, '\n   field_number = %s' % field_nb)

      field_nb_range = field_nb + 1
      field_range = range(field_nb_range)
      for iterator in field_range:
        # iterator take the field_id according to the field_nb
        # ie (0..field_nb)
        #iterator = it + 1
        LOG('ManageCSS', INFO, '   sub_field_id=%s' % iterator)
        if iterator == 0:
          class_name = field_name + '_class'
        else:
          class_name = field_name + '_class_' + str(iterator)
        LOG('ManageCSS', INFO, '   class_name=%s' % class_name)

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

      # final printing for testing
      LOG('ManageCSS', INFO, '\n\n   final printing')
      for iterator in field_range:
        if iterator == 0:
          class_name = field_name + '_class'
        else:
          class_name = field_name + '_class_' + str(iterator)
        LOG('ManageCSS', INFO, '    class=%s' % class_name)
        for prop_id in properties_css_dict['standard'][class_name].keys():
          LOG('ManageCSS', INFO, '      prop:%s=%s' % \
              (prop_id,properties_css_dict['standard'][class_name][prop_id]))


    return properties_css_dict

  security.declarePublic('setFinalProperties')
  def setFinalProperties( self
                        , properties_css_dict
                        , page_height
                        , space_between_pages):
    """
    adding 'page_end' class to add a div at the end of the last page
    in order to display the full last page under Konqueror
    Otherwize last page is cut and the user is not able to see the
    bottom of the document
    """
    properties_css_page = {}
    properties_css_page['position'] = 'relative'
    properties_css_page['margin-top'] = "%spx" % str(space_between_pages)
    properties_css_dict['head']['page_end'] = properties_css_page
    return properties_css_dict

  security.declarePublic('generateOutputContent')
  def generateOutputContent(self, properties_css_dict):
    """
    return a string containing the whole content of the CSS output
    from properties_css_dict
    """
    LOG('ManageCSS', INFO, 
        ' createmodule > printing output from css_class_generator')
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

  security.declarePublic('createOutputFile')
  def createOutputFile( self
                      , form_css_content
                      , form_css_id
                      , factory):
    """
    add a new file_object in zope, named form_css_id and containing
    the form_css_content
    """
    factory.addDTMLDocument(form_css_id, "css", form_css_content)


class ScribusParser:
  """
  Parses a Scribus file (pda) with PDF-elements inside
  """
  #declare security
  security = ClassSecurityInfo()

  security.declarePublic('getObjectTooltipProperty')
  def getObjectTooltipProperty(self, check_key, default_value, object_name, 
      object_dict):
    """
    check if 'check_key' exists in 'object_dict' and has a value
    if true, then returns this value, else returns 'default_value' and 
    log 'object_name'

    This function is used to get attributes'values in an object_dict and 
    to be sure a compatible value is returned (for that use default value)
    """
    if object_dict.has_key(check_key):
      # 'check_key' exists
      if len(object_dict[check_key]):
        # check_key corresponding value is not null
        # returning this value
        return object_dict[check_key]
      else:
        # check_key is null, logging and asigning default value
        LOG("WARNING : " + str(object_name), WARNING, "invalid " \
            + str(check_key) + ": using " + str(default_value))
        return default_value
    else:
      # check_key is null, logging and asigning default value
      LOG("WARNING : " + str(object_name), WARNING, "no " + str(check_key) \
      + ": using " + str(default_value))
      return default_value

  security.declarePublic('getXmlObjectPropertiesDict')
  def getXmlObjectsPropertiesDict(self, xml_string):
    """
    takes a string containing a whole document and returns
    a full dict of 'PAGE', containing a dict of 'PAGEOBJECT',
    containing a dict of all the relative attributes
    """

    # XXX this is a hack to correct a scribus problem
    # actualy scribus (version 1.3.3.12svn) use some invali xml caracters
    # like the '&#x5;' caracter wich is a carriage return caratere, used for
    # example in a text frame with many lines
    # this problem is well knowed by scribus community and seems to be
    # corrected in the 1.3.4 instable scribus version
    xml_string = xml_string.replace('&#x5;', '\n')
    xml_string = xml_string.replace('&#x4;', '\t')

    # Create DOM tree from the xml string
    LOG('ScribusParser', INFO, ' > create DOM tree')
    dom_tree = minidom.parseString(xml_string)

    # creating the root from the input file
    dom_root = dom_tree.documentElement


    # Here two cases are possible :
    # - if the Scribus Document format is 1.2.* or less, then
    #   the 'PAGE' contains all its 'PAGEOBJECT' elements so
    # - if the Scribus Document format is 1.3.*, then the 'PAGE'
    #   does not contain any other object, and each 'PAGEOBJECT'
    #   refers to its relative page_number using its 'OwnPage'
    #   property
    keep_page = 0
    if "Version" not in dom_root.attributes.keys():
      # no version propery is contained in the document
      # the content does not comply with the Scribus document
      # specification
      LOG('ScribusParser', INFO, 
          " Bad Scribus document format : no 'Version' property ")
      return (None, keep_page, 0)
    else:  

      version = dom_root.attributes["Version"].value
      if version[:3] == "1.2" :
        # Scribus document format is 1.2
        LOG('ScribusParser', INFO, ' found Scribus document format 1.2')

        #making a listing of all the PAGE objects
        LOG('ScribusParser', INFO, ' > making listing of all PAGE objects')
        page_list = dom_root.getElementsByTagName("PAGE")

        returned_page_dict = {}

        #for each PAGE object, searching for PAGEOBJECT
        for page in page_list:

          # getting page number
          # parsing method from the previous ScribusUtils
          page_number = -1
          if 'NUM' in page.attributes.keys():
            page_number = str(page.attributes['NUM'].value)

          LOG('ScribusParser', INFO, '  > PAGE NUM=%s' % str(page_number))

          # making a listing of all PAGEOBJECT in a specified PAGE
          page_object_list = page.getElementsByTagName("PAGEOBJECT")

          # initialising global output dictionary containing pages of elements
          returned_page_object_list = []

          # for each PAGEOBJECT, building dict with atributes
          for page_object in page_object_list:

            # initialising 
            returned_page_object = {}
            field_name = ''

            #iterating PAGEOBJECT attributes
            #old parsing method employed also here
            for node_id in page_object.attributes.keys():
              node_name = node_id.encode('utf8')
              node_value = page_object.attributes[node_id].value.encode('utf8')

              returned_page_object[node_name] = node_value

              if node_name == 'ANNAME':
                if node_value != '':
                  field_name = node_value.replace(' ', '_')

            if field_name != '' :
              #if 'PAGEOBJECT' has a valid name, then adding it to the global
              #dictionary containing all the 'PAGEOBJECT' of the 'PAGE'
              returned_page_object_list.append(returned_page_object)
              LOG('ScribusParser', INFO, 
                  '    > PAGEOBJECT = ' + str(field_name))

          #after having scanned all 'PAGEOBJECT' from a 'PAGE', adding the
          #relative informations to the list of 'PAGE' before going to 
          # the next one
          #in case the page is not empty
          if len(returned_page_object_list) != 0: 
            returned_page_dict[page_number] = returned_page_object_list

        LOG('ScribusParser', INFO, 
            '=> end ScribusParser.getXmlObjectPropertiesDict')
        return (returned_page_dict, keep_page, 0)

        # end parsing document version 1.2.*

      else:
        LOG('ScribusParser', INFO, 
            ' found Scribus Doucment format 1.3 or higher')
        # assuming version is compliant with 1.3.* specifications

        keep_page = 1

        # first of all getting DOCUMENT element to recover Scratch coordinates
        document_list = dom_root.getElementsByTagName("DOCUMENT")
        scratch_left = \
            int(float(document_list[0].attributes["ScratchLeft"].value))
        scratch_top = \
            int(float(document_list[0].attributes["ScratchTop"].value))
        page_gap = int(float(document_list[0].attributes["BORDERTOP"].value))
        scribus_page_width = \
            int(float(document_list[0].attributes["PAGEWIDTH"].value))
        scribus_page_height = \
           int(float(document_list[0].attributes["PAGEHEIGHT"].value)) 
        LOG('ScribusParser', INFO, 
            ' DOCUMENT > scratch_left = %s      scratch_top = %s' % \
            (scratch_left, scratch_top))
        #page_list = dom_root.getElementsByTagName("PAGE")
        page_object_list = dom_root.getElementsByTagName("PAGEOBJECT")

        # iterating 'PAGE' to build the first layer of the output structure
        #for page in page_list:
        #  page_number = page

        # iterating 'PAGEOBJECT' to check compatibility (need a 'ANNAME' 
        # property) and recover the related 'PAGE'
        returned_page_dict = {}
        for page_object in page_object_list:
          returned_page_object = {}
          field_name = ''
          field_OwnPage = ''
          # iterating field attributes
          for node_id in page_object.attributes.keys():
            node_name = node_id.encode('utf8')
            node_value = page_object.attributes[node_id].value.encode('utf8')

            if node_name == 'ANNAME':
              if node_value != '':
                field_name = node_value.replace(' ', '_')
                LOG('ScribusParser', INFO, '> found field : %s' % field_name)
            elif node_name == 'OwnPage':
              field_OwnPage = node_value
            elif node_name == 'XPOS':
              LOG('ScribusParser', INFO, 
                  '   > updating Xpos : %s - %s = %s' % \
                  (scratch_left+int(float(node_value)), scratch_left, 
                      node_value))
              node_value = str(int(float(node_value)) - scratch_left)
            elif node_name == 'YPOS':
              LOG('ScribusParser', INFO, 
                  '   > updating Ypos : %s - %s = %s' % \
                  (scratch_top+int(float(node_value)), scratch_top,
                    node_value))
              node_value = str(int(float(node_value)) - scratch_top)

            returned_page_object[node_name] = node_value

          if field_name != '':
            LOG('ScribusParser', INFO, 
                ' > field has the name : %s' % field_name)
            # field seems to be ok, just need to check if the related page
            # already exists in the 'returned_page_dict'
            if not field_OwnPage in returned_page_dict.keys():
              # page does not exists, need to create it before adding the field
              LOG('ScribusParser', INFO, 
                  '  > adding new page')
              returned_page_dict[field_OwnPage] = []
            returned_page_dict[field_OwnPage].append(returned_page_object)
        return (returned_page_dict, keep_page, page_gap)


  security.declarePublic('getPropertiesConversionDict')
  def getPropertiesConversionDict(self, text_page_dict, option_html):
    """
    takes a dict generated from 'getXmlObjectsProperties' method
    and returns a dict of PAGE including a list with usefull
    'PAGEOBJECT' attributes updated with standard attributes
    and special informations contained in the
    'ANTOOLTIP' attribute.

    usefull attributes are
    - position & size
    - type & inputformat (for erp5 and html)
    - creation order (using 'nb' property)
    - erp5 relative position (left, right, etc.)
    - title information
    - other properties (read_only, multiline, etc.)
    - etc.

    for each PAGE, all PAGEOBJECT are sorted according to their creation order
    'nb'
    """

    LOG('ScribusParser', INFO, '\n  => ScribusParser.getPropertiesConversion')
    returned_page_dict = {}

    # declaring ScribusParser object to run other functions
    sp = ScribusParser()

    for page_number in text_page_dict.keys():
      # iterating through 'PAGE' object of the document
      # id = page_number
      # content = page_content
      page_content = text_page_dict[page_number]

      LOG('ScribusParser', INFO, ' => PAGE = %s" % str(page_number)')

      # declaring special lists used to generate nb for all objects
      # this 'nb' property is usefull to define the object creation order
      # all objects are sorted (has nb / has no nb) and all objects without
      # nb attribte are added t othe end of the 'has nb' list
      nb_property_nbkey_list = []
      nb_property_nonbkey_list = []

      # declaring output object
      returned_object_dict = {}

      # if page_content.haskey('my_fax_field')
      # print "my_fax_field"
      for object_data in page_content:
        # iterating through 'PAGEOBJECT' of the page
        # id = object_name
        # content = object_content

        object_name = object_data['ANNAME']
        del object_data['ANNAME']
        object_content = object_data
        multiline_field= 0
        #multiline_field= object_content['ANFLAG']
        LOG('ScribusParser', INFO, '  => PAGEOBJECT = " + str(object_name)')
        # recovering other attributes list (string format) from 'ANTOOLTIP'
        text_tooltipfield_properties = \
           sp.getObjectTooltipProperty('ANTOOLTIP', '', object_name, 
               object_content)
        #recovering the page attributes

        #declaring output file
        tooltipfield_properties_dict = {}
        #splitting the different attributes
        tooltipfield_properties_list =  \
                    text_tooltipfield_properties.split('#')

        LOG('ScribusParser', INFO, 
            '      ' + str(tooltipfield_properties_list))

        # test if first argument is nb according to previous
        # naming-conventions i.e composed of three digits without
        # id 'nb:' written
        if  str(tooltipfield_properties_list[0]).isdigit():
          # first value of tooltilfield is digit : assuming this is
          # a creation-order information compliant with the previous
          # naming convention
          # modifying this field to make it compatible with new convention
          LOG('ScribusParser', INFO, '        => first element = ' + \
                str(tooltipfield_properties_list[0] + " is digit..."))
          LOG("WARNING : " + str(object_name), WARNING, "out-of-date " \
             + "for tooltipfield, please check naming_conventions")
          temp_nb = tooltipfield_properties_list[0]
          # deleting actual entry
          tooltipfield_properties_list.remove(temp_nb)
          # adding new entry to the list
          tooltipfield_properties_list.append( "nb:" + str(temp_nb))
          # end of translating work to get new standard compliant code
        for tooltipfield_property in tooltipfield_properties_list:
          #printing each property before spliting
          LOG('ScribusParser', INFO, '         ' + str(tooltipfield_property))
          # splitting attribute_id / attribute_value
          tooltipfield_properties_split = tooltipfield_property.split(':')
          if len(tooltipfield_properties_split) == 2:
            tooltipfield_id = tooltipfield_properties_split[0]
            tooltipfield_value = tooltipfield_properties_split[1]
            # making dictionary from 'ANTOOLTIP' attributes
            tooltipfield_properties_dict[tooltipfield_id] = \
                        tooltipfield_value
        # end of 'ANTOOLTIP' parsing

        # getting usefull attributes from scribus 'PAGEOBJECT
        #and 'ANTOOLTIP'
        #
        object_properties = {} 
        page_properties = {}
        # getting object position and size
        object_properties['position_x'] = sp.getObjectTooltipProperty(\
                                          'XPOS',
                                          '0',
                                          object_name,
                                          object_content)
        object_properties['position_y'] = sp.getObjectTooltipProperty(\
                                          'YPOS',
                                          '0',
                                          object_name,
                                          object_content)
        object_properties['size_x'] = sp.getObjectTooltipProperty(\
                                          'WIDTH',
                                          '100',
                                          object_name,
                                          object_content)
        object_properties['size_y'] = sp.getObjectTooltipProperty(\
                                          'HEIGHT',
                                           '17',
                                          object_name,
                                          object_content)

        # converting values to integer-compliant to prevent errors
        # when using them for that converting from 'str' -> 'float'
        # -> 'int' -> 'str'
        object_properties['position_x'] = \
              str(int(float(object_properties['position_x'])))
        object_properties['position_x'] = \
              str(int(float(object_properties['position_x'])))
        object_properties['position_y'] = \
              str(int(float(object_properties['position_y'])))
        object_properties['size_x'] = \
              str(int(float(object_properties['size_x'])))
        object_properties['size_y'] = \
              str(int(float(object_properties['size_y'])))

        # getting object title
        # object title can only be user-specified in the 'tooltip' dict
        object_properties['title'] = \
              sp.getObjectTooltipProperty('title',
                                          object_name,
                                          object_name,
                                          tooltipfield_properties_dict)

        # getting object order position for erp5 form
        temp_order = \
            sp.getObjectTooltipProperty('order',
                                        'none',
                                        object_name,
                                        tooltipfield_properties_dict)

        if temp_order not in  ['left','right']:
          # temp_order invalid
          # trying to get it from its position in original Scribus file
          if int(object_properties['position_x']) > 280.0 :
            temp_order = 'right'
          else :
            temp_order = 'left'
        object_properties['order'] = temp_order

        # getting special ANFLAG sub-properties
        temp_ANFLAG = long(sp.getObjectTooltipProperty('ANFLAG',
                                                       0,
                                                       object_name,
                                                       object_content))
        # initialising results
        anflag_properties = {}
        anflag_properties['noScroll'] = 0
        anflag_properties['noSpellCheck'] = 0
        anflag_properties['editable'] = 0
        anflag_properties['password'] = 0
        anflag_properties['multiline'] = 0
        anflag_properties['noExport'] = 0
        anflag_properties['required'] = 0
        anflag_properties['editable'] = 1
        # analysing result
        LOG('ScribusParser', INFO, '      => ANFLAG = ' + str(temp_ANFLAG))
        # These tests uses some special variables
        # defined at the begining of the script
        if temp_ANFLAG - long(def_noScroll) >= 0:
          # substracting value
          temp_ANFLAG = temp_ANFLAG - long(def_noScroll)
          # 'do not scroll' field
          # adding property
          anflag_properties['noscroll'] = 1
        if temp_ANFLAG - long(def_noSpellCheck) >= 0:
          temp_ANFLAG = temp_ANFLAG - long(def_noSpellCheck)
          # 'do not spell check' field
          anflag_properties['noSpellCheck'] = 1
        if temp_ANFLAG - long(def_editable) >= 0:
          temp_ANFLAG = temp_ANFLAG - long(def_editable)
          # 'editable' field
          anflag_properties['editable'] = 1
        if temp_ANFLAG - long(def_password) >= 0:
          temp_ANFLAG = temp_ANFLAG - long(def_password)
          # 'password' field
          anflag_properties['password'] = 1
        if temp_ANFLAG - long(def_multiLine) >= 0:
          temp_ANFLAG = temp_ANFLAG - long(def_multiLine)
          # 'multiline' field
          anflag_properties['multiline'] = 1
        if temp_ANFLAG - long(def_noExport) >= 0:
          temp_ANFLAG = temp_ANFLAG - long(def_noExport)
          # 'do not export data' field
          anflag_properties['noExport'] = 1
        if temp_ANFLAG - long(def_required) >= 0:
          temp_ANFLAG = temp_ANFLAG - long(def_required)
          # 'required field
          anflag_properties['required'] = 1
        if temp_ANFLAG == long(def_readOnly):
          # 'read only" field
          anflag_properties['editable'] = 0

        # getting maximum number of caracters the field can hold
        # note : only used for textfields ('StringField', 'IntegerField',
        # 'FloatField', etc.)
        # first checking user specifications in tooltipfield
        object_properties['maximum_input'] = \
              sp.getObjectTooltipProperty('maximum_input',
                                          0,
                                          object_name,
                                          tooltipfield_properties_dict)
        # if returned value is empty, then trying 'ANMC' Scribus property
        if object_properties['maximum_input'] == 0:
          object_properties['maximum_input'] = \
                sp.getObjectTooltipProperty('ANMC',
                                            '0',
                                            object_name,
                                            object_content)
        LOG('ScribusParser', INFO, 
            '      => MaxInput = %s' % object_properties['maximum_input'])

        # getting object type :
        # first checking for user-specified type in 'tooltip' properties
        if tooltipfield_properties_dict.has_key('type'):
          # 'type' id in tooltip : using it and ignoring other 'type'
          # information in scribus properties
          object_properties['type'] = tooltipfield_properties_dict['type']
        elif tooltipfield_properties_dict.has_key('title_item'):
          # if page_object has a special attribute 'title_item' this means
          # the field is a CheckBoxField
          object_properties['type'] = 'CheckBoxField'
        # if no user-specified type has been found, trying to
        # find scribus-type  
        elif object_content.has_key('ANTYPE'):
          # from scribus type (selected in the scribus PDF-form properties)
          object_type = str(object_content['ANTYPE'])
          if object_type == '2':
            #type 2 = PDF-Button : InputButtonField
            object_properties['type'] = 'InputButtonField'
          elif object_type == '3':
            #type 3 = PDF-Text : Stringfield by default
            object_properties['type'] = 'StringField'
            if anflag_properties['multiline'] == 1:
              # Stringfield is multiline, converting to TextAreaField
              object_properties['type'] = 'TextAreaField'
            elif object_content.has_key('ANFORMAT'):
              object_format = str(object_content['ANFORMAT'])
              # checking kind of Stringfield
              if object_format == '1':
                #type is number
                object_properties['type'] = 'IntegerField'
              elif object_format == '2':
                #type is percentage
                object_properties['type'] = 'FloatField'
              elif object_format == '3':
                #type is date
                object_properties['type'] = 'DateTimeField'
              elif object_format == '4':
                #type is time
                object_properties['type'] = 'DateTimeField'
          elif object_type == '4':
            # type 4 = PDF-Checkbox
            object_properties['type'] = 'CheckBoxField'
          elif object_type == '5':
            # type 5 = PDF-Combobox
            object_properties['type'] = 'ComboBox'
          elif object_type == '6':
            # type 6 = PDF-ListBox
            object_properties['type'] = 'ListBox'
        else:
          # object type not found in user-properties neither in
          # document-properties. logging and initialising with
          # default type
          LOG("WARNING : " + str(object_name),
              WARNING,
              "no 'type' found, please check your document properties")
          LOG('ScribusParser', WARNING, 
              '      => no type specified :  default = StringField') 
          object_properties['type'] = 'StringField'
        LOG('ScribusParser', INFO, 
            '      type = ' + str(object_properties['type']))


        # getting data_type relative to object type (used in
        # object property_sheet to save field value.
        object_properties['data_type'] = 'string'
        object_properties['default_data'] = ''
        if object_properties['type'] == 'IntegerField':
          object_properties['data_type'] = 'int'
          object_properties['default_data'] = 0
        if object_properties['type'] == 'CheckBoxField':
          object_properties['data_type'] = 'boolean'
          object_properties['default_data'] = 0
        if object_properties['type'] == 'DateTimeField':
          object_properties['data_type'] = 'date'
          object_properties['default_data'] = '1970/01/01'

        # getting 'required' property
        # checking for user data in tooltipfield. if nothing found then
        # taking hard-written value in anflag properties
        object_properties['required'] = \
            sp.getObjectTooltipProperty('required',
                                        anflag_properties['required'],
                                        object_name,
                                        tooltipfield_properties_dict)

        object_properties['editable'] = \
            sp.getObjectTooltipProperty('editable',
                                        anflag_properties['editable'],
                                        object_name,
                                        tooltipfield_properties_dict)

        # getting type properties for special types
        object_properties['rendering'] = 'single'
        # Stringfields handle properties
        # checkbox objects belongs to a group of checkbox
        if str(object_properties['type']) == 'CheckBox' :
          # checking if THIS checkbox is in a group
          object_properties['group'] = \
                sp.getObjectTooltipProperty('group',
                                            '0',
                                            object_name,
                                            tooltipfield_properties_dict)
          LOG('ScribusParser', INFO, 
              '      group = ' + str(object_properties['group']))  
        # object is listbox, and listbox have several possible values
        # WARNING listbox have not been tested in graphic rendering for
        # the moment. is there any use for listbox in PDF-like rendering ?
        if str(object_properties['type']) == 'ListBox':
          # checking if this listbox and the radioField has different possible values
          object_properties['items'] = \
                sp.getObjectTooltipProperty('items',
                                            '',
                                            object_name,
                                            tooltipfield_properties_dict)
        if str(object_properties['type']) == 'RadioField':
          # checking if the radioField has different possible values
          object_properties['items'] = \
                sp.getObjectTooltipProperty('items',
                                            '',
                                            object_name,
                                            tooltipfield_properties_dict)
          object_properties['orientation'] = \
                sp.getObjectTooltipProperty('orientation',
                                            '',
                                            object_name,
                                            tooltipfield_properties_dict)
        # object is datetimefield and need several informations
        if str(object_properties['type']) == 'DateTimeField':
          # has been tested successfully
          object_properties['rendering'] = 'multiple'
          # checking if field has input_order property
          object_properties['input_order'] = \
                sp.getObjectTooltipProperty('input_order',
                                            'ymd',
                                            object_name,
                                            tooltipfield_properties_dict)

          # checking if field has date_only property
          object_properties['date_only'] = \
                sp.getObjectTooltipProperty('date_only',
                                            '1',
                                            object_name,
                                            tooltipfield_properties_dict)

          # checking if special date separator is specified
          # most of PDF forms already have '/' character to differenciate
          # date fields, in this case no separator is needed and the script
          # will automatically insert ' ' between element.
          # > this value is not used in ScribusUtils.py , but in PDFForm.py
          # when creating the fdf file to fill the PDF form.
          if option_html == 1 and object_properties['editable'] == 1:
            object_properties['date_separator'] = ''
            object_properties['time_separator'] = ''
          else:
            object_properties['date_separator'] = \
                sp.getObjectTooltipProperty('date_separator',
                                            '/',
                                            object_name,
                                            tooltipfield_properties_dict)
            object_properties['time_separator'] = \
                sp.getObjectTooltipProperty('time_separator',
                                            ':',
                                            object_name,
                                            tooltipfield_properties_dict)

        # object is relationstringfield and needs some information
        if str(object_properties['type']) == 'RelationStringField':
          # has been tested successfully
          object_properties['rendering'] = 'multiple'
          object_properties['portal_type'] = \
                sp.getObjectTooltipProperty('portal_type',
                                            '0',
                                            object_name,
                                            tooltipfield_properties_dict)
          object_properties['base_category'] = \
                sp.getObjectTooltipProperty('base_category',
                                            '0',
                                            object_name,
                                            tooltipfield_properties_dict)
          object_properties['catalog_index'] = \
                sp.getObjectTooltipProperty('catalog_index',
                                            '0',
                                            object_name,
                                            tooltipfield_properties_dict)
          object_properties['default_module'] = \
                sp.getObjectTooltipProperty('default_module',
                                            '0',
                                            object_name,
                                            tooltipfield_properties_dict)

        # getting creation order from 'tooltip' properties
        # used to create ERP5 objects in a special order
        if tooltipfield_properties_dict.has_key('nb') and \
           str(tooltipfield_properties_dict['nb']).isdigit():
          # object has a nb properties containing its creation position
          # adding the object in the ordered list
          nb_value = int(tooltipfield_properties_dict['nb'])
          LOG('ScribusParser', INFO, 
              "      =>'nb' property specified : using it")
          LOG('ScribusParser', INFO, 
              '         > len(list)=%s' % len(nb_property_nbkey_list))
          # iterating through existing list to find right position
          # before inserting value
          if len(nb_property_nbkey_list) == 0:
            LOG('ScribusParser', WARNING, 
                "    => 'nb' list empty : adding without sorting")
            # list is empty : adding value without sort
            nb_property_nbkey_list.insert(0, (nb_value,object_name))
          elif nb_property_nbkey_list[len(nb_property_nbkey_list)-1][0] <= \
              nb_value:
            LOG('ScribusParser', INFO, "    => 'nb' end : adding at the end")
            # last element is smaller than new element : adding at the end
            nb_property_nbkey_list.append((nb_value, object_name))
          else:
            LOG('ScribusParser', INFO, 
                '    => checking for place to add the element')
            # searching where to insert the element in the ordered list
            for temp_key in range(len(nb_property_nbkey_list)):
              temp_value = nb_property_nbkey_list[temp_key][0]
              temp_content = nb_property_nbkey_list[temp_key][1]
              LOG('ScribusParser', INFO, 
                  "      @" + str(temp_key) + " temp=" + \
                  str(temp_value) + "/" + str(nb_value))
              if nb_value < temp_value:
                #first position where actual 'nb' is smaller than temp 'nb'
                # inserting new couple (nb_value,object_name) here
                LOG('ScribusParser', INFO, 
                    '      inserting here : ' + str(temp_value) + \
                    "/" + str(nb_value))
                nb_property_nbkey_list.insert(temp_key, (nb_value, 
                  object_name))
                # element has been insered , 
                # no need to continue the search => breaking
                break
        else:
          # object has no nb property. logging and adding it to the list of
          # nb-less objects. Script will automatically find a 'nb' value for this element
          LOG("WARNING : " + str(object_name), WARNING, 
              "no 'nb' defined : finding a free slot")
          LOG('ScribusParser', WARNING, 
              "      => no 'nb' property specified : post-processing "\
              "will try to define one")
          nb_property_nonbkey_list.append(object_name)

        # adding current object with its relative properties to the dict
        # before going to the next page_object
        returned_object_dict[object_name] = object_properties

      # final processing before returning full page with modified
      # page_object_properties : setting 'nb' property to all objects
      # without user-specified 'nb' property
      for object_name in nb_property_nonbkey_list:
        # listing all objects with no 'nb' declared
        # defining final position in output list : absolute pos + relative pos
        object_position = len(nb_property_nbkey_list) + 1 
        # and addind it to the end of the final nb-list
        # to give them a 'nb' property
        nb_property_nbkey_list.append((object_position,object_name))
        LOG('ScribusParser', INFO, 
            "    => 'nb' found for %s : %s" % (object_name, object_position))

      # now all page_object are referenced in the list, we just need to sort
      # the elements in the good order. for that a new list of objects 
      #is needed
      returned_object_list = []
      for nb_ind in range(len(nb_property_nbkey_list)):
        # iterating through final nb-list
        # getting list-object information
        (nb_key, nb_value) = nb_property_nbkey_list[nb_ind]
        # setting object's 'nb' property
        returned_object_dict[nb_value]['nb'] = nb_ind + 1
        # add the object at the end of the new list
        returned_object_list.append((nb_value, returned_object_dict[nb_value]))

      # adding returned list of object to the page dict
      # before going to the next page
      returned_page_dict[page_number] = returned_object_list

    # returning final dict containing all the modified data
    LOG('ScribusParser', INFO, 
        '  => end ScribusParser.getPropertiesConversion')
    return (returned_page_dict)

  security.declarePublic('initFieldDict')
  def initFieldDict(self):
    """
    initialize the global_properties dict. this dict will be filled
    with Field attributes (from getFieldAttributes)
    """
    # initializing sub dicts and attributes
    global_object_dict = {}
    global_page_number = 0
    # defining main dict
    global_properties = {}
    global_properties['object'] = global_object_dict
    global_properties['page'] = global_page_number
    global_properties['page_width'] = 595
    global_properties['page_height']= 842
    # return final main dict
    return global_properties




  security.declarePublic('getFieldAttributes')
  def getFieldAttributes(self,
                         field,
                         option_html,
                         page_id,
                         global_properties):
    """
    get only useful field attributes from properties_field
    and save them in global_properties
    """
    (id,properties_field) = field
    # declaring dict to store data
    object_dict = {}
    # getting usefull properties for field generation
    object_dict['title'] = str(properties_field['title'])
    object_dict['erp_type'] = str(properties_field['type'])
    object_dict['data_type'] = str(properties_field['data_type'])
    object_dict['default'] = properties_field['default_data']
    object_dict['nb'] = str(properties_field['nb'])
    object_dict['attributes'] = {}
    if option_html ==1:
      # pdf-like rendering
      object_dict['order'] = page_id
    else:
      # erp rendering
      object_dict['order'] = properties_field['order']
    # recovering attributes
    # required attribute specify if the user has to fill this field
    object_dict['attributes']['required'] =\
               properties_field['required']
    # editable attribute specify if the user can fill this field or not
    object_dict['attributes']['editable'] =\
               properties_field['editable']
    # max number of caracters that can be entered in a field
    # only used with String fieds (including Integer and Float fields)
    if 'maximum_input' in properties_field.keys():
      if 'display_maxwidth' in object_dict['attributes'].keys():
        object_dict['attributes']['display_maxwidth'] = \
                 int(properties_field['maximum_input'])
        # can only be effective without css class, i.e only effective
        # in a ERP5-like rendering
      if 'display_width' in object_dict['attributes'].keys():
        object_dict['attributes']['display_width'] = \
                 int(properties_field['maximum_width'])

    # getting special properties for DateTimeField objects
    if object_dict['erp_type'] == 'DateTimeField':
      # recovering ERP equivalent for user's input_order
      if properties_field['input_order'] in ['day/month/year', 'dmy', 'dmY']:
        object_dict['attributes']['input_order'] = 'dmy'
      elif properties_field['input_order'] in ['month/day/year','mdy', 'mdY']:
        object_dict['attributes']['input_order'] = 'mdy'
      elif properties_field['input_order'] in ['year/month/day','ymd', 'Ymd']:
        object_dict['attributes']['input_order'] = 'ymd'
      else:
        LOG('ScribusParser', INFO, 
            "   found incompatible 'input_order', assuming default ymd")
        object_dict['attributes']['input_order'] = 'ymd'
      # checking if date only or date + time
      object_dict['attributes']['date_only'] = \
          int(properties_field['date_only'])

      object_dict['attributes']['date_separator'] = \
          properties_field['date_separator']
      object_dict['attributes']['time_separator'] = \
          properties_field['time_separator']
    # getting special attributes for RelationStringField
    elif object_dict['erp_type'] == 'RelationStringField':
      portal_type_item = properties_field['portal_type'].capitalize()
      object_dict['attributes']['portal_type'] =\
                 [(portal_type_item,portal_type_item)]
      object_dict['attributes']['base_category'] =\
                 properties_field['base_category']
      object_dict['attributes']['catalog_index'] =\
                 properties_field['catalog_index']
      object_dict['attributes']['default_module'] =\
                 properties_field['default_module']
    # idem : special field concerning RadioField ( tested )
    elif object_dict['erp_type'] == 'RadioField':
      # radio fields have not been tested for the moment
      items = []
      for word_item in properties_field['items'].split('|'):
        items.append((word_item, word_item.capitalize()))
      object_dict['attributes']['items'] = items
      object_dict['attributes']['orientation'] = \
         properties_field['orientation']
    #elif object_dict['erp_type'] == 'CheckBoxField':
      # checkboxfield needs to have their field data updated
      # this is not done automatically so it is needed to do
      # it manually

    # save attributes to the global_properties dict
    global_properties['object'][id] = object_dict

  security.declareProtected('Import/Export objects', 'getContentFile')
  def getContentFile(self, file_descriptor):
    """ Get file content """
    return file_descriptor.read()
  security.declareProtected('Import/Export objects', 'getFileOpen')
  def getFileOpen(self, file_descriptor):
    """ Get file content """
    return file_descriptor.open('r')
  
InitializeClass(ScribusParser)
allow_class(ScribusParser)  

InitializeClass(ManageCSS)
allow_class(ManageCSS)

InitializeClass(ManageFiles)
allow_class(ManageFiles)

InitializeClass(ManageModule)
allow_class(ManageModule)
