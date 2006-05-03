##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Tomas Bernard <thomas@nexedi.com>
#     from an original experimental script written by :
#                    Jonathan Loriette <john@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Companyf
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import pdb

import string, types, sys

# class monitoring access security control
from Products.PythonScripts.Utility import allow_class
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass


from Form import BasicForm
from Products.Formulator.Field import ZMIField
from Products.Formulator.DummyField import fields
from Products.Formulator.MethodField import BoundMethod
from DateTime import DateTime
#import DateUtils
from Products.Formulator import Widget, Validator
from Products.Formulator.Errors import FormValidationError, ValidationError
from SelectionTool import makeTreeList,TreeListLine
from Selection import Selection, DomainSelection
import OFS
from AccessControl import ClassSecurityInfo
from zLOG import LOG
from copy import copy
from Acquisition import aq_base, aq_inner, aq_parent, aq_self
from Products.Formulator.Form import BasicForm
from Products.CMFCore.utils import getToolByName

from Products.ERP5Type.Utils import getPath

class PlanningBoxValidator(Validator.StringBaseValidator):
  """
  Class holding all methods used to validate a modified PlanningBox
  can be called only from a HTML rendering using wz_dragdrop script
  """
  def validate(self,field,key,REQUEST):
    """
    main method to solve validation
    first rebuild the whole structure but do not display it
    then recover the list of block moved and check the modifications to
    apply
    """

    # init params
    value = None
    form = field.aq_parent
    here = getattr(form, 'aq_parent', REQUEST)

    # recover usefull properties
    #pdb.set_trace()
    block_moved_string = REQUEST.get('block_moved')
    old_delta1 = REQUEST.get('old_delta1')
    old_delta2 = REQUEST.get('old_delta2')

    

    ##################################################
    ############## REBUILD STRUCTURE #################
    ##################################################
    # build structure
    structure = PlanningBoxWidgetInstance.render_structure(field=field, key=key, value=value, REQUEST=REQUEST, here=here)

    # getting coordinates script generator
    planning_coordinates_method = getattr(here,'planning_coordinates')
    # calling script to generate coordinates
    planning_coordinates = planning_coordinates_method(structure=structure)

    ##################################################
    ########## RECOVERING BLOK MOVED DICT ############
    ##################################################
    #  converting string to a structure
    block_moved_list = []
    if block_moved_string != '':
      block_moved_object_list = block_moved_string.split('*')
      for block_moved_object_string in block_moved_object_list:
        block_moved_dict = None
        block_moved_dict = {}
        block_moved_sub_list = block_moved_object_string.split(',')
        block_moved_dict['name'] = block_moved_sub_list[0]
        block_moved_dict['old_X'] = float(block_moved_sub_list[1])
        block_moved_dict['old_Y'] = float(block_moved_sub_list[2])
        block_moved_dict['new_X'] = float(block_moved_sub_list[3])
        block_moved_dict['new_Y'] = float(block_moved_sub_list[4])
        block_moved_dict['width'] = float(block_moved_sub_list[5])
        block_moved_dict['height'] = float(block_moved_sub_list[6])
        block_moved_list.append(block_moved_dict)
    else:
      return ''
    # block_moved_list now holds a list of structure recovered from the REQUEST.

    # XXX once this works, call a special python script 'planning_validator' to process
    # the content instead of hardcoding it in the 'PlanningBox' script
    # for the moment, to have faster and easier debugging, leaving this part of
    # code in the main script


    # dict aimed to hold all informations about block
    final_block_dict = {}

    # dict holding all the activities that will need an update because at least one
    # of the blocks concerned is moved
    activity_dict = {}

    ##################################################
    ########## GETTING BLOCK INFORMATIONS ############
    ##################################################
    # iterating each block_moved element and recovering all usefull properties
    # BEWARE : no update is done here as an activity can be composed of several
    # blocks and so we need first to check all the blocks moved
    for block_moved in block_moved_list:
      final_block = {}
      # recovering the block object from block_moved informations
      final_block['block_object'] = self.getBlockObject(block_moved['name'], structure.planning.content)
      # recovering original activity object
      final_block['activity_origin'] = final_block['block_object'].parent_activity
      # recovering original axis_group object
      final_block['group_origin'] = final_block['activity_origin'].parent_axis_element.parent_axis_group
      # recovering relative block information in planning_coordinates
      final_block['block_info'] = planning_coordinates['content'][block_moved['name']]


      # calculating delta
      # block_moved holds coordinates recovered from drag&drop script, while
      # block_info has the relative coordinates.
      # In fact the Drag&Drop java script used to get destination coordinates
      # gives them in absolute. so using original block position to get the
      # relative position
      deltaX = block_moved['old_X'] - final_block['block_info']['margin-left']
      deltaY = block_moved['old_Y'] - final_block['block_info']['margin-top']

      # calculating new block position:
      # width and height are already in the good format
      block_moved['left'] = block_moved['new_X'] - deltaX
      block_moved['top']  = block_moved['new_Y'] - deltaY

      # abstracting axis representation (for generic processing)
      if structure.planning.render_format == 'YX':
        block_moved['main_axis_position']      = block_moved['top']
        block_moved['main_axis_length']        = block_moved['height']
        block_moved['secondary_axis_position'] = block_moved['left']
        block_moved['secondary_axis_length']   = block_moved['width']
        # used afterwards to get destination group
        group_position = 'margin-top'
        group_length = 'height'
        # used afterwards to get secondary axis displacements and modifications
        axis_length = 'width'

      else:
        block_moved['main_axis_position']      = block_moved['left']
        block_moved['main_axis_length']        = block_moved['width']
        block_moved['secondary_axis_position'] = block_moved['top']
        block_moved['secondary_axis_length']   = block_moved['height']
        group_position = 'margin-left'
        group_length = 'width'
        axis_length = 'height'

      # calculating center of block over main axis to check block position
      block_moved['center'] = (block_moved['main_axis_length'] / 2) + block_moved['main_axis_position']

      # now that block coordinates are recovered as well as planning coordinates
      # recovering destination group over the main axis to know if the block has
      # been moved from a group to another
      group_destination = self.getDestinationGroup(structure, block_moved,planning_coordinates['main_axis'], group_position, group_length)

      if group_destination == None:
        # XXX need to take care of such a case :
        # block has been moved outside the content area
        pass

      # now that all informations about the main axis changes are
      # known, checking modifications over the secondary axis.
      secondary_axis_positions = self.getDestinationBounds(structure, block_moved, final_block['block_object'], planning_coordinates, axis_length)
      block_moved['secondary_axis_start'] = secondary_axis_positions[0]
      block_moved['secondary_axis_stop'] = secondary_axis_positions[1]

      final_block['block_moved'] = block_moved
      final_block['group_destination'] = group_destination

      #final_block_dict[block_moved['name']] = final_block
      try:
        activity_dict[final_block['activity_origin'].name].append(final_block)
      except KeyError:
        activity_dict[final_block['activity_origin'].name] = [final_block]


    ##################################################
    ############# UPDATING ACTIVITIES ################
    ##################################################
    update_dict = {}
    # now processing activity updates
    for activity_name in activity_dict.keys():
      # recovering list of moved blocks in the current activity
      activity_block_moved_list = activity_dict[activity_name]
      # recovering activity object from first moved block
      activity_object = activity_block_moved_list[0]['activity_origin']

      # now getting list of blocks related to the activity (moved or not)
      activity_block_list = activity_object.block_list

      # recovering new activity bounds
      new_bounds = self.getActivityBounds(activity_object, activity_block_moved_list, activity_block_list)

      # XXX call specific external method to round value in case hh:mn:s are useless

      # saving updating informations in the final dict
      update_dict[activity_object.object.getUrl()]={'start_date':new_bounds[0],'stop_date':new_bounds[1]}

    # all process is now finished, just need to return final dict
    return update_dict




  def getBlockObject(self, block_name, content_list):
    """
    recover the block related to the block_name inside the content_list
    """
    for block in content_list:
      if block.name == block_name:
        return block



  def getDestinationGroup(self, structure, block_moved, axis_groups, group_position, group_length):
    """
    recover destination group from block coordinates and main axis coordinates
    block_moved is a dict of properties.
    returns the group object itself, none if the block has no good coordinates
    """
    good_group_name = ''
    # recovering group name
    for axis_name in axis_groups.keys():
      if  axis_groups[axis_name][group_position] < block_moved['center'] and axis_groups[axis_name][group_position] + axis_groups[axis_name][group_length] > block_moved['center']:
        # the center of the block is between group min and max bounds
        # the group we are searching for is known
        good_group_name = axis_name
        break
    # if no group is found, this means the block has been put outside the bounds
    if good_group_name == '':
      return None
    # group name is known, searching corresponding group object
    for group in structure.planning.main_axis.axis_group:
      if group.name == good_group_name:
        return group
    return None



  def getDestinationBounds(self, structure, block_moved, block_object, planning_coordinates, axis_length):
    """
    check the new bounds of the block over the secondary axis according to its
    new position
    """

    # XXX CALENDAR
    # has to be improved : for now the axis bounds are recovered globally, it
    # implies that all groups have the same bounds, which is not the case in
    # calendar mode. for that will need to add special informations about the
    # group itself to know its own bounds.
    delta_start = block_moved['secondary_axis_position'] / planning_coordinates['frame']['content'][axis_length]
    delta_stop  = (block_moved['secondary_axis_position'] + block_moved['secondary_axis_length']) / planning_coordinates['frame']['content'][axis_length]

    # testing different cases of invalidation
    if delta_stop < 0 or delta_start > 1 :
      # block if fully out of the bounds
      # XXX must generate a block_error
      pass
    else:
      if delta_start < 0 or delta_stop > 1:
        # part of the block is inside
        pass

    axis_range = structure.basic.secondary_axis_info['bound_stop'] - structure.basic.secondary_axis_info['bound_start']

    # defining new final block bounds
    new_start = delta_start * axis_range + structure.basic.secondary_axis_info['bound_start']
    new_stop  = delta_stop * axis_range + structure.basic.secondary_axis_info['bound_start']

    return [new_start,new_stop]



  def getActivityBounds(self, activity, activity_block_moved_list, activity_block_list):
    """
    takes a list with modified blocks and another one with original blocks,
    returning new startactivity_block_moved_list & stop for the activity
    BEWARE : in case an activity bound was cut off to fit planning size, the
    value will not be updated (as the block was not on the real activity bound)
    """
    # getting list moved block names
    block_moved_name_list = map(lambda x: x['block_moved']['name'], activity_block_moved_list)


    for activity_block in activity_block_list:
      if activity_block.name in block_moved_name_list:
        # the block composing the activity has been moved, not taking care of
        # the original one, but only the final position (block_moved)
        for temp_block_moved in activity_block_moved_list:
          # recovering corresponding moved block
          if temp_block_moved['block_moved']['name'] == activity_block.name:
            # moved block has been found
            temp_start = temp_block_moved['block_moved']['secondary_axis_start']
            temp_stop  = temp_block_moved['block_moved']['secondary_axis_stop']
            break
      else:
        # the block has not been moved
        temp_start = activity_block.position_secondary.absolute_begin
        temp_stop  = activity_block.position_secondary.absolute_end
      # once the start & stop values are recovered, need to test them to check
      # if it is needed to update
      try:
        if temp_start < new_start:
          new_start = temp_start
        if temp_stop > new_stop:
          new_stop = temp_stop
      except NameError:
        # new_start is not defined because it is the first block found
        new_start = temp_start
        new_stop = temp_stop

    # new start & stop values are known
    # checking weither activity has been cut-off to fit the planning bounds 
    if activity.secondary_axis_begin != activity.secondary_axis_start:
      new_start = activity.secondary_axis_begin
    if activity.secondary_axis_end != activity.secondary_axis_stop:
      new_stop  = activity.secondary_axis_end

    return [new_start,new_stop]


