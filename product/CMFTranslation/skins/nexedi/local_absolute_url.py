## Script (Python) "local_absolute_url"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=lang=None,target=None
##title=
##

if lang is None: lang = context.gettext.get_selected_language()
relative_url = context.portal_url.getRelativeUrl(context)

return '%s/%s/%s' % (context.portal_url.getPortalObject().absolute_url(), lang,
                     relative_url)
