## Script (Python) "Base_doJump"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=jump_select, form_id=''
##title=
##
import string

Base_doAction = jump_select.split()
doAction0 = Base_doAction[0]
request = context.REQUEST

return request.RESPONSE.redirect(doAction0)
