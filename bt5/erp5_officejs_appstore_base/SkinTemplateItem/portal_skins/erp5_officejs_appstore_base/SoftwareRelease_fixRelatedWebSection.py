portal = context.getPortalObject()

software_release = context
software_product = software_release.getFollowUpValue(portal_type="Software Product")

web_site = software_product.SoftwareProduct_fixRelatedWebSite(batch_mode=True)

version = software_release.getReference()
context.log(version)
context.log("%s" % web_site.getRelativeUrl())
try:
  web_section = web_site.restrictedTraverse(version)
except KeyError:
  clipboard = web_site.getParentValue().manage_copyObjects(ids=['template_static'])
  context.REQUEST.set('__cp', clipboard) # CopySupport is using this to set
                           # tracebility information in edit_workflow history
  paste_result = web_site.manage_pasteObjects(cb_copy_data=clipboard)
  web_section = web_site[paste_result[0]['new_id']]
  web_section.edit(
    id=version,
    title=software_release.getVersion(),
    configuration_base_reference=version + "/",
  )

# Update development section to use version and follow_up
web_section.setCriterionPropertyList([
  "version",
])

web_section.setCriterion('version', version[:10])
web_section.setMembershipCriterionBaseCategoryList(['follow_up'])
web_section.setMembershipCriterionCategoryList(['follow_up/' + context.getRelativeUrl()])

if not default_page:
  # Update default page for development version.
  landing_publication_uid = portal.portal_categories.publication_section.application.landing_page.getUid()
  aggregate_list = portal.portal_catalog(
    portal_type="File",
    strict_follow_up_uid=context.getUid(),
    strict_publication_section_uid=landing_publication_uid,
    #XXX Hackish
    sort_on=[("modification_date", "descending")],
    limit=1,
    select_list=["relative_url"],
  )
  if aggregate_list:
    web_section.setAggregate(aggregate_list[0].relative_url)
else:
  web_section.setAggregate(default_page)
if web_manifest is not None:
  web_section.setProperty('configuration_webapp_manifest_url', web_manifest)

web_site.edit(
  configuration_latest_version=software_release.getReference()
)

return "Done"
