"""List all dead proxy fields
"""
portal_skin = context.REQUEST.get('portal_skin', 'View')

print("<html>")
for field_path, field in context.ZopeFind(
            context.portal_skins, obj_metatypes=['ProxyField'], search_sub=1):
  if field.getTemplateField() is None:
    print('<a href="%s/%s/manage_main?portal_skin=%s">%s</a><br />' % (context.absolute_url(), field_path, portal_skin, field_path))

print("</html>")
return printed
