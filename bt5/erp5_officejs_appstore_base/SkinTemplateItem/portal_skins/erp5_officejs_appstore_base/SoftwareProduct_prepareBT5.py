portal = context.getPortalObject()

# First make sure the site is in the correct state
website = context.SoftwareProduct_fixRelatedWebSite()
software_product = context

# Should make a script for that
if software_product.getId() != software_product.getReference().lower():
  software_product.setId(context.getReference().lower())

base_id = "%s-" % (context.getId())

# Start with the document list
path_list = []
document_list = portal.portal_catalog(
  portal_type= portal.getPortalDocumentTypeList(),
  validation_state="draft",
  strict_follow_up_uid=context.getUid(),
  select_list=('relative_url', ),
)

for brain in document_list:
  document = brain.getObject()
  # Update ID is necessary
  if not document.getId() == base_id + document.getReference().replace('.', '_'):
    document.setId(base_id + document.getReference().replace('.', '_'))
  path_list.append(document.getRelativeUrl())

# Append the software product
path_list.append(context.getRelativeUrl())

# Add the website development section (Really????)
path_list.append(website.getRelativeUrl())
path_list.append(website['development'].getRelativeUrl())
path_list.append(website['development'].getRelativeUrl() +  "/**")

if business_template_path:
  bt5 = portal.restrictedTraverse(business_template_path)
else:
  bt5 = portal.portal_templates.newContent(
    portal_type="Business Template",
    title='officejs-' + context.getReference().lower() + '-export',
  )

bt5.edit(
  template_path_list=path_list,
  template_keep_last_workflow_history_only_path_list=path_list,
  version=DateTime().HTML4(),
  )

return bt5.Base_redirect(
  '',
  keeps_items={
    'portal_status_message': portal.Base_translateString("Portal Template updated")
  }
)
