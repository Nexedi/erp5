## Script (Python) "doLanguage"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=language_select, form_id=''
##title=
##

context.Localizer.changeLanguage(language_select)
request = context.REQUEST

return request.RESPONSE.redirect(context.absolute_url())
