## Script (Python) "PT_update_total_list"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=totalizer, index_list=[0], value=0
##title=
##
# used in page templates to make sums
# uses a list named 'totalizer' which contains sums

for i in index_list :
  try :
    totalizer[i] = totalizer[i] + value 
  except :
    pass
