##############################################################################
#
# Copyright (c) 2003 Nexedi SARL and Contributors. All Rights Reserved.
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

import Globals
import App
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName, _getAuthenticatedUser
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Acquisition import aq_base, aq_parent, aq_inner, aq_acquire
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.CMFCore.WorkflowTool import addWorkflowFactory

from zLOG import LOG

class InteractionWorkflowDefinition (DCWorkflowDefinition):
    """
    The InteractionTool implements portal object
    interaction policies.

    An interaction is defined by
    a domain and a behaviour:

    The domain is defined as:

    - the meta_type it applies to

    - the portal_type it applies to

    - the conditions of application (category membership, value range,
      security, function, etc.)

    The transformation template is defined as:

    - pre method executed before

    - pre async executed anyway

    - post method executed after success before return

    - post method executed after success anyway

    This is similar to signals and slots except is applies to classes
    rather than instances. Similar to
    stateless workflow methods with more options. Similar to ZSQL scipts
    but in more cases.

    Examples of applications:

    - when movement is updated, apply transformation rules to movement

    - when stock is 0, post an event of stock empty

    - when birthday is called, call the happy birthday script
    
    ERP5 main application: specialize behaviour of classes "on the fly".
    Make the architecture as modular as possible. Implement connections
    à la Qt.

    Try to mimic: Workflow...

    Question: should be use it for values ? or use a global value model ?

    Status : OK


    Implementation:

    A new kind of workflow (stateless). Follow the DCWorkflow class.
    Provide filters (per portal_type, etc.). Allow inspection of objects ?
    """
    meta_type = 'Interaction Workflow'
    title = 'Interaction Workflow Definition'

    interactions = None

    security = ClassSecurityInfo()

    manage_options = (
        {'label': 'Properties', 'action': 'manage_properties'},
        {'label': 'Interactions', 'action': 'interactions/manage_main'},
        {'label': 'Variables', 'action': 'variables/manage_main'},
        {'label': 'Scripts', 'action': 'scripts/manage_main'},
        {'label': 'Permissions', 'action': 'manage_permissions'},
        ) + App.Undo.UndoSupport.manage_options

    def __init__(self, id):
        self.id = id
        from Interaction import Interaction
        self._addObject(Interaction('interactions'))
        from Products.DCWorkflow.Variables import Variables
        self._addObject(Variables('variables'))
        from Products.DCWorkflow.Worklists import Worklists
        self._addObject(Worklists('worklists'))
        from Products.DCWorkflow.Scripts import Scripts
        self._addObject(Scripts('scripts'))

Globals.InitializeClass(InteractionWorkflowDefinition)

addWorkflowFactory(InteractionWorkflowDefinition, id='interaction_workflow',
                                     title='Web-configurable interaction workflow')
