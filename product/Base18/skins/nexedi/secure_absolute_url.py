## Script (Python) "secure_absolute_url"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=lang=None,target=None
##title=
##

if target is None: target = context
if lang is None: lang = context.gettext.get_selected_language()
relative_url = context.portal_url.getRelativeUrl(target)

return '%s/%s/%s' % (context.secure_url, lang,
                     relative_url)
