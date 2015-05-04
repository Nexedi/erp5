##############################################################################
#
# Copyright (c) 2003 Nexedi SARL and Contributors. All Rights Reserved.
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
##############################################################################
""" Interaction in a web-configurable workflow.

$Id$
"""

from OFS.SimpleItem import SimpleItem
from Products.ERP5Type.Globals import DTMLFile, PersistentMapping
from Acquisition import aq_inner, aq_parent
from Products.ERP5Type import Globals
from AccessControl import ClassSecurityInfo

from Products.ERP5Type.Permissions import ManagePortal

from Products.DCWorkflow.ContainerTab import ContainerTab
from Products.DCWorkflow.Guard import Guard
from Products.DCWorkflow.Expression import Expression
from Products.DCWorkflow.Transitions import TRIGGER_WORKFLOW_METHOD

from Products.ERP5 import _dtmldir

class InteractionDefinition (SimpleItem):
    meta_type = 'Workflow Interaction'

    security = ClassSecurityInfo()
    security.declareObjectProtected(ManagePortal)

    title = ''
    description = ''
    new_state_id = ''
    trigger_type = TRIGGER_WORKFLOW_METHOD
    guard = None
    actbox_name = ''
    actbox_url = ''
    actbox_category = 'workflow'
    var_exprs = None  # A mapping.
    script_name = ()  # Executed before transition
    after_script_name = ()  # Executed after transition
    before_commit_script_name = () #Executed Before Commit Transaction
    activate_script_name = ()  # Executed as activity
    method_id = ()
    portal_type_filter = None
    portal_type_group_filter = None
    once_per_transaction = False
    temporary_document_disallowed = False

    manage_options = (
        {'label': 'Properties', 'action': 'manage_properties'},
        {'label': 'Variables', 'action': 'manage_variables'},
        )

    def __init__(self, id):
        self.id = id

    def getId(self):
        return self.id

    def getGuardSummary(self):
        res = None
        if self.guard is not None:
            res = self.guard.getSummary()
        return res

    def getGuard(self):
        if self.guard is not None:
            return self.guard
        else:
            return Guard().__of__(self)  # Create a temporary guard.

    def getVarExprText(self, id):
        if not self.var_exprs:
            return ''
        else:
            expr = self.var_exprs.get(id, None)
            if expr is not None:
                return expr.text
            else:
                return ''

    def getWorkflow(self):
        return aq_parent(aq_inner(aq_parent(aq_inner(self))))

    def getAvailableStateIds(self):
        return self.getWorkflow().states.keys()

    def getAvailableScriptIds(self):
        return self.getWorkflow().scripts.keys()

    def getAvailableVarIds(self):
        return self.getWorkflow().variables.keys()

    _properties_form = DTMLFile('interaction_properties', _dtmldir)

    def manage_properties(self, REQUEST, manage_tabs_message=None):
        '''
        '''
        return self._properties_form(REQUEST,
                                     management_view='Properties',
                                     manage_tabs_message=manage_tabs_message,
                                     )

    def setProperties(self, title,
                      portal_type_filter=None,
                      portal_type_group_filter=None,
                      trigger_type=TRIGGER_WORKFLOW_METHOD,
                      once_per_transaction=False,
                      temporary_document_disallowed=False,
                      script_name=(),
                      after_script_name=(),
                      before_commit_script_name=(),
                      activate_script_name=(),
                      actbox_name='', actbox_url='',
                      actbox_category='workflow',
                      method_id=(),
                      props=None, REQUEST=None, description=''):
        """
          Update transition properties
          XXX - then make sure that method_id is WorkflowMethod for portal_type_filter
          XXX - this will likely require dynamic
        """
        if type(method_id) is type(''):
            self.method_id = method_id.split()
        else:
            self.method_id = method_id
        if portal_type_filter is not None and 'None' in portal_type_filter:
          portal_type_filter = None
        if portal_type_group_filter is not None and 'None' in portal_type_group_filter:
          portal_type_group_filter = None
        if 'None' in after_script_name:
          after_script_name = ()
        if 'None' in activate_script_name:
          activate_script_name = ()
        if 'None' in script_name:
          script_name = ()
        if 'None' in before_commit_script_name:
          before_commit_script_name = ()
        self.portal_type_filter = portal_type_filter
        self.portal_type_group_filter = portal_type_group_filter
        self.title = str(title)
        self.description = str(description)
        self.trigger_type = int(trigger_type)
        self.once_per_transaction = bool(once_per_transaction)
        self.temporary_document_disallowed = bool(temporary_document_disallowed)
        self.script_name = script_name
        self.after_script_name = after_script_name
        self.before_commit_script_name = before_commit_script_name
        self.activate_script_name = activate_script_name
        g = Guard()
        if g.changeFromProperties(props or REQUEST):
            self.guard = g
        else:
            self.guard = None
        self.actbox_name = str(actbox_name)
        self.actbox_url = str(actbox_url)
        self.actbox_category = str(actbox_category)
        # reset cached methods
        self.getPortalObject().portal_types.resetDynamicDocuments()
        if REQUEST is not None:
            return self.manage_properties(REQUEST, 'Properties changed.')

    _variables_form = DTMLFile('interaction_variables', _dtmldir)

    def manage_variables(self, REQUEST, manage_tabs_message=None):
        '''
        '''
        return self._variables_form(REQUEST,
                                     management_view='Variables',
                                     manage_tabs_message=manage_tabs_message,
                                     )

    def getVariableExprs(self):
        ''' get variable exprs for management UI
        '''
        ve = self.var_exprs
        if ve is None:
            return []
        else:
            ret = []
            for key in ve.keys():
                ret.append((key,self.getVarExprText(key)))
            return ret

    def getWorkflowVariables(self):
        ''' get all variables that are available form
            workflow and not handled yet.
        '''
        wf_vars = self.getAvailableVarIds()
        if self.var_exprs is None:
                return wf_vars
        ret = []
        for vid in wf_vars:
            if not self.var_exprs.has_key(vid):
                ret.append(vid)
        return ret

    def addVariable(self, id, text, REQUEST=None):
        '''
        Add a variable expression.
        '''
        if self.var_exprs is None:
            self.var_exprs = PersistentMapping()

        expr = None
        if text:
          expr = Expression(str(text))
        self.var_exprs[id] = expr

        if REQUEST is not None:
            return self.manage_variables(REQUEST, 'Variable added.')

    def deleteVariables(self,ids=[],REQUEST=None):
        ''' delete a WorkflowVariable from State
        '''
        ve = self.var_exprs
        for id in ids:
            if ve.has_key(id):
                del ve[id]

        if REQUEST is not None:
            return self.manage_variables(REQUEST, 'Variables deleted.')

    def setVariables(self, ids=[], REQUEST=None):
        ''' set values for Variables set by this state
        '''
        if self.var_exprs is None:
            self.var_exprs = PersistentMapping()

        ve = self.var_exprs

        if REQUEST is not None:
            for id in ve.keys():
                fname = 'varexpr_%s' % id

                val = REQUEST[fname]
                expr = None
                if val:
                    expr = Expression(str(REQUEST[fname]))
                ve[id] = expr

            return self.manage_variables(REQUEST, 'Variables changed.')

    def getReference(self):
        return self.id

Globals.InitializeClass(InteractionDefinition)


class Interaction (ContainerTab):

    meta_type = 'Workflow Interaction'

    security = ClassSecurityInfo()
    security.declareObjectProtected(ManagePortal)

    all_meta_types = ({'name':InteractionDefinition.meta_type,
                       'action':'addInteraction',
                       'permission': 'Manage portal',
                       },)

    _manage_interaction = DTMLFile('interactions', _dtmldir)

    def manage_main(self, REQUEST, manage_tabs_message=None):
        '''
        '''
        return self._manage_interaction(
            REQUEST,
            management_view='Interactions',
            manage_tabs_message=manage_tabs_message,
            )

    def addInteraction(self, id, REQUEST=None):
        '''
        '''
        tdef = InteractionDefinition(id)
        self._setObject(id, tdef)
        if REQUEST is not None:
            return self.manage_main(REQUEST, 'Interaction added.')

    def deleteInteractions(self, ids, REQUEST=None):
        '''
        '''
        for id in ids:
            self._delObject(id)
        if REQUEST is not None:
            return self.manage_main(REQUEST, 'Interaction(s) removed.')

Globals.InitializeClass(Interaction)
