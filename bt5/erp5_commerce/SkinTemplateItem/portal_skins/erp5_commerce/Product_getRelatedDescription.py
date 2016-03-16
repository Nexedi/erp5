portal = context.getPortalObject()

#get cached description
# TODO

#get live description
web_page = portal.portal_catalog(portal_type='Web Page',
                                 default_follow_up_uid=context.getUid(),
                                 default_publication_section_uid=context.restrictedTraverse('portal_categories/publication_section/website/product/short_description').getUid(),
                                 #src__=1,
                                 )
if web_page is None or len(web_page) == 0:
  return context.Base_translateString("No more information for this product.")
return web_page[0].getObject().asStrippedHTML()