class PlanningBoxWidget(Widget.Widget):
  """
  PlanningBox main class used to run all the process in order to generate
  the structure of the Planning including all internal properties.
  Contains BasicStructure and PlanningStructure instances
  """



  property_names = Widget.Widget.property_names +\
  ['representation_type','main_axis_groups','size_header_height', 'size_border_width_left',
  'size_planning_width', 'size_y_axis_width','size_y_axis_space','size_planning_height','size_x_axis_height',
  'size_x_axis_space'
  ,'list_method','report_root_list','selection_name',
   'portal_types','sort','title_line','x_start_bloc','x_stop_bloc',
   'y_axis_method','constraint_method','color_script','info_center',
   'info_topleft','info_topright','info_backleft','info_backright',
   'security_index']

  # Planning properties (accessed through Zope Management Interface)


  # kind of representation to render :
  # Planning or Calendar
  representation_type = fields.TextAreaField('representation_type',
      title='representtion Type (YX or XY)',
      description='YX for horizontal or XY for vertical',
      default='YX',
      required=1)

  # added especially for new Planning Structure generation
  # is used to split result in pages in a ListBox like rendering
  # (delimitation over the main axis)
  main_axis_groups = fields.IntegerField('main_axis_groups',
      title='groups per page on main axis:',
      description=('number of groups displayed per page on main axis'),
      default=10,
      required=1)

  # setting header height
  size_header_height = fields.IntegerField('size_header_height',
      title='header height:',
      desciption=(
      'height of the planning header'),
      default=100,
      required=1)

  # setting left border size
  size_border_width_left = fields.IntegerField('size_border_width_left',
      title='Size border width left',
      desciption=(
      'setting left border size'),
      default=10,
      required=1)

  # setting the width of the Planning (excl. Y axis : only the block area)
  size_planning_width = fields.IntegerField('size_planning_width',
      title='Planning width:',
      desciption=(
      'size of the planning area, excluding axis size'),
      default=1000,
      required=1)

  # setting the with of the Y axis
  size_y_axis_width = fields.IntegerField('size_y_axis_width',
      title='Y axis width:',
      description=(
      'width of the Y axis'),
      default=200,
      required=1)

  # setting the with of the space (between Planning and Y axis)
  size_y_axis_space = fields.IntegerField('size_y_axis_space',
      title='Y axis space:',
      description=(
      'space between Y axis and PLanning content'),
      default=10,
      required=1)

  # setting the height of the Planning (excl. X axis)
  size_planning_height = fields.IntegerField('size_planning_height',
      title='Planning height:',
      description=(
      'size of the planning area, excluding axis_size'),
      default=800,
      required=1)

  # setting the height of the X axis
  size_x_axis_height = fields.IntegerField('size_x_axis_height',
      title='X axis height:',
      description=(
      'height of the X axis'),
      default=200,
      required=1)

  # setting the height of the space (between Planning and X axis)
  size_x_axis_space = fields.IntegerField('size_x_axis_space',
      title='X axis space:',
      description=(
      'space between X axis and PLaning content '),
      default=10,
      required=1)

  




  default = fields.TextAreaField('default',
      title='Default',
      description=(
      "Default value of the text in the widget."),
      default="",
      width=20, height=3,
      required=0)

  height_header = fields.IntegerField('height_header',
      title='height of the header (px):',
      description=(
      "value of the height of the header, required"),
      default=50,
      required=1)

  height_global_div = fields.IntegerField('height_global_div',
      title='height of the graphic (px):',
      description=(
      "value of the height of the graphic, required"),
      default=700,
      required=1)

  height_axis_x = fields.IntegerField('height_axis_x',
      title='height of X-axis (px):',
      description=(
      "value of the height of X-axis"),
      default=50,
      required=1)

  width_line = fields.IntegerField('width_line',
      title='width of the graphic (px):',
      description=(
      "value of width_line, required"),
      default=1000,
      required=1)

  space_line = fields.IntegerField('space_line',
      title='space between each line of the graphic (px):',
      description=("space between each line of the graphic,not required"),
      default=10,
      required=0)



  report_root_list = fields.ListTextAreaField('report_root_list',
      title="Report Root",
      description=("A list of domains which define the possible root."),
      default=[],
      required=0)



  selection_name = fields.StringField('selection_name',
      title='Selection Name',
      description=("The name of the selection to store selections params"),
      default='',
      required=0)

  portal_types = fields.ListTextAreaField('portal_types',
      title="Portal Types",
      description=("Portal Types of objects to list. Required."),
      default=[],
      required=0)

  sort = fields.ListTextAreaField('sort',
      title='Default Sort',
      description=("The default sort keys and order"),
      default=[],
      required=0)

  list_method = fields.MethodField('list_method',
      title='List Method',
      description=("Method to use to list objects"),
      default='',
      required=0)

  title_line = fields.StringField('title_line',
      title="specific method which fetches the title of each line: ",
      description=("specific method for inserting title in line"),
      default='',
      required=0)

  y_unity = fields.StringField('y_unity',
      title='Unity in Y-axis:',
      description=('The unity in Y-axis,not required'),
      default='',
      required=0)

  y_axis_width = fields.IntegerField('y_axis_width',
      title='width of Y-axis (px):',
      description=(
      "width of Y-axis, required"),
      default=200,
      required=1) 

  y_range = fields.IntegerField('y_range',
      title='number of range of Y-axis :',
      description=(
      "Number of Range of Y-axis, not required"),
      default=0,
      required=0) 

  x_range = fields.StringField('x_range',
      title='range of X-Axis:',
      description=('Nature of the subdivisions of X-Axes, not Required'),
      default='day',
      required=0)	

  x_axis_script_id = fields.StringField('x_axis_script_id',
      title='script for building the X-Axis:',
      description=('script for building the X-Axis'),
      default='',
      required=0)	

  x_start_bloc = fields.StringField('x_start_bloc',
      title='specific method which fetches the data for the beginning\
      of a block:',
      description=('Method for building X-Axis such as getstartDate\
      objects'),
      default='getStartDate',
      required=0)

  x_stop_bloc = fields.StringField('x_stop_bloc',
      title='specific method which fetches the data for the end of\
      each block',
      description=('Method for building X-Axis such getStopDate\
      objects'),
      default='getStopDate',
      required=0)	

  y_axis_method = fields.StringField('y_axis_method',
      title='specific method of data type for creating height of blocks',
      description=('Method for building height of blocks objects'),
      default='',
      required=0) 

  max_y  = fields.StringField('max_y',
      title='specific method of data type for creating Y-Axis',
      description=('Method for building Y-Axis objects'),
      default='',
      required=0)

  constraint_method = fields.StringField('constraint_method',
      title='name of constraint method between blocks',
      description=('Constraint method between blocks objects'),
      default='SET_DHTML',
      required=1)

  color_script = fields.StringField('color_script',
      title='name of script which allow to colorize blocks',
      description=('script for block colors object'),
      default='',
      required=0)

  info_center = fields.StringField('info_center',
      title='specific method of data called for inserting info in\
      block center',
      description=('Method for displaying info in the center of a\
      block object'),
      default='',
      required=0) 

  info_topright = fields.StringField('info_topright',
      title='specific method of data called for inserting info in\
      block topright',
      description=('Method for displaying info in the topright of a block\
      object'),
      default='',
      required=0)

  info_topleft = fields.StringField('info_topleft',
      title='specific method of data called for inserting info in\
      block topleft',
      description=('Method for displaying info in the topleft corner\
      of a block object'),
      default='',
      required=0)

  info_backleft = fields.StringField('info_backleft',
      title='specific method of data called for inserting info in\
      block backleft',
      description=('Method for displaying info in the backleft of a\
      block object'),
      default='',
      required=0)

  info_backright = fields.StringField('info_backright',
      title='specific method of data called for inserting info in\
      block backright',
      description=('Method for displaying info in the backright of a\
      block object'),
      default='',
      required=0)

  security_index = fields.IntegerField('security_index',
      title='variable depending on the type of web browser :',
      description=("This variable is used because the rounds of each\
      web browser seem to work differently"),
      default=2,
      required=0)



  def render_css(self,field, key, value, REQUEST):
    """
    first method called for rendering by PageTemplate form_view
    create the whole object based structure, and then call a special
    external PageTemplate (or DTML depending) to render the CSS code
    relative to the structure that need to be rendered
    """

    # build structure
    here = REQUEST['here']

    pdb.set_trace()
    structure = self.render_structure(field=field, key=key, value=value, REQUEST=REQUEST, here=here)

    if structure != None:
      # getting CSS script generator
      planning_css_method = getattr(REQUEST['here'],'planning_css')

      # recover CSS data buy calling DTML document
      CSS_data = planning_css_method(structure=structure)

      # saving structure inside the request to be able to recover it afterwards when needing
      # to render the HTML code
      REQUEST.set('structure',structure)

      # return CSS data
      return CSS_data
    else:
      REQUEST.set('structure',None)
      return None

  def render(self,field,key,value,REQUEST):
    """
    method called to render the HTML code relative to the planning.
    for that recover the structure previouly saved in the REQUEST, and then
    call a special Page Template aimed to render
    """

    # need to test if render is HTML (to be implemented in a page template)
    # or list (to generated a PDF output or anything else).

    # recover structure
    structure = REQUEST.get('structure')

    #pdb.set_trace()
    # getting HTML rendering Page Template
    planning_html_method = getattr(REQUEST['here'],'planning_content')

    # recovering HTML data by calling Page Template document
    HTML_data = planning_html_method(struct=structure)

    return HTML_data


  def render_structure(self, field, key, value, REQUEST, here):
    """ this method is the begining of the rendering procedure. it calls all
        methods needed to generate BasicStructure with ERP5 objects, and then
        creates the PlanningStructure before applying zoom.
        No code is generated (for example HTML code) contrary to the previous
        implementation of PlanningBox. The final rendering must be done through
        a PageTemplate parsing the PlanningStructure object.
        """

    # DATA DEFINITION


    # recovering usefull planning properties
    form = field.aq_parent # getting form
    list_method = field.get_value('list_method') # method used to list objects
    report_root_list = field.get_value('report_root_list') # list of domains
                                                # defining the possible root
    portal_types = field.get_value('portal_types') # Portal Types of objects to list
    # selection name used to store selection params
    selection_name = field.get_value('selection_name')
    # getting sorting keys and order (list)
    sort = field.get_value('sort')
    # contains the list of blocks that are not validated
    # for them a special rendering is done (special colors for example)
    list_error=REQUEST.get('list_block_error')
    if list_error==None : list_error = []

    # END DATA DEFINITION

    # XXX testing : uncoment to put selection to null 
    #here.portal_selections.setSelectionFor(selection_name, None)

    selection = here.portal_selections.getSelectionFor(
                      selection_name, REQUEST)

    # params contained in the selection object is a dictionnary.
    # must exist as an empty dictionnary if selection is empty.
    try:
      params = selection.getParams()
    except (AttributeError,KeyError):
      params = {}

    #if selection.has_attribute('getParams'):
    #  params = selection.getParams()

    # CALL CLASS METHODS TO BUILD BASIC STRUCTURE
    # creating BasicStructure instance (and initializing its internal values)
    self.basic = BasicStructure(here=here,form=form, field=field, REQUEST=REQUEST, list_method=list_method, selection=selection, params = params, selection_name=selection_name, report_root_list=report_root_list, portal_types=portal_types, sort=sort, list_error=list_error)
    # call build method to generate BasicStructure
    returned_value = self.basic.build()
    
    if returned_value == None:
      # in case group list is empty
      return None

    # CALL CLASS METHODS TO BUILD PLANNING STRUCTURE
    # creating PlanningStructure instance and initializing its internal values
    self.planning = PlanningStructure()
    # call build method to generate final Planning Structure
    self.planning.build(basic_structure = self.basic,field=field, REQUEST=REQUEST)

    # end of main process
    # structure is completed, now just need to return structure
    return self



