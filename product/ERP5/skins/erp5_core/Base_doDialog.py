## Script (Python) "Base_doDialog"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=dialog_select, form_id, dialog_category, selection_name, cancel_url
##title=
##
import string

Base_doAction = dialog_select.split()
doAction0 = Base_doAction[0]
request = context.REQUEST

return request.RESPONSE.redirect(doAction0 + '?selection_name=%s&dialog_category=%s&cancel_url=%s&form_id=%s' %
          (selection_name, dialog_category, cancel_url, form_id) )
