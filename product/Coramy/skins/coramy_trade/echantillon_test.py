## Script (Python) "echantillon_test"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
#lines_list = context.echantillon_modeliste_sql_worklist()
new_list = map((lambda x:x.getObject()),context.echantillon_modeliste_sql_worklist())
for item in new_list:
 if item == None:
  print 'erreur'

return printed