# instanciating class
PlanningBoxWidgetInstance = PlanningBoxWidget()

class BasicStructure:
  """
  First Structure recovered from ERP5 objects. Does not represent in any
  way the final structure used for rendering the Planning (for that see
  PlanningStructure class). for each returned object from ERP5's request,
  create a BasicGroup and stores all object properties.
  No zoom is applied on this structure
  """

  def __init__ (self, here='', form='', field='', REQUEST='', list_method='',
    selection=None, params = '', selection_name='', report_root_list='',
    portal_types='', sort=None, list_error=None):
    """ init main internal parameters """
    self.here = here
    self.form = form
    self.field = field
    self.REQUEST = REQUEST
    self.sort = sort
    self.selection = selection
    self.params = params
    self.list_method = list_method
    self.selection_name = selection_name # used in case no valid list_method 
                                         # has been found
    self.report_root_list = report_root_list
    self.portal_types = portal_types
    self.basic_group_list = None
    self.report_groups= '' # needed to generate groups
    self.list_error = list_error

    self.secondary_axis_occurence = []
    self.render_format = '' # 'list' in case output is a list containing the
                            # full planning structure without any selection


    self.main_axis_info = {}
    self.secondary_axis_info = {}


  def build(self):
    """
    build BasicStructure from given parameters, and for that do the
    specified processes :
    1 - define variables
    2 - building query
    3 - generate report_tree, a special structure containing all the
        objects with their values
    4 - create report_sections
    """

    default_params ={}
    current_section = None
    #params = self.selection.getParams()


    #recovering selection if necessary
    if self.selection is None:
      self.selection = Selection(params=default_params, default_sort_on=self.sort)
    else:
      # immediately updating the default sort value
      self.selection.edit(default_sort_on=self.sort)
      self.selection.edit(sort_on=self.sort)

    self.here.portal_selections.setSelectionFor(self.selection_name,
                                        self.selection,REQUEST=self.REQUEST)

    # building list of portal_types
    self.filtered_portal_types = map(lambda x: x[0], self.portal_types)
    if len(self.filtered_portal_types) == 0:
      self.filtered_portal_types = None

    report_depth = self.REQUEST.get('report_depth',None)
    # In report tree mode, need to remember if the items have to be displayed
    is_report_opened = self.REQUEST.get('is_report_opened',\
                                    self.selection.isReportOpened())
    portal_categories = getattr(self.form,'portal_categories',None)
    portal_domains = getattr(self.form,'portal_domains',None)

    ##################################################
    ############### BUILDING QUERY ###################
    ##################################################

    kw = self.params

    # remove selection_expression if present
    # This is necessary for now, because the actual selection expression in
    # search catalog does not take the requested columns into account. If
    # select_expression is passed, this can raise an exception, because stat
    # method sets select_expression, and this might cause duplicated column
    # names.
    if 'select_expression' in kw:
      del kw['select_expression']


    if hasattr(self.list_method, 'method_name'):
      if self.list_method.method_name == 'ObjectValues':
        # list_method is available
        self.list_method = self.here.objectValues
        kw = copy(self.params)
      else:
        # building a complex query so we should not pass too many variables
        kw={}
        if self.REQUEST.form.has_key('portal_type'):
          kw['portal_type'] = self.REQUEST.form['portal_type']
        elif self.REQUEST.has_key('portal_type'):
          kw['portal_type'] = self.REQUEST['portal_type']
        elif self.filtered_portal_types is not None:
          kw['portal_type'] = self.filtered_portal_types
        elif kw.has_key('portal_type'):
          if kw['portal_type'] == '':
            del kw['portal_type']

        # remove useless matter
        for cname in self.params.keys():
          if self.params[cname] != '' and self.params[cname] != None:
            kw[cname] = self.params[cname]

        # try to get the method through acquisition
        try:
          self.list_method = getattr(self.here, self.list_method.method_name)
        except (AttributeError, KeyError):
          pass
    elif self.list_method in (None,''):
      # use current selection
      self.list_method = None



    ##################################################
    ############ BUILDING REPORT_TREE ################
    ##################################################

    # assuming result is report tree, building it
    # When building the body, need to go through all report lines
    # each report line is a tuple of the form :
    #(selection_id, is_summary, depth, object_list, object_list_size, is_open)
    default_selection_report_path = self.report_root_list[0][0].split('/')[0]
    if (default_selection_report_path in portal_categories.objectIds()) or \
      (portal_domains is not None and default_selection_report_path in \
       portal_domaind.objectIds()):
      pass
    else:
      default_selection_root_path = self.report_root_list[0][0]
    selection_report_path = self.selection.getReportPath(default = \
     (default_selection_report_path,))

    # testing report_depth value
    if report_depth is not None:
      selection_report_curent = ()
    else:
      selection_report_current = self.selection.getReportList()

    # building report_tree_list
    report_tree_list = makeTreeList(here=self.here, form=self.form, root_dict=None,
     report_path=selection_report_path, base_category=None, depth=0,
     unfolded_list=selection_report_current, selection_name=self.selection_name,
     report_depth=report_depth,is_report_opened=is_report_opened,
     sort_on=self.selection.sort_on,form_id=self.form.id)

    # update report list if report_depth was specified
    if report_depth is not None:
      report_list = map(lambda s:s[0].getRelativeUrl(), report_tree_list)
      self.selection.edit(report_list=report_list)



    ##################################################
    ########### BUILDING REPORT_GROUPS ###############
    ##################################################
    # report_groups is another structure based on report_tree but
    # taking care of the object activities.
    # build two structures :
    # - report_groups : list of object_tree_lines composing the planning,
    #   whatever the current group depth, just listing all of them
    # - blocks_object : dict (object_tree_line.getObject()) of objects
    # (assuming objects is a list of activities).

    # first init parameters
    self.report_groups = []
    list_object = []
    self.nbr_groups=0
    object_list=[]
    self.report_activity_dict = {}
    indic_line=0
    index_line=0
    blocks_object={}
    select_expression = ''


    # now iterating through object_tree_list
    for object_tree_line in report_tree_list:
      # prepare query by defining selection report object
      self.selection.edit(report = object_tree_line.getSelectDomainDict())

      if object_tree_line.getIsPureSummary():
        # push new select_expression
        original_select_expression = kw.get('select_expression')
        kw['select_expression'] = select_expression
        self.selection.edit(params = kw)
        # pop new select_expression
        if original_select_expression is None:
          del kw['select_expression']
        else:
          kw['select_expression'] = original_select_expression

      if (object_tree_line.getIsPureSummary() and \
         selection_report_path[0]=='parent'):
        # object_tree_line is Pure summary : does not have any activity
        stat_result = {}
        index=1
        # adding current line to report_section where
        # line is pure Summary
        self.report_groups += [object_tree_line]
        self.nbr_groups = self.nbr_groups + 1

      else:
        # object_tree_line is not pure summary : it has activities
        # prepare query
        self.selection.edit(params = kw)


        if self.list_method not in (None,''):
          # valid list_method has been found
          self.selection.edit(exception_uid_list= \
             object_tree_line.getExceptionUidList())
          object_list = self.selection(method = self.list_method,
             context=self.here, REQUEST=self.REQUEST)    
        else:
          # no list_method found
          object_list = self.here.portal_selections.getSelectionValueList(
            self.selection_name, context=self.here, REQUEST=self.REQUEST)


        exception_uid_list = object_tree_line.getExceptionUidList()
        if exception_uid_list is not None:
          # Filter folders if parent tree :
          # build new object_list for current line
          # (list of relative elements)
          new_object_list = []
          for selected_object in object_list:
            if selected_object.getUid() not in exception_uid_list:
              new_object_list.append(selected_object)
          object_list = new_object_list

        #object_list = []
        add=1
        new_list = [x.getObject() for x in object_list]
        object_list = new_list

        # comparing report_groups'object with object_tree_line to check
        # if the object is already present.
        # this has to be done as there seems to be a 'bug' with make_tree_list
        # returning two times the same object...
        already_in_list = 0
        for object in self.report_groups:
          if getattr(object_tree_line.getObject(),'uid') == \
           getattr(object.getObject(),'uid') and \
           not(object_tree_line.getIsPureSummary()):
            # object already present, flag <= 0 to prevent new add
            already_in_list = 1
            #add=0
            break
        #pdb.set_trace()
        if add == 1: # testing : object not present, can add it
          # adding current line to report_section where
          # line is report_tree
          if already_in_list:
            self.report_groups = self.report_groups[:-1]
          self.report_groups += [object_tree_line]
          self.nbr_groups += 1
          #for p_object in object_list:
            #iterating and adding each object to current_list
          #  object_list.append(p_object)
          # XXX This not a good idea at all to use the title as a key of the
          # dictionnary
          self.report_activity_dict[object_tree_line.getObject().getTitle()] = object_list 

    self.selection.edit(report=None)
    LOG('self.report_activity_dict',0,self.report_activity_dict)


    ##################################################
    ########### GETTING MAIN AXIS BOUNDS #############
    ##################################################
    # before building group_object structure, need to recover axis begin & end
    # for main to be able to generate a 'smart' structure taking into account
    # only the area that need to be rendered. This prevents from useless processing

    # calculating main axis bounds
    self.getMainAxisInfo(self.main_axis_info)

    # applying main axis selection
    if self.report_groups != []:
      self.report_groups = self.report_groups[self.main_axis_info['bound_start']:
                                              self.main_axis_info['bound_stop']]
    else:
      # XXX need to handle this kind of error:
      # no group is available so the Y and X axis will be empty...
      return None


    ##################################################
    ############ GETTING SEC AXIS BOUNDS #############
    ##################################################
    # now that our report_group structure has been cut need to get secondary axis
    # bounds to add only the blocs needed afterwards

    # getting secondary_axis_occurence to define begin and end secondary_axis
    # bounds (getting absolute size)
    self.secondary_axis_occurence = self.getSecondaryAxisOccurence()


    # now getting start & stop bounds (getting relative size to the current
    # rendering)
    self.getSecondaryAxisInfo(self.secondary_axis_info)



    ##################################################
    ####### SAVING NEW PROPERTIES INTO REQUEST #######
    ##################################################
    if self.list_method is not None and self.render_format != 'list':
     self.selection.edit(params = self.params)
     self.here.portal_selections.setSelectionFor(self.selection_name, self.selection, REQUEST = self.REQUEST)


    ##################################################
    ######### BUILDING GROUP_OBJECT STRUCTURE ########
    ##################################################
    # building group_object structure using sub lines depth (in case of a
    # report tree) by doing this.
    # taking into account page bounds to generate only the structure needed

    # instanciate BasicGroup class in BasicStructure so that the structure can
    # be built
    self.buildGroupStructure()

    # everything is fine
    return 1


  def getSecondaryAxisOccurence(self):
    """
    get secondary_axis occurences in order to define begin and end bounds
    """
    secondary_axis_occurence = []

    # specific start & stop methods name for secondary axis
    start_method_id = self.field.get_value('x_start_bloc')
    stop_method_id= self.field.get_value('x_stop_bloc')
    for object_tree_group in self.report_groups:
      # recover method to et begin and end limits
      method_start = getattr(object_tree_group.getObject(),start_method_id,None)
      method_stop = getattr(object_tree_group.getObject(),stop_method_id,None)

      try:
        child_activity_list = self.report_activity_dict[object_tree_group.getObject().getTitle()]
      except (AttributeError, KeyError):
        child_activity_list = None

      #if method_start == None and child_activity_list != None:
      if child_activity_list not in (None, [], {}):
        # can not recover method from object_tree_group itself, trying
        # over the activity list
        # XXX in fact can not fail to recover method from object_tree_group
        # get : <bound method ImplicitAcquirerWrapper.(?) of <Project at /erp5/project_module/planning>>
        # so just trying if children exist
        for child_activity in child_activity_list:
          method_start = getattr(child_activity,start_method_id,None)
          method_stop = getattr(child_activity,stop_method_id,None)
          if method_start != None:
            block_begin = method_start()
          else:
            block_begin = None

          if method_stop != None:
            block_stop = method_stop()
          else:
            block_stop = None

          secondary_axis_occurence.append([block_begin,block_stop])

      else:
        # method sucessfully recovered
        # getting values
        if method_start != None:
          block_begin = method_start()
        else:
          block_begin = None

        if method_stop != None:
          block_stop = method_stop()
        else:
          block_stop = None

        secondary_axis_occurence.append([block_begin,block_stop])

    return secondary_axis_occurence


  def getSecondaryAxisInfo(self, axis_dict):
    """
    secondary_axis_ocurence holds couples of data (begin,end) related to
    basicActivity blocks, and axis if the instance representing the sec axis.
    it is now possible to recover begin and end value of the planning and then
    apply selection informations to get start and stop.
    """

    #pdb.set_trace()


    axis_dict['zoom_start'] = int(self.params.get('zoom_start',0))
    axis_dict['zoom_level'] = float(self.params.get('zoom_level',1))

    # recovering min and max bounds to get absolute bounds
    axis_dict['bound_begin'] = self.secondary_axis_occurence[0][0]
    axis_dict['bound_end'] = axis_dict['bound_begin']
    for occurence in self.secondary_axis_occurence:
      if (occurence[0] < axis_dict['bound_begin'] or axis_dict['bound_begin'] == None) and occurence[0] != None:
        axis_dict['bound_begin'] = occurence[0]
      if (occurence[1] > axis_dict['bound_end'] or axis_dict['bound_end'] == None) and occurence[1] != None:
        axis_dict['bound_end'] = occurence[1]
    axis_dict['bound_range'] = axis_dict['bound_end'] - axis_dict['bound_begin']
    # now start and stop have the extreme values of the second axis bound.
    # this represents in fact the size of the Planning

    # can now getting selection informations ( float range 0..1)
    axis_dict['bound_start'] = 0
    axis_dict['bound_stop'] = 1
    if self.selection != None:
      try:
        axis_dict['bound_start'] = self.selection.getSecondaryAxisStart()
        axis_dict['bound_stop'] = self.selection.getSecondaryAxisStop()
      except AttributeError: #XXX
        pass

    # getting secondary axis page step
    axis_zoom_step = axis_dict['bound_range'] / axis_dict['zoom_level']

    # now setting bound_start
    axis_dict['bound_start'] = axis_dict['zoom_start'] * axis_zoom_step + axis_dict['bound_begin']
    # for bound_stop just add page step
    axis_dict['bound_stop'] = axis_dict['bound_start'] + axis_zoom_step

    # saving current zoom values
    self.params['zoom_level'] = axis_dict['zoom_level']
    self.params['zoom_start'] = axis_dict['zoom_start']


  def getMainAxisInfo(self, axis_dict):
    """
    getting main axis properties (total pages, current page, groups per page)
    and setting selection bounds (start & stop).
    beware this justs calculate the position of the first group present on the
    page (same for the last one), applying the selection is another thing in
    case of report tree (if the first element is a sub group of a report for
    example).
    """

    #pdb.set_trace()
    axis_dict['bound_axis_groups'] = self.field.get_value('main_axis_groups')
    if axis_dict['bound_axis_groups'] == None:
      #XXX raise exception : no group defined
      pass


    # setting begin & end bounds
    axis_dict['bound_begin'] = 0
    axis_dict['bound_end'] = len(self.report_groups)
    if self.render_format == 'list':
      axis_dict['bound_start'] = 0
      axis_dict['bound_stop'] = axis_dict['bound_end']
      axis_dict['bound_page_total'] = 1
      axis_dict['bound_page_current'] = 1
      axis_dict['bound_page_groups'] = 1
    else:
      # recovering first group displayed on actual page
      try:
        # trying to recover from REQUEST
        axis_dict['bound_start'] = self.REQUEST.get('list_start')
        axis_dict['bound_start'] = int(axis_dict['bound_start'])
      except (AttributeError, TypeError):
        # recovering from params is case failed with REQUEST
        axis_dict['bound_start'] = self.params.get('list_start',0)
        if type(axis_dict['bound_start']) is type([]):
          axis_dict['bound_start'] = axis_dict['bound_start'][0]
        axis_dict['bound_start'] = int(axis_dict['bound_start'])
      axis_dict['bound_start'] = max(axis_dict['bound_start'],0)

      if axis_dict['bound_start'] > axis_dict['bound_end']:
        # new report_group is so small that previous if after the last element
        axis_dict['bound_start'] = axis_dict['bound_end']

      # updating start position to fit page size.
      axis_dict['bound_start'] -= (axis_dict['bound_start'] % axis_dict['bound_axis_groups'])

      # setting last group displayed on page
      axis_dict['bound_stop'] = min (axis_dict['bound_start'] + axis_dict['bound_axis_groups'], axis_dict['bound_end'])
      # calculating total number of pages
      axis_dict['bound_page_total'] = int(max(axis_dict['bound_end'] - 1,0) / axis_dict['bound_axis_groups']) + 1
      # calculating current page number
      axis_dict['bound_page_current'] = int(axis_dict['bound_start'] / axis_dict['bound_axis_groups']) + 1
      # adjusting first group displayed on current page
      axis_dict['bound_start'] = min(axis_dict['bound_start'], max(0, (axis_dict['bound_page_total']-1) * axis_dict['bound_axis_groups']))

      self.params['list_lines'] = axis_dict['bound_axis_groups']
      self.params['list_start'] = axis_dict['bound_start']


  def buildGroupStructure(self):
      """
      this procedure builds BasicGroup instances corresponding to the
      report_group_objects returned from the ERP5 request.
      """
      position = 0

      # iterating each element
      for report_group_object in self.report_groups:

        stat_result = {}
        stat_context = report_group_object.getObject().asContext(**stat_result)
        stat_context.domain_url = report_group_object.getObject().getRelativeUrl()
        stat_context.absolute_url = lambda x: report_group_object.getObject().absolute_url()
        url=getattr(stat_context,'domain_url','')
        # updating position_informations
        position +=1
        # recovering usefull informations
        title = report_group_object.getObject().getTitle()
        name = report_group_object.getObject().getTitle()
        depth = report_group_object.getDepth()
        is_open = report_group_object.is_open
        is_pure_summary = report_group_object.is_pure_summary

        # creating new group_object with all the informations collected
        child_group = BasicGroup( title=title, name=name, url=url, constraints=None, depth=depth, position=position, field =self.field, object=report_group_object, is_open=is_open, is_pure_summary=is_pure_summary)

        # creating activities related to the new group
        # first recovering activity list if exists
        report_activity_list = []
        if title in self.report_activity_dict.keys():
          report_activity_list = self.report_activity_dict[title]
        # linking activities to the bloc. the parameter is a list of elements
        # to link to the child_group object.
        child_group.setBasicActivities(report_activity_list,self.list_error,self.secondary_axis_info)

        try:
          self.basic_group_list.append(child_group)
        except (AttributeError):
          self.basic_group_list = []
          self.basic_group_list.append(child_group)


