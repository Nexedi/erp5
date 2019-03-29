# First retrieve the document
portal = context.getPortalObject()
document_list = portal.document_module.searchFolder(
  reference=reference,
  validation_state="shared",
  sort_on=[('version', 'DESC')],
)
if len(document_list) != 1:
  raise ValueError("Impossible to find document with reference %s" %(reference))
document = document_list[0].getObject()


# Then parse it
from Products.ERP5OOo.OOoUtils import OOoParser
parser = OOoParser()

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

parser.openFromString(str(document.getData()))

# Extract tables from the speadsheet file
filename = parser.getFilename()
spreadsheet_list = parser.getSpreadsheetsMapping(no_empty_lines=True)

spreadsheet_line_list = []

for table_name in spreadsheet_list.keys():
  if table_name != table:
    continue
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
    property_map[column_index] = column_id
    column_index += 1
  # This path_element_list help us to reconstruct the absolute path
  if line_id is not None:
    line_list = [sheet[int(line_id)-1],]
    line_index = int(line_id)
  else:
    line_list = sheet[1:]
    line_index = 2
  line_list = line_list[:limit]
  for line in line_list:
    if id_list and str(line_index) not in id_list:
      continue
    # Exclude empty lines
    if line.count('') + line.count(None) == len(line):
      continue

    # Prefetch line datas
    line_data = {"id" : str(line_index)}
    if not id_only:
      path_defined = []
      for cell_index, cell in enumerate(line):
        # Get the property corresponding to the cell data
        property_id = property_map[cell_index]
        if cell is not None and cell.strip()=='':
          # empty string is NOT a valid identifier
          cell=None
        if not cell:
          continue
        if line_data.has_key(property_id):
          if isinstance(line_data[property_id], str):
            cell_value_list = [line_data[property_id], cell]
            line_data[property_id] = cell_value_list
          else:
            line_data[property_id].append(cell)
        else:
          line_data[property_id] = cell
        # Proceed to next cell
        cell_index += 1
    line_index += 1
    spreadsheet_line_list.append(line_data)

return spreadsheet_line_list
