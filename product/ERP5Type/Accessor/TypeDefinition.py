##############################################################################
#
# Copyright (c) 2002-2003 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from DateTime import DateTime

"""
  Define the types available in property sheets and a typecasting method for
  each.
"""

# By setting ATTRIBUTE_PREFIX to '_', properties become private
# which allows to force users to use accessors only.
ATTRIBUTE_PREFIX = ''

# Type cast
def identity(value):
  return value

def asFloat(value):
  """
    Return the value as a float or a type-specific default value if it fails.
  """
  try:
    result = float(value)
  except TypeError:
    result = type_definition['float']['default']
  return result

def asDate(value):
  """
    Return the value as a date or a type-specific default value if it fails.
  """
  try:
    if isinstance(value,DateTime):
      result = value
    else:
      result = DateTime(value)
  except TypeError:
    result = type_definition['date']['default']
  return result

def asInt(value):
  """
    Return the value as an int or a type-specific default value if it fails.
  """
  try:
    result = int(value)
  except TypeError:
    result = type_definition['int']['default']
  return result

def asLong(value):
  """
    Return the value as a long or a type-specific default value if it fails.
  """
  try:
    result = long(value)
  except TypeError:
    result = type_definition['long']['default']
  return result

def asString(value):
  """
    Return the value as a string or a type-specific default value if it fails.
  """
  try:
    if value is None:
      result = ''
    else:
      result = str(value)
  except TypeError:
    result = type_definition['string']['default']
  return result

def asList(value):
  """
    Return the value as a list or a type-specific default value if it fails.
  """
  if type(value) in (type([]), type(())):
    result = list(value)
  elif type(value) is type('a'):
    result = value.split()
  else:
    result = [value]
  return result

type_definition = {
    'float'              : { 'cast'    : asFloat,
                             'null'    : ('', 'None', None,),
                             'default' : 0.0,
                             'isList'  : 0,
                           },
    'int'                : { 'cast'    : asInt,
                             'null'    : ('', 'None', None,),
                             'default' : 0,
                             'isList'  : 0,
                           },
    'long'               : { 'cast'    : asLong,
                             'null'    : ('', 'None', None,),
                             'default' : 0L,
                             'isList'  : 0,
                           },
    'date'               : { 'cast'    : asDate,
                             'null'    : ('', 'None', None,),
                             'default' : DateTime(0.0),
                             'isList'  : 0,
                           },
    'string'             : { 'cast'    : asString,
                             'null'    : ('',None, ),
                             'default' : '',
                             'isList'  : 0,
                           },
    'text'               : { 'cast'    : asString,
                             'null'    : ('',None,),
                             'default' : '',
                             'isList'  : 0,
                           },
    'boolean'            : { 'cast'    : asInt,
                             'null'    : ('', 'None', None,),
                             'default' : 0,
                             'isList'  : 0,
                           },
    'lines'              : { 'cast'    : asList,
                             'null'    : ('', None,),
                             'default' : [],
                             'isList'  : 1,
                           },
    'tokens'             : { 'cast'    : asList,
                             'null'    : ('', None,),
                             'default' : [],
                             'isList'  : 1,
                           },
    'selection'          : { 'cast'    : asList,
                             'null'    : ('', None,),
                             'default' : [],
                             'isList'  : 1,
                           },
    'multiple selection' : { 'cast'    : asList,
                             'null'    : ('', None,),
                             'default' : [],
                             'isList'  : 1,
                           },
                           # Content are subdocuments (ex. default_career)
    'content'             : { 'cast'    : identity,
                             'null'    : ('', 'None', None,),
                             'default' : None,
                             'isList'  : 0,
                           },
                           # Object are properties of any type (ex. data)
                           # and are considered as simple properties
    'object'             : { 'cast'    : identity, 
                             'null'    : ('', 'None', None,),
                             'default' : None,
                             'isList'  : 0,
                           },
    'tales'              : { 'cast'    : identity,
                             'null'    : ('', 'None', None,),
                             'default' : None,
                             'isList'  : 0,
                           },
}

list_types = ('lines', 'tokens', 'selection', 'multiple selection')


