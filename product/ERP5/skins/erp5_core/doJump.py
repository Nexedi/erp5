##parameters=jump_select, form_id=''

import string

doAction = jump_select.split()
doAction0 = doAction[0]
request = context.REQUEST

return request.RESPONSE.redirect(doAction0)
