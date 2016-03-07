"""Compatibility script for old portal type Base_printPdf actions.
"""
from Products.ERP5Type.Log import log
portal = context.getPortalObject()
log('Deprecated Base_printPdf action called on a %s. '
    'Remove this action to use global print action.' % context.getPortalType())

portal.changeSkin('Print')
return getattr(context, form_id)()
