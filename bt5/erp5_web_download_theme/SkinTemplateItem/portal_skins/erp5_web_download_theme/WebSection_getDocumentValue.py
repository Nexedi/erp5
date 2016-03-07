if portal is None: portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

# Find the applicable portal type
valid_portal_type_list = portal.getPortalDocumentTypeList()

# Find the applicable state
if validation_state is None:
  validation_state = ('released', 'released_alive', 'published', 'published_alive',
                      'shared', 'shared_alive', 'public', 'validated')

#set kw dict for all search
kw['portal_type'] = valid_portal_type_list
kw['validation_state'] = validation_state

# packages are without language, and can look like:
#   package.name.with._dots.and.underscore-0.1.0dev-r1980.tar.gz
# where:
#  package.name.with._dots.and.underscore -- name
#  0.1.0dev-r1980 -- version
#  tar.gz -- extension
# or like:
#   package-name-with-dots-and-minus-some-version.extension.uuk
# or even:
#   package_name-with-minus-version-with_minus.extension.ops
# or even:
#   package_like-this.and-version_like-this.extension.ex2
# or even:
#   package-like_och-version.1.2-dev3_Q.ext.ext
# some repositories (like pypi) are assuming case insensitive packages
# other (tarballs) are case sensitive
reference, extension_part = name.split('-', 1)
#Remove extension from last part only
if '.tar.' in extension_part:
  name_list = extension_part.rsplit('.', 2)
  version = name_list[0]
  extension = '.'.join(name_list[1:])
else:
  version, extension = extension_part.rsplit('.', 1)

kw.update(
  reference=reference,
  version=version
)
document_list = portal_catalog(limit=1, **kw)
if len(document_list) == 1:
  return document_list[0].getObject()
return None
