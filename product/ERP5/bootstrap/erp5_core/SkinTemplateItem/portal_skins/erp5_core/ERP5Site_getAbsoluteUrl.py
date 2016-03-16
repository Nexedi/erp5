"""This scripts return the public address of an ERP5 Site.
It should be used wherever you want to display a link to a page in the web
site (eg in automatic emails)
"""
return context.getPortalObject().absolute_url()
