##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Tool.BaseTool import BaseTool

try:
  from Products.ERP5Type.CopySupport import CopyContainer
  from Products.Zelenium.zuite import Zuite
  # CopyContainer must be before Zuite otherwise manage_afterAdd() is not
  # called on upgrade and uid is not set. See ERP5Type Folder import order
  # comments.
  class TestTool (CopyContainer, Zuite, BaseTool):
    """
      Container for fonctionnal tests.
    """
    id = 'portal_tests'
    meta_type = 'ERP5 Test Tool'
    portal_type = 'Test Tool'
    title = 'Tests'
    allowed_types = ('Zuite', )

    # Declarative Security
    security = ClassSecurityInfo()

    security.declarePublic('getZeleniumVersion')
    def getZeleniumVersion(self):
      """Returns the version of the zelenium product
      """
      return self.Control_Panel.Products.Zelenium.version

    # Override this method to force Zuite objects are recursed.
    def _recurseListTestCases( self, result, prefix, ob ):
      for tcid, test_case in ob.objectItems():
        if isinstance( test_case, Zuite ):
          result.extend( test_case.listTestCases(
                                        prefix=prefix + ( tcid, ) ) )

    # Override this method to produce ERP5-style reports.
    # security.declarePublic('postResults')
    # def postResults(self, REQUEST):
    #     """ Record the results of a test run.
    #     """
    #     return self.TestTool_reportResult(REQUEST)

    # Use BaseTool class's methods for properties instead of patched PropertyManager's
    _propertyMap = BaseTool._propertyMap
    _setProperty = BaseTool._setProperty
    getProperty = BaseTool.getProperty
    hasProperty = BaseTool.hasProperty

except ImportError:
  class TestTool (BaseTool):
    """
      This is not functional. You must install Zelenium.
    """
    id = 'portal_tests'
    meta_type = 'ERP5 Test Tool'
    portal_type = 'Test Tool'
    allowed_types = ('Zuite', )

    # Declarative Security
    security = ClassSecurityInfo()

InitializeClass(TestTool)
