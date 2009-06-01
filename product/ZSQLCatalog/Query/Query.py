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

from Products.ZSQLCatalog.interfaces.query import IQuery
from Interface.Verify import verifyClass

class Query(object):
  """
    This is the base class of all kind of queries. Its only purpose is to be
    able to distinguish any kind of value from a query.
  """

  __implements__ = IQuery
  __allow_access_to_unprotected_subobjects__ = 1

  def asSQLExpression(self, sql_catalog, column_map, only_group_columns):
    """
      To enable SQL rendering, overload this method in a subclass.
    """
    raise TypeError, 'A %s cannot be rendered as an SQL expression.' % (self.__class__.__name__, )

  def asSearchTextExpression(self, sql_catalog, column=None):
    """
      To enable Search Text rendering, overload this method in a subclass.
    """
    raise TypeError, 'A %s cannot be rendered as a SearchText expression.' % (self.__class__.__name__, )

  def registerColumnMap(self, sql_catalog, column_map):
    """
      This method must always be overloaded by subclasses.
    """
    raise NotImplementedError, '%s is incompeltely implemented.' % (self.__class__.__name__, )

verifyClass(IQuery, Query)