class BasicGroup:
  """
  A BasicGroup holds informations about an ERP5Object and is stored
  exclusively in BasicStructure. for each activity that will need to be
  represented in the PlanningBox, a BasicActivity is created and added to
  the current structure (for example BasicGroup represents an employee,
  and each BasicActivity represents a task the employee has).
  *Only one BasicGroup present while in Calendar mode.
  *BasicGroup instance itself can hold other BasicGroups in case of
  ReportTree mode to handle child groups.
  """

  def __init__ (self, title='', name='',url='', constraints='', depth=0, position=0, field = None, object = None, is_open=0, is_pure_summary=1):
    self.title = title
    self.name = name
    self.url = url
    self.basic_group_list = None # used with ReportTree
    self.basic_activity_list = None # bloc activities
    self.constraints = constraints# global contraints applying to all group
    self.depth = depth # depth of the actual group (report_tree mode)
    self.position = position # position of current group in the selection
    self.field = field # field object itself. used for several purposes
    self.object = object # ERP5 object returned & related to the group
    self.is_open = is_open # define is report is opened  or not
    self.is_pure_summary = is_pure_summary # define id report is single or has sons

    # specific start and stop bound values specifiec to the current group and used
    # in case of calendar mode
    self.start = None
    self.stop = None


  def setBasicActivities(self,activity_list, list_error,secondary_axis_info):
    """
    link a list of activities to the current object.
    + recover group properties. Used in case activity is built from Group itself
    + create a BasicActivity for each activity referenced in the list if 
      necessary
    + add the activity to the current group.
    + update secondary_axis_occurence
    """


    # specific begin & stop methods for secondary axis
    object_begin_method_id = self.field.get_value('x_start_bloc')
    object_end_method_id= self.field.get_value('x_stop_bloc')

    # recover method to et begin and end limits
    method_begin = getattr(self.object.getObject(),object_begin_method_id,None)
    method_end = getattr(self.object.getObject(),object_end_method_id,None)


    # specific block text_information methods
    info_center = self.field.get_value('info_center')
    info_topleft = self.field.get_value('info_topleft')
    info_topright = self.field.get_value('info_topright')
    info_backleft = self.field.get_value('info_backleft')
    info_backright = self.field.get_value('info_backright')


    info = {}

    # getting info method from activity itself if exists
    info_center_method = getattr(self.object.getObject(),info_center,None)
    info_topright_method = getattr(self.object.getObject(),info_topright,None)
    info_topleft_method = getattr(self.object.getObject(),info_topleft,None)
    info_backleft_method = getattr(self.object.getObject(),info_backleft,None)
    info_backright_method = getattr(self.object.getObject(),info_backright,None)

    # if method recovered is not null, then updating
    if info_center_method!=None: info['info_center']=str(info_center_method())
    if info_topright_method!=None: info['info_topright']=str(info_topright_method())
    if info_topleft_method!=None: info['info_topleft']=str(info_topleft_method())
    if info_backleft_method!=None: info['info_backleft'] =str(info_backleft_method())
    if info_backright_method!=None: info['info_backright']=str(info_backright_method())


    

    #if method_begin == None and activity_list not in ([],None):
    if activity_list not in ([],None):

      # modifying iterating mode from original PlanningBox.py script to prevent
      # useless and repetitive tests.
      # this process should be somehow quicker and smarter
      indic=0

      # iterating each activity linked to the current group
      for activity_content in activity_list:

        # group does not have valid begin_method, trying to find them on
        # the activity itself.
        method_begin = getattr(activity_content,object_begin_method_id,None)
        method_end = getattr(activity_content,object_end_method_id,None)


        # interpreting results and getting begin and end values from 
        # previously recovered method
        block_begin = None
        block_end = None
        if method_begin !=None:
          block_begin = method_begin()
        else:
          block_begin = None

        if method_end != None:
          block_end = method_end()
        else:
          block_end = None


        # ahndling case where activity bound is not defined
        if block_begin == None:
          block_begin = secondary_axis_info['bound_start']
          current_color='#E4CCE1'
        if block_end == None:
          block_end = secondary_axis_info['bound_stop']
          current_color='#E4CCE1'
        # testing if activity is visible according to the current zoom selection over
        # the secondary_axis
        if  block_begin > secondary_axis_info['bound_stop'] or block_end < secondary_axis_info['bound_start']:
          # activity will not be displayed, stopping process
          pass
        else:
          # activity is somehow displayed. checking if need to cut its bounds
          if block_begin < secondary_axis_info['bound_start']:
            # need to cut begin bound
            block_start = secondary_axis_info['bound_start']
          else: block_start = block_begin

          if block_end > secondary_axis_info['bound_stop']:
            block_stop = secondary_axis_info['bound_stop']
          else:
            block_stop = block_end

          # defining name
          name = "Activity_%s_%s" % (self.object.getObject().getTitle(),str(indic))

          # getting info text from activity itself if exists
          info_center_method = getattr(activity_content,info_center,None)
          info_topright_method = getattr(activity_content,info_topright,None)
          info_topleft_method = getattr(activity_content,info_topleft,None)
          info_backleft_method = getattr(activity_content,info_backleft,None)
          info_backright_method = getattr(activity_content,info_backright,None)

          # if value recovered is not null, then updating 
          if info_center_method!=None: info['info_center']=str(info_center_method())
          if info_topright_method!=None: info['info_topright']=str(info_topright_method())
          if info_topleft_method!=None: info['info_topleft']=str(info_topleft_method())
          if info_backleft_method!=None: info['info_backleft'] =str(info_backleft_method())
          if info_backright_method!=None: info['info_backright']=str(info_backright_method())

          color_script = getattr(activity_content.getObject(), self.field.get_value('color_script'),None)
          # calling color script if exists to set up activity_color
          current_color=''
          if color_script !=None:
            current_color = color_script(activity_content.getObject())

          # testing if some activities have errors
          error = 'false'
          if list_error not in (None, []):
            for activity_error in list_error:
              if activity_error[0][0] == name:
                error = 'true'
                break

          stat_result = {}
          stat_context = activity_content.getObject().asContext(**stat_result)
          stat_context.domain_url = activity_content.getObject().getRelativeUrl()
          stat_context.absolute_url = lambda x: activity_content.getObject().absolute_url()

          # creating new activity instance
          activity = BasicActivity(title=info['info_center'],name=name,object = stat_context.getObject(),  url=stat_context.getUrl(),absolute_begin=block_begin, absolute_end=block_end, absolute_start = block_start, absolute_stop = block_stop, color = current_color, info_dict=info, error=error)


          # adding new activity to personal group activity list
          try:
            self.basic_activity_list.append(activity)
          except (AttributeError):
            self.basic_activity_list = []
            self.basic_activity_list.append(activity)
          # incrementing indic used for differenciating activities in the same 
          # group (used for Activity naming)
          indic += 1

          info = None
          info = {}


    else:

      # specific color scriptactivity
      color_script = getattr(self.object.getObject(), self.field.get_value('color_script'),None)


      # calling color script if exists to set up activity_color
      current_color=''
      if color_script !=None:
        current_color = color_script(self.object.getObject())


      # getting begin and end values from previously recovered method
      if method_begin !=None:
        block_begin = method_begin()
      else:
        block_begin = None

      if method_end != None:
        block_end = method_end()
      else:
        block_end = None

      # testing if activity is visible according to the current zoom selection over
      # the secondary_axis
      if block_begin == None:
        block_begin = secondary_axis_info['bound_start']
        current_color='#E4CCE1'
      if block_end == None:
        block_end = secondary_axis_info['bound_stop']
        current_color='#E4CCE1'
      if  (block_begin > secondary_axis_info['bound_stop'] or block_end < secondary_axis_info['bound_start']):
      #  # activity will not be displayed, stopping process
        pass
      else:
        # activity is somehow displayed. checking if need to cut its bounds
        if block_begin < secondary_axis_info['bound_start']:
          # need to cut begin bound
          block_start = secondary_axis_info['bound_start']
        else: block_start = block_begin

        if block_end > secondary_axis_info['bound_stop']:
          block_stop = secondary_axis_info['bound_stop']
        else:
          block_stop = block_end

        # testing if some activities have errors
        error = 'false'
        if list_error not in (None,[]):
          for activity_error in list_error:
            if activity_error[0][0] == name:
              error = 'true'
              break

        # defining name
        name = "Activity_%s" % (self.object.getObject().getTitle())

        # creating new activity instance
        activity = BasicActivity(title=info['info_center'], name=name, object = self.object.object, url=self.url, absolute_begin=block_begin, absolute_end=block_end, absolute_start=block_start, absolute_stop=block_stop,color = current_color, info_dict=info, error=error)

        # adding new activity to personal group activity list
        try:
          self.basic_activity_list.append(activity)
        except (AttributeError):
          self.basic_activity_list = []
          self.basic_activity_list.append(activity)





