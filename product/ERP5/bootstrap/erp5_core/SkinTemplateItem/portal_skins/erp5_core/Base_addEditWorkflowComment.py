"""Adds an entry in edit workflow history with given comment.
"""
assert REQUEST is None and not container.REQUEST.args
context.getPortalObject().portal_workflow.doActionFor(
    context,
    'edit_action',
    comment=comment
)
