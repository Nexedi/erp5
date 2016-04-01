portal = context.getPortalObject()

web_site = context.getFollowUpValue(portal_type="Web Site")

# Create Web Site if necessary
if not web_site:
  # XXX Hardcoded templ
  web_site = portal.web_site_module.officejs_app_template.Base_createCloneDocument(batch_mode=True)
  web_site.edit(
    title=context.getTitle(),
    short_title=context.getTitle(),
  )
  context.setFollowUpValue(web_site)

development_section = web_site["development"]
if not development_section.getAggregate():
  aggregate_list = portal.portal_catalog(
    portal_type="Web Page",
    strict_follow_up_uid=context.getUid(),
    strict_publication_section_uid=portal.portal_categories.publication_section.application.landing_page.getUid(),
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
# XXX Should fix default page for development version.
