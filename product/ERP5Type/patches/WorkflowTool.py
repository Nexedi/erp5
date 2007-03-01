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

from zLOG import LOG

# Make sure Interaction Workflows are called even if method not wrapped

from Products.CMFCore.WorkflowTool import WorkflowTool
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition

def WorkflowTool_wrapWorkflowMethod(self, ob, method_id, func, args, kw):

    """ To be invoked only by WorkflowCore.
        Allows a workflow definition to wrap a WorkflowMethod.

        By default, the workflow tool takes the first workflow wich
        support the method_id. In ERP5, with Interaction Worfklows, we
        may have many workflows wich can support a worfklow method,
        that's why we need this patch.

        Current implementation supports:
        - at most 1 DCWorkflow per portal type per method_id
        - as many Interaction workflows as needed per portal type

        NOTE: automatic transitions are invoked through
        _findAutomaticTransition in DC Workflows.

        TODO: make it possible to have multiple DC Workflow
        per portal type per method_id
    """
    # Check workflow containing the workflow method
    wf_list = []
    wfs = self.getWorkflowsFor(ob)
    if wfs:
      for w in wfs:
        if (hasattr(w, 'isWorkflowMethodSupported')
            and w.isWorkflowMethodSupported(ob, method_id)):
          wf_list.append(w)
    else:
      wfs = ()
    # If no transition matched, simply call the method    
    # And return
    if len(wf_list)==0:
      return apply(func, args, kw)
    # Call notifyBefore on each workflow
    for w in wfs:
      w.notifyBefore(ob, method_id, args=args, kw=kw)
    # Call the method on matching workflows
    only_interaction_defined = 1
    for w in wf_list:
      if w.__class__.__name__ != 'InteractionWorkflowDefinition':
        only_interaction_defined = 0
        # XXX - There is a problem here if the same workflow method
        # is used by multiple workflows. Function "func" will be
        # called multiple times. Patch or changes required to mak
        # sure func is only called once.
        # Solution consists in reimplementing _invokeWithNotification
        # at the level of each workflow without notification
        # (ex. _invokeWithoutNotification)
        result = self._invokeWithNotification(
            [], ob, method_id, w.wrapWorkflowMethod,
            (ob, method_id, func, args, kw), {})
    # If only interaction workflows are defined, we need to call the method
    # manually
    if only_interaction_defined:
      result = apply(func, args, kw)
    # Call notifySuccess on each workflow
    for w in wfs:
      w.notifySuccess(ob, method_id, result, args=args, kw=kw)
    return result
    
WorkflowTool.wrapWorkflowMethod = WorkflowTool_wrapWorkflowMethod

def DCWorkflowDefinition_notifyBefore(self, ob, action, args=None, kw=None):
    '''
    Notifies this workflow of an action before it happens,
    allowing veto by exception.  Unless an exception is thrown, either
    a notifySuccess() or notifyException() can be expected later on.
    The action usually corresponds to a method name.
    '''
    pass

def DCWorkflowDefinition_notifySuccess(self, ob, action, result, args=None, kw=None):
    '''
    Notifies this workflow that an action has taken place.
    '''
    pass

DCWorkflowDefinition.notifyBefore = DCWorkflowDefinition_notifyBefore
DCWorkflowDefinition.notifySuccess = DCWorkflowDefinition_notifySuccess
