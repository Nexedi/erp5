## Script (Python) "Container_printLabel"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# print container label
container = context

if container.aq_parent.getDeliveryMode() == 'Transporteur/Extand' :
  container.Container_printExtandLabel()
else :
  container.Container_printMetoLabel()
