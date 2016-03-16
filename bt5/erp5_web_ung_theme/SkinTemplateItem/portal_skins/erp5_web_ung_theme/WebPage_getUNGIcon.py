portal_type = context.getPortalType()
icon_portal_type_dict = {"Web Table": "table.jpg", 
                         "Web Illustration": "svg.png",
                         "Web Page": "document.gif"}
return "<img src='ung_images/%s'/>" % icon_portal_type_dict.get(portal_type)
