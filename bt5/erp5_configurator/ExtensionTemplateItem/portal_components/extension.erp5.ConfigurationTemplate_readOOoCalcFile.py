##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
#                    Ivan Tyagov <ivan@nexedi.com>
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

# This extension should be replaced by a clever parser provided by
# ERP5OOo or probably by CloudOOo itself.

from io import BytesIO

def read(self, filename, data):
  """
  Return a OOCalc as a BytesIO
  """
  if data is None:
    oo_template_file = getattr(self, filename)
    fp = BytesIO(oo_template_file)
  else:
    fp = BytesIO(data)
  fp.filename = filename
  return fp

def getIdFromString(string):
  """
    This function transform a string to a safe id.
    It is used here to create a safe category id from a string.
  """
  if string is None:
    return None
  clean_id = ''
  translation_map = { "a": ['\xe0']
                    , "e": ['\xe9', '\xe8']
                    }
  #string = string.lower()
  string = string.strip()
  # oocalc inserts some strange chars when you press - key in a text cell.
  # Following line is a workaround for this,
  # because \u2013 does not exist in latin1
  string = string.replace(u'\u2013', '-')
  for char in string.encode('utf-8'):#('iso8859_1'):
    if char == '_' or char.isalnum():
      clean_id += char
    elif char.isspace() or char in ('+', '-'):
      clean_id += '_'
    else:
      for (safe_char, char_list) in translation_map.items():
        if char in char_list:
          clean_id += safe_char
          break
  return clean_id

def convert(self, filename, data=None):
  from Products.ERP5OOo.OOoUtils import OOoParser
  OOoParser = OOoParser()
  import_file = read(self, filename, data)

  # Extract tables from the speadsheet file
  OOoParser.openFile(import_file)
  filename = OOoParser.getFilename()
  spreadsheets = OOoParser.getSpreadsheetsMapping()

  table_dict = {}
  for table_name, table in spreadsheets.items():
    if not table:
      continue
    # Get the header of the table
    columns_header = table[0]
    # Get the mapping to help us to know the property according a cell index
    property_map = {}
    column_index = 0
    for column in columns_header:
      column_id = getIdFromString(column)
      # The column has no header information
      # The column has a normal header
      property_map[column_index] = column_id
      column_index += 1

    # Construct categories data (with absolut path) from table lines
    object_list = []

    for line in table[1:]:
      object_property_dict = {}

      # Exclude empty lines
      if line.count('') + line.count(None) == len(line):
        continue

      # Analyse every cells of the line
      cell_index = 0
      for cell in line:
        # Ignore empty cells, do the test on the generated id
        # because getIdFromString() is more restrictive
        cell_id = getIdFromString(cell)
        if cell_id not in ('', None):
          # Get the property corresponding to the cell data
          property_id = property_map[cell_index]
          # Convert the value to something like '\xc3\xa9' not '\xc3\xa9'
          object_property_dict[property_id] = cell.encode('UTF-8')
        cell_index += 1

      if len(object_property_dict) > 0:
        object_list.append(object_property_dict)
    table_dict[table_name.encode('UTF-8')] = object_list

  if len(table_dict.keys()) == 1:
    return object_list
  else:
    return table_dict
