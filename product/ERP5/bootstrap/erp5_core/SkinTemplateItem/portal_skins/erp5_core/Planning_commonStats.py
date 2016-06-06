<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="PythonScript" module="Products.PythonScripts.PythonScript"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>Script_magic</string> </key>
            <value> <int>3</int> </value>
        </item>
        <item>
            <key> <string>_bind_names</string> </key>
            <value>
              <object>
                <klass>
                  <global name="NameAssignments" module="Shared.DC.Scripts.Bindings"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>_asgns</string> </key>
                        <value>
                          <dictionary>
                            <item>
                                <key> <string>name_container</string> </key>
                                <value> <string>container</string> </value>
                            </item>
                            <item>
                                <key> <string>name_context</string> </key>
                                <value> <string>context</string> </value>
                            </item>
                            <item>
                                <key> <string>name_m_self</string> </key>
                                <value> <string>script</string> </value>
                            </item>
                            <item>
                                <key> <string>name_subpath</string> </key>
                                <value> <string>traverse_subpath</string> </value>
                            </item>
                          </dictionary>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>_body</string> </key>
            <value> <string encoding="cdata"><![CDATA[

"""\n
XXX temporary function to recover statistics when needed\n
=> will be put in an external script.\n
recover a list with temporary objects we want to apply stats on.\n
(can be object itself, list of direct sons, list of all sons using\n
recursive method, etc.)\n
Then take this special list of objects and return a list of special\n
temp_objects to display as blocks \'as they are\'\n
"""\n
from Products.ERP5Type.Log import log\n
from Products.ERP5Type.Document import newTempMovement as newTempBase\n
from string import zfill\n
\n
# first recovering methods to apply on tasks\n
start_property_id = field.get_value(\'x_start_bloc\')\n
stop_property_id= field.get_value(\'x_stop_bloc\')\n
size_property_id = field.get_value(\'y_size_block\')\n
\n
\n
\n
###########################################################\n
########### CREATING LIST OF TEMP STAT OBJECTS ############\n
###########################################################\n
# find a way to get all related objects with their sub-objects\n
# this list of objects must be stored in a list\n
# for now considering applying statistics on object_list\n
# XXX bug : can not apply getExceptionUidList() method on object_tree_line.\n
# <<unauthorized access>>\n
#selection.edit(exception_uid_list= object_tree_line.getExceptionUidList())\n
input_object_list = selection(method = list_method,context= selection_context,\n
                                  REQUEST=REQUEST)\n
\n
temp_object_list = []\n
temp_object_id = 0\n
# now applying statictic rule.\n
# for now statistic rules are static\n
\n
\n
for input_object in input_object_list:\n
  # recovering input_object attributes\n
  block_begin = input_object.getObject().getProperty(start_property_id,None)\n
  block_end = input_object.getObject().getProperty(stop_property_id,None)\n
  block_size = input_object.getObject().getProperty(size_property_id,None)\n
  if block_begin != None and block_end != None:\n
    # do not create stat on non completed objects.\n
    # prevent bug while size property is not defined on the object\n
    if block_size == None: block_size = block_end - block_begin\n
    #updating block_size value\n
    block_size = float(block_size) / (block_end - block_begin)\n
    # creating new object\n
    temp_object = newTempBase(context.getPortalObject(),id=str(temp_object_id), uid =\'new_%s\' % zfill(temp_object_id, 4) )\n
    # editing object with new values\n
    log("%s" % (",".join([start_property_id, str(block_begin),stop_property_id, str(block_end),size_property_id, str(block_size)])))\n
    temp_object.setProperty(start_property_id, block_begin)\n
    temp_object.setProperty(stop_property_id, block_end)\n
    temp_object.setProperty(size_property_id, block_size)\n
    # adding new object to list\n
    temp_object_list.append(temp_object)\n
    temp_object_id += 1\n
\n
###########################################################\n
################ BUILDING STATS ACTIVITES #################\n
###########################################################\n
\n
# building a special list structure.\n
prop_list = []\n
for temp_stat in temp_object_list:\n
  block_begin = temp_stat.getProperty(start_property_id)\n
  block_end   = temp_stat.getProperty(stop_property_id)\n
  block_size  = temp_stat.getProperty(size_property_id)\n
\n
  prop_list.append([block_begin, float(block_size)])\n
  prop_list.append([block_end  ,-(float(block_size))])\n
\n
\n
# now sorting list to put start & stop in the right order\n
prop_list.sort()\n
# now building new list of temp object with updated properties\n
size = 0\n
temp_stat_object_list = []\n
for index in range(len(prop_list) - 1):\n
  # iterating all prop_list elements except the last one\n
  current_prop = prop_list[index]\n
  size += current_prop[1] # new size is relative to the previous size\n
  start = current_prop[0] # current start\n
  stop = prop_list[index+1][0] # current stop is the begining of the next block\n
  temp_stat_object_id = 0\n
\n
  if size > 0:\n
    # size is not null\n
    # building new tempObject\n
    temp_stat_object_id += 1\n
    temp_stat_object = newTempBase(context.getPortalObject(),str(temp_stat_object_id), uid =\'new_%s\' % zfill(temp_stat_object_id, 4))\n
    # editing object with new values\n
    temp_stat_object.setProperty(start_property_id, start)\n
    temp_stat_object.setProperty(stop_property_id, stop)\n
    temp_stat_object.setProperty(size_property_id, size)\n
    # adding new object to list\n
    temp_stat_object_list.append(temp_stat_object)\n
    temp_stat_object_id +=1\n
\n
return temp_stat_object_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>selection=None,list_method=None, selection_context=None, report_tree_list = None, object_tree_line=None, REQUEST=None, field=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Planning_commonStats</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
