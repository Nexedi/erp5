portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

#web section title and url id in production
#hardcoded as this is completely arbitrary
app_list_dict = {
                 'Text Editor' : 'texteditor', #osp-3
                 'Jabber Client' : 'jabberclient', #osp-14
                 'Bookmark Manager' : 'bookmark', #osp-10
                 'Illustration Editor' : 'svgeditor', #osp-9
                 'Slide Editor' : 'slide', #osp-42
                 'OnlyOffice Spreadsheet' : 'spreadsheet', #osp-7
                 'OnlyOffice Text' : 'text', #osp-6
                 'Onlyoffice Presentation' : 'presentation', #osp-8
                 'Mynij Search' : 'mynij', #osp-46
                 'OfficeJS Javascript Editor' : 'codemirror', #osp-34
                 'Notebook' : 'iodide-notebook', #osp-29
                 'Image Editor' : 'imageeditor', #osp-11
                 'OfficeJs HR' : 'hr', #osp-27
                 'Valentin Smart Assistant Publication' : 'smartassistant', #osp-28
                 'Web Table' : 'webtable', #osp-12
                 'PDF Viewer' : 'pdfreader', #osp-5
                 'OfficeJS Monitor' : 'monitor', #osp-22
                 'Roque Test App' : 'roqueapp' #for dev instance REMOVE
}

app_list_web_site = portal.web_site_module['application-list']
app_web_section_dict = {x.getId(): x for x in app_list_web_site.objectValues(portal_type="Web Section")}

for software_product in portal_catalog(portal_type="Software Product"):
  if software_product.getReference().lower() in app_web_section_dict:
    print "software product has app!"
    web_site = software_product.getFollowUpValue(portal_type="Web Section")
    app_url_prefix = app_list_dict[web_site.getTitle()]
    software_product.setReference(app_url_prefix)
    #use update script instead?
    web_site.setId(app_url_prefix)
    software_product.setFollowUpValue(web_site)

return printed
