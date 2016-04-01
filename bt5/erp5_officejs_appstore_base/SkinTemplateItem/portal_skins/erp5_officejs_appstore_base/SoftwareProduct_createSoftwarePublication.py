portal = context.getPortalObject()
person = context.ERP5Site_getAuthenticatedMemberPersonValue()

# Generate Version Number
# XXX Should Check that version of this software doesn't already exists
import hashlib
version = hashlib.sha224("%s-%s-%s" % (context.getReference(), version_title, DateTime())).hexdigest()[:10]


# Create Software Publication
# It carries the software publication process
software_publication = portal.software_publication_module.newContent(
  portal_type="Software Publication",
  description=description,
  source=person.getRelativeUrl(),
  # We should probably use a more simple reference using an incremental id generator
  reference="SP-" + context.getReference() + "-" + version,
  title=context.getTitle() + ' release ' + version_title,
)

# Create Software Release
# This is the result of the publication process. It is an aggregate of the line
software_release = portal.software_release_module.newContent(
  portal_type="Software Release",
  reference=context.getReference() + "-" + version,
  title=context.getTitle() + ' release ' + version_title + '-' + version,
  # XXX the follow_up lkink is actually nonsense and redundant
  follow_up=context.getRelativeUrl(),
  version=version_title,
)

# Create Software Publication Line
software_publication_line = software_publication.newContent(
  portal_type="Software Publication Line",
  title=software_publication.getTitle() + " Publication",
  resource=context.getRelativeUrl(),
  aggregate=[
    software_release.getRelativeUrl(),
    context.getSaleSupplyLineAggregate(),
  ]
)

# Create Web Section And Web Section Predicate
# The predicate look for version and validation_state=submitted
web_site = context.SoftwareProduct_fixRelatedWebSite()

section = web_site['development'].Base_createCloneDocument(batch_mode=True)
section.edit(
  title="%s %s" % (context.getTitle(), version_title),
  short_title=context.getTitle(),
  description=context.getDescription(),
  id=version_title,
)

membership_criterion_category_list = ['follow_up/' + software_release.getRelativeUrl()]
def webSectionUpdatePredicate(current_section):
  current_section.setCriterionPropertyList([
      'version',
      'validation_state',
    ])
  
  current_section.setCriterion('version', version)
  current_section.setCriterion('validation_state', 'submitted')
  current_section.setMembershipCriterionCategoryList(membership_criterion_category_list)
  for child_section in current_section.objectValues(portal_type="Web Section"):
    webSectionUpdatePredicate(child_section)

webSectionUpdatePredicate(section)

# Clone all curent Web Document and share them with the correct Version
web_document_list = portal.portal_catalog(
  portal_type=portal.getPortalDocumentTypeList(),
  strict_follow_up_uid=context.getUid(),
  validation_state="draft",
  # XXX This is hackish
  sort_on=[("modification_date", "descending")],
)

# We clone all related Web Document, set the correct version and submit them
for web_document in web_document_list:
  released_web_document = web_document.Base_createCloneDocument(batch_mode=True)
  released_web_document.setVersion(version)
  released_web_document.setFollowUpValue(software_release)
  released_web_document.submit()
  if released_web_document.getPublicationSection() == "application/landing_page":
    section.setAggregate(released_web_document.getRelativeUrl())


# For now everything is submitted on creation, maybe it should be done by the developer
software_release.submit()
software_publication.submit()

return software_publication.Base_redirect(
  '',
  keep_items={
    'portal_status_message': context.Base_translateString("Software Publication Request Created"),
  },
)
