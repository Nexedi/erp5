portal = context.getPortalObject()
if not relative_url:
  software_product = portal.software_product_module.newContent(
    portal_type="Software Product",
  )
else:
  software_product = portal.restrictedTraverse(relative_url)

edit_kw = {
  "product_line": product_line,
}
if title:
  edit_kw['title'] = title
else:
  title = software_product.getTitle()

if description:
  edit_kw['description'] = description
if activate_kw:
  edit_kw['activate_kw'] = activate_kw

context.log(edit_kw)
software_product.edit(**edit_kw)

software_product_url = software_product.getRelativeUrl()

software_publication = context

software_publication.edit(
  title=title + " " + software_publication.getTitle(),
  activate_kw=activate_kw
)

software_publication_line = software_publication.objectValues(
  portal_type="Software Publication Line",
)[0]

software_release = software_publication_line.getAggregateValue(portal_type="Software Release")

software_release.edit(
  title=title + " " + software_release.getTitle(),
  follow_up=software_product_url,
  activate_kw=activate_kw
)

software_publication_line.edit(
  resource=software_product_url,
  aggregate=[
    software_release.getRelativeUrl(),
    software_product.getSaleSupplyLineAggregate(),
  ],
  activate_kw=activate_kw
)

return software_publication.Base_redirect(
  "",
  keep_items={
    'portal_status_message': portal.Base_translateString("Your demand is being processed, please wait status to move to 'Submitted' to review your application before final submission")
  }
)
