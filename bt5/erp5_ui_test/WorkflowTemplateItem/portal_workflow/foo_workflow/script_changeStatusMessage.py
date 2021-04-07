"""
This will be used for Selenium test, set a particular message
to portal_status_message variable
"""


document = state_change['object']
request = document.REQUEST

from Products.ERP5Type.Message import translateString

request.set('portal_status_message', translateString('Status Message Changed.'))
