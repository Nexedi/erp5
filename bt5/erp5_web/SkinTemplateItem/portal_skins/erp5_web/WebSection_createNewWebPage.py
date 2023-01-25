request = context.REQUEST
request_form = request.form
from ZTUtils import make_query
portal = context.getPortalObject()
title = context.getTitle('Unknown')
translateString = context.Base_translateString
web_page_module = context.web_page_module

# Find the applicable language
language = portal.Localizer.get_selected_language()

# Create a new empty page
web_page = web_page_module.newContent(portal_type = 'Web Page',
                                      title="New Page of Section %s" % title,
                                      version="1", language=language)


# Copy categories into new Web Page
category_list = context.getMembershipCriterionCategoryList()
web_page.setCategoryList(web_page.getCategoryList() + category_list)


# Return the new page in the section context
keep_items = dict(editable_mode=1,
              portal_status_message=translateString("New Web Page of section ${web_section}.",
              mapping = dict(web_section=title)))

request_form.update(keep_items)
message = make_query(dict([(k, v) for k, v in request_form.items() if k and v is not None]))

redirect_url = '%s/%s/view?%s' % (
            context.absolute_url(), web_page.getRelativeUrl(),message)

# return to the new page in the section context
return context.REQUEST.RESPONSE.redirect(redirect_url)
