"""
  Create a blog message for current Web Section.
  Try to guess as much as possible from current Web Section.
"""

portal = context.getPortalObject()
portal_type = 'Web Page'
module = portal.getDefaultModule(portal_type=portal_type)

# set predicate settings for current Web Section
membership_criterion_category_list = context.getMembershipCriterionCategoryList()

# generate nice reference from title
reference = context.Base_generateReferenceFromString(title)
existing_document = context.getDocumentValue(reference)
if existing_document is not None:
  # if there are other document which reference duplicates just add some random part
  # so we can distinguish)
  reference = '%s-%s' %(context.Base_generateRandomString(), reference)

article = module.newContent(portal_type=portal_type,
                  title=title,
                  version=version,
                  text_content=text_content,
                  subject_list=subject_list,
                  site_list=site_list,
                  reference=reference,
                  publication_section_list=publication_section_list,
                  language=language,
                  group_list=group_list,
                  function_list=function_list,
                  effective_date=effective_date,
                  classification=classification)
article.setCategoryList(membership_criterion_category_list)
article.submit("Automatic Submit")

portal_status_message = context.Base_translateString("New Blog Message created. It will be submitted for approval before it becomes visible.")
return context.Base_redirect('', keep_items = dict(portal_status_message=portal_status_message ))
