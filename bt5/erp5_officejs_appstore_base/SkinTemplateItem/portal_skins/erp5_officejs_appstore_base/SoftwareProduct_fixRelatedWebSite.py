portal = context.getPortalObject()

web_site = context.getFollowUpValue(portal_type="Web Site")

# Create Web Site if necessary
if not web_site:
  # XXX Hardcoded templ
  web_site = portal.web_site_module.officejs_app_template.Base_createCloneDocument(batch_mode=True)
  web_site.edit(
    title=context.getTitle(),
    short_title=context.getTitle(),
    id=context.getReference().lower(),
  )
  context.setFollowUpValue(web_site)

# This is dangerous
if not web_site.getId() == context.getReference().lower():
  web_site.setId(context.getReference().lower())


# Update version on development document
# XX Do we need version???
document_list = portal.portal_catalog(
  portal_type= portal.getPortalDocumentTypeList(),
  validation_state="draft",
  strict_follow_up_uid=context.getUid(),
)

# XX Doesn't seem to be unique enough
version = context.getReference()[:6] + "-dev"
for document_brain in document_list:
  document = document_brain.getObject()
  document.setVersion(version)


development_section = web_site["development"]
# Update development section to use version and follow_up
development_section.setCriterionPropertyList([
  "version",
  "validation_state",
])
development_section.setCriterion('version', version)
development_section.setCriterion('validation_state', 'draft')
development_section.setMembershipCriterionBaseCategoryList(['follow_up'])
development_section.setMembershipCriterionCategoryList(['follow_up/' + context.getRelativeUrl()])


# Update default page for development version.
landing_publication_uid = portal.portal_categories.publication_section.application.landing_page.getUid()
aggregate_list = portal.portal_catalog(
  portal_type="Web Page",
  strict_follow_up_uid=context.getUid(),
  strict_publication_section_uid=landing_publication_uid,
  validation_state="draft",
  #XXX Hackish
  sort_on=[("modification_date", "descending")],
  limit=1,
  select_list=["relative_url"],
)
if aggregate_list:
  development_section.setAggregate(aggregate_list[0].relative_url)

development_section.setTitle(context.getTitle() + " Development")
development_section.setShortTitle(context.getShortTitle())
development_section.setDescription(context.getDescription())

return web_site
