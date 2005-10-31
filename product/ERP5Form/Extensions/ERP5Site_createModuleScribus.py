def ERP5Site_createModuleScribus(self, form_id=None, module_portal_type=None,
        portal_skins_folder=None, object_portal_type=None, object_title=None, module_id=None,
        module_title=None, selection_index=None, selection_name=None, import_scribus_file=None,
        import_pdf_file=None, **kw) :
  """ Creates a module, portal_type and ERP5Form from a scribus and
      PDFForm file"""
  context = self
  from Products.Formulator.Errors import ValidationError, FormValidationError

  from Products.ERP5Form.ScribusUtils import ScribusParser
  ScribusParser = ScribusParser()

  from Products.ERP5Form.CreatePropertySheet import LocalGenerator
  generator = LocalGenerator()

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
  portal_types.manage_addTypeInformation( 'ERP5 Type Information'
                                        , typeinfo_name = 'ERP5Type: ERP5 Folder'
                                        , id            = module_portal_type
                                        )
  module_portal_type_value = portal_types[module_portal_type]


  # Set allowed content types
  module_portal_type_value.allowed_content_types = (object_portal_type_id, )
  module_portal_type_value.filter_content_types  = 1

  action_list = module_portal_type_value.listActions()
  module_portal_type_value.deleteActions(selections=range(0, len(action_list)))

  form_view_pdf = object_portal_type_id.replace(' ','') + '_view' +\
                  object_portal_type_id.replace(' ','') + 'AsPdf'
  form_view_list = object_title.replace(' ','') + 'Module_view' +\
                   object_portal_type_id.replace(' ','') + 'List'

  # Parameters to addAction : id, name, action, condition, permission,
  # category, visible=1, REQUEST=None
  module_portal_type_value.addAction( "view"
                                    , "View"
                                    , "string:${object_url}/%s"%form_view_list
                                    , ""
                                    , "View"
                                    , "object_view"
                                    )

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

  # Create the default ERP5 Form in order to view the object
  form_view_id = object_portal_type_id.replace(' ','') + '_view'
  factory = skin_folder.manage_addProduct['ERP5Form']
  factory.addERP5Form( form_view_id
                     , title  = object_title
                     )
  form_view_id_object = skin_folder[form_view_id]
  form_view_id_object.rename_group('Default', 'left')
  default_groups = ['right', 'center', 'bottom', 'hidden']
  for group in default_groups:
    form_view_id_object.add_group(group)

  object_title_view = object_title + ' Module View'
  factory = skin_folder.manage_addProduct['ERP5Form']
  factory.addERP5Form( form_view_list
                     , title  = object_title_view
                     )
  form_view_list_object = skin_folder[form_view_list]

  form_list_id = form_view_list_object.id
  form_list = form_view_list_object.restrictedTraverse(form_list_id)

  form_view_list_object.rename_group('Default', 'left')
  #default_groups = ['right', 'center', 'bottom', 'hidden']
  for group in default_groups:
    form_view_list_object.add_group(group)

  title_module = ''
  for word in module_title.split():
    title_module += str(word.capitalize() + ' ')
    
    
  # Add ListBox Field
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
  field_attributes.values['columns'] = [('id', 'ID'), ('title', 'Title'), ('description', 'Description')]
  field_attributes.values['list_action'] = 'list'
  field_attributes.values['search'] = 1
  field_attributes.values['select'] = 1
  field_attributes.values['selection_name'] = '%s_selection' % module_id
  
  form_id = form_view_id_object.id
  form = form_view_id_object.restrictedTraverse(form_id)

  # import and manage Scribus File
  xml_string = ScribusParser.getContentFile(import_scribus_file)

  if xml_string == None:
    #print "no field was defined in the Scribus file"
    pass
  else:
    # get properties from Scribus File
    output_string = str(xml_string)

    text_field_list = ScribusParser.getXmlObjectsProperties(xml_string)

    widget_properties = ScribusParser.getPropertiesConversion(text_field_list)
    
    # add field from OrderedWidgetProperties in ERP5 Module created

    radiofield_widget_properties = {}
    position = {}
    
    # personal_properties is used to create PropertySheet
    personal_properties_list = []

    for index in range(len(widget_properties)):
      id = str(widget_properties[index][0])
      properties_field = widget_properties[index][1]
      
      if properties_field.has_key('type'):
        field_type = str(properties_field['type'])
        title = str(properties_field['title'])
        form_view_id_object.manage_addField(id, title, field_type)

        context = skin_folder[form_view_id]
        form_id = context.id

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
          for word_item in properties_field['items']:
            items.append((word_item, word_item.capitalize()))

          field_attributes.values['items'] = items
        
        position[id] = properties_field['order']
        
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
  
    # Order field
    for field in form.get_fields():
      key = str(field.id)
      if position.has_key(key) == 1 and position[key] == 'right':
        field.move_field_group(key, 'left', 'right')

  # manage_settings

  values = {}

  values['title'] = str(object_portal_type)
  values['row_length'] = 4
  values['name'] = str(form_view_id)
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

  # Import and manage PDF File before filling of default TALES expressions in cells
  factory.addPDFForm(form_view_pdf, object_title, pdf_file = import_pdf_file)

  for c in skin_folder.objectValues():
    if c.getId() == form_view_pdf :
      for cell_name in c.getCellNames():
        if cell_name[0:3] == 'my_':
          cellName = []
          for word in cell_name[3:].split('_'):
            word = word.capitalize()
            cellName.append(word)
          if cellName[-1] == 'List' :
            TALES = 'python: ", ".join(here.get' + "".join(cellName) + '())'
          else :
            TALES = 'python: here.get' + "".join(cellName) + '()'
          c.setCellTALES(cell_name, TALES)

  # Create PropertySheet and Document
  name_file = ''
  title_module = ''
  for word in object_portal_type.split():
    name_file += word.capitalize()
    title_module += str(word.capitalize() + ' ')
    
  generator.generateLocalPropertySheet(name_file, personal_properties_list)
  generator.generateLocalDocument(name_file, object_portal_type)

  # Reload register local property sheets
  from Products.ERP5Type.Utils import initializeLocalPropertySheetRegistry
  initializeLocalPropertySheetRegistry()
  # Reload register local classes
  from Products.ERP5Type.Utils import initializeLocalDocumentRegistry
  initializeLocalDocumentRegistry()
  
  
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
  

