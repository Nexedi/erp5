##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                     Ivan Tyagov <ivan@nexedi.com>
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
# of the License,] or (at your option) any later version.
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

from Key import BaseKey
    
class FloatKey(BaseKey):
  """ FloatKey key is an ERP5 portal_catalog search key which is used to render
      float like SQL expression.
  """
  # default type of sub Queries to be generated out fo a search string
  default_key_type = 'float'
  
  tokens =  ('OR', 'AND', 'NOT', 'FLOAT',
             'GREATERTHAN', 'GREATERTHANEQUAL', 
             'LESSTHAN', 'LESSTHANEQUAL')
             
  sub_operators = ('GREATERTHAN', 'GREATERTHANEQUAL', 
                    'LESSTHAN', 'LESSTHANEQUAL', 'NOT')
  

  # Note: Order of placing rules (t_WORD for example) is very important
  def t_OR(self, t):
    r'(\s+OR\s+|\s+or\s+)'
    # operator must have leading and trailing ONLY one white space character
    # otherwise it's treated as a WORD
    t.value = 'OR'
    return t

  def t_AND(self, t):
    r'(\s+AND\s+|\s+and\s+)'
    # operator must have leading and trailing ONLY one white space character
    # otherwise it's treated as a WORD
    t.value = 'AND'
    return t  
  
  def t_NOT(self, t):
    r'(\s+NOT\s+|\s+not\s+|!=)'
    # operator must have leading and trailing ONLY one white space character
    # otherwise it's treated as a WORD
    t.value = '!=' 
    return t     
    
  t_GREATERTHANEQUAL = r'>='  
  t_LESSTHANEQUAL = r'<='  
  t_GREATERTHAN = r'>'
  t_LESSTHAN = r'<'  

  def t_FLOAT(self, t):
    r'[\d.][\d.]*'
    # FLOAT is a float number
    value = t.value.replace('"', '').strip()
    t.value = "%s" %value
    return t   
  
  def quoteSQLString(self, value, format):
    """ Return a quoted string of the value. """
    # Make sure there is no space in float values
    return "'%s'" %str(value).replace(' ', '')    

  def quoteSQLKey(self, key, format):
    """ Return a quoted string of the value. """
    if format is not None:
      float_format = format.replace(' ', '')
      if float_format.find('.') >= 0:
        precision = len(float_format.split('.')[1])
        key = "TRUNCATE(%s,%s)" % (key, precision)    
    return key    
