portal = state_change.getPortal()

# invalidate the cache for security
portal.portal_caches.clearCache(cache_factory_list=('erp5_content_short',))

# Using PAS removes the need of anything else in this script
if portal.acl_users.meta_type == 'Pluggable Auth Service':
  return

# Get the assignment object and its parent
assignment_object = state_change['object']
person_object     = assignment_object.getParentValue()

# Call the script if available
person_security_script = getattr(person_object, 'Person_updateUserSecurityGroup', None)

if person_security_script is not None:
  person_security_script()
