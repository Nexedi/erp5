"""Parses a spreadsheet containing categories and returns a mapping.

`import_file` must be a spreadsheet in a format supported by openoffice

`invalid_spreadsheet_error_handler` is the callback method that will be called if
the spreadsheet is invalid. The method must accept one parameter, an
explanation of the error.
The error handler can return a boolean, true meaning that the rest of the
spreadsheet have to be processed, false meaning that the processing should
stop.
If no error_callback is given, the default action is to raise a ValueError on
the first error encountered.

The returned mapping has the following structure:
  
  { 'base_category_id':
       # list of category info
       ( { 'path': 'bc/1',
           'id': '1',
           'title': 'Title 1' },
         { 'path': 'bc/1/2'
           'id': '2',
           'title': 'Title 2' }, ), }

This scripts guarantees that the list of category info is sorted in such a
way that parent always precedes their children.
"""
from Products.ERP5Type.Message import translateString
from Products.ERP5OOo.OOoUtils import OOoParser
parser = OOoParser()
category_list_spreadsheet_mapping = {}
error_list = []

def default_invalid_spreadsheet_error_handler(error_message):
  raise ValueError(error_message)

if invalid_spreadsheet_error_handler is None:
  invalid_spreadsheet_error_handler = default_invalid_spreadsheet_error_handler

property_id_set = context.portal_types.Category.getInstancePropertySet()
property_id_set.update(getattr(context.portal_types, 'Base Category').getInstancePropertySet())

def getIDFromString(string=None):
  """
    This function transform a string to a safe and beautiful ID.
    It is used here to create a safe category ID from a string.
    But the code is not really clever...
  """
  if string is None:
    return None
  clean_id = ''
  translation_map = { 'a'  : [u'\xe0', u'\xe3']
                    , 'e'  : [u'\xe9', u'\xe8']
                    , 'i'  : [u'\xed']
                    , 'u'  : [u'\xf9']
                    , '_'  : [' ', '+']
                    , '-'  : ['-', u'\u2013']
                    , 'and': ['&']
                    }
  # Replace odd chars by safe ascii
  string = string.lower()
  string = string.strip()
  for (safe_char, char_list) in translation_map.items():
    for char in char_list:
      string = string.replace(char, safe_char)
  # Exclude all non alphanumeric chars
  for char in string:
    if char.isalnum() or char in translation_map.keys():
      clean_id += char
  # Delete leading and trailing char which are not alpha-numerics
  # This prevent having IDs with starting underscores
  while len(clean_id) > 0 and not clean_id[0].isalnum():
    clean_id = clean_id[1:]
  while len(clean_id) > 0 and not clean_id[-1].isalnum():
    clean_id = clean_id[:-1]

  return clean_id

# if the file is not an open office format, try to convert it using oood
# FIXME: use portal_transforms
content_type = 'unknown'
if hasattr(import_file, 'headers'):
  content_type = import_file.headers.get('Content-Type', '')
if not (content_type.startswith('application/vnd.sun.xml')
   or content_type.startswith('application/vnd.oasis.opendocument')):
  from Products.ERP5Type.Document import newTempOOoDocument
  tmp_ooo = newTempOOoDocument(context, "_")
  tmp_ooo.edit(data=import_file.read(),
               content_type=content_type)
  tmp_ooo.convertToBaseFormat()
  _, import_file_content = tmp_ooo.convert('ods')
  parser.openFromString(str(import_file_content))
else:
  parser.openFile(import_file)

# Extract tables from the speadsheet file
spreadsheet_list = parser.getSpreadsheetsMapping(no_empty_lines=True)


