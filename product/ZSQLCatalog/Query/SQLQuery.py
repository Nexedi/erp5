##############################################################################
#
# Copyright (c) 2002-2006 Nexedi SARL and Contributors. All Rights Reserved.
# Copyright (c) 2007-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Vincent Pelletier <vincent@nexedi.com>
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

from Query import Query
from Products.ZSQLCatalog.SQLExpression import SQLExpression
from Products.ZSQLCatalog.interfaces.query import IQuery
from zope.interface.verify import verifyClass

class SQLQuery(Query):
  """
    This Query subclass is used to wrap raw SQL text.
    Use of this class is strongly discouraged, and it is only here for
    backward compatibility.
  """
  def __init__(self, payload):
    """
      payload (string)
        Raw SQL text.
    """
    if not isinstance(payload, basestring):
      raise TypeError, 'Payload must be a string, got a %r: %r' % (type(payload), payload)
    assert len(payload)
    self.payload = '(' + payload + ')'

  def _asSearchTextExpression(self, sql_catalog, column=None):
    return False, None

  def asSQLExpression(self, sql_catalog, column_map, only_group_columns):
    return SQLExpression(self, where_expression=self.payload)

  def registerColumnMap(self, sql_catalog, column_map):
    """
      There is nothing to register for this type of Query subclass.
    """
    pass

  def __repr__(self):
    return '<%s (%r)>' % (self.__class__.__name__, self.payload)

verifyClass(IQuery, SQLQuery)

