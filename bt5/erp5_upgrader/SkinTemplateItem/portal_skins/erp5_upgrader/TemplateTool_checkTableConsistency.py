"""
Check for some table consistency according to the create table list.
If `fixit` is True, then it will create/drop table or alter existing tables
"""
portal = context.getPortalObject()
show_source = not(fixit)
output = portal.portal_catalog.upgradeSchema(src__=show_source)
if fixit:
  for line in output:
    if "ALTER TABLE `measure`" in line and "ADD COLUMN `variation_text_line_1`" in line:
      output += ["reindexing resources for new variation_text_line_* structure"]
      portal.portal_catalog.searchAndActivate(
        portal_type=portal.getPortalResourceTypeList(),
        method_id='recursiveReindexObject')
return output
