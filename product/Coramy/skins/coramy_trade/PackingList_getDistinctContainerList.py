## Script (Python) "PackingList_getDistinctContainerList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# this method return a list of distinct containers
# it returns a sorted list of tuples (object container, range)
# the range is a tuple (first number of this container, last number of this container)

delivery = context

container_list = delivery.contentValues(filter={'portal_type' : 'Container'})

ordered_container_list = context.sort_object_list(unordered_list=container_list, sort_order = (('int_index', 'ASC'),) )

final_container_list = []
if len(container_list) > 0 :
  container_ref = container_list[0].getContainerText()
  container_object = container_list[0]
  first_container = 1
  last_container = 1
else :
  container_ref = ''
  container_object = None
  first_container = 0
  last_container = 0

for container in ordered_container_list :
  if container.getContainerText() != container_ref :
    # append tuple in final_container_list
    final_container_list.append((container_object,(first_container,last_container)))
    # reset variables
    container_object = container
    first_container = container.getIntIndex()
    container_ref = container.getContainerText()
  last_container = container.getIntIndex()

# append final container in final_container_list 
final_container_list.append((container_object,(first_container,last_container)))

return final_container_list
