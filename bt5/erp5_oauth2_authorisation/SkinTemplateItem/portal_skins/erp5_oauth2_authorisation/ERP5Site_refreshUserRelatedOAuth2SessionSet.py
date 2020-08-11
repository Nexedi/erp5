"""
Call  on all valid OAuth2 Session document related to any of given user documents.
"""
# Proxy roles: Manager, to be allowed to view and modify all OAuth2 Sessions.
from collections import defaultdict
portal_type_dict = defaultdict(set)
for user_value in user_value_list:
  portal_type_dict[user_value.getPortalType()].add(user_value)
user_value_set = set()
portal = context.getPortalObject()
portal_types = portal.portal_types
for portal_type, document_value_set in portal_type_dict.iteritems():
  # Ignore non-user documents
  if 'ERP5User' in getattr(
    getattr(
      portal_types,
      portal_type,
      None,
    ),
    'getTypePropertySheetList',
    lambda: (),
  )():
    user_value_set.update(document_value_set)
if user_value_set:
  for oauth2_session_value in portal.portal_catalog(
    portal_type='OAuth2 Session',
    validation_state='validated',
    strict__source_section__uid=[
      x.getUid()
      for x in user_value_set
    ],
  ):
    oauth2_session_value.refreshAccessToken()
