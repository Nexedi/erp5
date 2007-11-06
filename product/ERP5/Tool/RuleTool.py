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

from Products.CMFCore.utils import UniqueObject

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile
from Products.ERP5Type.Core.Folder import Folder
from Products.ERP5Type import Permissions
from Products.CMFCore.utils import getToolByName

from Products.ERP5 import _dtmldir

from zLOG import LOG

class RuleTool (UniqueObject, Folder):
    """
    The RulesTool implements portal object
    transformation policies.

    An object transformation template is defined by
    a domain and a transformation pattent:

    The domain is defined as:

    - the meta_type it applies to

    - the portal_type it applies to

    - the conditions of application (category membership, value range,
      security, function, etc.)

    The transformation template is defined as:

    - a tree of portal_types starting on the object itself

    - default values for each node of the tree, incl. the root itself

    When a transformation is triggered, it will check the existence of
    each node and eventually update values

    Transformations are very similar to XSLT in the XML world.

    Examples of applications:

    - generate accounting movements from a stock movement

    - generate a birthday event from a person

    ERP5 main application : generate submovements from movements
    according to templates. Allows to parametrize modules
    such as payroll.

    Try to mimic: XSL semantics

    Status : OK

    NEW NAME : Rules Tool

    TODO: XXX Please use BaseTool
    """
    id = 'portal_rules'
    meta_type = 'ERP5 Rule Tool'
    portal_type = 'Rule Tool'
    allowed_types = ( 'ERP5 Order Rule', 'ERP5 Transformation Rule', 'ERP5 Zero Stock Rule', 'ERP5 Delivery Rule', 'ERP5 Amortisation Rule')

    # Declarative Security
    security = ClassSecurityInfo()

    #
    #   ZMI methods
    #
    manage_options = ( ( { 'label'      : 'Overview'
                         , 'action'     : 'manage_overview'
                         }
                        ,
                        )
                     + Folder.manage_options
                     )

    security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
    manage_overview = DTMLFile( 'explainRuleTool', _dtmldir )

    # Filter content (ZMI))
    def __init__(self):
        return Folder.__init__(self, RuleTool.id)

    # Filter content (ZMI))
    def filtered_meta_types(self, user=None):
        # Filters the list of available meta types.
        all = RuleTool.inheritedAttribute('filtered_meta_types')(self)
        meta_types = []
        for meta_type in self.all_meta_types():
            if meta_type['name'] in self.allowed_types:
                meta_types.append(meta_type)
        return meta_types

    security.declareProtected(Permissions.AccessContentsInformation,
        'searchRuleList')
    def searchRuleList(self, movement, tested_base_category_list=[], **kw):
      """
      this method searches for rules, as predicates against movement

      - the rule must be in "validated" state
      - the rule must be of a known portal type
      - Predicate criterions can be used (like start_date_range_min)
      """
      domain_tool = getToolByName(self, "portal_domains")

      rule_list = domain_tool.searchPredicateList(context=movement,
          tested_base_category_list=tested_base_category_list,
          portal_type=self.getPortalRuleTypeList(),
          validation_state="validated", **kw) #XXX "validated" is hardcoded

      return rule_list

InitializeClass(RuleTool)
