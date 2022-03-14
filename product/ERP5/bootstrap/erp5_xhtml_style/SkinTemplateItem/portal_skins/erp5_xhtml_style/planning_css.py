"""
Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
            Thomas Bernard   <thomas@nexedi.com>

This program is Free Software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
"""

"""
This script is aimed to generate the CSS code needed to display correctly the
PlanningBox in HTML style (i.e using HTML code + CSS class for positionning).
The process is based on the strucutre passed in parameter (i.e 'structure').

Beware this only generates CSS code, and need to use the 'planning_coordinates'
script ('planning_css') to have CSS compliant code, no HTML generation is
done in this script.
"""
properties_structure = context.planning_coordinates(basic, planning)
"""
- the properties_structure returned from the planning_coordinates script is somehow
special : it is a dict defined by the areas of data
- then each area is itself a dict defined by the name of the object (axis, group, block, etc.)
- finally the objects holds a dict with all the proprieties
"""


# udating properties if necessary.
# This process is only usefull when displaying a planning that failed to
# validate. In such a case the block properties are updated to match their
# last position.
block_string = basic.REQUEST.get('previous_block_moved','')
if block_string != '':
  # block_list is not empty, need to recover porperties and update the blocks
  # that need to be refreshed
  block_object_list = block_string.split('*')
  for block_object_string in block_object_list:
    block_dict = None
    block_dict = {}
    block_sub_list = block_object_string.split(',')
    block_dict['name'] = block_sub_list[0]
    block_dict['old_X'] = float(block_sub_list[1])
    block_dict['old_Y'] = float(block_sub_list[2])
    block_dict['new_X'] = float(block_sub_list[3])
    block_dict['new_Y'] = float(block_sub_list[4])
    block_dict['width'] = float(block_sub_list[5])
    block_dict['height'] = float(block_sub_list[6])
    # recovering corresponding block coordinates object in properties_structure
    block_properties = properties_structure['content'][block_dict['name']]
    # list of dict of blocks has been recovered
    # need to find deltaX and deltaY
    deltaX = block_dict['old_X'] - block_properties['margin-left']
    deltaY = block_dict['old_Y'] - block_properties['margin-top']
    # updating position
    block_properties['margin-left'] = block_dict['new_X'] - deltaX
    block_properties['margin-top'] = block_dict['new_Y'] - deltaY
    # updating size
    block_properties['width']  = block_dict['width']
    block_properties['height'] = block_dict['height']

else:
  # no unvalidated block, using actual properties
  pass

# build list from dictionnary structure
# this list will e converted to a string afterwards
returned_list = []
for area_name in list(properties_structure.keys()):
  css_dict = properties_structure[area_name]
  for class_name in list(css_dict.keys()):
    if class_name == 'planning_content':
      returned_list.append('.%s{' % class_name)
    elif class_name == 'planning_box':
      returned_list.append('.%s{' % class_name)
    else:
      returned_list.append('#%s{' % class_name)
    for id_ in list(css_dict[class_name].keys()):
      if same_type(css_dict[class_name][id_], ''):
        returned_list.append('%s:%s;\n' % (id_, css_dict[class_name][id_]))
      else:
        # if data is type float or integer then need to add 'px' at the end
        returned_list.append('%s:%s%s;\n' % (id_, int(css_dict[class_name][id_] + 0.5), 'px'))
    returned_list.append('}\n')
returned_list.append(" \
.planning_box_topleft{ position:absolute;left:0;top:0;} \n \
.planning_box_topright{position:absolute;right:0;top:0;} \n \
.planning_box_botleft{ position:absolute;bottom:0;left:0;} \n \
.planning_box_botright{position:absolute;right:0;bottom:0;} \n \
.planning_box_center{position:absolute; left:0; right:0; top:40%;}")


# now joining list to build the final CSS string
# and returning it
return "\n" + "".join(returned_list)
