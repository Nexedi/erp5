## Script (Python) "doLanguage"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=language_select
##title=
##

from Products.ERP5Type.Cache import clearCache

# XXX Localizer-dependent
portal = context.getPortalObject()
portal.Localizer.changeLanguage(language_select)

# XXX should invalidate cached data specific to current user
clearCache()
