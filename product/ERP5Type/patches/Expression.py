##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002,2005 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

# Expression patch

from Products.CMFCore.Expression import Expression as CMFCore_Expression
from Products.DCWorkflow import Expression
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.PageTemplates.Expressions import getEngine
from Products.PageTemplates.Expressions import SecureModuleImporter
from AccessControl.SecurityManagement import getSecurityManager
from Products.DCWorkflow.Expression import StateChangeInfo

def Expression_hash(self):
  return hash(self.text)

CMFCore_Expression.__hash__ = Expression_hash

# compatibility according to the new structure of workflow:
# deploy script getter to return a list of script.
def _createExprContext(sci):
    '''
    An expression context provides names for TALES expressions.
    '''
    ob = sci.object
    wf = sci.workflow
    script_dict = {script.getReference(): script
                   for script in wf.getScriptValueList()}
    container = aq_parent(aq_inner(ob))
    data = {
        'here':         ob,
        'object':       ob,
        'container':    container,
        'folder':       container,
        'nothing':      None,
        'root':         ob.getPhysicalRoot(),
        'request':      getattr( ob, 'REQUEST', None ),
        'modules':      SecureModuleImporter,
        'user':         getSecurityManager().getUser(),
        'state_change': sci,
        'transition':   sci.transition,
        'status':       sci.status,
        'kwargs':       sci.kwargs,
        'workflow':     wf,
        'scripts':      script_dict,
        }
    return getEngine().getContext(data)

Expression.createExprContext = _createExprContext
