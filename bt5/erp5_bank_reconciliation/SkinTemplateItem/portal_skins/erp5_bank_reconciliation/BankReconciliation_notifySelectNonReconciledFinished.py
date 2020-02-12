from Products.ERP5Type.Message import translateString
context.getPortalObject().portal_workflow.doActionFor(
  context, 'edit_action', comment=translateString('Select non reconciled transactions finished'))
