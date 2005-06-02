## Script (Python) "Base_doModule"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=module_select=None, form_id=''
##title=
##
if not module_select : return
import string

Base_doAction = module_select.split()
doAction0 = Base_doAction[0]
doAction0 += '/view'
request = context.REQUEST

return request.RESPONSE.redirect(doAction0)
