"""
  Get the reference list of all validated business configuration related to the logged user.
"""
from Products.ERP5Type.Log import log

portal = context.getPortalObject()
reference = portal.portal_membership.getAuthenticatedMember().getId()
kw = {'reference': reference}

# XXX: This try except is used in case of connection refused
# and to make sure that the user interface will never be broken.
try:
  return context.portal_wizard.callRemoteProxyMethod(
                     'WitchTool_getBusinessConfigurationReferenceList',
                     use_cache=1,
                     ignore_exceptions=0,
                     **kw)
except:
  log('Base_getUserRemoteBusinessConfigurationReferenceList: '
      'Could not retrieve the Business Configuration reference list.', level=100)
  return []
