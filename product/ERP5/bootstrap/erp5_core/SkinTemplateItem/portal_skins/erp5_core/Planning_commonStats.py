"""
XXX temporary function to recover statistics when needed
=> will be put in an external script.
recover a list with temporary objects we want to apply stats on.
(can be object itself, list of direct sons, list of all sons using
recursive method, etc.)
Then take this special list of objects and return a list of special
temp_objects to display as blocks 'as they are'
"""
from Products.ERP5Type.Log import log
from Products.ERP5Type.Document import newTempMovement as newTempBase
from string import zfill

# first recovering methods to apply on tasks
start_property_id = field.get_value('x_start_bloc')
stop_property_id= field.get_value('x_stop_bloc')
size_property_id = field.get_value('y_size_block')



###########################################################
########### CREATING LIST OF TEMP STAT OBJECTS ############
###########################################################
# find a way to get all related objects with their sub-objects
# this list of objects must be stored in a list
# for now considering applying statistics on object_list
# XXX bug : can not apply getExceptionUidList() method on object_tree_line.
# <<unauthorized access>>
#selection.edit(exception_uid_list= object_tree_line.getExceptionUidList())
input_object_list = selection(method = list_method,context= selection_context,
                                  REQUEST=REQUEST)

temp_object_list = []
temp_object_id = 0
# now applying statictic rule.
# for now statistic rules are static


for input_object in input_object_list:
  # recovering input_object attributes
  block_begin = input_object.getObject().getProperty(start_property_id,None)
  block_end = input_object.getObject().getProperty(stop_property_id,None)
  block_size = input_object.getObject().getProperty(size_property_id,None)
  if block_begin != None and block_end != None:
    # do not create stat on non completed objects.
    # prevent bug while size property is not defined on the object
    if block_size == None: block_size = block_end - block_begin
    #updating block_size value
    block_size = float(block_size) / (block_end - block_begin)
    # creating new object
    temp_object = newTempBase(context.getPortalObject(),id=str(temp_object_id), uid ='new_%s' % zfill(temp_object_id, 4) )
    # editing object with new values
    log("%s" % (",".join([start_property_id, str(block_begin),stop_property_id, str(block_end),size_property_id, str(block_size)])))
    temp_object.setProperty(start_property_id, block_begin)
    temp_object.setProperty(stop_property_id, block_end)
    temp_object.setProperty(size_property_id, block_size)
    # adding new object to list
    temp_object_list.append(temp_object)
    temp_object_id += 1

###########################################################
################ BUILDING STATS ACTIVITES #################
###########################################################

# building a special list structure.
prop_list = []
for temp_stat in temp_object_list:
  block_begin = temp_stat.getProperty(start_property_id)
  block_end   = temp_stat.getProperty(stop_property_id)
  block_size  = temp_stat.getProperty(size_property_id)

  prop_list.append([block_begin, float(block_size)])
  prop_list.append([block_end  ,-(float(block_size))])


# now sorting list to put start & stop in the right order
prop_list.sort()
# now building new list of temp object with updated properties
size = 0
temp_stat_object_list = []
for index in range(len(prop_list) - 1):
  # iterating all prop_list elements except the last one
  current_prop = prop_list[index]
  size += current_prop[1] # new size is relative to the previous size
  start = current_prop[0] # current start
  stop = prop_list[index+1][0] # current stop is the begining of the next block
  temp_stat_object_id = 0

  if size > 0:
    # size is not null
    # building new tempObject
    temp_stat_object_id += 1
    temp_stat_object = newTempBase(context.getPortalObject(),str(temp_stat_object_id), uid ='new_%s' % zfill(temp_stat_object_id, 4))
    # editing object with new values
    temp_stat_object.setProperty(start_property_id, start)
    temp_stat_object.setProperty(stop_property_id, stop)
    temp_stat_object.setProperty(size_property_id, size)
    # adding new object to list
    temp_stat_object_list.append(temp_stat_object)
    temp_stat_object_id +=1

return temp_stat_object_list
