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

import sys
from collections import defaultdict
from zLOG import LOG, INFO
from Products.ERP5Type.Tool.BaseTool import BaseTool
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod

class RuleTool(BaseTool):
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

  """
  id = 'portal_rules'
  meta_type = 'ERP5 Rule Tool'
  portal_type = 'Rule Tool'
  title = 'Rules'
  allowed_types = ( 'ERP5 Order Rule', 'ERP5 Transformation Rule',
                    'ERP5 Zero Stock Rule', 'ERP5 Delivery Rule',
                    'ERP5 Amortisation Rule')

  # Declarative Security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'searchRuleList')
  def searchRuleList(self, movement, tested_base_category_list=None, **kw):
    """
    this method searches for rules, as predicates against movement

    - the rule must be in "validated" state
    - the rule must be of a known portal type
    - Predicate criterions can be used (like start_date_range_min)
    """
    portal = self.getPortalObject()

    # XXX: For performance reasons, current implementation does not use
    #      DomainTool._searchPredicateList anymore, because in most cases, it
    #      does not filter anything before actualling calling Predicate.test()
    #      Properties must be added on rules to minimize the number of test
    #      scripts/expressions, like the portal types of the possible parent
    #      applied rules, so that filtering can be done via the catalog.
    #      Then it would be possible to use Domain Tool again.
    #return portal.domain_tool._searchPredicateList(context=movement,
    #  tested_base_category_list=tested_base_category_list,
    #  portal_type=portal.getPortalRuleTypeList(),
    #  validation_state="validated", **kw) #XXX "validated" is hardcoded

    # Most rules are only configured through their test_method_id,
    # so filter out them quickly before calling Predicate.test()
    rule_list = []
    for rule in portal.portal_catalog.unrestrictedSearchResults(
        portal_type=portal.getPortalRuleTypeList(),
        validation_state="validated", **kw): #XXX "validated" is hardcoded
      rule = rule.getObject()
      try:
        for test_method_id in rule.getTestMethodIdList():
          if test_method_id == 'Rule_testFalse' or \
             not getattr(movement, test_method_id)(rule):
            break
        else:
          if rule.test(movement,
              tested_base_category_list=tested_base_category_list):
            rule_list.append(rule)
      except Exception:
        # Maybe the script is old (= it takes no argument). Or we should not
        # have called it (= rule would have been excluded before, depending
        # on other criterions). Or there may be a bug.
        # We don't know why it failed so let Predicate.test() do the work.
        if rule.test(movement,
            tested_base_category_list=tested_base_category_list):
          rule_list.append(rule)

    return rule_list

  security.declarePrivate('updateSimulation')
  @UnrestrictedMethod
  def updateSimulation(self, message_list):
    expandable_dict = defaultdict(list)
    for m in message_list:
      expandable_dict[m.object].append(m)
    try:
      for expandable, message_list in six.iteritems(expandable_dict):
        kw = {}
        for m in message_list:
          kw.update(m.kw)
          m.result = None
        LOG("RuleTool", INFO, "Updating simulation for %s: %r"
                              % (expandable.getPath(), kw))
        expandable._updateSimulation(**kw)
    except Exception:
      exc_info = sys.exc_info()
      for m in message_list:
        m.raised(exc_info)

InitializeClass(RuleTool)
