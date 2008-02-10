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

class QueryMixin:
  """
    Mixing class which implements methods which are
    common to all kinds of Queries
  """
  operator = None
  format = None
  type = None

  def __call__(self, **kw):
    return self.asSQLExpression(**kw)  

  def getOperator(self):
    return self.operator

  def getFormat(self):
    return self.format

  def getType(self):
    return self.type

  def getRange(self):
    return self.range

  def getTableAliasList(self):
    return self.table_alias_list

  def getSearchMode(self):
    """Search mode used for Full Text search
    """
    return self.search_mode
    
  def getSearchKey(self):
    """Search mode used for Full Text search
    """
    return self.search_key
  
  def getKey(self):
    return self.key

  def getValue(self):
    return self.value 
    
  def getOperator(self):
    return self.operator.upper().strip()

  def asSearchTextExpression(self):
    raise NotImplementedError
    
  def asSQLExpression(self, key_alias_dict=None,
                      keyword_search_keys=None,
                      datetime_search_keys=None,
                      full_text_search_keys=None,
                      ignore_empty_string=1, stat__=0):
    """
      Return a dictionnary containing the keys and value types:
        'where_expression': string
        'select_expression_list': string
    """
    raise NotImplementedError

  def getSQLKeyList(self):
    """
      Return a list of keys used by this query and its subqueries.
    """
    raise NotImplementedError
  
  def getRelatedTableMapDict(self):
    """
      Return for each key used by this query (plus ones used by its
      subqueries) the table alias mapping.
    """
    raise NotImplementedError

  def _quoteSQLString(self, value):
    """Return a quoted string of the value.
       XXX: Left for backwards compatability!
    """
    format = self.getFormat()
    type = self.getType()
    if format is not None and type is not None:
      if type == 'date':
        if hasattr(value, 'strftime'):
          value = value.strftime(format)
        if isinstance(value, basestring):
          value = "STR_TO_DATE('%s','%s')" % (value, format)
      if type == 'float':
        # Make sure there is no space in float values
        value = value.replace(' ','')
        value = "'%s'" % value
    else:
      if getattr(value, 'ISO', None) is not None:
        value = "'%s'" % value.toZone('UTC').ISO()
      else:
        value = "'%s'" % sql_quote(str(value))
    return value

  def _quoteSQLKey(self, key):
    """Return a quoted string of the value.
       XXX: Left for backwards compatability!
    """
    format = self.getFormat()
    type = self.getType()
    if format is not None and type is not None:
      if type == 'date':
        key = "STR_TO_DATE(DATE_FORMAT(%s,'%s'),'%s')" % (key, format, format)
      if type == 'float':
        float_format = format.replace(' ','')
        if float_format.find('.') >= 0:
          precision = len(float_format.split('.')[1])
          key = "TRUNCATE(%s,%s)" % (key, precision)
    return key    