class BasicActivity:
  """ Represents an activity, a task, in the group it belongs to. Beware
      nothing about multitask rendering. """

  def __init__ (self, title='', name='',object = None, url='', absolute_begin=None,
    absolute_end=None,absolute_start=None,absolute_stop=None, constraints='', color=None, error='false', info_dict= None):
    self.title = title
    self.name = name
    self.object = object
    self.url = url
    self.absolute_begin = absolute_begin # absolute values independant of any
                                         # hypothetic zoom
    self.absolute_end = absolute_end
    self.absolute_start = absolute_start
    self.absolute_stop = absolute_stop
    self.constraints = constraints# constraints specific to the current Activity
    self.color = color
    self.info_dict = info_dict
    self.error = error




class PlanningStructure:
  """ class aimed to generate the Planning final structure, including :
      - activities with their blocs (so contains Activity structure)
      - Axis informations (contains Axis Structure).
      The zoom properties on secondary axis are applied to this structure.
      """


  def __init__ (self,):
    self.main_axis = ''
    self.secondary_axis = ''
    self.content = []
    self.content_delimiters = None


  def build(self,basic_structure=None, field=None, REQUEST=None):
    """
    main procedure for building Planning Structure
    do all the necessary process to construct a full Structure compliant with all
    expectations (axis, zoom, colors, report_tree, multi_lines, etc.). From this
    final structure just need to run a PageTemplate to get an HTML output, or any
    other script to get the Planning result in the format you like...
    """

    # XXX defining render_format
    # afterwards will be defined as a planningBox's property field or (perhaps even better)
    # a on the fly button integrated over the planning representation 
    #render_format = field.get_value('render_format')
    self.render_format = field.get_value('representation_type')
    #self.render_format = 'YX'



    # declaring main axis
    self.main_axis = Axis(title='main axis', name='axis',
                     unit='', axis_order=1,axis_group=[])

    # declaring secondary axis
    self.secondary_axis = Axis(title='sec axis', name='axis',
                     unit='', axis_order=2, axis_group=[])

    # linking axis objects to their corresponding accessor, i.e X or Y
    # this allows the planning to be generic.
    if self.render_format == 'YX':
      self.Y = self.main_axis
      self.X = self.secondary_axis
    else:
      self.Y = self.secondary_axis
      self.X = self.main_axis

    # initializing axis properties
    self.X.name = 'axis_x'
    self.Y.name = 'axis_y'


    # recovering secondary_axis_ bounds
    self.secondary_axis.start = basic_structure.secondary_axis_info['bound_start']
    self.secondary_axis.stop = basic_structure.secondary_axis_info['bound_stop']


    self.main_axis.size =  self.buildGroups(basic_structure=basic_structure)

    #pdb.set_trace()
    # call method to build secondary axis structure
    # need start_bound, stop_bound and number of groups to build
    self.buildSecondaryAxis(basic_structure)


    # completing axisgroup informations according to their bounds
    self.buildMainAxis()

    # the whole structure is almost completed : axis_groups are defined, as
    # axis_elements with their activities. Just need to create blocks related to
    # the activities (special process only for Calendar mode) with their
    # BlockPosition
    self.buildBlocs()


  def buildSecondaryAxis(self,basic_structure):
    """
    build secondary axis structure
    """
    """
    pdb.set_trace()
    # defining min and max delimiter number
    delimiter_min_number = 4
    date_stop = self.secondary_axis.stop
    date_start = self.secondary_axis.start
    date_range = date_stop - date_start

    # testing delimiter_type to apply (day, week, month, year)
    # from smallest type to biggest
    type_list = [['year',  365],
                 ['month',  30],
                 ['week',    7],
                 ['day',     1]
                 ]
    # default good_type is last one (if nothing else matches)
    good_type = type_list[-1]
    for date_type in type_list:
      # iterating each delimiter_type and testing if it matches the delimitation
      # number definition
      if date_range / date_type[1] >= delimiter_min_number:
        good_type = date_type
        break

    # good type is known need to get first delimiter after start_date
    # for that use special function getClosestDate (cf. DateUtils.py)
    first_delimiter = getClosestDate(date=None, target_date=date_start, precision=good_type[0], before=0)


    delimiter_list = []
    current_delimiter = first_delimiter
    while current_delimiter.Date() < date_stop.Date():
      delimiter_list.append(current_delimiter.Date())
      #DateUtils.addToDate(current_delimiter,


      self.secondary_axis.axis_group.append(axis_group)


    return None

    """
    # getting secondary axis script generator
    planning_secondary_axis_method = getattr(basic_structure.here,'planning_secondary_axis')
    # calling script to generate axis_group_list
    group_list = planning_secondary_axis_method(self.secondary_axis.start, self.secondary_axis.stop, 4)
    axis_group_number = 0
    for group_title in group_list:
      # adding new group to list of groups
      axis_group = AxisGroup(name='Group_sec_' + str(axis_group_number), title=group_title)

      # updating informations
      axis_group.axis_element_start = axis_group_number
      axis_group.axis_element_number = 1
      axis_group.axis_element_stop  = axis_group_number + 1

      self.secondary_axis.axis_group.append(axis_group)
      axis_group = None
      axis_group_number += 1


  def buildMainAxis (self):
    """
    complete axis infomations (and more precisely axis position objects) thanks
    to the actual planning structure
    """

    # processing main axis
    for axis_group_element in self.main_axis.axis_group:
      axis_group_element.position_main.absolute_begin = float(axis_group_element.axis_element_start - 1) / float(self.main_axis.size)
      axis_group_element.position_main.absolute_end = float(axis_group_element.axis_element_stop) / float(self.main_axis.size)
      axis_group_element.position_main.absolute_range = float(axis_group_element.axis_element_number) / float(self.main_axis.size)
      axis_group_element.position_secondary.absolute_begin = 0
      axis_group_element.position_secondary.absolute_end = 1
      axis_group_element.position_secondary.absolute_range= 1

    for axis_group_element in self.secondary_axis.axis_group:
      axis_group_element.position_main.absolute_begin = 0
      axis_group_element.position_main.absolute_end = 1
      axis_group_element.position_main.absolute_range= 1
      axis_group_element.position_secondary.absolute_begin = float(axis_group_element.axis_element_start) / float(len(self.secondary_axis.axis_group))
      axis_group_element.position_secondary.absolute_end = float(axis_group_element.axis_element_stop) / float(len(self.secondary_axis.axis_group))
      axis_group_element.position_secondary.absolute_range= float(1) / float(len(self.secondary_axis.axis_group))


  def buildGroups (self, basic_structure=None):
    """
    build groups from activities saved in the structure groups.
    """
    axis_group_number = 0
    axis_element_already_present=0
    for basic_group_object in basic_structure.basic_group_list:
      axis_group_number += 1
      axis_group = AxisGroup(name='Group_' + str(axis_group_number), title=basic_group_object.title, object = basic_group_object.object, axis_group_number = axis_group_number, is_open=basic_group_object.is_open, is_pure_summary=basic_group_object.is_pure_summary, url = basic_group_object.url,depth = basic_group_object.depth, secondary_axis_start= self.secondary_axis.start, secondary_axis_stop= self.secondary_axis.stop)
      if self.render_format == 'YX':
        axis_group.position_y = axis_group.position_main
        axis_group.position_x = axis_group.position_secondary
      else:
        axis_group.position_y = axis_group.position_secondary
        axis_group.position_x = axis_group.position_main
      # init absolute position over the axis
      # XXX if a special axisGroup length is needed (statistics, or report_tree),
      # then it should be implemented here.
      axis_group.position_secondary.absolute_begin = 0
      axis_group.position_secondary.absolute_end= 1
      axis_group.position_secondary.absolute_range = 1
      # updating axis_group properties
      axis_group.fixProperties(form_id = basic_structure.form.id, selection_name = basic_structure.selection_name)
      # updating start value
      axis_group.axis_element_start = axis_element_already_present + 1
      activity_number = 0
      if basic_group_object.basic_activity_list != None:
        # need to check if activity list is not empty : possible in case zoom
        # selection is used over the secondary axis
        for basic_activity_object in basic_group_object.basic_activity_list:
          activity_number += 1
          # create new activity in the PlanningStructure
          activity = Activity(name='Group_' + str(axis_group_number) + '_Activity_' + str(activity_number), title=basic_activity_object.title, object=basic_activity_object.object, color=basic_activity_object.color, link=basic_activity_object.url, secondary_axis_begin=basic_activity_object.absolute_begin, secondary_axis_end=basic_activity_object.absolute_end, secondary_axis_start=basic_activity_object.absolute_start, secondary_axis_stop=basic_activity_object.absolute_stop, primary_axis_block=self, info=basic_activity_object.info_dict, render_format=self.render_format)
          # adding activity to the current group
          axis_group.addActivity(activity,axis_element_already_present)
      else:
        # basic_activity_list is empty : need to add a empty axis_element to
        # prevent bug or crash
        axis_group.axis_element_number = 1
        new_axis_element = AxisElement(name='Group_' + str(axis_group_number) + '_AxisElement_1', relative_number= 1 , absolute_number = axis_group.axis_element_start, parent_axis_group=axis_group)
        # add new activity to this brand new axis_element
        new_axis_element.activity_list = []
        axis_group.axis_element_list = []
        axis_group.axis_element_list.append(new_axis_element)

      axis_group.axis_element_stop = axis_element_already_present + axis_group.axis_element_number
      axis_element_already_present = axis_group.axis_element_stop
      try:
        self.main_axis.axis_group.append(axis_group)
      except AttributeError:
        self.main_axis.axis_group = []
        self.main_axis.axis_group.append(axis_group)
    return axis_element_already_present


  def buildBlocs(self):
    """
    iterate the whole planning structure to get various activities and build
    their related blocs.
    """
    try:
      for axis_group_object in self.main_axis.axis_group:
        for axis_element_object in axis_group_object.axis_element_list:
          for activity in axis_element_object.activity_list:
            activity.addBlocs(main_axis_start=0, main_axis_stop=self.main_axis.size, secondary_axis_start=self.secondary_axis.start, secondary_axis_stop=self.secondary_axis.stop,planning=self)
    except TypeError:
      pass




