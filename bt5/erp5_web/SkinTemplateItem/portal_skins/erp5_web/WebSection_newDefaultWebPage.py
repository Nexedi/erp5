portal = context.getPortalObject()
title = context.getTitle('Unknown')
translateString = context.Base_translateString
web_page_module = portal.getDefaultModule('Web Page')

# Find the applicable language
language = portal.Localizer.get_selected_language()

# Create a new empty page
web_page = web_page_module.newContent(portal_type = 'Web Page',
                                      title="Default Page for Section %s" % title,
                                      reference="default-%s" % context.getId(),
                                      version="1", language=language)

# Create relation between section and page
context.setDefaultAggregateValue(web_page)

# Return the new page in the section context
return web_page.Base_redirect('view',
          keep_items = dict(editable_mode=1,
            portal_status_message = translateString("New default Web Page for section ${web_section}.",
          mapping = dict(web_section = title))))