for table_name in spreadsheet_list.keys():
  sheet = spreadsheet_list[table_name]
  if not sheet:
    continue
  # Get the header of the table
  columns_header = sheet[0]
  # Get the mapping to help us know the property according a cell index
  property_map = {}
  column_index = 0
  path_index = 0
  for column in columns_header:
    column_id = getIDFromString(column)
    # This give us the information that the path definition has started
    path_def_started = 'path_0' in property_map.values()
    # The path of the category has started to be expressed
    if column_id == 'path':
      property_map[column_index] = 'path_' + str(path_index)
      path_index += 1
    # The column has no header information
    elif column_id in (None, ''):
      # Are we in the middle of the path definition ?
      # If the path definition has started and not ended
      if path_def_started and path_index is not None:
        property_map[column_index] = 'path_' + str(path_index)
        path_index += 1
      # else : The path definition is not started or is finished, so ignore the column
    # The column has a normal header
    else:
      # If there is a new column with a header and the path definition has
      # started, that seems the path definition has ended
      property_map[column_index] = column_id.encode('utf8')
    column_index += 1

  # Construct categories data (with absolute path) from table lines
  # The first category is the Base category
  # 1 table = 1 base category
  base_category_name = table_name
  base_category_id = getIDFromString(base_category_name)
  if same_type(base_category_name, u''):
    base_category_name = base_category_name.encode('utf8')
  if same_type(base_category_id, u''):
    base_category_id = base_category_id.encode('utf8')
  category_list = category_list_spreadsheet_mapping.setdefault(base_category_id, [])
  category_list.append({ 'path' : base_category_id
                    , 'title': base_category_name
                    })

  # This path_element_list help us to reconstruct the absolute path
  path_element_list = []
  line_index = 2
  for line in sheet[1:]:
    # Exclude empty lines
    if line.count('') + line.count(None) == len(line):
      continue

    # Prefetch line datas
    line_data = {}
    path_defined = []
    for cell_index, cell in enumerate(line):
      # Get the property corresponding to the cell data
      property_id = property_map[cell_index]
      if cell is not None and cell.strip()=='':
        # empty string is NOT a valid identifier
        cell=None
      line_data[property_id] = cell
      if cell and property_id.startswith('path_'):
        path_defined.append(cell)
        if len(path_defined) > 1:
          invalid_spreadsheet_error_handler(
              translateString("More that one path is defined in ${table}"
              " at line ${line}: ${path_defined}",
                  mapping=dict(path_defined=repr(path_defined),
                               table=table_name,
                               line=line_index)))

    # Analyse every cell of the line
    category_property_list = {}
    cell_index = 0
    for (property_id, cell_data) in line_data.items():

      # Try to generate a cell id from cell data
      cell_id = getIDFromString(cell_data)
      # Returned cell_id can be None or '' (empty string). Both have different meaning:
      #   None : no data was input by the user.
      #   ''   : data entered by the user, but no good transformation of the string to a safe ID.

      # If the cell_id tranformation return an empty string, and if the cell is a path item,
      # we should try to use other line data to get a safe id.
      if cell_id == '' and property_id.startswith('path_'):
        for alt_id_source in ['id', 'title']:
          if line_data.has_key(alt_id_source):
            cell_id = getIDFromString(line_data[alt_id_source])
            if cell_id not in ('', None):
              break

      # Ignore empty cells
      if cell_id not in ('', None):
        # Handle normal properties
        if not property_id.startswith('path_'):
          if same_type(cell_data, u''):
            cell_data = cell_data.encode('utf8')
          category_property_list[property_id] = cell_data
        # Handle 'path' property
        else:
          path_element_id = cell_id
          # Initialize the list of path elements to the cell element
          absolute_path_element_list = [path_element_id,]
          # Get the depth of the current element
          element_depth = int(property_id[5:]) # 5 == len('path_')
          # Get a path element for each depth level to reach the 0-level
          for searched_depth in range(element_depth)[::-1]:
            # Get the first path element that correspond to the searched depth
            for element in path_element_list[::-1]:
              if element['depth'] == searched_depth:
                # Element found, add it to the list
                absolute_path_element_list.append(element['value'])
                # Get the next depth
                break
          path = '/'.join([base_category_id,] + absolute_path_element_list[::-1])
          if same_type(path, u''):
            path = path.encode('utf8')
          category_property_list['path'] = path

          # Save the current raw path item value as title if no title column defined
          if 'title' not in category_property_list.keys():
            clean_title = cell_data.strip()
            # Only set title if it look like a title
            # (i.e. its tranformation to ID is not the same as the original value)
            if clean_title != cell_id:
              category_property_list['title'] = clean_title

          # Detect invalid IDs
          if path_element_id in property_id_set:
            cont = invalid_spreadsheet_error_handler(
                      translateString("The ID ${id} in ${table} at line ${line} is invalid, it's a reserved property name",
                        mapping=dict(id=path_element_id, table=table_name, line=line_index)))
            if not cont:
              return 

          # Detect duplicate IDs
          for element in path_element_list[::-1]:
            if element['depth'] != element_depth:
              break
            if element['value'] == path_element_id:
              cont = invalid_spreadsheet_error_handler(
                      translateString(
                      "Duplicate ID found in ${table} at line ${line} : ${id}",
                        mapping=dict(id=element['value'], table=table_name, line=line_index)))
              if not cont:
                return


          # Detect wrong hierarchy
          if path_element_list:
            current_depth = element_depth
            for element in path_element_list[::-1]:
              if element['depth'] > current_depth:
                break # we are now on another branch
              if element['depth'] == current_depth:
                continue # we are on the same level
              elif element['depth'] == (current_depth - 1):
                current_depth = element['depth']
                continue # we are on the direct parent (current level - 1)
              else:
                cont = invalid_spreadsheet_error_handler(
                        translateString(
                           "Wrong hierarchy found for ID ${id} and depth ${depth} in ${table} at line ${line} ",
                             mapping=dict(id=path_element_id,
                                       depth=element_depth, table=table_name, line=line_index)))
                if not cont:
                  return


          # Save the path element
          path_element_list.append({ 'depth': element_depth
                               , 'value': path_element_id
                               })

      # Proceed to next cell
      cell_index += 1
    line_index += 1
    if len(category_property_list) > 0 and 'path' in category_property_list.keys():
      category_list.append(category_property_list)
if error_list:
  return {'error_list':error_list}
else:
  return category_list_spreadsheet_mapping
