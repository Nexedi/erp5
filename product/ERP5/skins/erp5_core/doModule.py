##parameters=module_select, form_id=''

import string

doAction = module_select.split()
doAction0 = doAction[0]
doAction0 += '/view'
request = context.REQUEST

return request.RESPONSE.redirect(doAction0)
