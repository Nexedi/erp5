## Script (Python) "local_absolute_url"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=lang=None,affiliate_path=None,target=None
##title=
##

if lang is None: lang = context.gettext.get_selected_language()

if target is None:
  relative_url = context.portal_url.getRelativeUrl(context)
else:
  relative_url = context.portal_url.getRelativeUrl(target)

try:
  if affiliate_path is None:
    affiliate_path = context.AFFILIATE_PATH
except:
  affiliate_path = ''

return '%s/%s/%s%s' % (context.portal_url.getPortalObject().absolute_url(), lang,
                     affiliate_path, relative_url)

