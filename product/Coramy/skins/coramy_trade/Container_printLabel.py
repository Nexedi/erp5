## Script (Python) "Container_printLabel"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=user_name=None
##title=
##
# get the name of the printer
printer_name = context.Coramy_userLabelPrinterDefinition(user_name=user_name)

# print container label
container = context

if container.aq_parent.getDeliveryMode() == 'Transporteur/Extand' :
  container.Container_printExtandLabel(printer_name=printer_name)
else :
  container.Container_printMetoLabel(printer_name=printer_name)
