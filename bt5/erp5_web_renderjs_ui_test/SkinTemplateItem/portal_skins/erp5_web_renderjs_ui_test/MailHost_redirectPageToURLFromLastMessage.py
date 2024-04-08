import re
from Products.ERP5Type.Utils import bytes2str
last_message_text = bytes2str(context.getMessageList()[-1][2])
__traceback_info__ = last_message_text

return container.REQUEST.RESPONSE.redirect(re.findall(r"http.*", last_message_text)[0])
