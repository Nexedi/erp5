## Script (Python) "PackingList_setTargetStopToTargetStart"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
packing_list = context
packing_list.setTargetStopDate(packing_list.getTargetStartDate())