class Activity:
  """
  Class representing a task in the Planning, for example an appointment or
  a duration. Can be divided in several blocs for being rendered correctly
  (contains Bloc Structure).
  Activity instance are not rendered but only their blocs. This Activity
  structure is used for rebuilding tasks from bloc positions when
  validating the Planning.
  """
  def __init__ (self,name=None, title=None, object=None, types=None, color=None, link=None, secondary_axis_begin=None, secondary_axis_end=None, secondary_axis_start=None, secondary_axis_stop=None, primary_axis_block=None, info=None, render_format='YX'):
    self.name = name # internal activity_name
    self.title = title # displayed activity_name
    self.object = object
    self.types = types # activity, activity_error, info
    self.color = color # color used to render all Blocs
    self.link = link # link to the ERP5 object
    # self.constraints = constraints
    self.block_list = None # contains all the blocs used to render the activity
    self.secondary_axis_begin =secondary_axis_begin
    self.secondary_axis_end=secondary_axis_end
    self.secondary_axis_start=secondary_axis_start
    self.secondary_axis_stop=secondary_axis_stop
    self.primary_axis_block = primary_axis_block
    self.block_bounds = None
    self.info = info
    self.parent_axis_element = None
    self.render_format= render_format

  def isValidPosition(self, bound_begin, bound_end):
    """
    can check if actual activity can fit within the bounds, returns :
    - 0 if not
    - 1 if partially ( need to cut the activity bounds to make it fit)
    - 2 definitely
    """
    if self.secondary_axis_begin > bound_end or self.secondary_axis_end < bound_begin:
      return 0
    elif self.secondary_axis_begin > bound_begin and self.secondary_axis_end < bound_end:
      return 1
    else:
      return 2


  def addBlocs(self, main_axis_start=None, main_axis_stop=None, secondary_axis_start=None, secondary_axis_stop=None,planning=None):
    """
    define list of (begin & stop) values for blocs representing the actual
    activity (can have several blocs if necessary).
    """

    # recover list of bounds
    if self.secondary_axis_start != None or self.secondary_axis_stop != None:
      secondary_block_bounds = self.splitActivity()
    else:
      secondary_block_bounds = [[self.secondary_axis_start,self.secondary_axis_stop]]

    block_number = 0
    # iterating resulting list
    for (start,stop) in secondary_block_bounds:

      block_number += 1
      # create new block instance
      new_block = Bloc(name=self.name + '_Block_' + str(block_number) ,color=self.color,link=self.link, number = block_number, render_format=self.render_format, parent_activity=self)

      #pdb.set_trace()
      new_block.buildInfoDict(info_dict = self.info)

      # updating secondary_axis block position
      if self.secondary_axis_start != None:
        new_block.position_secondary.absolute_begin = start
      else:
        new_block.position_secondary.absolute_begin = secondary_axis_start
      if self.secondary_axis_stop != None:
        new_block.position_secondary.absolute_end = stop
      else:
        new_block.position_secondary.absolute_end = secondary_axis_stop
      new_block.position_secondary.absolute_range = stop - start
      # updating main_axis block position
      new_block.position_main.absolute_begin = self.parent_axis_element.absolute_number - 1
      new_block.position_main.absolute_end = self.parent_axis_element.absolute_number
      new_block.position_main.absolute_range = new_block.position_main.absolute_end - new_block.position_main.absolute_begin

      # now absolute positions are updated, and the axis values are known
      # (as parameters), processing relative values
      new_block.position_secondary.relative_begin = \
          float(new_block.position_secondary.absolute_begin - secondary_axis_start) / float(secondary_axis_stop - secondary_axis_start)
      new_block.position_secondary.relative_end = \
          float(new_block.position_secondary.absolute_end - secondary_axis_start) / float(secondary_axis_stop - secondary_axis_start)
      new_block.position_secondary.relative_range = \
          new_block.position_secondary.relative_end - new_block.position_secondary.relative_begin
      new_block.position_main.relative_begin = \
          float(new_block.position_main.absolute_begin - main_axis_start) / float(main_axis_stop - main_axis_start)
      new_block.position_main.relative_end = \
          float(new_block.position_main.absolute_end - main_axis_start) / float(main_axis_stop - main_axis_start)
      new_block.position_main.relative_range = \
          new_block.position_main.relative_end - new_block.position_main.relative_begin

      try:
        self.block_list.append(new_block)
      except AttributeError:
        # in case this is the first add 
        # need to initialize the list
        self.block_list = []
        self.block_list.append(new_block)
        
      try:
        planning.content.append(new_block)
      except AttributeError:
        planning.content = []
        planning.content.append(new_block)

  def splitActivity(self):
    """
    Used for splitting an activity in multiple bloc.
    [EDIT] will not be used to split Calendar axis (by date time depending on
           the axis size), but will certainly be used afterwards in all cases
           to split activity in multiple blocs according to some external
           constraints (do not work sat & sun, or for a dayly planning do not
           work from 18P.M to 9A.M).
           will use an external script to do so.
    """
    # XXX not implemented yet
    return [(self.secondary_axis_start,self.secondary_axis_stop)]




