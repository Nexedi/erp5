def ERP5Site_createModuleScribus(self, form_id=None, module_portal_type=None,
        portal_skins_folder=None, object_portal_type=None, object_title=None, module_id=None,
        module_title=None, selection_index=None, selection_name=None, import_scribus_file=None,
        import_pdf_file=None, option_html=None,desired_height=None, desired_width=None, import_image_1=None, import_image_2=None,
        import_image_3=None, **kw) :
  """ Creates a module, portal_type and ERP5Form from a scribus and
      PDFForm file"""
  context = self
  
  
  # IMPORTING MODULES
  from Products.Formulator.Errors import ValidationError, FormValidationError
  from Products.ERP5Form.ScribusUtils import ScribusParser
  from Products.ERP5Form.ScribusUtils import ManageModule
  from Products.ERP5Form.ScribusUtils import ManageFiles
  from Products.ERP5Form.ScribusUtils import ManageCSS
  from Products.ERP5Form.CreatePropertySheet import LocalGenerator
  # importing module to get an access to the 'searchFolder' method
  # needed to be able to list the objects in 'list_object_view' form
  from Products.ERP5.ERP5Site import ERP5Site
  from zLOG import LOG

  # CREATING MODULES INSTANCES
  ScribusParser = ScribusParser()
  ManageModule = ManageModule()
  ManageFiles = ManageFiles()
  ManageCSS = ManageCSS()
  generator = LocalGenerator()

  # DECLARING VARIABLES
  def_lineNumberInList = 20 # JPS-XXX - hardcoded
  def_colorRequired = 'rgb(192,192,255)' # JPS-XXX - hardcoded
  def_colorRequiredError = 'rgb(128,128,255)' # JPS-XXX - hardcoded
  def_color = '#F6FFFF' # JPS-XXX - hardcoded
  def_colorError = 'rgb(255,64,64)' # JPS-XXX - hardcoded

  # recovering objects
  portal = context.getPortalObject()
  portal_types = portal.portal_types
  object_portal_type_id = object_portal_type
  desired_height= desired_height
  desired_width= desired_width
  resolution= 300 # JPS-XXX - hardcoded
  option_html = option_html

  # DECLARING NAMES
  # declaring names for ERP5 objects, such as Form, DTML Document, etc.
  # these names are stored in a dict (object_names)
  object_names = ManageModule.setObjectNames(object_portal_type_id,
                                             object_title)

  # CREATING NEW PORTAL TYPE FOR THE MODULE
  # Manage the creation of a ne portal_type for the module
  # (module is not saved for the moment, but properties can be
  # updated)
  ManageModule.setModulePortalType(portal_types,
                                   object_portal_type_id,
                                   module_portal_type,
                                   object_names
                                  )

  # PROCESSING SKIN FOLDER
  # Process and create if necessary the skins_folder defined by the user.
  # return the skin_folder object
  skin_folder = ManageModule.setSkinFolder(portal,
                                           portal_skins_folder)
      
     
  # ERP FORM LIST PROCESSING
  # Create ERP5 Form in order to view the module
  # set up the factory based on skin_folder
  factory = skin_folder.manage_addProduct['ERP5Form']
  
  # run the factory to create the new object (ERP5Form)
  ManageFiles.setERP5Form(factory,
                          str(object_names['view_list']),
                          str(object_title + ' Module View'))
  
  # manage the module form and set up the list inside
  # update form properties with generic module values
  # and implement the objects' listing inside the form
  ManageModule.setModuleForm(object_title,
                             skin_folder,
                             object_names['view_list'],
                             module_title,
                             module_id,
                             def_lineNumberInList)
                             

  # INIT ATTRIBUTES DICT
  # global_properties is a special dict destinated to
  # keep all the field and page data safe during the
  # parsing, allowing them to be updated when needed
  # and used if necessary.
  global_properties = ScribusParser.initFieldDict()
  

  
  # PARSER VARIABLES DECLARATION
  # the following variable will recover the final CSS
  # file's content object (string) before saving it
  # onto the hard disk
  form_css_content = ""
  # properties_css_dict is used to store class informations
  properties_css_dict = {}
  # init page number
  page_number_int = 0
  scale_factor=0
  # import scribus file
  # take the input ScribusFile and read the content
  xml_string = ScribusParser.getContentFile(import_scribus_file)
  if xml_string == None:
    print "no field was defined in the Scribus file"
    pass
  else:
    
    # GETTING FULL SCRIBUS DOCUMENT PROPERTIES
    # get string from ScribusFile content
    output_string = str(xml_string)
    
    print " createmodule > ScribusParser.getXmlObjectPropertiesDict"
    # building a tree from the output string elaborated from the
    # original Scribus file.
    # create a list of pages containing a dict of all the page_objects
    # elements with their attributes 'as they are' (so without any check
    # for data integrity or unuseful values).
    # This procedure already makes a selection of parameters and take all the
    # unnecessary page_objects off.
    #import pdb
    #pdb.set_trace()
    (text_field_list,keep_page,page_gap) = ScribusParser.getXmlObjectsPropertiesDict(xml_string)
    print " createmodule < ScribusParser.getXmlObjectPropertiesDict\n"
    
    
    print " createmodule > ScribusParser.getPropertiesConversionDict"
    # parsing text_field_list created from the getXmlObjectsPropertiesDict
    # to extract all the usefull properties and organize elements. Then check
    # attributes to get properties values.
    # This represents the main process of the script.
    (widget_properties) = ScribusParser.getPropertiesConversionDict(text_field_list)

    print " createmodule < ScribusParser.getPropertiesConversionDict\n"
    
   
    

    # testing if final rendering is PDF-like
    if option_html ==1 :
      print " createmodule > generating background"
      ## BACKGROUND GENERATOR
      # extract background pictures from the PDF document, convert them in the right
      # format (JPG) and add them to the skin folder as Image objects.
      # used only with option_html == 1
      # recover image_size
      image_size=ManageFiles.setBackgroundPictures(import_pdf_file,object_names,skin_folder,desired_height,desired_width,resolution)
      
      page_height,page_width,original_page_height,original_page_width = image_size
      
      print "   height = " + str(page_height)
      print "   width = " + str(page_width)
      print " createmodule < background generated\n"    
      
    # add field from OrderedWidgetProperties in ERP5 Module created
    # radiofield_widget_properties = {}
    position = {}
    # personal_properties_list is used to create PropertySheet
    personal_properties_list = []

    # recovering number of pages
    global_properties['page'] = len(widget_properties)  

    # CSS FILE INIT
    # init the CSS dict by creating sub-dicts to store various information
    # i.e : 'head', 'standard' ,'error', etc.
    # these sub-dicts are stored in the properties_css_dict
    properties_css_dict = ManageCSS.setInit()

    # BEGINING DATA INTERPRETATION
    print " createmodule > begining data interpretation"
    #iterating pages
    #print "   %s" % int(global_properties['page'])
    for page_iterator in range(int(global_properties['page'])):
      page_number = str(page_iterator)
      page_content = widget_properties[page_number]
      page_id = "page_" + page_number

      if option_html == 1:
        # CSS PAGE DEFINITION (PAGE AND BACKGROUND IMAGE)
        # get CSS class properties relative to the actual page
        # (background picture position, picture size, etc.)
        # and add them to the css dict
  width_groups,height_groups = ManageFiles.getPageattributes(
                                              global_properties,
                                              import_pdf_file)
        properties_css_dict,properties_page,actual_width,actual_height = ManageCSS.setPageProperties(
                                   properties_css_dict,
                                   page_iterator,
                                   page_id,
                                   page_height,
           page_width,
           original_page_width,
           original_page_height,width_groups,height_groups)

      # RESUME DATA INTERPRETATION
      # iterating pageobjects in page
      for index in range(len(page_content)):
        (id, properties_field) = page_content[index]
        # testing each page_content
        if properties_field.has_key('type'):

          if option_html ==1:
            # CSS FIELD PROPERTIES
            # get CSS class properties related to the actual page_object
            # in the page (position, size, color, etc.) and add them to
            # the css_dict
            properties_css_dict = ManageCSS.setFieldProperties(
                                           properties_css_dict,
                                           page_content[index],
                                           page_width,
             page_height,
             page_iterator,
             page_gap,
             keep_page,
             0,
             0,
             properties_page,actual_width,actual_height)


          # recover useful page_object attributes from scribus dict
          # to be able to create and update correctly the fields
          # composing the form

          ScribusParser.getFieldAttributes(page_content[index],
                                           option_html,
                                           page_id,
                                           global_properties)

    # CSS CLASS (generateOutputContent)
    if option_html ==1:

      # add last properties to css dict, including implementation
      # of a n+1 page to prevent bug when rendering under Konqueror
      ManageCSS.setFinalProperties(properties_css_dict,page_height)

      # generate output string from dict
      form_css_content = ManageCSS.generateOutputContent(properties_css_dict)

      # save CSS string content into ERP5
      ManageFiles.setCSSFile(factory,object_names['css'],form_css_content)
      



  # CREATING OBJECT FORM AND MANAGING GROUPS
  print " createmodule > generate fields in ERP Form"
  # CREATING ERP5 OBJECT FORM
  # create ERP5 Form to handle object view
  ManageFiles.setERP5Form(factory,
                          object_names['view_id'],
                          object_title)

  # update Form groups to have right number of groups with
  # corresponding names (depending on the kind of display)
  default_groups = ManageModule.setObjectForm(skin_folder,
                                              object_names,
                                              option_html,
                                              global_properties,
                                              object_portal_type)

  # create fields corresponding to the page_objects
  # recovered from the scribus file
  
  ManageModule.setFieldsInObjectForm(skin_folder,
                                     object_names,
                                     default_groups,
                                     global_properties,
                                     option_html
                                     )
  
  print " createmodule < fields created in ERP5 Form\n"

                                     
                                     
  # PDF IMPORTATION AND TALES GENERATION
  print " createmodule > managing PDF settings"
  # read all the content of the PDF document and save it in the skin_folder
  # as a PDFForm. then iterate the fields to get the corresponding TALES
  # expressions and save them in the PDFForm.
  ManageFiles.setPDFForm(factory,
                         skin_folder,
                         object_names,
                         object_title,
                         pdf_file = import_pdf_file
                         )
  print " createmodule < PDF settings managed\n"
  


  # PROPERTYSHEET AND DOCUMENT CREATION
  
  print " createmodule > PropertySheet and Document creation"
  # recover personal properties and save them in a PropertySheet
  # then create the Document related to the object
  ManageFiles.setPropertySheetAndDocument(global_properties,
                                          object_portal_type,
                                          generator,
                                          skin_folder,
                                          object_names)
  # as new document and PropertySheet are created, it is needed to reload the
  # registry.
  from Products.ERP5Type.Utils import initializeLocalPropertySheetRegistry
  initializeLocalPropertySheetRegistry()
  from Products.ERP5Type.Utils import initializeLocalDocumentRegistry
  initializeLocalDocumentRegistry()
  print " createmodule < PropertySheet and Document imported\n"
  
  
  

  # OBJECT PORTAL TYPE
  # create PortalType for the object
  ManageModule.setObjectPortalType(portal_types,
                                   object_portal_type_id,
                                   object_portal_type,
                                   object_names
                                   )

                                   
  
  # Finally add the module to the site
  ManageModule.registerModule(portal,
                              module_id,
                              module_portal_type,
                              object_portal_type)


  # manage redirection URL
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

  # redirect
  portal.REQUEST.RESPONSE.redirect(redirect_url )
