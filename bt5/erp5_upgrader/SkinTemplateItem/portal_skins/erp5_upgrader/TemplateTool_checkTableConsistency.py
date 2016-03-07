"""
Check for some table consistency according to the create table list.
If `fixit` is True, then it will create/drop table or alter existing tables
"""
portal = context.getPortalObject()
show_source = not(fixit)
return portal.portal_catalog.upgradeSchema(src__=show_source)
