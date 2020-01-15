from Products.ERP5OOo.OOoUtils import OOoParser
import string

request  = container.REQUEST

def getSpreadsheet(file):
  ooo_parser = OOoParser()

  # Extract tables from the speadsheet file
  if file is None:
    return {}
  elif hasattr(file, 'headers'):
    # if the file is not an open office format, try to convert it using oood
    content_type = file.headers.get('Content-Type', '')
    if not (content_type.startswith('application/vnd.sun.xml')
       or content_type.startswith('application/vnd.oasis.opendocument')):

      tmp_ooo = context.newContent(temp_object=True, portal_type='OOo Document',
        id=file.filename)
      tmp_ooo.edit(data=file.read(), content_type=content_type)
      tmp_ooo.convertToBaseFormat()
      ignored, import_file_content = tmp_ooo.convert('ods')
      ooo_parser.openFromString(str(import_file_content))
    else:
      ooo_parser.openFile(file)
  else:
    ooo_parser.openFromString(file)


  return ooo_parser.getSpreadsheetsMapping()

def cleanUid(uid):
  """method which clean an Uid"""
  clean = uid.strip(string.ascii_letters+'_')
  return long(clean)

# if listbox is empty, then we are in the first step
if listbox is None:
  listbox = []

if len(listbox) == 0:
  # First step
  # The purpose of this step is to read the first line of the spreadsheet_name
  # and to propose a mapping interface to the user
  spreadsheets = getSpreadsheet(import_file)

  # Put the result of OOo parsing in the request
  request.set('ooo_import_spreadsheet_data', spreadsheets)

  # Start a session and store the content of the file
  session_id = context.browser_id_manager.getBrowserId(create=1)
  session = context.portal_sessions[session_id]
  temp_file = context.newContent(temp_object=True, portal_type='File', id=session_id)
  temp_file.edit(spreadsheet_mapping=spreadsheets)

  #create a temporary file_name
  timestamp = "%s" % DateTime.timeTime(DateTime())
  timestamp = timestamp.split('.')[0]
  temp_import_file_name = "temp_file_%s" % timestamp
  # Put the generated file_name in the request
  request.set('temp_import_file_name', temp_import_file_name)
  session[temp_import_file_name] = temp_file

  return context.Base_viewFileImportMappingDialog(REQUEST=request)

else:
  # Second Step
  # Read the mapping entered by the user, and import the spreadsheet's lines

  if import_file is not None:
    spreadsheets = getSpreadsheet(import_file)
  else:
    # Get the file content from the session
    session_id = context.browser_id_manager.getBrowserId()
    session = context.portal_sessions[session_id]
    # get the temp_file_name from the request
    temp_file_name = request.get('temp_file_name')
    # Should raise an error if this implementation is buggy
    temp_file = session[temp_file_name]
    # Clear this session after import is done
    session[temp_file_name] = None
    spreadsheets = temp_file.getProperty('spreadsheet_mapping')

  # Build the data mapping
  mapping = {}
  request.set('ooo_import_spreadsheet_data', spreadsheets)

  listbox_ordered_lines = context.Base_getSpreadsheetColumnNameList()

  for line in listbox_ordered_lines:

    # The gererated uid in Base_getSpreadsheetColumnNameList is like new_000001
    # We just use the number '0000001' to index the line in the dict
    listbox_id = cleanUid(line.getUid())
    portal_type_property = None
    if same_type(listbox, dict):
      portal_type_property = listbox[listbox_id]['portal_type_property_list']
    else:
      for listbox_dict in listbox:
        listbox_key = cleanUid(listbox_dict['listbox_key'])
        if listbox_key == listbox_id:
          portal_type_property = listbox_dict['portal_type_property_list']
          break

    if portal_type_property not in ('', None):
      spreadsheet_name = getattr(line, 'spreadsheet_name')
      column_name = getattr(line, 'spreadsheet_column')

      portal_type, property = portal_type_property.split('.', 1)

      if not mapping.has_key(spreadsheet_name):
        mapping[spreadsheet_name] = (portal_type, {})
      mapping[spreadsheet_name][1][column_name] = property

      # portal_type should be the same for all columns
      if portal_type != mapping[spreadsheet_name][0]:
        raise AttributeError, "Portal type is not the same for all columns"

  # If no mapping is given
  if not mapping:
    return context.Base_redirect(form_id=form_id,
                                 keep_items={'portal_status_message': 'Please Define a mapping.'})

  # Create the active process for all the lines
  active_process_value = context.portal_activities.newActiveProcess()
  active_process_path  = active_process_value.getRelativeUrl()
  # Convert each spreadsheet
  for sheet_name, sheet_data in spreadsheets.items():

    # Build a data structure to associate column index with column title
    column_index = {}
    if sheet_data:
      for column_id in range(len(sheet_data[0])):
        column_index[column_id] = sheet_data[0][column_id]

    # Build a data structure to associate column index with object property and portal type
    column_mapping = {}
    for (column_name, property_dict) in mapping[spreadsheet_name][1].items():
      for (column_id, column_title) in column_index.items():
        if column_name == column_title:
          column_mapping[column_id] = property_dict
          break

    # Create a dict to describe each line in property
    for line in sheet_data[1:]:

      imported_line_property_dict = {}

      for line_property_index in range(len(line)):
        if column_mapping.has_key(line_property_index):
          property_value = line[line_property_index]
          if property_value:
            # Create a new property value
            property_id = column_mapping[line_property_index]
            imported_line_property_dict[property_id] = property_value.encode('UTF-8')
      
       
      # If the line is not empty, activate an activity for it
      if imported_line_property_dict not in [{}, None]:
        tag = "OOo_import_%s" % active_process_value.getId()
        portal_type = mapping[spreadsheet_name][0]
        active_object = context.activate(tag=tag,
                         priority=1,
                         activity="SQLQueue",
                         active_process=active_process_path)
 
        if getattr(context, import_file_line_script, None) is None:
          raise AttributeError, 'specified script "%s" does not exists' % import_file_line_script

        getattr(active_object, import_file_line_script)(context.getRelativeUrl(),
                portal_type,
                imported_line_property_dict,
                active_process=active_process_path)

  #Add the active_process in the selection
  context.Base_addActiveProcessInSelection(active_process_path=active_process_path)

  return context.Base_redirect(form_id='Base_viewFileImportReportDialog',
                               keep_items={
                                 'active_process': active_process_path,
                                 'portal_status_message': 'OpenOffice document importing report.'})

raise NotImplementedError
