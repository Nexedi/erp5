## Script (Python) "Container_printMetoLabel"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=printer_name=''
##title=
##
from Products.Coramy.MetoAPI import selectMeter, startFormat, setDecoration, setPrintSpeed, setPaperSpeed, setPixel, setTemparature, setNumber, endFormat, printText, printLine, printFrame, setAsdFont

raw_string = ''
container = context
"""
# selecting printer (user dependent)
local_user = container.portal_membership.getAuthenticatedMember().getUserName()
if local_user == 'Nicole_Denis' :
  printer_name = 'Meto_XS40_2'
elif local_user == 'Christelle_Megret' :
  printer_name = 'Meto_XS40_3'
elif local_user == 'Jocelyne_Olejarz' :
  printer_name = 'Meto_XS40_4'
elif local_user == 'Nathalie_Wadoux' :
  printer_name = 'Meto_XS40_5'
elif local_user == 'Joelle_Gorriez':
  printer_name = 'Meto_XS40_6'
elif local_user == 'Chantal_Hannequin' :
  printer_name = 'Meto_XS40_5'
elif local_user == 'Gaelle_Manier' :
  printer_name = 'Meto_XS40_6'
else :
  printer_name = 'Meto_XS40_2'
"""
delivery = container.aq_parent
client_title = delivery.getDestinationValue(portal_type=['Organisation']).getTitle()
client_address_items = delivery.getDestinationValue(portal_type=['Organisation']).getDefaultAddress().asText(country='France').split('\n')
client_address_1 = client_address_items[0]
if len(client_address_items) > 2 :
  client_address_2 = client_address_items[1]
else :
  client_address_2 = ''
client_city = client_address_items[len(client_address_items)-1]

# Printing protocol starts here
# first set some parameters
raw_string += selectMeter()
raw_string += setAsdFont()
#raw_string += setDecoration(1)
raw_string += startFormat()
raw_string += setPrintSpeed()
raw_string += setPaperSpeed()
raw_string += setTemparature()

# then design the label
raw_string += printLine(1, 3, 138, 100, 10, 10)
raw_string += printText(1, "9", 0, 0, 2, 8, 139, 'Expediteur', 10)
raw_string += printText(1, "9", 0, 0, 3, 52, 138, 'Destinataire', 10)
raw_string += printFrame(1, 3, 3, 100, 145, 2, 2, 10)
raw_string += printLine(1, 41, 3, 0.5, 145, 10)
raw_string += printLine(1, 11, 3, 0.2, 135, 10)

raw_string += printText(2, "9", 0, 0, 2, 31, 131, 'Coramy', 10)
raw_string += printText(2, "9", 0, 0, 1, 24, 131, '5 bis, rue Denis Cordonnier', 10)
raw_string += printText(2, "9", 0, 0, 1, 16, 131, '59820 GRAVELINES', 10)

raw_string += printText(2, "9", 0, 0, 2, 91, 131, client_title, 10)
raw_string += printText(2, "9", 0, 0, 2, 79, 131, client_address_1, 10)
raw_string += printText(2, "9", 0, 0, 2, 69, 131, client_address_2, 10)
raw_string += printText(2, "9", 0, 0, 3, 57, 131, client_city, 10)
raw_string += printText(2, "9", 0, 0, 3, 46, 131, '', 10)

raw_string += printText(2, "9", 0, 0, 1, 5, 131, delivery.getId(), 10)
raw_string += printText(2, "9", 0, 0, 1, 5, 86, str(container.getIntIndex()), 10)

if delivery.getDeliveryMode() != None:
  raw_string += printText(2, "9", 0, 0, 1, 5, 46, delivery.getDeliveryMode(), 10)

raw_string += printText(4, "d", 8, 2, 220, 37, 8, container.getSerialNumber(), 10)

# set the quentity to print
raw_string += setNumber()
raw_string += endFormat()

# send data to printer
context.sendRawToCups(printer_name, raw_string)
