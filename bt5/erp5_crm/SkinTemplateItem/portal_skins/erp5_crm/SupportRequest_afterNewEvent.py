"""Add a note to increase modification date of support request.

This script has proxy roles, so that even users who cannot modify
the support request can still increase the modification date this way.
"""
from Products.ERP5Type.Message import translateString

context.getPortalObject().portal_workflow.doActionFor(
  context,
  'edit_action',
  comment=translateString(
    "New event ${event_reference}",
    mapping={
      'event_reference': event.getReference()}))