class Bloc:
  """
  structure that will be rendered as a bloc, a task element.
  Blocs are referenced in the Activity they belong to (logical structure),
  but are also referenced in their relative AxisElement (to be able to
  calculate the number of lines required for rendering when having
  multi-tasking in parallel).
  Contains Bloc Structure for position informations.
  """

  def __init__ (self, name=None, types=None,
                color=None, info=None, link=None, number=0,
                constraints=None, secondary_start=None, secondary_stop=None, render_format='YX', parent_activity = None):
    """
    creates a Bloc object
    """
    self.name = name # internal name
    self.types = types # activity, activity_error, info
    self.color = color
    self.info = info # dict containing text with their position
    self.link = link # on clic link
    self.number = number
    self.title=''
    self.parent_activity = parent_activity
    self.constraints = constraints
    # list of all the groups the bloc belongs to (reportTree)
    #self.container_axis_group = container_AxisGroup
    # integer pointing to the AxisElement containing the bloc (multitasking)
    #self.container_axis_element = container_AxisElement
    self.position_main = Position()
    self.position_secondary = Position(absolute_begin=secondary_start,absolute_end=secondary_stop)
    if render_format == 'YX':
      self.position_y = self.position_main
      self.position_x = self.position_secondary
    else:
      self.position_y = self.position_secondary
      self.position_x = self.position_main
    self.render_dict = None
    
  def buildInfoDict (self, info_dict=[]):
    """
    create Info objects to display text & images, then link them to the current object
    """
    #XXX /4
    self.info = {}
    title_list = []
    #pdb.set_trace()
    title_list.append(self.buildInfo(info_dict=info_dict, area='info_topleft'))
    title_list.append(self.buildInfo(info_dict=info_dict, area='info_topright'))
    title_list.append(self.buildInfo(info_dict=info_dict, area='info_center'))
    title_list.append(self.buildInfo(info_dict=info_dict, area='info_botleft'))
    title_list.append(self.buildInfo(info_dict=info_dict, area='info_botright'))
    # updating title
    self.title = " | ".join(title_list)

  def buildInfo(self,info_dict=[],area=None):
    if area in info_dict:
      # creating new object
      info = Info(info = info_dict[area], link = self.link)
      # saving new object to block dict
      self.info[area] = info
      # recovering text information
      return info_dict[area]
    else:
      return ''

