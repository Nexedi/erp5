##############################################################################
#
# Copyright (c) 2001 Zope Foundation and Contributors.
# Copyright (c) 2015 Nexedi SA and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName, SUBTEMPLATE

# To load all erp5.component.tool.* so that they can be added through 'ERP5
# Site' => Add 'ERP5 Tool'.
from Products.CMFCore.utils import addInstanceForm
def manage_addToolForm(self, REQUEST):

    """ Show the add tool form.
    """
    from Products.ERP5.ERP5Site import getSite
    import erp5.component.tool
    seen_tool_component_set = set()
    for tool_component in getSite().portal_components.objectValues(portal_type='Tool Component'):
        if tool_component.getValidationState() == 'validated':
            module_name = tool_component.getReference()
            # In case there are several versions, only load the 'default' one
            if module_name not in seen_tool_component_set:
                erp5.component.tool.find_load_module(module_name)
                seen_tool_component_set.add(module_name)

    # self is a FactoryDispatcher.
    toolinit = self.toolinit
    tl = []
    for tool in toolinit.tools:
        tl.append(tool.meta_type)

    return addInstanceForm(addInstanceForm, self, REQUEST,
                           factory_action='manage_addTool',
                           factory_meta_type=toolinit.meta_type,
                           factory_product_name=toolinit.product_name,
                           factory_icon=toolinit.icon,
                           factory_types_list=tl,
                           factory_need_id=0)

import Products.CMFCore.utils
Products.CMFCore.utils.manage_addToolForm = manage_addToolForm
