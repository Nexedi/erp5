# This code is to be removed in near future, because we will migrate
# to a Python Script. This is put temporarily for a demo.

def ERP5Site_createModuleScribus(self, form_id=None, module_portal_type=None,
        portal_skins_folder=None, object_portal_type=None, object_title=None, module_id=None,
        module_title=None, selection_index=None, selection_name=None, import_scribus_file=None,
        import_pdf_file=None, option_html=None, import_image_1=None, import_image_2=None,
        import_image_3=None, **kw) :
  """ Creates a module, portal_type and ERP5Form from a scribus and
      PDFForm file"""
  context = self
  from Products.Formulator.Errors import ValidationError, FormValidationError

  from Products.ERP5Form.ScribusUtils import ScribusParser
  ScribusParser = ScribusParser()

  from Products.ERP5Form.CreatePropertySheet import LocalGenerator
  generator = LocalGenerator()

  # importing module to get an access to the 'searchFolder' method
  # needed to be able to list the objects in 'list_object_view' form
  from Products.ERP5.ERP5Site import ERP5Site
  
  from zLOG import LOG

  #import Products.ERP5Form.Folder
  # TODO
  #   - Allow in the module only the new document, we must activate the filter
  #   - handle an optionnal "description" parameter
  #   - set the form action to "Base_edit"
  #   - print : pdf
  #   - export : xml
  #   - report : last modified
  #   - security : 5A


  portal = context.getPortalObject()
  portal_types = portal.portal_types
  object_portal_type_id = object_portal_type

  

  # Create a new portal_type for the module
  #
  portal_types.manage_addTypeInformation( 'ERP5 Type Information'
                                        , typeinfo_name = 'ERP5Type: ERP5 Folder'
                                        , id            = module_portal_type
                                        )
  module_portal_type_value = portal_types[module_portal_type]


  # Set allowed content types
  module_portal_type_value.allowed_content_types = (object_portal_type_id, )
  module_portal_type_value.filter_content_types  = 1
  # building a list of all the portal_type actions
  action_list = module_portal_type_value.listActions()
  # cleaning all portal_type informations
  module_portal_type_value.deleteActions(selections=range(0, len(action_list)))
  # declaring form names
  form_view_pdf = object_portal_type_id.replace(' ','') + '_view' +\
                  object_portal_type_id.replace(' ','') + 'AsPdf'
  form_view_list = object_title.replace(' ','') + 'Module_view' +\
                   object_portal_type_id.replace(' ','') + 'List'
  # declaring css dtml name
  form_css_id = object_portal_type_id.replace(' ','') + '.css'

 
  # Parameters to addAction : id, name, action, condition, permission,
  # category, visible=1, REQUEST=None
  module_portal_type_value.addAction( "view"
                                    , "View"
                                    , "string:${object_url}/%s"%form_view_list
                                    , ""
                                    , "View"
                                    , "object_view"
                                    )

  # SKIN PROCESSING
  # Create the skin directory if does not exist yet
  portal_skins_folder_name = portal_skins_folder
  portal_skins = portal.portal_skins
  if not portal_skins_folder_name in portal.portal_skins.objectIds():
    portal_skins.manage_addFolder(portal_skins_folder_name)
  skin_folder = portal.portal_skins[portal_skins_folder_name]
  # Add new folders into skin paths.
  for skin_name, selection in portal_skins.getSkinPaths():
    selection = selection.split(',')
    if portal_skins_folder_name not in selection:
      new_selection = [portal_skins_folder_name,]
      new_selection.extend(selection)
      portal_skins.manage_skinLayers( skinpath = tuple(new_selection)
                                    , skinname = skin_name
                                    , add_skin = 1
                                    )

  # ERP FORM PROCESSING
  # Create the default ERP5 Form in order to view the objects
  form_view_id = object_portal_type_id.replace(' ','') + '_view'
  factory = skin_folder.manage_addProduct['ERP5Form']
  factory.addERP5Form( form_view_id
                     , title  = object_title
                     )
  form_view_id_object = skin_folder[form_view_id]
  #if option_html != None :
  #  form_view_id_object.rename_group('Default')
  #form_view_id_object.rename_group('Default', 'left')
  if option_html != 1:
    # using default ERP5 positioning convention
    # creating groups
    form_view_id_object.rename_group('Default','left')
    default_groups = ['right', 'center', 'bottom', 'hidden']
    for group in default_groups:
      form_view_id_object.add_group(group)
  # page groups corresponding to graphic view are defined on the flyn
  # when parsing pages to get fields.
  # default field will be removed at the end
  
    
    
  # Define CSS file and object informations
  # first CSS file name
  form_css_id = object_portal_type_id.replace(' ','') + '_css.css'
  # then CSS content object (string)
  form_css_content = ""
  #properties_css_dict is used to store class informations
  properties_css_dict = {}  
  
  # Create Module ERP5 Form in order to view the module
  object_title_view = object_title + ' Module View'
  factory = skin_folder.manage_addProduct['ERP5Form']
  factory.addERP5Form( form_view_list
                     , title  = object_title_view
                     )   
  form_view_list_object = skin_folder[form_view_list]

  form_list_id = form_view_list_object.id
  form_list = form_view_list_object.restrictedTraverse(form_list_id)
  #defining groups for objects listing
  form_view_list_object.rename_group('Default', 'left')
  default_groups = ['right', 'center', 'bottom', 'hidden']
  # adding groups
  for group in default_groups:
    form_view_list_object.add_group(group)

  title_module = ''
  for word in module_title.split():
    title_module += str(word.capitalize() + ' ')
    
  # Add ListBox Field to list the created objects
  id = 'listbox'
  title = title_module
  field_type = 'ListBox'
  form_view_list_object.manage_addField(id, title, field_type)
   
  # manage ListBox settings
  values_settings = {}
  values_settings['pt'] = "form_list"
  values_settings['action'] = "Base_doSelect"
  
  # set the form settings
  for key, value in values_settings.items():
    setattr(form_view_list_object, key, value)
  
  # manage edit property of ListBox
  field_attributes = getattr(form_view_list_object, id)
  field_attributes.values['lines'] = 20
  # adding field columns
  field_attributes.values['columns'] = [('id', 'ID'), ('title', 'Title'), ('description', 'Description')]
  field_attributes.values['list_action'] = 'list'
  field_attributes.values['search'] = 1
  field_attributes.values['select'] = 1
  field_attributes.values['selection_name'] = '%s_selection' % module_id
  # adding 'list_method' to be able to list the objects of a folder
  # WARNING : this field does not contains the name of the method (as
  # a string instance) but the method itself (as method instance)
  list_method = getattr(ERP5Site,'searchFolder')
  # a stange BUG occurs when saving method in field_attributes
  # method adress is well get and saved in the listField
  # but crashing when registrering new portal type inside
  # erp5... I do not know why !
  #field_attributes.values['list_method'] = list_method
  print "METHOD : name = %s" % list_method.__name__
  print "METHOD : type = %s" % list_method.__class__
  print "METHOD : doc  = %s" % list_method.__doc__
  
  form_id = form_view_id_object.id
  form = form_view_id_object.restrictedTraverse(form_id)

  # import and manage Scribus File
  xml_string = ScribusParser.getContentFile(import_scribus_file)

  page_number_int = 0
  
  if xml_string == None:
    LOG("ScribusParser",1,"Scribus file is empty !")
    print "no field was defined in the Scribus file"
    pass
  else:
    # get properties from Scribus File
    output_string = str(xml_string)
    
    #getting page objects with their attributes
    #LOG("ScribusParser",0,"getXmlObjectProperties...")
    print " createmodule > ScribusParser.getXmlObjectProperties"
    text_field_list = ScribusParser.getXmlObjectsProperties(xml_string)
    print " createmodule < ScribusParser.getXmlObjectProperties\n"

    #splitting tooltip-text to recover usefull attributes
    #LOG("ScribusParser",0,"getPropertiesConversion...")
    print " createmodule > ScribusParser.getPropertiesConversion"
    widget_properties = ScribusParser.getPropertiesConversion(text_field_list)
    print " createmodule < ScribusParser.getPropertiesConversion\n"
    
    # add field from OrderedWidgetProperties in ERP5 Module created
    radiofield_widget_properties = {}
    position = {}
    
    # personal_properties is used to create PropertySheet
    personal_properties_list = []
    page_number_int = len(widget_properties)

    # declaring dicts used to generate CSS file
    # css_page is a class container. each class is composed in the css_page
    # before being saved in a css_dict
    properties_css_page = {}
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

    # declaring page size
    # FIXME : this value has to be taken from the image size or the document size.
    # to be dynamicly set
    page_height = 850
    page_width = 610

    # DO NOT WORK !
    # print "opening image"
    # page_image = Image.open(import_image_1)
    # print "getting properties"
    # page_image_properties = page_image.size
    # print page_image_properties
    # print " getting width"
    # page_width = int(page_image_properties[1])
    # page_height = int(page_image_properties[0])
    
    LOG("ScribusParser",0,"begining interpretation of data")
    print " createmodule > begining data interpretation"
    #iterating pages
    for page_iterator in range(len(widget_properties)):
      page_number = str(page_iterator)
      page_content = widget_properties[page_number]
      page_id = "page_" + page_number
      
      if option_html == 1:
        # Processing current page for CSS data
        # getting properties
        properties_css_page = {}
        properties_css_page['position'] = 'relative'
        if page_iterator == 0:
          properties_css_page['margin-top'] = "0px"
        else:
          properties_css_page['margin-top']= "%spx" % (page_height + 20)
        # adding properties dict to golbal dict
        properties_css_dict_head[page_id] = properties_css_page

        # creating image class for background
        properties_css_background = {}
        # making background id
        properties_css_background_id =  page_id + '_background'
        #getting properties
        properties_css_background['position'] = 'absolute'
        properties_css_dict_head[properties_css_background_id] = properties_css_background

        #creating corresponding page group to form
        if page_number == '0':
          # if first page, renaming 'default' group into 0 group
          form_view_id_object.rename_group('Default',page_id)
          print "   > renamed 'default' group to %s" % page_id
        else :
          # adding bandt new group for page
          form_view_id_object.add_group(page_id)
          print "   > added new group %s " % page_id
      
      #iterating pageobjects in page
      for index in range(len(page_content)):
        (id, properties_field) = page_content[index]
                        
        if properties_field.has_key('type'):
          field_type = str(properties_field['type'])
          title = str(properties_field['title'])
          form_view_id_object.manage_addField(id, title, field_type)
  
          context = skin_folder[form_view_id]
          form_id = context.id

          if option_html ==1:
            # Processing object for CSS data
            #declaring dict containing all css data
            # _stand for general display
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
            #getting position and size
            properties_css_object_stand['width'] = str(properties_field['size_x']) + 'px'
            properties_css_object_error['width'] = str(properties_field['size_x']) + 'px'
            properties_css_object_stand['height'] = str(properties_field['size_y']) + 'px'
            properties_css_object_error['height'] = str(properties_field['size_y']) + 'px'
            properties_css_object_stand['margin-left'] = str(properties_field['position_x']) + 'px'
            properties_css_object_error['margin-left'] = str(properties_field['position_x']) + 'px'
            properties_css_object_err_d['margin-left'] = str(page_width + 20 ) + 'px'
            properties_css_object_stand['margin-top'] = str(properties_field['position_y']) + 'px'
            properties_css_object_error['margin-top'] = str(properties_field['position_y']) + 'px'
            properties_css_object_err_d['margin-top'] = str(properties_field['position_y']) + 'px'
            # adding special text_color for text error
            properties_css_object_err_d['color'] = 'rgb(255,0,0)'
            # adding properties to relatives dicts
            properties_css_dict_standard[id] = properties_css_object_stand
            properties_css_dict_error[id] = properties_css_object_error
            properties_css_dict_err_d[id] = properties_css_object_err_d
            # then getting additional properties
            if properties_field['required'] ==1:
              # field is required: using special color
              # color is specified as light-blue when standard
              # color = 'green' when error
              properties_css_dict_standard[id]['background'] = 'rgb(192,192,255)'
              properties_css_dict_error[id]['background'] = 'rgb(128,128,255)'
            else:
              properties_css_dict_standard[id]['background'] = '#F6FFFF'
              properties_css_dict_error[id]['background'] = 'rgb(255,64,64)'
          
            #adding field to the corresponding page group
            position[id] = page_id
            form_view_id_object.move_field_group(id,'page_0',position[id])
            #print "    > added %s to %s (graphic mode) " % (id,position[id])
            #print properties_css_dict_error[id]['background'] 
            #print properties_css_dict_standard[id]['background']
          else:
            # no graphic view
            # position is defined corresponding to ERP5 view
            position[id] = properties_field['order']
            form_view_id_object.move_field_group(id,'left',position[id])
            #print "    > added %s to %s (ERP mode)" % (id,position[id])
          
          # modify value of property
          form = context.restrictedTraverse(form_id)
          field_attributes = getattr(form, id)
          
          type = 'string'
  
          if field_type == 'DateTimeField':
            type = 'date'
            field_attributes.values['input_order'] = properties_field['input_order']
            field_attributes.values['date_only'] = properties_field['date_only']
            field_attributes.values['required'] = properties_field['required']
  
          elif field_type == 'RelationStringField':
            portal_type_item = properties_field['portal_type'].capitalize()
            field_attributes.values['portal_type'] = [(portal_type_item, portal_type_item)]
            field_attributes.values['base_category'] = properties_field['base_category']
            field_attributes.values['catalog_index'] = properties_field['catalog_index']
            field_attributes.values['default_module'] = properties_field['default_module']
          
          elif field_type == 'RadioField':
            radiofield_widget_properties[id] = {'description' : ''}
            items = []
            for word_item in properties_field['items'].split('|'):
              items.append((word_item, word_item.capitalize()))
  
            field_attributes.values['items'] = items

          elif field_type in ['StringField','IntegerField','Floatfield']:
            field_attributes.values['maximum_input'] = properties_field['maximum_input']
            #print "   => saved 'maximum_input' value"
          
          # check that the property is local ...
          if id.startswith('my') and not (
              # ... and not in black list
              # FIXME: this list must be configurable outside this script
                    id.startswith('my_source') or 
                    id.startswith('my_destination') or
                    id in ('my_start_date', 'my_stop_date') ) :
            personal_properties = { 'id' : id[3:],
                                    'description' : '',
                                    'type' : type,
                                    'mode': 'w' }

            personal_properties_list.append(personal_properties)

    # adding 'page_end' class to add a div at the end of the last page
    # in order to display the full last page under Konqueror
    properties_css_page = {}
    properties_css_page['position'] = 'relative'
    properties_css_page['margin-top'] = "%spx" % str( page_height)
    properties_css_dict_head['page_end'] = properties_css_page
    print " createmodule < end of data interpretation"
    print "\n"


    # CSS CLASS
    if option_html ==1:
      print " createmodule > printing output from css_class_generator"
      form_css_content =  "/*-- special css form generated through ScribusUtils module     --*/"
      form_css_content += "/*-- to have a graphic rendering with 'form_html' page template --*/\n"
      form_css_content += "/* head : classes declared for general purpose */\n"
      # iterating classes in document's head
      for class_name in properties_css_dict_head.keys():
        # getting class properties_dict
        class_properties = properties_css_dict_head[class_name]
        # joining exerything
        output_string = "." + str(class_name) + " {" \
                        + "; ".join(["%s:%s" % (id, val) for id, val in class_properties.items()]) \
                        + "}"
        # adding current line to css_content_object
        form_css_content += output_string + "\n"
      form_css_content += "\n/* standard field classes */ \n"
      # adding standard classes
      for class_name in properties_css_dict_standard.keys():
        class_properties = properties_css_dict_standard[class_name]
        output_string = "." + str(class_name) + " {" \
                        + "; ".join(["%s:%s" % (id,val) for id,val in class_properties.items()]) \
                        + "}"
        form_css_content += output_string + "\n"
      form_css_content += "\n/* error field classes */\n"
      #adding error classes
      for class_name in properties_css_dict_error.keys():
        class_properties = properties_css_dict_error[class_name]
        output_string = "." + str(class_name) + "_error {" \
                        + "; ".join(["%s:%s" % (id,val) for id, val in class_properties.items()]) \
                        + "}"
        form_css_content += output_string + "\n"
      form_css_content += "\n/* text_error field classes */ \n"
      # adding field error classes
      for class_name in properties_css_dict_err_d.keys():
        class_properties = properties_css_dict_err_d[class_name]
        output_string = "." + str(class_name) + "_error_display {" \
                        + "; ".join(["%s:%s" % (id,val) for id,val in class_properties.items()]) \
                        + "}"
        form_css_content += output_string + "\n"
    
      #print form_css_content
      print " createmodule < end output \n"
    
      print " createmodule > creating output CSS file"
      factory.addDTMLDocument(form_css_id,"css",form_css_content)
      print " createmodule < CSS file creation\n"


  print " createmodule > managing Form settings"
  # manage global form settings
  values = {}
  values['title'] = str(object_portal_type)
  values['row_length'] = 4
  values['name'] = str(form_view_id)
  # the 'pt' field has to be changed from 'form_view' to 'form_html'
  # when generating graphic interface.
  if option_html ==1:
    values['pt'] = "form_html"
  else:
    values['pt'] = "form_view"
  values['action'] = "Base_edit"
  values['update_action'] = ""
  values['method'] = 'POST'
  values['enctype'] = 'multipart/form-data'
  values['encoding'] = "UTF-8"
  values['stored_encoding'] = 'UTF-8'
  values['unicode_mode'] = 0
  # set the form settings
  for key, value in values.items():
    setattr(form, key, value)
  print " createmodule < settings managed\n"



  print " createmodule > managing PDF settings"
  # Import and manage PDF File before filling of default TALES expressions in cells
  # first import the PDFForm in the skin folder
  factory.addPDFForm(form_view_pdf, object_title, pdf_file = import_pdf_file)

  
  for c in skin_folder.objectValues():

    if c.getId() == form_view_pdf :
      print "    %s selected" % c.getId()
      cell_name_list = c.getCellNames()
      print "      %s" % cell_name_list
      for cell_name in cell_name_list:
        if cell_name[0:3] == 'my_':
          cellName_list = []
          for word in cell_name[3:].split('_'):
            word = word.capitalize()
            cellName_list.append(word)
          if cellName_list[-1] == 'List' :
            TALES = 'python: ", ".join(here.get' + "".join(cellName_list) + '())'
          else :
            TALES = 'python: here.get' + "".join(cellName_list) + '()'
          print "      cell : %s => TALES expression : %s " % (cell_name,TALES)
          c.setCellTALES(cell_name, TALES)
  print " createmodule < PDF settings managed\n"




  print " createmodule > importing background pictures"
  # Import and register background images for HTML display
  if option_html == 1:
    
    # saving pdf content to aspecific file on hard disk
    temp_pdf = open('/tmp/ScribusUtilsTempPDF.tmp','w')
    # moving cursor to begining of file
    import_pdf_file.seek(0)
    # reading content
    temp_content = import_pdf_file.read()
    print "    > inputfile read : %sb" % len(temp_content)
    # writing content to outputfile
    temp_pdf.write(temp_content)
    print "    > inputfile written"
    # closing outputfile
    temp_pdf.close()

    # running first conversion from PDF to PPM
    import commands
    result = commands.getstatusoutput('pdftoppm -r 72 /tmp/ScribusUtilsTempPDF.tmp /tmp/ScribusUtilsTempPPM')
    print "    > pdftoppm result(%s) : %s" % (result[0],result[1])

    # running second conversion from PPM to JPEG
    result = commands.getstatusoutput('convert /tmp/ScribusUtilsTempPPM* jpg:/tmp/ScribusUtilsTempJPG')
    print "    > convert result(%s) : %s" % (result[0],result[1])

    # getting list of resulting pictures
    result = commands.getstatusoutput('ls /tmp/ | grep ScribusUtilsTempJPG')
    print "    > getting list of final pictures"

    image_number = 0
    for image in result[1].split('\n'):
      # result[1] contains the output string
      # splitting this output string in lines to get
      # the string parameters
      
      # opening resulting pictures
      temp_jpg = open('/tmp/%s' % image,'r')
      print "    > open picture : len=%sb" % len(temp_jpg.read())

      # saving content to zope folder
      form_page_id = object_portal_type_id.replace(' ','')+ "_background_" + str(image_number)
      add_image = skin_folder.manage_addProduct['OFSP'].manage_addImage
      add_image(form_page_id,temp_jpg,"background image")

      # incrementing image number before going to next one
      image_number +=1

    # deleting temporary files
    result = commands.getstatusoutput('rm -f /tmp/ScribusUtilsTemp*')
    print "    > remove temp files"
    
    #factory = skin_folder.manage_addProduct['Images']
    """
    if page_number_int > 0 :
      # image specified for first page_element
      form_page_id = object_portal_type_id.replace(' ','') + "_background_" + "0"
      add_image = skin_folder.manage_addProduct['OFSP'].manage_addImage
      add_image(form_page_id,import_image_1,"background image")
    if page_number_int > 1 :
      form_page_id = object_portal_type_id.replace(' ','') + "_background_" + "1"
      add_image = skin_folder.manage_addProduct['OFSP'].manage_addImage
      add_image(form_page_id,import_image_2,"background image 2")
    if page_number_int > 2:
      form_page_id = object_portal_type_id.replace(' ','') + "_background_" + "2"
      add_image = skin_folder.manage_addProduct['OFSP'].manage_addImage
      add_image(form_page_id,import_image_3,"background image 3")
    """
  print " createmodule < background pictures imported\n"

  # get background picture size.
  #skin_folder



  # Create PropertySheet and Document
  print " createmodule > PropertySheet and Document creation"
  name_file = ''
  title_module = ''
  for word in object_portal_type.split():
    name_file += word.capitalize()
    title_module += str(word.capitalize() + ' ')
    
  generator.generateLocalPropertySheet(name_file, personal_properties_list)
  print "   PropertySheet : %s" % name_file
  generator.generateLocalDocument(name_file, object_portal_type)
  print "   Document : %s" % name_file
  
  # Reload register local property sheets
  from Products.ERP5Type.Utils import initializeLocalPropertySheetRegistry
  initializeLocalPropertySheetRegistry()

  # Reload register local classes
  from Products.ERP5Type.Utils import initializeLocalDocumentRegistry
  initializeLocalDocumentRegistry()
  print " createmodule < PropertyShett and Document imported\n"
  


  
  # Then add the portal_type corresponding to the new object
  typeinfo_name_ERP5Type = str('ERP5Type: ERP5 ' + object_portal_type)
  #context.log("typeinfo_name_ERP5Type", typeinfo_name_ERP5Type)
  #context.log("object_portal_type_id", object_portal_type_id)
  portal_types.manage_addTypeInformation(
                    'ERP5 Type Information'
                  , typeinfo_name = typeinfo_name_ERP5Type
                  , id            = object_portal_type_id)

  object_portal_type_value = portal_types[object_portal_type_id]
  # Set default actions
  action_list = object_portal_type_value.listActions()
  object_portal_type_value.deleteActions(
                  selections=range(0, len(action_list)))
  # parameters to addAction : id, name, action, condition, permission,
  # category, visible=1, REQUEST=None
  object_portal_type_value.addAction( "view"
                                    , "View"
                                    , "string:${object_url}/%s" % form_view_id
                                    , ""
                                    , "View"
                                    , "object_view"
                                    )
  object_portal_type_value.addAction( "print"
                                    , "Print"
                                    , "string:${object_url}/%s" % form_view_pdf
                                    , ""
                                    , "View"
                                    , "object_print"
                                    )
  object_portal_type_value.addAction( "metadata"
                                    , "Metadata"
                                    , "string:${object_url}/Base_viewMetadata"
                                    , ""
                                    , "Manage properties"
                                    , "object_view"
                                    )
  
  object_portal_type_value.addAction( "history"
                                    , "History"
                                    , "string:${object_url}/Base_viewHistory"
                                    , ""
                                    , "Manage properties"
                                    , "object_view"
                                    )
  
  # Finally add the module to the site
  portal.newContent( id          = str(module_id)
                   , portal_type = str(module_portal_type)
                   , title       = title_module
                   )

  
  if not selection_index:
    redirect_url = '%s/view?%s' % ( portal.absolute_url()
                                , 'portal_status_message=Module+Created.'
                                )
  else:
    redirect_url = '%s/view?selection_index=%s&selection_name=%s&%s' % (
                              portal.absolute_url()
                            , selection_index
                            , selection_name
                            , 'portal_status_message=Module+Created.'
                            )


  portal.REQUEST.RESPONSE.redirect( redirect_url )