class Position:
  """
  gives a bloc [/or an area] informations about it's position on the X or Y
  axis. can specify position in every kind of axis : continuous or listed
  with lower and upper bound.
  """

  def __init__ (self, absolute_begin=None,
                absolute_end=None, absolute_size=None,
                relative_begin=None, relative_end=None, relative_size=None):
    # absolute size takes the bloc size in the original unit for the axis
    self.absolute_begin = absolute_begin
    self.absolute_end = absolute_end
    self.absolute_size = absolute_size
    # selative size in % of the current axis size
    self.relative_begin = relative_begin
    self.relative_end = relative_end
    self.relative_size = relative_size


class Axis:
  """
  Structure holding informations about a specified axis.Can be X or Y axis.
  Is aimed to handle axis with any kind of unit : continuous or listed (
  including possibly a listed ReportTree).
  Two of them are needed in a PlanningStructure to have X and Y axis.
  In case of listed axis, holds AxisGroup Structure.
  """

  def __init__(self, title=None, unit=None, types=None, axis_order=None, name=None, axis_group=None):
    self.title = title # axis title
    self.unit = unit # unit kind (time, nb... person, task, etc.)
    self.types = types # continuous / listed (incl. ReportTree)
    self.name = name
    self.size = 0 # value
    # axis group is a single group that contain the axis structure.
    # defined to be able to use a generic and recursive method to 
    self.axis_group = axis_group
    # specify if axis is primary or secondary.
    # - if primary axis in Planning, zoom selection is applied thanks to 
    # a cut over the basic structure objects (based on their position and
    # their length).
    # - if secondary axis in Planning, then need to apply the second zoom
    # bounds (application will be based on two bounds : start & stop)
    self.axis_order = axis_order
    # dict containing all class properties with their values
    self.render_dict=None


class AxisGroup:
  """
  Class representing an item, that can have the following properties :
  - one or several rendered lines (multiTasking) : contains AxisElement
  structure to hold this.
  - one or several sub groups (ReportTree) : contains AxisGroup structure
  to hold sub groups elements.
  """

  def __init__ (self, name='', title='', object = None,
                axis_group_list=None, axis_group_number=0,
                axis_element_list=None, axis_element_number=0, is_open=0, is_pure_summary=1,depth=0, url=None, axis_element_already_insered= 0, secondary_axis_start=None, secondary_axis_stop=None):
    self.name = name
    self.title = title
    self.object = object # physical object related to the current group (used to validate modifications)
    self.axis_group_list = axis_group_list # ReportTree
    self.axis_group_number = axis_group_number
    self.axis_element_list = axis_element_list # Multitasking
    self.axis_element_number = axis_element_number
    self.axis_element_start = None
    self.axis_element_stop = None
    # dict containing all class properties with their values
    self.render_dict=None
    self.is_open = is_open
    self.is_pure_summary = is_pure_summary
    self.depth = depth
    self.url = url
    self.link = None # link to fold or unfold current report in report-tree mode
    self.position_main = Position()
    self.position_secondary = Position()
    self.position_x = None
    self.position_y = None
    # UPDATE secondary axis_bounds are now linked to each axis_group to support
    # calendar output( were each axis_group has its own start and stop)
    self.secondary_axis_start = secondary_axis_start
    self.secondary_axis_stop = secondary_axis_stop


  def fixProperties(self, form_id=None, selection_name=None):
    """
    using actual AxisGroup properties to define some special comportement that
    the axisGroup should have, especially in case of report-tree
    """
    if self.is_open:
      # current report is unfold, action 'fold'
      self.link = 'portal_selections/foldReport?report_url=' + self.url + '&form_id='+ form_id + '&list_selection_name=' + selection_name
      self.title = '[-] ' + self.title
    else:
      # current report is fold, action 'unfold'
      self.link = 'portal_selections/unfoldReport?report_url=' + self.url + '&form_id='+ form_id + '&list_selection_name=' + selection_name
      self.title = '[+] ' + self.title
    

  def addActivity(self, activity=None, axis_element_already_insered= 0):
    """
    procedure that permits to add activity to the corresponding AxisElement.
    can create new Axis Element in the actual Axisgroup if necessary.
    Permits representation of MULTITASKING
    """

    # declaring variable used to check if activity has already been added
    added = 0
    try:
      # iterating each axis_element of the axis_group
      for axis_element in self.axis_element_list:
  
        can_add = 1
        # recovering all activity properties of the actual axis_element and
        # iterating through them to check if one of them crosses the new one
        for activity_statement in axis_element.activity_list:
  
          if activity_statement.isValidPosition(activity.secondary_axis_begin, activity.secondary_axis_end) != 0:
            # isValidPosition returned 1 or 2, this means the activity already
            # present does prevent from adding the new activity as there is
            # coverage on the current axis_element.
            # stop iterating actual axis_element and try with the next one
            can_add = 0
            break
  
        if can_add:
          # the whole activity_statements in actual axis have been succesfully
          # tested without problem.
          # can add new activity to the actual axis_element
          added = 1
          axis_element.activity_list.append(activity)
  
          # updating activity properties
          activity.parent_axis_element = axis_element
          
          # no need to check the next axis_elements to know if they can hold the
          # new activity as it is already added to an axis_element
          break
  
      if not added:
        # all axis_elements of the current group have been tested and no one can
        # contain the new activity.
        self.axis_element_number += 1
        # Need to create a new axis_element to hold the new activity
        new_axis_element = AxisElement(name='Group_' + str(self.axis_group_number) + '_AxisElement_' + str(self.axis_element_number), relative_number=self.axis_element_number, absolute_number=axis_element_already_insered  + self.axis_element_number)
  
        # add new activity to this brand new axis_element
        new_axis_element.activity_list = []
        new_axis_element.activity_list.append(activity)
  
        # updating activity properties
        activity.parent_axis_element = new_axis_element
  
        # register the axis_element to the actual group.
        self.axis_element_list.append(new_axis_element)
    except TypeError:
      # in case axis_element_list is Empty (first activity to the group)
      # Need to create a new axis_element to hold the new activity
      self.axis_element_number += 1
      new_axis_element = AxisElement(name='Group_' + str(self.axis_group_number) + '_AxisElement_1', relative_number= self.axis_element_number, absolute_number = axis_element_already_insered + self.axis_element_number, parent_axis_group=self)

      # add new activity to this brand new axis_element
      new_axis_element.activity_list = []
      new_axis_element.activity_list.append(activity)

      # updating activity properties
      activity.parent_axis_element = new_axis_element

      # register the axis_element to the actual group.
      self.axis_element_list = []
      self.axis_element_list.append(new_axis_element)


class AxisElement:
  """
  Represents a line in an item. In most cases, an AxisGroup element will
  hold ony one AxisElement (simple listed axis), but sometimes more
  AxisElements are required (multi, simultaneous tasking).
  AxisElement is linked with the blocs displayed in it : this is only
  usefull when doing multitasking to check if a new bloc can be added to an
  existing AxisElement or if it is needed to create a new AxisElement in
  the AxisGroup to hold it.
  """
  def __init__ (self,name='', relative_number=0, absolute_number=0, activity_list=None, parent_axis_group = None):
    self.name = name
    self.relative_number = relative_number # personal AxisElement id in the AxisGroup
    self.absolute_number = absolute_number # id in the current rendering
    self.activity_list = activity_list
    # dict containing all class properties with their values
    self.render_dict=None
    self.parent_axis_group = parent_axis_group


class Info:
  """
  Class holding all informations to display an info text div inside of a block or
  AxisGroup or whatever
  """
  security = ClassSecurityInfo()

  def __init__(self, info=None, link=None, title=None):
    self.info = info
    self.link = link
    self.title = title

  security.declarePublic('edit')
  def edit(self, info=None):
     """
     special method allowing to update Info content from an external script
     """
     self.info = info

# declaring validator instance
PlanningBoxValidatorInstance = PlanningBoxValidator()

class PlanningBox(ZMIField):
    meta_type = "PlanningBox"
    widget = PlanningBoxWidgetInstance
    validator = PlanningBoxValidatorInstance
    security = ClassSecurityInfo()
    security.declareProtected('Access contents information', 'get_value')
    def get_value(self, id, **kw):
      if id == 'default' and kw.get('render_format') in ('list', ):
        return self.widget.render(self, self.generate_field_key() , None , 
                                  kw.get('REQUEST'),
                                  render_format=kw.get('render_format'))
      else:
        return ZMIField.get_value(self, id, **kw)

    def render_css(self, value=None, REQUEST=None):
      return self.widget.render_css(self,'',value,REQUEST)


InitializeClass(BasicStructure)
allow_class(BasicStructure)
InitializeClass(BasicGroup)
allow_class(BasicGroup)
InitializeClass(BasicActivity)
allow_class(BasicActivity)
InitializeClass(PlanningStructure)
allow_class(PlanningStructure)
InitializeClass(Activity)
allow_class(Activity)
InitializeClass(Bloc)
allow_class(Bloc)
InitializeClass(Position)
allow_class(Position)
InitializeClass(Axis)
allow_class(Axis)
InitializeClass(AxisGroup)
allow_class(AxisGroup)
InitializeClass(AxisElement)
allow_class(AxisElement)
InitializeClass(Info)
allow_class(Info)
