## Script (Python) "change_language"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST
##title=Modify the language cookie
##
lang = REQUEST['lang']

path = context.absolute_url()[len(REQUEST['SERVER_URL']):] or '/'
REQUEST.RESPONSE.setCookie('LOCALIZER_LANGUAGE', lang, path=path)

REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])
