## Script (Python) "Base_doModule"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=module_select, form_id=''
##title=
##
import string

Base_doAction = module_select.split()
doAction0 = Base_doAction[0]
doAction0 += '/view'
request = context.REQUEST

return request.RESPONSE.redirect(doAction0)
