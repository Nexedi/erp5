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
This script is aimed to generate the coordinates and the properties necessary to
display correctly the PlaningBox in HTML style (i.e using HTML code + CSS class
for positionning). The process is based on the strucutre passed in parameter (i.e
'structure').
Beware this only generates a dict based structure, and need to be passed through
the CSS script ('planning_css') to have CSS compliant code, no HTML generation is
done in this script.

This script is also used by the validator script in order to recover the
groups of moved blocks
"""


# the following values are hard-defined and can be modified if necessary to comply with
# special constraints (big fonts for example)

# caracter height
car_height = 10
# caracter width
car_width = 6
# space to insert between each depth
depth_width = 10
# the same over the vertical axis
depth_height = 10

size_planning_width = basic.field.get_value('size_planning_width')
size_x_axis_height = basic.field.get_value('size_x_axis_height')
size_x_axis_space = basic.field.get_value('size_x_axis_space')
size_border_width_left = basic.field.get_value('size_border_width_left')
size_header_height = basic.field.get_value('size_header_height')
size_planning_height = basic.field.get_value('size_planning_height')
size_y_axis_width = basic.field.get_value('size_y_axis_width')
size_y_axis_space = basic.field.get_value('size_y_axis_space')
y_axis_position = basic.field.get_value('y_axis_position')
x_axis_position = basic.field.get_value('x_axis_position')


properties_structure = {
  'base': {},
  'frame': {},
  'report_axis': {},
  'lane_axis': {},
  'line': {},
  'content': {},
  'info': {},
}


# getting number of elements to display on the main axis
if planning.report_axis.size != basic.report_axis_info['bound_axis_groups']:
  # number of groups to display over the main axis is different from the expected
  # value : updating planning size to fit exactly the number of groups
  if planning.report_axis == planning.Y:
    # updating Y axis
    report_axis_step = float(size_planning_height) / float(basic.report_axis_info['bound_axis_groups'])
    size_planning_height = report_axis_step * planning.report_axis.size
  else:
    report_axis_step = float(size_planning_width) / float(basic.report_axis_info['bound_axis_groups'])
    size_planning_width = report_axis_step * planning.report_axis.size
else:
  if planning.report_axis == planning.Y:
    report_axis_step = float(size_planning_height) / float(basic.report_axis_info['bound_axis_groups'])
  else:
    report_axis_step = float(size_planning_width) / float(basic.report_axis_info['bound_axis_groups'])

# defining planning area CSS class
# XXX it can be moved to globals
planning_dict = {
  'position': 'relative',
  'border-style': 'solid',
  'border-color':  'inherit',
  'border-width': 0,
  'background': 'inherit',
  'width': size_planning_width + size_border_width_left + size_y_axis_width + size_y_axis_space + 20,
  'height': size_header_height + size_x_axis_height + size_x_axis_space + size_planning_height + 100,
  'margin-top': 0,
  'margin-left': 0,
}

properties_structure['base']['planning_box']  = planning_dict




# recovering axis CSS class information
for axis in (planning.Y, planning.X):
  axis_depth = None
  axis_dict= {
    'position': 'absolute',
    'border-style': 'solid',
    'border-color': 'inherit',
    'border-width': 0,
    'background': 'inherit',
  }
  # adding cursors position information
  axis_previous = {
    'position': 'absolute',
    'border-width': 0,
  }
  axis_next = {
    'position': 'absolute',
    'border-width': 0,
  }
  if axis == planning.X:
    # current axis is X axis
    # positionning it
    axis_dict['width'] = size_planning_width
    axis_dict['height'] = size_x_axis_height
    if not x_axis_position:
      axis_dict['margin-top'] = size_header_height
    else:
      axis_dict['margin-top'] = size_header_height + size_planning_height + size_x_axis_space
    if y_axis_position:
      axis_dict['margin-left'] = size_border_width_left
    else:
      axis_dict['margin-left'] = size_border_width_left + size_y_axis_width + size_y_axis_space

    axis_previous['margin-left'] = -20
    axis_previous['margin-top'] = (axis_dict['height'] - 15) // 2
    axis_next['margin-left'] = axis_dict['width'] + 5
    axis_next['margin-top'] = axis_previous['margin-top']

    if axis == planning.report_axis:
      # current axis is main axis : need to implement depth widget
      axis_depth = {
        'margin-left': -10,
        'margin-top': 0,
        'border-width': 0,
        'position': 'absolute',
      }
      # updating axis previous values
      axis_previous['margin-left'] = axis_previous['margin-left'] - 10
  else:
    # current axis is Y axis
    # positionning it
    axis_dict['width'] = size_y_axis_width
    axis_dict['height'] = size_planning_height
    if not x_axis_position:
      axis_dict['margin-top'] = size_header_height + size_x_axis_height + size_x_axis_space
    else:
      axis_dict['margin-top'] = size_header_height
    if y_axis_position:
      axis_dict['margin-left'] = size_border_width_left + size_planning_width + size_y_axis_space
    else:
      axis_dict['margin-left'] = size_border_width_left


    axis_previous['margin-left'] = (axis_dict['width'] -15) // 2
    axis_previous['margin-top'] = -20
    axis_next['margin-left'] = axis_previous['margin-left']
    axis_next['margin-top'] = axis_dict['height'] + 5
    if axis == planning.report_axis:
      axis_depth = {
        'margin-left': 0,
        'bottom': '100%',
        'border-width': 0,
        'position': 'absolute',
      }
      # updating axis previous values
      axis_previous['margin-top'] = axis_previous['margin-top'] - 10
  # adding axis_definitions to dictionnary
  properties_structure['frame'][axis.name] = axis_dict
  properties_structure['frame'][axis.name + '_previous'] = axis_previous
  properties_structure['frame'][axis.name + '_next'] = axis_next
  if axis_depth != None:
    properties_structure['frame'][axis.name + '_depth'] = axis_depth


# now processing groups over the main axis, including their info object
# at the same time generating line to separate each group
for axis_group in planning.report_axis.axis_group:
  axis_group_dict={
    'position': 'absolute',
    'border-style': 'solid',
    'border-width': 1,
  }
  #axis_group_dict['background'] = '#d5e6de'
  if axis_group.property_dict['stat'] == 1 :
    axis_group_dict['background'] = '#ddefe7'
  # info definition
  axis_info_dict= {}
  #axis_info_dict['position'] = 'absolute'
  #axis_info_dict['border-style'] = 'solid'
  #axis_info_dict['border-color'] = '#53676e'
  #axis_info_dict['border-width'] = 0
  # group line separator definition
  axis_line_dict = {
    'position': 'absolute',
    'border-style': 'solid',
    'border-width': 0,
  }
  if planning.report_axis == planning.X:
    # current axis is X axis
    axis_group_dict['width'] = float(axis_group.axis_element_number) * report_axis_step
    axis_group_dict['margin-left'] = float( axis_group.axis_element_start -1) * report_axis_step
    axis_group_dict['height'] = size_x_axis_height - axis_group.depth * depth_height
    axis_group_dict['margin-top'] = axis_group.depth * depth_height
    axis_info_dict['margin-top'] = axis_group.depth * depth_height
    axis_info_dict['margin-left'] = 1
    # dotted line must be vertical
    if axis_group.depth == 0 :
      #current group is main group : line must be bold
      axis_line_dict['border-left-width'] = 3
    else:
      axis_line_dict['border-left-width'] = 1
    #axis_line_dict['border-top-width'] = 0
    axis_line_dict['height'] = size_planning_height
    #axis_line_dict['width'] = 0
    axis_line_dict['margin-left'] = axis_group_dict['margin-left']
    #axis_line_dict['margin-top'] = 0

    # processing depth
    for depth in range(axis_group.depth):
      axis_depth_dict = {
        'position': 'absolute',
        'border_style': 'solid',
        'border-color': '#53676e',
        'border-width': 1,
        'background': '#53676e',
        'margin-top': depth * depth_height,
        'margin-left': axis_group_dict['margin-left'],
        'width': axis_group_dict['width'],
        'height': depth_height,
      }

      # adding current depth line info to properties structure
      properties_structure['info'][axis_group.name + '_depth_' + str(depth)] = axis_depth_dict


    # updating info size
    if axis_group_dict['height'] - axis_info_dict['margin-top'] < car_height:
      # block height is too low to be able to display any text
      # removing block title but keeping tooltip
      axis_group.info_title.edit('')
    else:
      # height matches info
      if len(axis_group.info_title.info) * car_width > axis_group_dict['width']:
        # defining number of caracts to leave
        nb = max((axis_group_dict['width'] - car_width * 3) // car_width, 0 )
        # cutting activity
        axis_group.info_title.edit(axis_group.info_title.info[:int(nb)] + '..')


    if axis_group.axis_element_number > 1:
      # subgroups are present
      for axis_element_number in range(axis_group.axis_element_number)[1:]:
        # iterating each subgroup except the first one
        # for each of them, building a new line over the axis as a delimiter
        axis_element_dict = {
          'position': 'absolute',
          'border-right-width': 0,
          'border-bottom-width': 0,
          'border-left-width': 1,
          'border-top-width': 0,
          'border-style': 'dotted',
          'width': 0,
          'height': size_planning_height,
          'margin-left': axis_group_dict['margin-left'] + axis_element_number * report_axis_step,
          'margin-top': 0,
        }

        # adding current sub line info to properties_structure
        properties_structure['line'][axis_group.name + '_line_' + str(axis_element_number)] = axis_element_dict

  else:
    # current axis is Y axis
    axis_group_dict['margin-left'] = axis_group.depth * depth_width
    axis_group_dict['width'] = size_y_axis_width - axis_group.depth * depth_width
    axis_group_dict['margin-top'] = float( axis_group.axis_element_start - 1) * report_axis_step
    axis_group_dict['height'] = float(axis_group.axis_element_number) * report_axis_step
    #axis_group_dict['text-align'] = 'center'
    #axis_group_dict['vertical-align'] = 'middle'

    # positionning info object in the middle of the axisGroup
    #axis_info_dict['margin-top'] = ((float(axis_group_dict['height']) - car_height ) / 2.0)
    #axis_info_dict['margin-top'] = -12
    #axis_info_dict['margin-left'] = axis_group.depth * depth_width + depth_width / 2
    #axis_info_dict['margin-left']='auto'
    #axis_info_dict['margin-right']='auto'
    #axis_info_dict['margin-top']='auto'
    #axis_info_dict['margin-bottom']='auto'

    # main line must be horizontal
    if axis_group.depth == 0:
      axis_line_dict['border-top-width'] = 2
    else:
      axis_line_dict['border-top-width'] = 1
    #axis_line_dict['border-left-width'] = 0
    axis_line_dict['width'] = size_planning_width
    #axis_line_dict['height'] = 0
    #axis_line_dict['margin-left'] = 0
    axis_line_dict['margin-top'] = axis_group_dict['margin-top']


    # processing depth
    for depth in range(axis_group.depth):
      axis_depth_dict = {
        'position': 'absolute',
        'border_style': 'solid',
        'border-color': '#53676e',
        'border-width': 1,
        'background': '#53676e',
        'margin-top': axis_group_dict['margin-top'],
        'margin-left': depth * depth_width,
        'width': depth_width,
        'height': axis_group_dict['height'],
      }

      # adding current depth line info to properties structure
      properties_structure['info'][axis_group.name + '_depth_' + str(depth)] = axis_depth_dict



    # updating info size
    if axis_group_dict['height'] < car_height:
      # block height is too low to be able to display any text
      # removing block title but keeping tooltip
      axis_group.info_title.edit('')
    else:
      # height matches info
      if len(axis_group.info_title.info) * car_width > axis_group_dict['width']:
        # defining number of caracts to leave
        nb = max((axis_group_dict['width'] - car_width * 3) // car_width, 0 )
        # cutting activity
        axis_group.info_title.edit(axis_group.info_title.info[:int(nb)] + '..')



    if axis_group.axis_element_number > 1:
      # subgroup are present
      for axis_element_number in range(axis_group.axis_element_number)[1:]:
        # iterating each subgroup except the first one
        # for each of them, building a new line over the axis as a delimiter
        axis_element_dict = {
          'position': 'absolute',
          'border-right-width': 0,
          'border-bottom-width': 0,
          'border-left-width': 0,
          'border-top-width': 1,
          'border-style': 'dotted',
          'width': size_planning_width,
          'height': 0,
          'margin-left': 0,
          'margin-top': axis_group_dict['margin-top'] + axis_element_number * report_axis_step,
        }

        # adding current sub line info to properties_structure
        properties_structure['line'][axis_group.name + '_line_' + str(axis_element_number)] = axis_element_dict


  # adding axis_definitions to dictionnary
  properties_structure['report_axis'][axis_group.name] = axis_group_dict
  properties_structure['line'][axis_group.name + '_line'] = axis_line_dict
  #properties_structure['info'][axis_group.name + '_info'] = axis_info_dict



# processing lane_axis_group
for lane_axis_group in planning.lane_axis.axis_group:
  lane_axis_group_dict={
    'position': 'absolute',
    'border-color': 'inherit',
    'border-style': 'solid',
    'border-width': 1,
    'background': 'inherit',
  }
  # info definition
  lane_axis_info_dict= {
    'position': 'absolute',
  }
  #lane_axis_info_dict['border-style'] = 'solid'
  #lane_axis_info_dict['border-color'] = '#53676e'
  #lane_axis_info_dict['border-width'] = 0
  # line definition
  lane_axis_line_dict = {
    'position': 'absolute',
  }
  if lane_axis_group.delimiter_type == 0:
    lane_axis_line_dict['border-style'] = 'dotted'
  else:
    lane_axis_line_dict['border-style'] = 'solid'
  lane_axis_line_dict['border-right-width'] = 0
  lane_axis_line_dict['border-bottom-width'] = 0
  if planning.report_axis == planning.Y:
    # current axis is X axis
    lane_axis_group_dict['width'] = lane_axis_group.position_lane.absolute_range * size_planning_width
    lane_axis_group_dict['margin-left'] = lane_axis_group.position_lane.absolute_begin * size_planning_width
    lane_axis_group_dict['height'] = size_x_axis_height
    lane_axis_group_dict['margin-top'] = lane_axis_group.depth
    lane_axis_info_dict['margin-top'] = 1
    lane_axis_info_dict['margin-left'] = 1
    # dotted line must be vertical
    if lane_axis_group.delimiter_type == 2:
      lane_axis_line_dict['border-left-width'] = 2
    else:
      lane_axis_line_dict['border-left-width'] = 1
    lane_axis_line_dict['border-top-width'] = 0
    lane_axis_line_dict['height'] = size_planning_height
    lane_axis_line_dict['width'] = 0
    lane_axis_line_dict['margin-left'] = lane_axis_group_dict['margin-left']
    lane_axis_line_dict['margin-top'] = 0

    # updating info size
    if lane_axis_group_dict['height'] - lane_axis_info_dict['margin-top'] < car_height:
      # block height is too low to be able to display any text
      # removing block title but keeping tooltip
      lane_axis_group.info_title.edit('')
    else:
      # height matches info
      if len(lane_axis_group.info_title.info) * car_width > lane_axis_group_dict['width']:
        # defining number of caracts to leave
        nb = max((lane_axis_group_dict['width'] - car_width * 3) // car_width, 0 )
        # cutting activity
        lane_axis_group.info_title.edit(lane_axis_group.info_title.info[:int(nb)] + '..')
    # adding axis_definitions to dictionnary
    properties_structure['lane_axis'][lane_axis_group.name] = lane_axis_group_dict
    properties_structure['line'][lane_axis_group.name + '_line'] = lane_axis_line_dict
    #properties_structure['info'][lane_axis_group.name + '_info'] = lane_axis_info_dict

  else:
    # current axis is Y axis
    lane_axis_group_dict['margin-left'] = lane_axis_group.depth
    lane_axis_group_dict['width'] = size_y_axis_width
    lane_axis_group_dict['margin-top'] =  lane_axis_group.position_lane.absolute_begin * size_planning_height
    lane_axis_group_dict['height'] = lane_axis_group.position_lane.absolute_range * size_planning_height
    # positionning info object in the middle of the axisGroup
    lane_axis_info_dict['margin-top'] = ((float(axis_group_dict['height']) - car_height ) / 2.0)
    lane_axis_info_dict['margin-top'] = 0
    lane_axis_info_dict['margin-left'] = 1
    # dotted line must be horizontal
    lane_axis_line_dict['border-left-width'] = 0
    if lane_axis_group.delimiter_type == 2:
      lane_axis_line_dict['border-top-width'] = 2
    else:
      lane_axis_line_dict['border-top-width'] = 1
    lane_axis_line_dict['width'] = size_planning_width
    lane_axis_line_dict['height'] = 0
    lane_axis_line_dict['margin-left'] = 0
    lane_axis_line_dict['margin-top'] = lane_axis_group_dict['margin-top']


    # updating info size
    if lane_axis_group_dict['height'] < car_height:
      # block height is too low to be able to display any text
      # removing block title but keeping tooltip
      lane_axis_group.info_title.edit('')
    else:
      # height matches info
      if len(lane_axis_group.info_title.info) * car_width > lane_axis_group_dict['width']:
        # defining number of caracts to leave
        nb = max((lane_axis_group_dict['width'] - car_width * 3) // car_width, 0 )
        # cutting activity
        lane_axis_group.info_title.edit(lane_axis_group.info_title.info[:int(nb)] + '..')

    # adding axis_definitions to dictionnary
    properties_structure['lane_axis'][lane_axis_group.name] = lane_axis_group_dict
    properties_structure['line'][lane_axis_group.name + '_line'] = lane_axis_line_dict
    #properties_structure['info'][lane_axis_group.name + '_info'] = lane_axis_info_dict


# defining CSS properties for content
content_dict={
  'position': 'absolute',
  'width': size_planning_width,
  'height': size_planning_height,
  'background': '#ffffff',
  'border-style': 'solid',
  'border-color': '#53676e',
  'border-width': 1,
}
if y_axis_position:
  content_dict['margin-left'] = size_border_width_left
else:
  content_dict['margin-left'] = size_border_width_left + size_y_axis_width + size_y_axis_space
if not x_axis_position:
  content_dict['margin-top'] = size_header_height + size_x_axis_height + size_x_axis_space
else:
  content_dict['margin-top'] = size_header_height
properties_structure['frame']['planning_content'] = content_dict



# processing blocks in the planning content
block_border_width = 1
for block_object in planning.content:
  block_dict = {
    'position': 'absolute',
    'border-style': 'solid',
    'border-color':  '#53676e',
    'border-width': block_border_width,
  }

  if block_object.error == 1:      # task has error (not validated)
    block_dict['background'] = '#e4c4da'
  elif block_object.warning == 1:  # other bloc in the same task has error
    block_dict['background'] = '#e9e3f0'
  elif block_object.property_dict['stat'] == 1:  # stat
    block_dict['background'] = '#97b0c1'
    block_dict['border-color'] = '#97b0c1'
  elif block_object.color != '':   # color specified
    block_dict['background'] = block_object.color
  else:                            # default color
    block_dict['background'] = '#bdd2e7'

  # XXX Define the frozen Blocs
  if context.PlanningBox_isFrozenBlock(block=block_object):
    block_dict['border-width'] = 0

  block_dict['height'] = block_object.position_y.relative_range * size_planning_height
  if block_object.parent_activity.height is not None:
    block_dict['height'] = block_dict['height']*block_object.parent_activity.height

  # the width - border width * 2 (left and right)
  # When you edit one object, border was added as a part of size. So 2*border-width pixels
  # was added every edition. 2 is because left and right.
  # the width - border-width * 2 (left and right)
  block_dict['width'] = (block_object.position_x.relative_range * size_planning_width) - \
                                                                           (2*block_border_width)
  #block_dict['height'] = block_object.position_y.relative_range * size_planning_height
  block_dict['margin-left'] = block_object.position_x.relative_begin * size_planning_width
  block_dict['margin-top'] = block_object.position_y.relative_begin * size_planning_height

  if block_object.parent_activity.property_dict['stat'] == 0:
    # the whole following process is aimed to take care of the non-stat blocks

    if planning.report_axis == planning.Y and block_object.parent_activity.property_dict['stat'] == 0:
      if block_object.parent_activity.object.getUid() not in basic.sec_layer_uid_list:
        # Y axis is main axis
        # adapt Y block size
        block_dict['height'] = block_dict['height'] - 10
        block_dict['margin-top'] = block_dict['margin-top'] + 5
    elif block_object.parent_activity.property_dict['stat'] == 0:
      # X axis is main axis
      # adapt X block size
      block_dict['width'] = block_dict['width'] - 10
      block_dict['margin-left'] = block_dict['margin-left'] + 5

    # for each block processing its info objects and placing them
    # testing if there is enough room horizontally to display the info,
    # first checking when 2 info on the same line (top or bottom)
    top_string = ''
    top_list = []
    bot_string = ''
    bot_list = []
    center = ''
    # recovering full string that will have to be displayed on the top & bottom line
    for info_name in block_object.info.keys():
      if 'top' in info_name:
        top_string += block_object.info[info_name].info
        top_list.append(info_name)
      if 'bot' in info_name:
        bot_string += block_object.info[info_name].info
        bot_list.append(info_name)
      if 'center' in info_name:
        center = info_name
    # checking if block length can fit them
    if (len(top_string) * car_width) > block_dict['width']:
      # block is too short, escaping top line
      for top_id in top_list:
        block_object.info[top_id].edit('.')
    if (len(bot_string) * car_width) > block_dict['width']:
      for bot_id in bot_list:
        block_object.info[bot_id].edit('.')
    # testing if need to update center info object (horizontal test)
    # as center info is automatically splitted into lines if necessary, need to check
    # the length of the biggest line.
    center_content_list = block_object.info[center].info.split(' ')
    center_length = 0
    for center_content_string in center_content_list:
      if center_length < len(center_content_string):
        center_length = len(center_content_string)
    # now center_length contains the maximum length of a line
    # applying test
    if center_length * car_width > block_dict['width']:
      # center length is too long, escaping it
      block_object.info[center].edit('__')

    # now testing vertical limit (..)
    # lines contains the nuber of 'lines' to display
    lines = 1 # center line is always present
    for list_object in (top_list,bot_list):
      if list_object is not (None,[]):
        lines += 1
    if block_dict['height'] < car_height:
      # there is no room to display any text in the block
      # escaping all text
      for info_name in block_object.info.keys():
        block_object.info[info_name].edit('')
    else:
      if block_dict['height'] < (car_height* lines):
      # there is not enought room to display all the text in the block
      # keeping only the most important : center
        for list_object in (top_list,bot_list):
          for info_name in list_object:
            block_object.info[info_name].edit('')
    # now processing standard testing and positionning
    # testing if the info can fit inside the block horizontally
    """
    for info_name in block_object.info.keys():
      block_info_dict = None
      block_info_dict = {}
      block_info_dict['position'] = 'absolute'
      if 'top' in info_name:
        #block_info_dict['margin-top'] = 0
        pass
      if 'bot' in info_name:
        #block_info_dict['margin-top'] = block_dict['height'] - car_height
        block_info_dict['margin-top'] = - car_height - 5
        block_info_dict['top'] = '100%'
      if 'left' in info_name:
        #block_info_dict['margin-left'] = 0
        pass
      if 'right' in info_name:
        #block_info_dict['margin-left'] = block_dict['width'] - (car_width * len(block_object.info[info_name].info))
        #block_info_dict['margin-right'] = 0
        block_info_dict['left'] = '100%'
        block_info_dict['margin-left'] = -(car_width * len(block_object.info[info_name].info))
      if 'center' in info_name:
        #block_info_dict['margin-left'] = (block_dict['width'] - (car_width * len(block_object.info[info_name].info)))/2
        block_info_dict['margin-left'] = - (car_width * len(block_object.info[info_name].info)) /2
        block_info_dict['left'] = '50%'
        #if block_info_dict['margin-left'] < 0:
        #  block_info_dict['margin-left'] = 0
        #block_info_dict['margin-left'] = block_info_dict['margin-left']
        block_info_dict['top'] = '50%'
        block_info_dict['margin-top'] = - car_height / 2
        #block_info_dict['margin-top'] = (block_dict['height'] - car_height)/2
      if 'error' in info_name:
        #block_info_dict['margin-left'] = 0
        block_info_dict['width'] = block_dict['width']
        block_info_dict['margin-top'] = block_dict['height']

      properties_structure['info'][block_object.name + '_' + info_name] = block_info_dict
    """


  properties_structure['content'][block_object.name] = block_dict

"""
planning_box_dict=None
planning_box_dict={}
planning_box_dict['position']='absolute'
planning_box_dict['width'] =
planning_box_dict['height'] =
properties_structure['base']['planning_box'] = planning_box_dict
"""
return properties_structure
