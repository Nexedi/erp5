## Script (Python) "manage_after_clone"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
print " "

o = context.getObject()

context.manage_afterClone(o)

print "manage_afterClone() Done"

return printed
