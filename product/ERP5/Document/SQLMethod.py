# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ayush Tiwari <ayush.tiwari@nexedi.com>
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

from AccessControl import ClassSecurityInfo

from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.PythonScripts.PythonScript import \
  PythonScript as ZopePythonScript
from Products.ZSQLMethods.SQL import SQL as ZSQL
from Products.ERP5.mixin.expression import ExpressionMixin

# New ZSQLMethod addition function
def manage_addSQLMethod(self, id, title='',
                connection_id = '',
                arguments = '',
                template = '',
                REQUEST=None,
                *args,
                **kw):
  """
  Add ERP5 SQL Method to the folder
  """
  id = str(id)
  title = str(title)

  # Create SQLMethod object container
  c = SQLMethod(id, title, connection_id, arguments, template, self)

  self._setObject(id, c)
  c = self._getOb(id)
  if REQUEST is not None:
    REQUEST['RESPONSE'].redirect( 'manage_main' )
  return c

class SQLMethod(XMLObject, ZSQL, ExpressionMixin):
  """SQLMethod for ERP5.
  """

  meta_type = 'ERP5 SQL Method'
  portal_type = 'SQL Method'
  icon = None

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Add constructor methods
  constructors = (manage_addSQLMethod,)

  # Override manage and manage_main with ZSQL manage and manage_main respectively
  manage = manage_main = ZSQL.manage
  manage_main._setName('manage_main')

  # View content list, replace /view, Standard option in SQLMethod
  manage_options = ( ZSQL.manage_options[0], ) + \
     ({'icon':'', 'label':'View','action':'view'},) + \
     ZSQL.manage_options[2:]

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.SQLMethod
                    , PropertySheet.CatalogFilter
                    )

  # Inheritence conflicts solved
  __call__    = ZSQL.__call__
  __getitem__ = ZSQL.__getitem__
  PUT         = ZSQL.PUT
  index_html  = ZSQL.index_html
  manage_FTPget = ZSQL.manage_FTPget
  dav__init     = ZSQL.dav__init

  def __init__(self, id, title='',
               connection_id = '',
               arguments = '',
               template = ''
               ):
    """
    Assign attributes to this class and override ZSQL init method to have
    consistency with manage_edit(as ZSQL init also creates manage_edit)
    """
    # Add the properties as the attributes for the SQL Method objects
    # Useful while migrating data from ZSQLMethods to ERP5 SQLMethod objects
    self.id = id

    # Initializing ZSQL class object is important as this will call manage_edit
    # which will change database method properties
    ZSQL.__init__(self, id, title, connection_id, arguments, template)

  def _setArgumentsSrc(self, value):
    """
    We need to override this so as to generate _arg attribute for SQL Method.

    'manage_edit' function for ZSQL Method is responsible for creating '_arg'
    attribute from arguments_src property. That's why it is required to
    call it everytime we edit arguments_src separately.
    """
    self._baseSetArgumentsSrc(value)
    title = self.getTitle()
    arguments = self.getArgumentsSrc()
    src = self.getSrc()
    connection_id = self.getConnectionId()
    self.manage_edit(title, connection_id, arguments, src)

  def _edit(self, **kw):
    """
    'manange_edit' function for ZSQLMethod needs to be called everytime after
    editing SQLMethod object. This would insure the update of _arg and
    template attribute for SQLMethod which are used while creating query.

    https://github.com/zopefoundation/Products.ZSQLMethods/blob/master/src/Shared/DC/ZRDB/DA.py#L353
    """
    XMLObject._edit(self, **kw)
    src = self.getSrc()
    title = self.title
    if title is None:
      title = ''
    connection_id = self.getConnectionId()
    self.manage_edit(title, connection_id, self.arguments_src, src)

InitializeClass(SQLMethod)
