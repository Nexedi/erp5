## Script (Python) "PieceTissu_printMetoLabel"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.Coramy.MetoAPI import selectMeter, startFormat, setDecoration, setPrintSpeed, setPaperSpeed, setPixel, setTemparature, setNumber, endFormat, printText, printLine, printFrame

raw_string = ''
item = context
printer_name = 'Meto_XS40'

try :
  item_id = item.getResourceValue().getTitle()
  title_items = item.getColoris().split('/')
  if len(title_items) > 0 :
    item_title = title_items[len(title_items)-1][0:min(len(title_items[len(title_items)-1]),12)]
  else :
    item_title = ''
except :
  item_id = ' '
  item_title = ' '
item_code = item.getId()
item_code = '0'*(6-len(item_code))+item_code

# Printing protocol starts here
# first set some parameters
raw_string += selectMeter()
#raw_string += setDecoration(1)
raw_string += startFormat()
raw_string += setPrintSpeed()
raw_string += setPaperSpeed()
raw_string += setPixel()
raw_string += setTemparature()

# then design the label
raw_string += printText(1, "9", 1, 1, 4, 10, 20, item_id, 10)
raw_string += printText(1, "9", 1, 1, 3, 2, 14, item_title, 10)
raw_string += printText(1, "d", 8, 2, 80, 4, 5, item_code, 10)
raw_string += printText(4, "d", 8, 2, 80, 36, 5, item_code, 10)
raw_string += printText(1, "9", 1, 1, 3, 7, 1, item_code, 10)
raw_string += printText(4, "9", 1, 1, 3, 40, 9, item_code, 10)

# set the quentity to print
raw_string += setNumber()
raw_string += endFormat()

# send data to printer
context.sendRawToCups(printer_name, raw_string)
