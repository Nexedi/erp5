## Script (Python) "PT_reset_total_list"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=totalizer, index_list=[0]
##title=
##
# used in page templates to reset some total_sums
# uses a list named 'totalizer' which contains sums

for i in index_list :
  try :
    totalizer[i] = 0
  except :
    pass
