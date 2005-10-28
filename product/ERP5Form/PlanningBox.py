##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jonathan Loriette <john@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
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
import string, types, sys
from Form import BasicForm
from Products.Formulator.Field import ZMIField
from Products.Formulator.DummyField import fields
from Products.Formulator.MethodField import BoundMethod
from DateTime import DateTime
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

class PlanningBoxValidator(Validator.StringBaseValidator):
  def validate(self, field, key, REQUEST):
    """allows to check if one block is not outside of the planning"""
    bmoved=REQUEST.get('block_moved')
    form = field.aq_parent
    height_global_div= field.get_value('height_global_div')    
    width_line = field.get_value('width_line')
    here = getattr(form, 'aq_parent', REQUEST)
    space_line=field.get_value('space_line')
    selection_name = field.get_value('selection_name')
    sort = field.get_value('sort')
    color_script=getattr(here,field.get_value('color'),None)
    height_header = field.get_value('height_header')
    height_global_div = field.get_value('height_global_div')
    height_axis_x=field.get_value('height_axis_x')
    meta_types = field.get_value('meta_types')
    list_method = field.get_value('list_method')
    report_root_list = field.get_value('report_root_list')
    portal_types = field.get_value('portal_types')
    object_start_method_id = field.get_value('x_start_bloc')
    object_stop_method_id= field.get_value('x_stop_bloc')
    y_axis_width = field.get_value('y_axis_width')
    script=getattr(here,field.get_value('x_axis_script_id'),None)
    scriptY = getattr(here,field.get_value('max_y'),None)
    x_range = field.get_value('x_range')
    info_center = field.get_value('info_center')
    info_topleft = field.get_value('info_topleft')        
    info_topright = field.get_value('info_topright')
    info_backleft = field.get_value('info_backleft')
    info_backright = field.get_value('info_backright')
    block_height= getattr(here,field.get_value('y_axis_method'),None)
    portal_url = here.portal_url()
    list_error=REQUEST.get('list_block_error')
    old_delta2 = REQUEST.get('old_delta2')
    lineb= REQUEST.get('line_begin')
    if old_delta2!='None':
      if old_delta2!='':
        if old_delta2!={}:
          old_delta2=convertStringToDict(old_delta2)
    else:
      old_delta2={}
    
    #first we rebuild the initial object structure with only line and activity block.
    
    # list_object is the variable that contains all the structure of the graphic.
    # Basically, it a list a Line Object.
    list_object=[]
    selection = here.portal_selections.getSelectionFor(selection_name, REQUEST=REQUEST)
    default_params = {}
    if selection is None:
      selection = Selection(params=default_params, default_sort_on = sort)
    else:
      selection.edit(default_sort_on = sort)
      selection.edit(sort_on = sort)       
    here.portal_selections.setSelectionFor(selection_name, selection, REQUEST=REQUEST)
    current_top = height_header
    #we check what is the current zoom in order to redefine height & width
    current_zoom = selection.getZoom()
    current_zoom= float(current_zoom)
    if current_zoom<=1:
      height_global_div = round(height_global_div * current_zoom)
      width_line = round(width_line * current_zoom)
      space_line = round(space_line * current_zoom)  
    #we build line
    (list_object,nbr_line,report_sections,blocks_object)=createLineObject(meta_types=meta_types,
                                                            selection=selection,
                                                            selection_name=selection_name,field=field,
                                                            REQUEST=REQUEST,list_method=list_method,
                                                            here=here,report_root_list=report_root_list,
                                                            y_axis_width=y_axis_width,width_line=width_line,
                                                            space_line=space_line,
                                                            height_global_div=height_global_div,
                                                            height_header=height_header,
                                                            height_axis_x=height_axis_x,form=form,
                                                            current_top=current_top,portal_types=portal_types)
    # blocks_object is a dictionnary that contains all informations used for building blocks of each line
 
    #we build x_occurence (used for the range in x-Axis 
    x_occurence=[]
    #report_sections contains treeListLine instance objects
    for treelistobject in report_sections: 
      method_start = getattr(treelistobject.getObject(),object_start_method_id,None)
      method_stop= getattr(treelistobject.getObject(),object_stop_method_id,None)
      if method_start!=None:
        block_begin = method_start()
      else:
        block_begin = None
      
      if method_stop!=None:
        block_stop= method_stop()
      else:
        block_stop=None
      if block_begin != None: 
       x_occurence.append([block_begin,block_stop])
      #if method start is None it means that we construct the graphic with informations contained
      #in blocks_object. 
      if method_start == None and report_sections!={}:
        for Ablock in blocks_object:
          #object_content is the current object used for building a block.
          #For instance if the context is a project, then object_content is an orderLine.
          for object_content in blocks_object[Ablock]:
            method_start = getattr(object_content,object_start_method_id,None)
            method_stop= getattr(object_content,object_stop_method_id,None)
              
            if method_start!=None:
              block_begin = method_start()
            else:
              block_begin = None
            
            if method_stop!=None:
              block_stop= method_stop()
            else:
              block_stop=None
              
            if block_begin!=None:# and block_stop!=None:
              x_occurence.append([block_begin,block_stop])
          
      params=selection.getParams()
      start=params.get('list_start')
      
      x_axe=script(x_occurence,x_range,float(current_zoom),start)
      y_max= 1
      current_max = 1
      #this part is used for determining the maximum through datas fetched via scriptY
      #y_max is used when blocks have different height.
      if scriptY != None:
        for s in report_sections:
          current_max=scriptY(s.getObject())
          if current_max > y_max:
            y_max = current_max
      else:
        y_max = 1
      indic_line=0
      while indic_line != len(report_sections):
        # o is a Line object, for each line, we add its blocks via insertActivityBlock
        for o in list_object:
          if o.title == report_sections[indic_line].getObject().getTitle():
            if list_object != [] and report_sections[indic_line].getDepth()==0:
              o.insertActivityBlock(line_content=report_sections[indic_line].getObject(),
                                    object_start_method_id=object_start_method_id,
                                    object_stop_method_id=object_stop_method_id,
                                    x_axe=x_axe,field=field,info_center=info_center,
                                    info_topright=info_topright,info_topleft=info_topleft,
                                    info_backleft=info_backleft,info_backright=info_backright,
                                    list_error=list_error,old_delta=['None','None'],REQUEST=REQUEST,
                                    blocks_object=blocks_object,width_line=width_line,
                                    script_height_block=block_height,y_max=y_max,color_script=color_script)                                                      
              break
        indic_line+=1 
    
    #  the structure is now rebuilt
    block_moved = [] 
    bloc_and_line=[] # store the line and the coordinates of block moved
    if bmoved != '':
      block_moved=convertStringToList(bmoved)
    else:
      return ''
    
    # When a block is moved, we fetch its object Line and its corresponding object Blocks*
    # via returnBlock 
    for current_block in block_moved:
      bloc_and_line=returnBlock(current_block,list_object,bloc_and_line)
    
    #At this point, we know which blocks have moved and the line they belong  
    #IMPORTANT INFORMATION ABOUT RECORD:
    #There is a problem with absolute and relative coordinates, that is why we do not
    #directly use coordinates from bmoved, but only 'delta' which allows to find correct
    #coordinates 
    my_field = None
    prev_delta='' #we store the current delta in a formated string
    list_block_error = []
    errors = []
    error_result = {}
    prev_deltaX=0
    prev_deltaY=0
    deltaX = 0 
    deltaY = 0 
    correct = 1 # correct = 1 if the block is correct otherwise correct = 0
    new_object_planning = {} #structure returned
    for mblock in bloc_and_line:
      if old_delta2!=None:
        # For each block that has moved, we add its former coordinates and its delta
        if old_delta2.has_key(mblock[1].name):
          prev_deltaX=float(old_delta2[mblock[1].name][0])
          prev_deltaY=float(old_delta2[mblock[1].name][1])
      deltaX =float(mblock[0][3]) - float(mblock[0][1])+prev_deltaX 
      deltaY = float(mblock[0][4]) - float(mblock[0][2])+prev_deltaY
      widthblock= float(mblock[0][5])
      heightblock=float(mblock[0][6])
      if mblock[1].url!='':
        url = mblock[1].url
      else:
        url= mblock[2].url
      # several test to know if a block is correct. If it is not, wee add it to list_block_error.
      if mblock[1].begin <0:
        deltaX = (mblock[1].begin)*mblock[2].width + float(mblock[0][3]) +prev_deltaX
      # mblock[1] is a  block ; mblock[2] is a line
      if (mblock[1].marge_top)*mblock[2].height+mblock[2].top+deltaY >mblock[2].top+mblock[2].height:  
        correct = 0
      if (mblock[1].marge_top)*mblock[2].height+heightblock+mblock[2].top+deltaY< mblock[2].top:
        correct = 0
      if (mblock[1].begin)*mblock[2].width+widthblock+mblock[2].begin+deltaX <mblock[2].begin:
        correct = 0
      if (mblock[1].begin)*mblock[2].width + deltaX+ mblock[2].begin> mblock[2].begin + mblock[2].width:
        correct = 0
      if correct == 0:
        list_block_error.append(mblock)
        err = ValidationError(StandardError,mblock[1])
        errors.append(err)
        if prev_delta!='':
          prev_delta+='*'
        prev_delta+=str(mblock[1].name)+','+str(deltaX)+','+str(deltaY)
        # we store once again old_delta because we will need it when a block is moved again.     
      else:
        new_object_planning = convertDataToDate(mblock,x_axe,width_line, deltaX, 
                                                deltaY, url, new_object_planning,lineb)  
    REQUEST.set('list_block_error',list_block_error)
    REQUEST.set('old_delta1',prev_delta)
    if len(errors)>0:
      raise FormValidationError(errors,{})
    return new_object_planning

def convertDataToDate(mblock,x_axe,width_line, deltaX, deltaY, object_url,
                      new_object_planning, lineb):                 
  """this is in this method that we calculate new startdate & stopdate in order 
     to save them"""  
  delta_axe = (DateTime(x_axe[0][-1])-DateTime(x_axe[0][0]))
  #lineb is used to know where really starts the line due to problems with others html tags.
  begin = (mblock[2].begin - float(mblock[0][3])+(float(lineb)-mblock[2].begin))*(-1)
  length = float(mblock[0][5])
  axe_begin = DateTime(x_axe[0][0])
  coeff = float(delta_axe) / float(mblock[2].width)
  delta_start = begin * coeff
  delta_length = length * coeff
  new_start = axe_begin + delta_start
  new_stop=new_start + delta_length
  new_object_planning[object_url]={'start_date':new_start,'stop_date':new_stop}
  return new_object_planning    


PlanningBoxValidatorInstance=PlanningBoxValidator()        


def returnBlock(block_searched,planning_struct,block_and_line):
  """return a specific structre containing the block object and its line 
   thanks to its name"""
  for line in planning_struct:
    for block in line.content:
      if block.name == block_searched[0]:
        block_and_line.append([block_searched,block,line])   
        break
      else:
        if line.son!=[]:
          block_and_line = returnBlock(block_searched,line.son,block_and_line)
  return block_and_line

def convertStringToList(import_string):
  """ convert a string from this type 'name,x,y,w,h-name,x,y,w,h...' to a list"""
  list_moved= []
  r_List = import_string.split('*')
  for i in r_List:
    current_block = i.split(',')
    list_moved.append(current_block)
  return list_moved

def convertStringToDict(import_string):
  """ convert a string from this type name,x1,x2,x,y,w,h*name,x1,x2,x,y,w,h
      to list of dictionnaries where the key is the name""" 
  dic={}
  r_List=import_string.split('*')
  for i in r_List:
    current_block = i.split(',')
    dic[current_block[0]]=[current_block[1],current_block[2]]
  return dic    

  
def createLineObject(meta_types,selection,selection_name,field,REQUEST,list_method,
                     here,report_root_list,y_axis_width,width_line,space_line,
                     height_global_div,height_header,height_axis_x,form,current_top,portal_types):
  """creates Line Object and stores it in list_object"""
  report_sections = []
  filtered_portal_types = map(lambda x: x[0], portal_types)
  if len(filtered_portal_types) == 0:
    filtered_portal_types = None
  section_index = 0
  if len(report_sections) > section_index:
    current_section = report_sections[section_index]
  elif len(report_sections):
    current_section = report_sections[0]
  else:
    current_section = None
  filtered_meta_types = map(lambda x: x[0], meta_types)
  params = selection.getParams()
  sort = field.get_value('sort')
  selection.edit(default_sort_on = sort)
  kw=params
  report_depth = REQUEST.get('report_depth', None)
  is_report_opened = REQUEST.get('is_report_opened', selection.isReportOpened())
  portal_categories = getattr(form, 'portal_categories', None)
  if 'select_expression' in kw:
    del kw['select_expression']
  if hasattr(list_method, 'method_name'):
    if list_method.method_name == 'objectValues':
      list_method = here.objectValues
      kw = copy(params)
      kw['spec'] = filtered_meta_types
    else:
     # The Catalog Builds a Complex Query
      kw = {}
      if REQUEST.form.has_key('portal_type'):
        kw['portal_type'] = REQUEST.form['portal_type']
      elif REQUEST.has_key('portal_type'):
        kw['portal_type'] = REQUEST['portal_type']
      elif filtered_portal_types is not None:
        kw['portal_type'] = filtered_portal_types
      elif filtered_meta_types is not None:
        kw['meta_type'] = filtered_meta_types
      elif kw.has_key('portal_type'):
        if kw['portal_type'] == '':
          del kw['portal_type']
      # Remove useless matter
      for cname in params.keys():
        if params[cname] != '' and params[cname]!=None:
          kw[cname] = params[cname]
      # Try to get the method through acquisition
      try:
        list_method = getattr(here, list_method.method_name)
      except AttributeError:
        pass
  elif list_method in (None, ''): # Use current selection
    list_method = None
  select_expression = ''
  default_selection_report_path = report_root_list[0][0].split('/')[0]
  if default_selection_report_path in portal_categories.objectIds() or \
    (portal_domains is not None and default_selection_report_path in portal_domains.objectIds()):
    pass
  else:
    default_selection_report_path = report_root_list[0][0]          
  selection_report_path = selection.getReportPath(default = (default_selection_report_path,))
  if report_depth is not None:
    selection_report_current = ()
  else:
    selection_report_current = selection.getReportList()
  report_tree_list = makeTreeList(here=here, form=form, root_dict=None,report_path=selection_report_path,
                                  base_category=None,depth=0, 
                                  unfolded_list=selection_report_current, selection_name=selection_name, 
                                  report_depth=report_depth,
                                  is_report_opened=is_report_opened, sort_on=selection.sort_on,
                                  form_id=form.id)
  
  if report_depth is not None:
    report_list = map(lambda s:s[0].getRelativeUrl(), report_tree_list)
    selection.edit(report_list=report_list)
  report_sections = []
  list_object = []
  nbr_line=0
  object_list=[]    
  indic_line=0 
  index_line = 0
  blocks_object= {}  
  for object_tree_line in report_tree_list:      
    selection.edit(report = object_tree_line.getSelectDomainDict())            
    if object_tree_line.getIsPureSummary():
      original_select_expression = kw.get('select_expression')
      kw['select_expression'] = select_expression
      selection.edit( params = kw )
      if original_select_expression is None:
        del kw['select_expression']
      else:
        kw['select_expression'] = original_select_expression
    
    if object_tree_line.getIsPureSummary() and selection_report_path[0]=='parent':
      stat_result = {}
      index = 1
      report_sections += [object_tree_line]
      nbr_line+=1       
    else:
      # Prepare query
      selection.edit( params = kw )
      if list_method not in (None, ''):
        selection.edit(exception_uid_list=object_tree_line.getExceptionUidList())
        object_list = selection(method = list_method, context=here, REQUEST=REQUEST)
      else:
        object_list = here.portal_selections.getSelectionValueList(selection_name,
                                                          context=here, REQUEST=REQUEST)
      
      exception_uid_list = object_tree_line.getExceptionUidList()
      if exception_uid_list is not None:
      # Filter folders if this is a parent tree
        new_object_list = []
        for o in object_list:
        #LOG('exception_uid_list', 0, '%s %s' % (o.getUid(), exception_uid_list))
          if o.getUid() not in exception_uid_list:
            new_object_list.append(o)
                      
        object_list = new_object_list
      
      current_list=[]
      add = 1
      #a test with 'add' variable because maketreelist return two times the 
      #same object when it is open, don't know why...
      for object in report_sections:
        if getattr(object_tree_line.getObject(),'uid') == getattr(object.getObject(),'uid'):
          add = 0
          break  
      if add == 1:       
        report_sections += [object_tree_line] 
        nbr_line+=1
        for p in object_list:
          current_list.append(p.getObject())
        blocks_object[object_tree_line.getObject()]=current_list
  selection.edit(report=None)
  index = 0
  #we start to build our line object structure right here.
  index_report=0
  for line_report in report_sections:
    stat_result = {}
    stat_context = line_report.getObject().asContext(**stat_result)
    stat_context.domain_url = line_report.getObject().getRelativeUrl()
    stat_context.absolute_url = lambda x: line_report.getObject().absolute_url()     
    url=getattr(stat_context,'domain_url','')

    if line_report.getDepth() == 0:
      paternity = 1    
      height=(height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))/float(nbr_line)
      line = Line(title=line_report.getObject().getTitle(),
                   name='fra' + str(indic_line),
                   begin=y_axis_width,
                   width=width_line,
                   height=height,
                   top=current_top,color='#ffffff',
                   paternity=paternity,url=url)    
      list_object.append(line)
      
      if paternity == 0:
        height=(height_global_div-height_header-height_axis_x-
               ((nbr_line-1)*space_line))/(float(nbr_line)) + (space_line)  
        current_top=current_top+height

      else:
        if (index+1)<=(len(report_sections)-1): 
          if report_sections[index+1].getDepth()==0:
            height=((height_global_div-height_header-height_axis_x-
                   (((nbr_line-1))*space_line))/float(nbr_line))+ (space_line)
            current_top=current_top+height    
          else:
            height=((height_global_div-height_header-height_axis_x-
                   (((nbr_line-1))*space_line))/float(nbr_line))
            current_top=current_top+height 
    else:
      current_index = 0      
      while line_report.getDepth() == report_sections[index-current_index].getDepth():
        current_index += 1
      if report_sections[index-current_index].getDepth() == 0:
        current_top=list_object[len(list_object)-1].createLineChild(report_sections,field,
                                current_top,y_axis_width,width_line,space_line,height_global_div,
                                height_header,height_axis_x,nbr_line,index,url)
      else : # in this case wee add a son to a son
        depth=0 
        current_son=list_object[len(list_object)-1]
        while depth != (line_report.getDepth()-1):
          current_son=list_object[len(list_object)-1].son[len(list_object[len(list_object)-1].son)-1]
          depth+=1
        current_top=current_son.createLineChild(report_sections,field,current_top,y_axis_width,
                                                 width_line,space_line,height_global_div,height_header
                                                ,height_axis_x,nbr_line,index,url)    
    index += 1
    indic_line+=1
  return (list_object,nbr_line,report_sections,blocks_object)

def createGraphicCall(current_line,graphic_call):
  """ create html code of children used by graphic library to know which block can be moved.
      Refers to javascript library for more information"""
  for line in current_line.son:
    for block in line.content:
      if block.types=='activity' or block.types=='activity_error':
        graphic_call+='\"'+block.name+'\",'
      elif block.types=='info':
        graphic_call+='\"'+block.name+'\"+NO_DRAG,'   
    if line.son!=[]: # case of a son which has sons...
      graphic_call+=createGraphicCall(line,graphic_call)        
  return graphic_call
  
class PlanningBoxWidget(Widget.Widget):
    property_names = Widget.Widget.property_names +\
                     ['height_header', 'height_global_div','height_axis_x', 'width_line','space_line',
                     'list_method','report_root_list','selection_name','portal_types',
                     'meta_types','sort','title_line','y_unity','y_axis_width','y_range','x_range',
                     'x_axis_script_id','x_start_bloc','x_stop_bloc','y_axis_method','max_y',
                     'constraint_method','color_script','info_center','info_topleft','info_topright',
                     'info_backleft','info_backright','security_index']
    
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
                                description=(
        "space between each line of the graphic,not required"),
                                default=10,
                                required=0)   
                                
    report_root_list = fields.ListTextAreaField('report_root_list',
                                 title="Report Root",
                                 description=(
        "A list of domains which define the possible root."),
                                 default=[],
                                 required=0)
  
    selection_name = fields.StringField('selection_name',
                                 title='Selection Name',
                                 description=('The name of the selection to store'
                                              'params of selection'),
                                 default='',
                                 required=0)
                                 
    portal_types = fields.ListTextAreaField('portal_types',
                                 title="Portal Types",
                                 description=(
        "Portal Types of objects to list. Required."),
                                 default=[],
                                 required=0)
                                 
    meta_types = fields.ListTextAreaField('meta_types',
                                 title="Meta Types",
                                 description=(
        "Meta Types of objects to list. Required."),
                                 default=[],
                                 required=0)
                                                              
    sort = fields.ListTextAreaField('sort',
                                 title='Default Sort',
                                 description=('The default sort keys and order'),
                                 default=[],
                                 required=0)
  
    list_method = fields.MethodField('list_method',
                                 title='List Method',
                                 description=('The method to use to list'
                                             'objects'),
                                 default='searchFolder',
                                 required=0)                             

    title_line = fields.StringField('title_line',
                                title='specific method which fetches the title of each line: ',
                                description=('specific method for inserting title in line'),
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
                                 title='specific method which fetches the data for the beginning of a\
                                        block:',
                                 description=('Method for building X-Axis such as getstartDate'
                                              'objects'),
                                 default='getStartDate',
                                 required=0)	
    
    x_stop_bloc = fields.StringField('x_stop_bloc',
                                 title='specific method which fetches the data for the end of each block',
                                 description=('Method for building X-Axis such getStopDate'
                                              'objects'),
                                 default='',
                                 required=0)	

 
    y_axis_method = fields.StringField('y_axis_method',
                                 title='specific method of data type for creating height of blocks',
                                 description=('Method for building height of blocks'
                                              'objects'),
                                 default='',
                                 required=0) 
                                 

    max_y  = fields.StringField('max_y',
                                 title='specific method of data type for creating Y-Axis',
                                 description=('Method for building Y-Axis'
                                              'objects'),
                                 default='',
                                 required=0)

  
  
    constraint_method = fields.StringField('constraint_method',
                                          title='name of constraint method between blocks',
                                          description=('Constraint method between blocks'
                                                      'objects'),
                                          default='SET_DHTML',
                                          required=1)
  
    
    color_script = fields.StringField('color_script',
                                        title='name of script which allow to colorize blocks',
                                        description=('script for block colors'  
                                                    'objects'),                        
                                        default='',   
                                        required=0)  
    
    
    info_center = fields.StringField('info_center',
                                 title='specific method of data called for inserting info in block center',
                                 description=('Method for displaying info in the center of a block'
                                              'objects'),
                                 default='',
                                 required=0) 
   
    info_topright = fields.StringField('info_topright',
                                 title='specific method of data called for inserting info in block topright',
                                 description=('Method for displaying info in the topright of a block'
                                              'objects'),
                                 default='',
                                 required=0)
                                 
    info_topleft = fields.StringField('info_topleft',
                                 title='specific method of data called for inserting info in block topleft',
                                 description=('Method for displaying info in the topleft corner of a block'
                                              'objects'),
                                 default='',
                                 required=0)                             
                                 
    info_backleft = fields.StringField('info_backleft',
                                 title='specific method of data called for inserting info in block backleft',
                                 description=('Method for displaying info in the backleft of a block'
                                              'objects'),
                                 default='',
                                 required=0)
    info_backright = fields.StringField('info_backright',
                                 title='specific method of data called for inserting info in block backright',
                                 description=('Method for displaying info in the backright of a block'
                                              'objects'),
                                 default='',
                                 required=0)
   
    security_index = fields.IntegerField('security_index',
                                title='variable depending of the type of web browser :',
                                description=("This variable is used because the rounds of each\
                                              web browser seem to work differently"),
                                default=2,
                                required=0) 	 
                                                                                       
    def render_css(self, field, key, value, REQUEST):
        """In this method we build our structure object, then we return all the style sheet of each div"""
        
        # DATA DEFINITION 
        height_header = field.get_value('height_header')
        height_global_div = field.get_value('height_global_div')
        height_axis_x=field.get_value('height_axis_x')
        width_line = field.get_value('width_line')
        space_line = field.get_value('space_line')
        selection_name = field.get_value('selection_name')
        security_index = field.get_value('security_index')
        y_unity = field.get_value('y_unity')
        y_axis_width = field.get_value('y_axis_width')
        y_range = field.get_value('y_range')
        portal_types= field.get_value('portal_types')
        meta_types = field.get_value('meta_types')
        x_range=field.get_value('x_range')
        here = REQUEST['here']
        title=field.get_value('title')
        list_method = field.get_value('list_method')
        report_root_list = field.get_value('report_root_list')
        scriptY = getattr(here,field.get_value('max_y'),None)
        script=getattr(here,field.get_value('x_axis_script_id'),None)
        block_height= getattr(here,field.get_value('y_axis_method'),None)
        constraint_method = field.get_value('constraint_method')
        color_script = getattr(here,field.get_value('color_script'),None)
        #info inside a block
        
        info_center = field.get_value('info_center')
        info_topleft = field.get_value('info_topleft')        
        info_topright = field.get_value('info_topright')
        info_backleft = field.get_value('info_backleft')
        info_backright = field.get_value('info_backright')

        object_start_method_id = field.get_value('x_start_bloc')
        object_stop_method_id= field.get_value('x_stop_bloc')
        form = field.aq_parent
        sort = field.get_value('sort')   
        x_occurence=[] # contains datas of start and stop of each block like
                       # this [ [ [x1,x2],[x1,x2] ],[ [x1,x2],[x1,x2] ],.....] 
                       #it is not directly coordinates but datas.                    
        x_axe=[] # will contain what wee need to display in X-axis.
        yrange=[] # we store the value in Y-axis of each block 
        nbr=1
        blocks_object={}      
        current_top=height_header
        line_list=[] #in this list we store all the objects of type Line
        giant_string='' #will contain all the html code.
        report_sections=[]
        list_error=REQUEST.get('list_block_error')
        old_delta=[REQUEST.get('old_delta1'),REQUEST.get('old_delta2')]
        # END DATA DEFINITION                         
        
        # we fetch fold/unfold datas 
        #here.portal_selections.setSelectionFor(selection_name, None)#uncoment to put selection to null
        selection = here.portal_selections.getSelectionFor(selection_name, REQUEST=REQUEST)
        default_params = {}
        if selection is None:
          selection = Selection(params=default_params, default_sort_on = sort)
        else:
          selection.edit(default_sort_on = sort)
          selection.edit(sort_on = sort)       
        here.portal_selections.setSelectionFor(selection_name, selection, REQUEST=REQUEST)
        # we check what is the current zoom in order to redefine height & width
        if selection is None:
          current_zoom = 1
        else:
          current_zoom = selection.getZoom()
        current_zoom= float(current_zoom)
        if current_zoom<=1:
          height_global_div = round(height_global_div * current_zoom)
          width_line = round(width_line * current_zoom)
          space_line = round(space_line * current_zoom)  
        #we build lines 
        (line_list,nbr_line,report_sections,blocks_object)=createLineObject(meta_types=meta_types,
                                                                selection=selection,
                                                                selection_name=selection_name,field=field,
                                                                REQUEST=REQUEST,list_method=list_method,
                                                                here=here,report_root_list=report_root_list,
                                                                y_axis_width=y_axis_width,
                                                                width_line=width_line,space_line=space_line,
                                                                height_global_div=height_global_div,
                                                                height_header=height_header,
                                                                height_axis_x=height_axis_x,form=form,
                                                                current_top=current_top,
                                                                portal_types=portal_types)
        #we build x_occurence (used for the range in x-Axis 
        
        for tree_list_object in report_sections:
          method_start = getattr(tree_list_object.getObject(),object_start_method_id,None)
          method_stop= getattr(tree_list_object.getObject(),object_stop_method_id,None)
          if method_start!=None:
            block_begin = method_start()
          else:
            block_begin = None
          
          if method_stop!=None:
            block_stop= method_stop()
          else:
            block_stop=None
          
          if block_begin!=None:# and block_stop!=None:  
            x_occurence.append([block_begin,block_stop])
          
          if method_start == None and report_sections!={}:
            for Ablock in blocks_object:
              for object_content in blocks_object[Ablock]:
                method_start = getattr(object_content,object_start_method_id,None)
                method_stop= getattr(object_content,object_stop_method_id,None)
              
                if method_start!=None:
                  block_begin = method_start()
                else:
                  block_begin = None
            
                if method_stop!=None:
                  block_stop= method_stop()
                else:
                  block_stop=None
              
                if block_begin!=None:# and block_stop!=None:
                  x_occurence.append([block_begin,block_stop])
          
        params=selection.getParams()
        start=params.get('list_start')
        
        x_axe=script(x_occurence,x_range,float(current_zoom),start)
        #x_axe[0] is a list of chronological dates that wich represents the 
        #the range of the graphic.for example: 
        #x_axis=[['2005/11/04','2005/12/04' etc.],['april','may','june' etc.]
        #,start_delimiter,delta]
        # we add mobile block to the line object 
        
        y_max= 1
        current_max = 1
        if scriptY != None:
          for s in report_sections:
            current_max=scriptY(s.getObject())
            if current_max > y_max:
              y_max = current_max
        else:
          y_max = 1

        indic_line=0
        while indic_line != len(report_sections):
          for object_line in line_list:
            if object_line.title == report_sections[indic_line].getObject().getTitle():
              if line_list != [] and report_sections[indic_line].getDepth()==0:
                object_line.insertActivityBlock(line_content=report_sections[indic_line].getObject(),
                                      object_start_method_id=object_start_method_id,
                                      object_stop_method_id=object_stop_method_id,
                                      x_axe=x_axe,field=field,info_center=info_center,
                                      info_topright=info_topright,info_topleft=info_topleft,
                                      info_backleft=info_backleft,info_backright=info_backright,
                                      list_error=list_error,old_delta=old_delta,REQUEST=REQUEST,
                                      blocks_object=blocks_object,width_line=width_line,
                                      script_height_block=block_height,y_max=y_max,color_script=color_script)                                                      
                break
          indic_line+=1
        # At this point line_list contains our tree of datas. Then we
        # add others labels, indicators etc. for the graphic.

        #One constructs the vertical dotted line
        if x_axe != []:        
          marge_left=y_axis_width+width_line/float(len(x_axe[1]))
          for i in line_list:
            i.appendVerticalDottedLine(x_axe,width_line,marge_left)

        #one constructs the maximum horizontal dotted line 10px under the top of the line
        maximum_y=y_max
        marge_top=10
        if y_range!=0:
          for i in line_list:  
            i.appendHorizontalDottedLine(marge_top,maximum_y,height_global_div,height_header,
                                         height_axis_x,nbr_line,y_range,y_max)
        #end construct of horizontal dotted line 

        # we construct y-axis
        way=[]    
        y=[] #we store here the objects for creating y-axis 
        level=0
        current_top=height_header
        idx=0
        
        for i in line_list:
          current_top=i.buildYtype(way=way,y=y,level=level,y_axis_width=y_axis_width,
                                   height_global_div=height_global_div,height_header=height_header,
                                   height_axis_x=height_axis_x,nbr_line=nbr_line,current_top=current_top,
                                   space_line=space_line,y_max=y_max,y_range=y_range,
                                   y_unity=y_unity,selection_name=selection_name,form=form)  
          height=((height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))/\
                 float(nbr_line))+space_line
          current_top=y[-1].top+height
          idx+=1
        line_list=y+line_list #we need to add the y-axis block at the beginning of our structure
                                  #otherwise the display is not correct;don't know why...

        #build X axis 
        line_list.append(Line('','axis_x',y_axis_width,width_line,height_axis_x,\
                                current_top-space_line)) 
        line_list[-1].createXAxis(x_axe,width_line,y_axis_width)
        if x_axe!=[]:
          x_subdivision=width_line/float(len(x_axe[1]))
        else:
          x_subdivision = 0
        REQUEST.set('line_list',line_list)  
        REQUEST.set('report_root_list',report_root_list)
        REQUEST.set('selection_name',selection_name)
        REQUEST.set('x_axe',x_axe)
        REQUEST.set('start',start)
        REQUEST.set('delta1',old_delta[0])
        REQUEST.set('delta2',old_delta[1])
        REQUEST.set('constraint_method',constraint_method)
        for i in line_list:
          giant_string+=i.render_css(y_axis_width,security_index,x_subdivision)   
        return giant_string
    
    def render(self,field, key, value, REQUEST):
        """ this method return a string called 'giant_string' wich contains the planningbox html
            of the web page""" 
        here = REQUEST['here']
        portal_url= here.portal_url()
        title=field.get_value('title')
        line_list = REQUEST.get('line_list')
        x_axe = REQUEST.get('x_axe')  
        width_line = field.get_value('width_line')
        start_page=REQUEST.get('list_start')
        height_global_div = field.get_value('height_global_div')
        y_axis_width = field.get_value('y_axis_width')
        report_root_list=REQUEST.get('report_root_list')
        selection_name = field.get_value('selection_name')
        start_page=REQUEST.get('start')
        report_root_list = field.get_value('report_root_list')
        constraint_method=REQUEST.get('constraint_method')
        #the following javascript function allows to know where is exactly situated 
        #the beginning of lines in absolute coordinates since we have problems due to 
        #others tags (form,tr,table...) which are declared previously in the html.    
        
        giant_string="""<script type="text/javascript">
        function setLineBegin()
        {
        document.forms["main_form"]["line_begin"].value = document.getElementById("fra0").offsetLeft;
        }
        window.onmousemove = setLineBegin;
        </script>"""
        
        # we record current delta in delta1, and we record old_delta in delta2
        odelta=[REQUEST.get('delta1'),REQUEST.get('delta2')]
        selection = here.portal_selections.getSelectionFor(selection_name, REQUEST=REQUEST)
        giant_string+='<input type=\"hidden\" name=\"list_selection_name\" value='+selection_name+' />\n'
        
        #header of the graphic###
        giant_string+='<div id=\"header\" style=\"position:absolute;width:'+str(width_line+y_axis_width)+\
                      'px;height:'+str(height_global_div)+'px;background:#d5e6de;margin-left:0px;\
                       border-style:solid;border-color:#000000;border-width:1px;margin-top:1px\">\
                       <table><tr><td><h3><u>'+title+'</h3></u></td><td>'

        selection = here.portal_selections.getSelectionFor(selection_name, REQUEST=REQUEST)
        if selection is None:
          selection_report_path = report_root_list[0]
        else:  
          selection_report_path = selection.getReportPath()
        
        report_tree_options = ''
        for c in report_root_list:
          if c[0] == selection_report_path:
            report_tree_options += """<option selected value="%s">%s</option>\n""" % (c[0], c[1])
          else:
            report_tree_options += """<option value="%s">%s</option>\n""" % (c[0], c[1])
        
        report_popup = """<select name="report_root_url"
                       onChange="submitAction(this.form,'%s/portal_selections/setReportRoot')">
                       %s</select></td>\n""" % (here.getUrl(),report_tree_options)
        giant_string += report_popup
        
        #now we declare zoom widget 
        if selection != None:
          current_zoom=selection.getZoom()
        else:
          current_zoom = 1
        zoom=(0.25,0.5,0.75,1,2,4,8,10)
        zoom_select= """<td>
              <select name="zoom" onChange="submitAction(this.form,'"""
        zoom_select+=here.getUrl()+ '/portal_selections/setZoom\')">'
        for z in zoom:
          if z == float(current_zoom):
            zoom_select+='<option selected value=\"'+str(z)+'\">x'+str(z)+'</option>\n'
          else:
            zoom_select+='<option value=\"'+str(z)+'\">x'+str(z)+'</option>\n'
        giant_string += zoom_select
        
        
        #now the page number widget 
        pages='</select></td><td><select name="list_start" title=Change  \
        onChange="submitAction(this.form,\''+here.getUrl()+'/portal_selections/setPage\')">'
        selected=''
        date_planning=''
        if x_axe!=[]:
          x_planning=x_axe[2]
          delta=x_axe[3]
          if isinstance(x_planning, DateTime):
            date_planning = x_planning
            for p in range(1,float(current_zoom)+1):
              if x_planning == start_page :
                selected= 'selected '
              else:
                selected= '' 
              pages+='<option '+selected+'value=\"'+str(date_planning.Date())+'\">'+str(p)+' of '\
                     +str(current_zoom)+'</option>\n'
              date_planning+=delta
              x_planning=date_planning.Date()
          else:
            for p in range(1,float(current_zoom)+1):
              axe_index = 0
              while x_planning != x_axe[0][axe_index]:
                axe_index+=1 
              
              if x_planning == start_page :
                selected= 'selected '
              else:
                selected= '' 
              pages+='<option '+selected+'value=\"'+str(x_axe[0][axe_index])+'\">'+str(p)+' of '\
                     +str(current_zoom)+'</option>\n'
              axe_index = axe_index + delta       
              current_item = x_axe[0][axe_index]
        else:
          x_planning=[]
          delta=0
  
        pages+='</select></td></tr></table></div>\n'        
        giant_string += pages 
        #just because setPage wants it
        giant_string += '<input type=\"hidden\" name=\"listbox_uid:list\">\n'
        #we change old_delta2 to  old_delta1
        giant_string += '<input type=\"hidden\" name=\"old_delta1\" value=\"'+str(odelta[0])+'\">\n'
        giant_string += '<input type=\"hidden\" name=\"old_delta2\" value=\"'+str(odelta[0])+'\">\n' 
        giant_string+= '<input type=\"hidden\" name=\"block_moved\">\n'
        giant_string+= '<input type=\"hidden\" name=\"line_begin\">\n'

        for i in range(0,len(line_list)):
          giant_string+=line_list[i].render(portal_url,y_axis_width)    

        #here is the declaration of four divs which are used for redimensionning
        giant_string+='<div id=\"top\" style=\"position:absolute;width:5px;height:5px;\
                        background:#a45d10\"></div>\n'
        giant_string+='<div id=\"right\" style=\"position:absolute;width:5px;height:5px;\
                        background:#a45d10"></div>\n'
        giant_string+='<div id=\"bottom\" style=\"position:absolute;width:5px;height:5px\
                       ;background:#a45d10\"></div>\n'
        giant_string+='<div id=\"left\" style=\"position:absolute;width:5px;height:5px;\
                       background:#a45d10\"></div>\n'
        giant_string+='<script type=\"text/javascript\">\n'+ constraint_method + '('

        for i in range(0,len(line_list)):
          graphic_call=''
          for j in line_list[i].content:
            if j.types=='activity' or j.types=='activity_error':
              giant_string+='\"'+j.name+'\",'
            elif j.types=='info':
              giant_string+='\"'+j.name+'\"+NO_DRAG,'
          current_object=line_list[i]
          if current_object.son!=[]:  
           giant_string+=createGraphicCall(current_object,graphic_call)     
        giant_string+='\"top\"+CURSOR_N_RESIZE+VERTICAL, \"right\"+CURSOR_E_RESIZE+HORIZONTAL,\
                       \"bottom\"+CURSOR_S_RESIZE+VERTICAL,\
                       \"left\"+CURSOR_W_RESIZE+HORIZONTAL);\n'
        giant_string+='</script> </div> \n '
        return giant_string  

# class line 
class Line:
  """objects which represent a line directly in a planningbox"""
  def __init__(self,title='',name='',begin=0,width=0,height=0,top=0,color='',son=None,y_type='none',
               paternity=0,url=''):  
    """used for building a Line object"""
    if son is None:
     son = []
    self.title=title
    self.name=name
    self.begin=begin
    self.width=width
    self.height=height
    self.top=top
    self.content=[]
    self.color=color
    self.son=son
    self.y_type=y_type
    self.paternity=paternity
    self.url=url

  def render(self,portal_url,y_axis_width):
    """ creates "pure" html code of the line, its Block, its son """
    html_render='<div id=\"'+self.name+'\"></div>\n'
    for block in self.content:
      if block.types=='activity' or block.types=='activity_error':
        #checks if the block starts before the beginning of the line               
        if ((self.begin+block.begin*self.width) < self.begin): 
          html_render+='<div id=\"'+block.name+'\" ondblclick=\"showGrips()\" onclick=\"if (dd.elements.'\
                       +block.name+'.moved==0){dd.elements.'+block.name+'.moveBy('+\
                       str(round(block.begin*self.width))+',0);dd.elements.'+block.name+'.resizeTo('+\
                       str(round(block.width*self.width))+','+ str(block.height*(self.height-10))+\
                       ');dd.elements.'+block.name+'.moved=1;} \">'
        # "done" is used because otherwise everytime we move the block it will execute moveby()
        #checks if the block is too large for the end of the line if it is the case, one cuts the block
        elif ((block.width*self.width)+(self.begin+block.begin*self.width)>self.width+y_axis_width): 
          html_render+='<div id=\"'+block.name+'\" ondblclick=\"showGrips()\" onclick=\"dd.elements.'\
                       +block.name+'.resizeTo('+str(round(block.width*self.width))+','\
                       +str(block.height*(self.height-10))+') \">'
        else:
          html_render+='<div id=\"'+block.name+'\" ondblclick=\"showGrips()\">'      
        # we add info Block inside the div thanks to the render method of the Block class
        html_render+=block.render(self.width,self.height,portal_url,self.begin,y_axis_width,self)      
        html_render+='</div>\n'
      elif block.types!='info':
        html_render+='<div id=\"'+block.name+'\">'+str(block.text)+'</div>\n'      
    if self.son!=[]:
      for i in self.son:
        html_render+=i.render(portal_url,y_axis_width)      
    return html_render    
    
    
  def render_css(self,y_axis_width,security_index,x_subdivision):
    """creates style sheet of each div which represents a Line instance """
    css_render='#'+self.name+'{position:absolute;\nborder-style:solid;\nborder-color:#53676e;\
                               \nborder-width:1px;\n'
    data={}
    if self.color!='':
      css_render+='background:'+str(self.color)+';\n'
    css_render+='height:'+str(self.height)+'px;\n'
    css_render+='margin-left:'+str(self.begin)+'px;\n'
    css_render+='margin-top:'+str(self.top)+'px;\n'
    if self.y_type=='father1':
      css_render+='border-bottom-width:0px;'
    elif self.y_type=='son1':
      css_render+='border-top-width:0px;\nborder-bottom-width:0px;\n'    
    elif self.y_type=='son2':
      css_render+='border-top-width:0px;'
    css_render+='width:'+str(self.width)+'px;\n}'
    for block in self.content: #we generate block's css
      if block.types=='activity' or block.types=='activity_error':
        if block.types=='activity':
          css_render+='#'+block.name+'{position:absolute;\nbackground:'+block.color+';\nborder-style:solid;\
                      \nborder-color:#53676e;\nborder-width:1px;\n'
        if block.types=='activity_error':
          css_render+='#'+block.name+'{position:absolute;\nbackground:'+block.color+';\nborder-style:solid;\
                      \nborder-color:#ff0000;\nborder-width:1px;\n'
        css_render+='height:'+str((block.height*(self.height-10))-security_index)+'px;\n' 
        #-10 because wee don't want a block sticked to border-top of the line
        if ((self.begin+block.begin*self.width) < self.begin) and block.types!='activity_error': 
        #checks if the block starts before the beginning of the line
          css_render+='margin-left:'+str(self.begin)+'px;\n' 
          css_render+='width:'+str((block.width*self.width+block.begin*self.width))+'px;\n' 
        #checks if the block is too large for the end of the line. if it is the case, one cuts the block  
        elif ((block.width*self.width)+(self.begin+block.begin*self.width)>self.width+y_axis_width) and \
               block.types!='activity_error': 
          css_render+='width:'+str(round(block.width*self.width)-((self.begin+block.begin*self.width+
          block.width*self.width)-(self.width+y_axis_width)))+'px;\n'
          css_render+='margin-left:'+str(round(self.begin+block.begin*self.width))+'px;\n' 
        else:  
          css_render+='width:'+str(round(block.width*self.width))+'px;\n'
          css_render+='margin-left:'+str(round(self.begin+block.begin*self.width))+'px;\n' 
        css_render+='margin-top:'+str(self.top+10+block.marge_top*(self.height-10))+'px;}\n'
        # we add info Block inside the div  
        css_render+=block.render_css(self.width,self.height,self,y_axis_width)       
        
      elif block.types=='text_x' : 
        data={'border-style:':'solid;','border-color:':'#53676e;','border-width:':'1px;',
              'margin-left:':str(block.begin)+'px;',
              'margin-top:':str(round(1+self.top+self.height/2))+'px;'}
        
      elif block.types=='text_y':
        data={'border-style:':'solid;','border-color:':'#53676e;','border-width:':'0px;',  
              'margin-left:':str(self.width/4)+'px;',
              'margin-top:':str(round(1+self.top+self.height/2))+'px;'}


      elif block.types=='vertical_dotted':
        data={'border-style:':'dotted;','border-color':'#53676e;',
              'margin-left:':str(block.begin)+'px;','margin-top:':str(1+round(self.top))+'px;',
              'height:':str(self.height)+'px;',
              'border-left-width:':'1px;','border-right-width:':'0px;','border-top-width:':'0px;',    
              'border-bottom-width:':'0px;'}

      elif block.types=='horizontal_dotted': 
        data={'border-style:':'dotted;','border-color:':'#53676e;',
               'margin-left:':str(self.begin)+'px;','margin-top:':str(self.top+block.marge_top)+'px;',
               'border-left-width:':'0px;','border-right-width:':'0px;',
               'border-top-width:':'1px;','border-bottom-width:':'0px;',
               'width:':str(self.width)+'px;'}

      elif block.types=='y_coord':
        data={'border-style:':'solid;','border-color:':'#53676e;','border-width:':'0px;',
               'margin-left:':str(self.width-(len(block.text)*5))+'px;',
               'margin-top:':str(self.top+block.marge_top)+'px;',
               'height:':'','border-left-width:':'1px;','border-right-width:':'0px;',
               'border-top-width:':'0px;','border-bottom-width':'0px;','font-size:':'9px;'}
            
      elif block.types=='vertical':
        data={'border-style:':'solid;','border-color:':'#53676e;',
              'margin-left:':str((self.width/4)+block.begin)+'px;',
              'margin-top:':str(round(self.top)-self.height/2+13)+'px;',
              'height:':str(block.height)+'px;','border-left-width:':'1px;',
              'border-right-width:':'0px;','border-top-width:':'0px;', 
              'border-bottom-width:':'0px;'}
                       
      elif block.types=='horizontal':
        data={'border-style:':'solid;','border-color:':'#53676e;',
              'margin-left:':str((self.width/4)+block.begin)+'px;',
              'margin-top:':str(round(1+self.top+self.height/2))+'px;',
              'height:':'1px;','border-left-width:':'0px;','border-right-width:':'0px;',
              'border-top-width:':'1px;','border-bottom-width:':'0px;','width:':'16px;','height:':'1px;',
             }      

      if block.types!='activity':
        if block.types!='activity_error':
          if block.types!='info':
            css_render+='#'+block.name+'{position:absolute;\n'
            for key in data:
              css_render+=key + data[key] + '\n'
            css_render+='}\n'  

    if self.son!=[]:
      for i in self.son:
        css_render+=i.render_css(y_axis_width,security_index,x_subdivision);
    return css_render      

  def addBlock(self,name,block,error=0):
    """just create and add a block inside 'content' attribut of a Line instance""" 
    type_block=''
    if error == 0:
      type_block='activity'
    else:
      type_block='activity_error'
    self.content.append(Block(type_block,name=name,begin=block[0],width=block[1],height=block[2],text='',
                              content=block[3],marge_top=block[4],url=block[5],color=block[6]))
    
    
  def addBlockInfo(self,name):
    """add a block info inside an activity block"""
    self.content.append(Block('info',name,0,0,0,''))
    
  def addBlockTextY(self,name,text):
    """ add a text  block in y-axis"""
    self.content.append(Block('text_y',name,0,0,0,text))  
  
  def addBlockCoordY(self,name,text,marge_top):
    """ add a text block in y-axis (coordinates) """
    self.content.append(Block('y_coord',name,0,0,0,text,{},marge_top))  
    
  def addBlockTextX(self,name,begin,text):
    """ add a text block in x-axis"""
    self.content.append(Block('text_x',name,begin,0,0,text))    
    
  def addBlockDottedVert(self,name,begin):
    """ add a vertical dotted line"""
    self.content.append(Block('vertical_dotted',name,begin,0,0,''))  
    
  def addBlockDottedHoriz(self,name,marge_top):
    """append a dotted horizontal block"""
    self.content.append(Block('horizontal_dotted',name,0,0,0,'',{},marge_top))   
  
  def addBlockVertical(self,name,marge_top,height,marge_left):
    """append a vertical block(line)""" 
    self.content.append(Block('vertical',name,marge_left,0,height,'',{},marge_top)) 
     
  def addBlockHorizontal(self,name,marge_top,height,marge_left):
    """append a horizontal  block (line)""" 
    self.content.append(Block('horizontal',name,marge_left,0,height,'',{},marge_top))    
         
  def appendVerticalDottedLine(self,x_axe,width_line,marge_left):
    """append a vertical dotted  block"""
    current_marge=marge_left
    indic=0
    for j in x_axe[1]:
      nameblock='Block_vert_'+self.name+str(indic)
      self.addBlockDottedVert(nameblock,current_marge)
      current_marge+=width_line/float(len(x_axe[1]))   
      indic+=1
    if self.son!=[]:
      for i in self.son:
        i.appendVerticalDottedLine(x_axe,width_line,marge_left) 
      
  def buildYtype(self,way=[],y=[],level=0,y_axis_width=0,height_global_div=0,height_header=0,
                 height_axis_x=0,nbr_line=0,current_top=0,space_line=0,y_max=0,y_range=0,
                 y_unity=0,selection_name='',form=0): 
    """ used for determining the type of each part of y axis taking into account father and children
       'way' is a list whichs allows to determinate if the current block is a type 'son1' or 'son2'.
        y parameter is a list which contains all the objects for creating y-axis.  

    """
    report_url=self.url
    if level==0:
      name='axis'+str(self.name)
      if self.son!=[]:
        y.append(Line('',name,1,y_axis_width,
                ((height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))/float(nbr_line)),
                current_top,'',[],'father1'))
      else:
        y.append(Line('',name,1,y_axis_width,((height_global_div-height_header-height_axis_x-\
        ((nbr_line-1)*space_line))/float(nbr_line)),current_top,'',[],'father2'))
        
      if self.paternity==1:
        if self.son!=[]:
          y[-1].addBlockTextY('ytext'+name,str(3*'&nbsp '*level)+\
          '<a href="portal_selections/foldReport?report_url='+report_url+'&form_id='+\
          form.id+'&list_selection_name='+selection_name+'">-'+self.title+'</a>')
        else:
          y[-1].addBlockTextY('ytext'+name,str(3*'&nbsp '*level)+\
          '<a href="portal_selections/unfoldReport?report_url='+\
          report_url+'&form_id='+form.id+'&list_selection_name='+\
          selection_name+'">+'+self.title+'</a>')
      else:
        y[-1].addBlockTextY('ytext'+name,str(3*'&nbsp '*level)+self.title)
      
      #one constructs the indicators
      if y_range!=0:
        y[-1].createIndicators(y_unity,y_range,y_max,height_global_div,height_header,height_axis_x,nbr_line)
      
      if self.son!=[]:
        level+=1
        for j in range(0,len(self.son)):
          if j==(len(self.son)-1):
            way.append(1)
          else:
            way.append(0)
          current_top+=((height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))/
                       float(nbr_line))  
         
          current_top=self.son[j].buildYtype(way=way,y=y,level=level,y_axis_width=y_axis_width,
                                             height_global_div=height_global_div,
                                             height_header=height_header,
                                             height_axis_x= height_axis_x,nbr_line=nbr_line,
                                             current_top=current_top,space_line=space_line,
                                             y_max=y_max,y_range=y_range,
                                             y_unity=y_unity,selection_name=selection_name,form=form)
          del way[-1]
  
    else:
      if self.son!=[]:
        name=str(self.name)
        for num in way:
          name=name+str(num)
        y.append(Line('',name,1,y_axis_width,((height_global_div-height_header-height_axis_x)/float(nbr_line))
                      ,current_top,'',[],'son1'))

        if self.paternity==1:
          if self.son!=[]:
            y[-1].addBlockTextY('ytext'+name,str(3*'&nbsp '*level)+\
                                      '<a href="portal_selections/foldReport?report_url='+report_url+\
                                      '&form_id='+form.id+'&list_selection_name='+selection_name+'">-'+\
                                      self.title+'</a>')
          else:
            y[-1].addBlockTextY('ytext'+name,str(3*'&nbsp '*level)+\
                                      '<a href="portal_selections/unfoldReport?report_url='+report_url+\
                                      '&form_id='+form.id+'&list_selection_name='+selection_name+'">+'\
                                      +self.title+'</a>') 
        else:
          y[-1].addBlockTextY('ytext'+name,str(3*'&nbsp '*level)+self.title)

        # one constructs the stick
        y[-1].addBlockVertical('stickVer'+name,current_top-
                                    ((height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))\
                                    /float(nbr_line)),
                                    (height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))\
                                    /float(nbr_line),3*level*5-18) 
                                     #5 is the width of the standart font, maybe a future parameter
        y[-1].addBlockHorizontal('stickHor'+name,current_top-
                                    ((height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))\
                                    /float(nbr_line)),
                                    (height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))\
                                    /float(nbr_line),3*level*5-18) 
        #one constructs the indicators
        if y_range!=0:
          y[-1].createIndicators(y_unity,y_range,y_max,height_global_div,height_header,height_axis_x,nbr_line)
        level+=1
        for j in range(0,len(self.son)):
          current_top+=((height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))/\
                       float(nbr_line))
          if j==(len(self.son)-1):
            way.append(1)
          else:
            way.append(0)
          current_top=self.son[j].buildYtype(way=way,y=y,level=level,y_axis_width=y_axis_width,
                                             height_global_div=height_global_div,
                                             height_header=height_header,height_axis_x=height_axis_x,
                                             nbr_line=nbr_line,current_top=current_top,
                                             space_line=space_line,y_max=y_max,y_range=y_range,
                                             y_unity=y_unity,selection_name=selection_name,form=form)
          del way[-1]
      else:
        name=str(self.name)
        test='true'
        for num in way:
          name=name+str(num)
          if num==0:
            test='false'
        if test=='true':
          y.append(Line('',name,1,y_axis_width,((height_global_div-height_header-height_axis_x-\
                       ((nbr_line-1)*space_line))/float(nbr_line)),current_top,'',[],'son2'))
        else:
          y.append(Line('',name,1,y_axis_width,((height_global_div-height_header-height_axis_x-\
                       ((nbr_line-1)*space_line))/float(nbr_line)),current_top,'',[],'son1'))
          
        if self.paternity==1:
          if self.son!=[]:
            y[-1].addBlockTextY('ytext'+name,str(3*'&nbsp '*level)+
            '<a href="portal_selections/foldReport?report_url='+report_url+
            '&form_id='+form.id+'&list_selection_name='+selection_name+'">-'+self.title+'</a>')
          else:
            y[-1].addBlockTextY('ytext'+name,str(3*'&nbsp '*level)+
            '<a href="portal_selections/unfoldReport?report_url='+report_url+
            '&form_id='+form.id+'&list_selection_name='+selection_name+'">+'+self.title+'</a>')
            
        else:
          y[-1].addBlockTextY('ytext'+name,str(3*'&nbsp '*level)+self.title)  
  
        # one constructs the sticks
        y[-1].addBlockVertical('stickVer'+name,current_top-((height_global_div-height_header-\
                               height_axis_x-((nbr_line-1)*space_line))/float(nbr_line)),
                               (height_global_div-height_header-height_axis_x)/float(nbr_line),\
                               3*level*5-18)  
        y[-1].addBlockHorizontal('stickHor'+name,current_top-((height_global_div-height_header\
                                 -height_axis_x-((nbr_line-1)*space_line))/float(nbr_line)),
                                 (height_global_div-height_header-height_axis_x)/float(nbr_line),\
                                 3*level*5-18) 
        #one constructs the indicators   
        if y_range!=0:
          y[-1].createIndicators(y_unity,y_range,y_max,height_global_div,height_header,\
                                 height_axis_x,nbr_line)
    return current_top      

  def createIndicators(self,y_unity,y_range,y_max,height_global_div,height_header,\
                       height_axis_x,nbr_line):
    """creates a blocks used for y-axis coordinates"""
    
    maximum_y=y_max
    marge_top=0
    indic=0
    while maximum_y>=0:
      nameblock='Block_'+self.name+str(indic)
      text=str('%.2f' %maximum_y)+y_unity    
      self.addBlockCoordY(nameblock,text,marge_top) 
      maximum_y=maximum_y-(y_max/float(y_range)) 
      marge_top+=(((height_global_div-height_header-height_axis_x)/float(nbr_line))-10)/y_range 
      indic+=1


  def appendHorizontalDottedLine(self,marge_top,maximum_y,height_global_div,height_header,
                                 height_axis_x,nbr_line,y_range,y_max): 
    """creates a horizontal dotted line """
    current_top=marge_top
    max_y=maximum_y
    indic=0
    if y_range !=0:
      while max_y>=0:
        nameblock='Block_hor_'+self.name+str(indic)
        self.addBlockDottedHoriz(nameblock,current_top) 
        max_y=max_y-(y_max/float((y_range-1)))  #-1 because we don't want a dotted line on the X-axis
        #10px under the top of the line . float is important here!
        current_top+=(((height_global_div-height_header-height_axis_x)/float(nbr_line))-marge_top)/y_range
        indic+=1
      if self.son!=[]:
        for i in self.son:
          i.appendHorizontalDottedLine(marge_top,maximum_y,height_global_div,
                                       height_header,height_axis_x,nbr_line,y_range,y_max)
     
  def appendActivityBlock(self,list_block,list_error,old_delta,REQUEST):
    """create an activity block"""
    indic=0
    name_block=''
    prev_deltaX=0
    prev_deltaY=0
    old_delta2=old_delta[1]
    if old_delta2!='None' and old_delta2!=None:
      if old_delta2!='':
        if old_delta2!={}:
          old_delta2=convertStringToDict(old_delta2)
    else:
      old_delta2={}  
    
    for data_block in list_block:
      name_block='ActivityBlock_'+self.name+'_'+str(indic)
      if list_error != None: 
        for blockerror in list_error: #we are about to build block with red border
          if blockerror[0][0] == name_block:
            if old_delta2.has_key(name_block):
              prev_deltaX=float(old_delta2[name_block][0])
              prev_deltaY=float(old_delta2[name_block][1])
            deltaX =float(blockerror[0][3]) - float(blockerror[0][1])+prev_deltaX 
            deltaY = float(blockerror[0][4]) - float(blockerror[0][2])+prev_deltaY
            #data_block_error is [begin,width,top,info,height]
            begin=(blockerror[1].begin*blockerror[2].width+deltaX)/blockerror[2].width
            width=float(blockerror[0][5])/blockerror[2].width
            top=((blockerror[1].marge_top)*(blockerror[2].height-10)+deltaY)/(blockerror[2].height-10)
            height=float(blockerror[0][6])/(blockerror[2].height-10)
            data_block_error= [begin,width,height,data_block[3],top,blockerror[1].url]
            self.addBlock(name_block,data_block_error,1)  
          else:
            self.addBlock(name_block,data_block)
      else:
        self.addBlock(name_block,data_block)  
      indic+=1
    
  def createXAxis(self,x_axe,width_line,y_axis_width):
    """creates x-axis """
    marge_left=y_axis_width
    indic1=0
    if x_axe!=[]:
      for i in x_axe[1]:
        nameblock='block_'+self.name+str(indic1)
        self.addBlockTextX(nameblock,marge_left,i)
        indic1+=1  
        marge_left+=width_line/float(len(x_axe[1]))
        
  def addSon(self,son):
    """add a child Line to a Line """
    self.son.append(son)       

  def createLineChild(self,report_section=None,field='',current_top=0,y_axis_width=0,
                      width_line=0,space_line=0,height_global_div=0,height_header=0,
                      height_axis_x=0,nbr_line=0,current_index=0,url=''): 
    """ create the Line object which is the son of an other Line Object"""
    if len(report_section[current_index].getObject().objectValues())!=0:
      paternity=1
    else:
      paternity=0   
    son=Line(title=str(report_section[current_index].getObject().getTitle()),
              name=self.name+'s'+str(current_index) ,begin=y_axis_width,width=width_line,
              height=(height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))\
              /float(nbr_line),top=current_top,color='#ffffff',paternity=paternity,url=url) 
    if (current_index+1)<=(len(report_section)-1): 
     if report_section[current_index+1].getDepth() == 0:
       current_top=current_top+((height_global_div-height_header-height_axis_x-
                   ((nbr_line-1)*space_line))/float(nbr_line))+space_line       
     else:
       current_top=current_top+((height_global_div-height_header-height_axis_x-
                   ((nbr_line-1)*space_line))/float(nbr_line))
    self.addSon(son)                
    return current_top 

  def insertActivityBlock(self,line_content=None,object_start_method_id=None,object_stop_method_id=None,
                          x_axe=[],field='',info_center='',info_topright='',info_topleft='',
                          info_backleft='',info_backright='',list_error='',old_delta='',REQUEST=None,
                          blocks_object={},width_line=0,script_height_block=None,y_max = 1,color_script=None):
    """allows to create the mobile block objects"""
    #first we check if the block has information
    center= getattr(line_content,info_center,None) 
    topright = getattr(line_content,info_topright,None)
    topleft = getattr(line_content,info_topleft,None)
    backleft= getattr(line_content,info_backleft,None)
    backright= getattr(line_content,info_backright,None)
    info={}
    if center!=None: info['center']=str(center())
    if topright!=None: info['topright']=str(topright())
    if topleft!=None: info['topleft']=str(topleft())
    if backleft!=None: info['botleft']=str(backleft())
    if backright!=None: info['backright']=str(backright()) 
    marge=0
    method_start = getattr(line_content,object_start_method_id,None)  
    method_stop= getattr(line_content,object_stop_method_id,None)
    wrong_left=0 
    wrong_right=0
    list_block=[]
    current_color=''
    if method_start==None and blocks_object!={}:
      for Ablock in blocks_object:
        #object_content is the current object used for building a block.
        #For instance if the context is a project, then object_content is an orderLine.
        for object_content in blocks_object[Ablock]:
          if self.title == Ablock.getObject().getTitle(): 
            method_start = getattr(object_content,object_start_method_id,None)  
            method_stop= getattr(object_content,object_stop_method_id,None)     
    
            if method_start != None:
              block_begin = method_start()
            else:
              block_begin = None
      
            if method_stop!=None:
              block_stop= method_stop()
            else:
              block_stop=None
            if isinstance(block_begin,DateTime):    
                if round(block_begin-DateTime(x_axe[0][0]))>0:
                  block_left=float(round(block_begin-DateTime(x_axe[0][0])))/round(
                             (DateTime(x_axe[0][-1])+1)-DateTime(x_axe[0][0]))
                elif round(block_begin-DateTime(x_axe[0][0]))==0:
                  block_left=0
                else:
                  block_left=float(round(block_begin-DateTime(x_axe[0][0])))/round(
                         (DateTime(x_axe[0][-1])+1)-DateTime(x_axe[0][0]))

                if block_stop-DateTime(x_axe[0][0])<=0:
                  wrong_left = 1  #means that the block is outside of x-axis range
        
                if block_begin-DateTime(x_axe[0][-1])>=0:            
                  wrong_right = 1 #the same
      
                block_right=float(round(block_stop-DateTime(x_axe[0][0])))/round(
                              (DateTime(x_axe[0][-1])+1)-DateTime(x_axe[0][0]))
                
                center= getattr(object_content,info_center,None) 
                topright = getattr(object_content,info_topright,None)
                topleft = getattr(object_content,info_topleft,None)
                backleft= getattr(object_content,info_backleft,None)
                backright= getattr(object_content,info_backright,None)
                info={}
                if center!=None: info['center']=str(center())
                if topright!=None: info['topright']=str(topright())
                if topleft!=None: info['topleft']=str(topleft())
                if backleft!=None: info['botleft']=str(backleft())
                if backright!=None: ignfo['botright']=str(backright())
                url = getattr(object_content,'domain_url','')
                url = object_content.getUrl()
                
                #if there is a script wich allows to know the height of the current block,
                #then we use it, otherwise block's height is 0,75
                if script_height_block == None or y_max==1:
                  height = 0.75
                else:
                  height = float(script_height_block(object_content))/y_max
                
                if color_script != None:
                  current_color = color_script(object_content)
                
                if wrong_left!=1 and wrong_right!=1: # if outside we do not display
                  list_block.append([block_left,block_right-block_left,height,info,1-height,url,current_color])
            else:
              if block_begin !=None:
                for i in x_axe[0]:
                  if block_begin==i:
                    center= getattr(object_content,info_center,None) 
                    topright = getattr(object_content,info_topright,None)
                    topleft = getattr(object_content,info_topleft,None)
                    backleft= getattr(object_content,info_backleft,None)
                    backright= getattr(object_content,info_backright,None)
                    info={}
                    if center!=None: info['center']=str(center())
                    if topright!=None: info['topright']=str(topright())
                    if topleft!=None: info['topleft']=str(topleft())
                    if backleft!=None: info['botleft']=str(backleft())
                    if backright!=None: ignfo['botright']=str(backright())
                    url = getattr(object_content,'domain_url','')
                    if script_height_block == None or y_max==1:
                      height = 0.75
                    else:
                      height = float(script_height_block(object_content))/y_max
                    if color_script != None:
                      current_color = color_script(object_content) 
                    list_block.append([marge,(block_stop-block_begin)/(float(len(x_axe[0]))),height,info,
                                      1-height,url,current_color])   
               # 0.75(height) need to be defined        
                  marge+=1/float(len(x_axe[0])) 
    else:
      if method_start != None:
        block_begin = method_start()
      else:
        block_begin = None
      
      if method_stop!=None:
        block_stop= method_stop()
      else:
        block_stop=None
      # if datas are DateTime type we need to do special process.
      if isinstance(block_begin,DateTime):    
        if round(block_begin-DateTime(x_axe[0][0]))>0:
          block_left=float(round(block_begin-DateTime(x_axe[0][0])))/float(
                     (DateTime(x_axe[0][-1])+1)-DateTime(x_axe[0][0]))
        elif round(block_begin-DateTime(x_axe[0][0]))==0:
          block_left=0
        else:
          block_left=float(round(block_begin-DateTime(x_axe[0][0])))/round(
                 (DateTime(x_axe[0][-1]+1))-DateTime(x_axe[0][0]))

        if block_stop!=None:
          if block_stop-DateTime(x_axe[0][0])<=0:
            wrong_left = 1  #means that the block is outside of x-axis range
        
        if block_begin-DateTime(x_axe[0][-1])>=0:            
          wrong_right = 1 #the same
        if block_stop!=None:
          block_right=float(round(block_stop-DateTime(x_axe[0][0])))/round(
                            (DateTime(x_axe[0][-1])+1)-DateTime(x_axe[0][0]))
        
        if wrong_left!=1 and wrong_right!=1: # if outside we do not display
          if script_height_block == None or y_max==1:
            height = 0.75
          else:
            height = float(script_height_block(line_content.getObject()))/y_max
          if color_script != None:
            current_color = color_script(line_content)  
          if block_stop != None:  
            list_block.append([block_left,block_right-block_left,height,info,1-height,'',current_color])
          else:
            list_block.append([block_left,1/(float(len(x_axe[0]))),height,info,1-height,'',current_color])
          
      else:
        if block_begin !=None:
          if block_stop !=None:
            for i in x_axe[0]:
              if block_begin==i:
                if script_height_block == None or y_max==1:
                  height = 0.75
                else:
                  height = float(script_height_block(line_content.getObject()))/y_max
                if color_script != None:
                  current_color = color_script(object_content)
              list_block.append([marge,1/(float(len(x_axe[0]))),height,info,1-height,'',current_color])   
                # 0.75(height) need to be defined        
              marge+=1/float(len(x_axe[0]))
          else:
            for i in x_axe[0]:
              if isinstance(block_begin,list): 
                for item in block_begin:
                  if item == i:
                    if script_height_block == None or y_max==1:
                      height = 0.75
                    else:
                      height = float(script_height_block(line_content.getObject()))/y_max
                    if color_script != None:
                      current_color = color_script(object_content) 
                    list_block.append([marge,1/(float(len(x_axe[0]))),height,info,1-height,'',current_color])  
              marge+=1/float(len(x_axe[0]))
    if list_block!=[]:
      self.appendActivityBlock(list_block,list_error,old_delta,REQUEST) 
      
    if self.son!=[]:
      son_line= line_content.objectValues()
      indic=0
      while indic != len(son_line):
        indic2=0
        for s in son_line:
          if s.getTitle() == self.son[indic].title:
            
            self.son[indic].insertActivityBlock(line_content=s,object_start_method_id=object_start_method_id,
                                                object_stop_method_id=object_stop_method_id,x_axe=x_axe,
                                                field=field,info_center=info_center,
                                                info_topright=info_topright,info_topleft=info_topleft,
                                                info_backleft=info_backleft,info_backright=info_backright,
                                                list_error=list_error,old_delta=old_delta,REQUEST=REQUEST,
                                                width_line=width_line,
                                                script_height_block=script_height_block,
                                                color_script=color_script)
        indic+=1
  
        
# class block      
class Block:
  def __init__(self,types,name,begin,width=0,height=0,text='',content={},marge_top=0,id='',url='',color=''):
    """creates a block object"""
    self.types=types
    self.name=name
    self.begin=begin
    self.width=width
    self.height=height
    self.text=text
    self.content=content #stores info block in a dictionnary
    self.marge_top=marge_top
    if color=='':
      self.color='#bdd2e7'
    else: 
      self.color=color 
    self.id = name
    self.url = url
  
  def render(self,line_width,line_height,portal_url,line_begin,y_axis_width,line):
    """used for inserting text in a block. one calculates how to organise the space.
    one defines a width and height parameters (in pixel) which can be 
    changed (depends on the size and the font used).
    One fetches content which is a dictionnary like 
    this {'center':'ezrzerezr','topright':'uihiuhiuh',
          'topleft':'jnoinoin','botleft':'ioioioioi','botright':'ononono'}
    """ 
    string=''
    font_height=10
    font_width=6
    info=''
    #checks if the block starts before the beginning of the line
    if ((line_begin+self.begin*line_width) < line_begin): 
      block_width=self.width+self.begin 
    #checks if the block is too large for the end of the line. if it is the case, one cuts the block
    elif ((self.width*line_width)+(line_begin+self.begin*line_width)>line_width+y_axis_width): 
      block_width=self.width*line_width-((line_begin+self.begin*line_width+self.width*line_width)\
                  -(line_width+y_axis_width))
      block_width=block_width/line_width
    else:
      block_width=self.width
    return self.buildInfoBlockBody(line_width,block_width,font_width,line_height,font_height,
                                   line,portal_url)
    
  def render_css(self,line_width,line_height,line,y_axis_width):
    """used for inserting info inside an activity block"""
    string=''
    font_height=10
    font_width=6
    line_begin=line.begin
    #checks if the block starts before the beginning of the line
    if ((line_begin+self.begin*line_width) < line_begin) and self.types!='activity_error':
      block_width=self.width+self.begin
    #checks if the block is too large for the end of the line. if it is the case, one cuts the block  
    elif ((self.width*line_width)+(line_begin+self.begin*line_width)>line_width+y_axis_width) \
          and self.types!='activity_error':
      block_width=self.width*line_width-((line_begin+self.begin*line_width+self.width*line_width)\
                  -(line_width+y_axis_width))
      block_width=block_width/line_width
    else:
      block_width=self.width
    return self.buildInfoBlockCss(font_height,line_height,block_width,line_width,font_width,line)
    

  def addInfoCenter(self,info): 
    """add info in center of a block"""    
    self.content['center']=info  
    
  def addInfoTopLeft(self,info): 
    """add info in the top left corner of a block """   
    self.content['topleft']=info
  
  def addInfoTopRight(self,info): 
    """add info in the top right corner of a block"""    
    self.content['topright']=info
  
  def addInfoBottomLeft(self,info): 
    """add info in the bottom left corner of a block"""    
    self.content['botleft']=info
  
  def addInfoBottomRight(self,info): 
    """add info in the bottom right corner of a block"""    
    self.content['botright']=info
   

  def buildInfoBlockBody(self,line_width,block_width,font_width,line_height,font_height,line,portal_url):
    """ create the body of the html for displaying info inside a block"""
    string=''
    #line_height=line_height-10
    already=0
    block_name=''
    length_list_info=0
    info=''
    curr_url = ''
    for i in self.content:
      if self.content[i]!=None:
        length_list_info += 1
    for i in self.content:
      if length_list_info==5:
        test_height= font_height<=((self.height*line_height)/3)
        test_width= ((len(self.content[i])*font_width)<=((block_width*line_width)/3))
      if length_list_info==4 or length_list_info==3:
        test_height= font_height<=((self.height*line_height)/2)
        test_width= ((len(self.content[i])*font_width)<=((block_width*line_width)/2))
      if length_list_info==2:
        test_height=font_height<=(self.height*line_height)
        test_width= (len(self.content[i]*font_width)<=((block_width*line_width)/2))
      if length_list_info==1: 
        test_height= font_height<=(self.height*line_height)
        test_width= (len(self.content[i]*font_width)<=(block_width*line_width))   
      if test_height & test_width:
        if self.url!='':
          curr_url = self.url
        else:
          curr_url = line.url
        string+='<div id=\"'+self.name+i+'\"><a href=\"'+portal_url+'/'+curr_url+'\">'+ self.content[i]
        string+='</a href></div>\n' 
      else: #one adds interogation.png  
        if ((self.width*line_width>=15) & (self.height*line_height>=15)): 
          info+=self.content[i]+'|'
          if already==0 or i=='center':
            block_name=self.name+i
            already=1
    if already==1:
      string+='<div id=\"'+block_name+'\" title=\"'+info+'\"><a href=\"'+portal_url+'/'+curr_url+'\">\
              <img src=\"'+portal_url+'/images/question.png\" height=\"15\" width=\"15\"></a href> '
      string+='</div>\n'   
    return string     


  def buildInfoBlockCss(self,font_height,line_height,block_width,line_width,font_width,line):
    """used for creating css code when one needs to add info inside a block"""
    string=''
    already=0#used when we add interro.png 
    list_info_length = 0 #counts number of info inside a block(between 0 and 5)
    for j in self.content:
      if  self.content[j]!= None:
        list_info_length += 1 
    if list_info_length ==0:return ''

    #definition of coefficient for different cases of info display.
    matrix = {
    ('center',5):{'left':2,'top':2},
    ('center',4):{'left':0,'top':0},
    ('center',3):{'left':2,'top':2},
    ('center',2):{'left':2,'top':2},
    ('center',1):{'left':2,'top':2},
    
    ('topright',5):{'left':1.01,'top':0},
    ('topright',4):{'left':1.01,'top':0},
    ('topright',3):{'left':1.01,'top':0},
    ('topright',2):{'left':1.01,'top':2},
    ('topright',1):{'left':1.01,'top':0},
    
    ('topleft',5):{'left':0,'top':0},
    ('topleft',4):{'left':1,'top':1},
    ('topleft',3):{'left':0,'top':0},
    ('topleft',2):{'left':0,'top':0},
    ('topleft',1):{'left':0,'top':0},
    
    ('botleft',5):{'left':0,'top':1},
    ('botleft',4):{'left':0,'top':1},
    ('botleft',3):{'left':0,'top':1},
    ('botleft',2):{'left':0,'top':1},
    ('botleft',1):{'left':0,'top':1},
    
    ('botright',5):{'left':1.01,'top':1.1},
    ('botright',4):{'left':1.01,'top':1.1},
    ('botright',3):{'left':1.01,'top':1.1},
    ('botright',2):{'left':1.01,'top':1.1},
    ('botright',1):{'left':1.01,'top':1.1}
    }   
    #definition of coefficient for different cases, when info strings are too long,
    #we use a small picture. The coefficient are suitable for are 15x15px picture. 
    matrix_picture = {
    ('center',5):{'left':2,'top':2},
    ('center',4):{'left':0,'top':0},
    ('center',3):{'left':2,'top':2},
    ('center',2):{'left':0,'top':2},
    ('center',1):{'left':2,'top':2},
    
    ('topright',5):{'left':1,'top':0},
    ('topright',4):{'left':1,'top':0},
    ('topright',3):{'left':1,'top':0},
    ('topright',2):{'left':1,'top':2},
    ('topright',1):{'left':0,'top':0},
    
    ('topleft',5):{'left':0,'top':0},
    ('topleft',4):{'left':1,'top':1},
    ('topleft',3):{'left':0,'top':0},
    ('topleft',2):{'left':0,'top':0},
    ('topleft',1):{'left':0,'top':0},
    
    ('botleft',5):{'left':0,'top':1},
    ('botleft',4):{'left':0,'top':1},
    ('botleft',3):{'left':0,'top':1},
    ('botleft',2):{'left':0,'top':1}, 
    ('botleft',1):{'left':0,'top':1},
    
    ('botright',5):{'left':1,'top':1},
    ('botright',4):{'left':0,'top':0},
    ('botright',3):{'left':0,'top':0},
    ('botright',2):{'left':0,'top':0},
    ('botright',1):{'left':1,'top':1}
    }  
    
    idx= 0
    margin_left=0
    margin_top=0
   
    for block in self.content:         
      matrix_data = matrix[(block,list_info_length)]
      left = matrix_data['left']
      top= matrix_data['top']
      if left == 0:
        margin_left=0
      else:
        margin_left = round(((block_width*line_width)/left)-(font_width*len(self.content[block]))/left)  
      if top==0:
        margin_top=0  
      else:
        margin_top = round(((self.height*(line_height-10))/top)-(font_height))
      if list_info_length==5:
        test_height= font_height<=((self.height*(line_height))/3)
        test_width= ((len(self.content[block])*font_width)<=((block_width*line_width)/3))
      if list_info_length==4 or list_info_length==3:
        test_height= font_height<=((self.height*(line_height))/2)
        test_width= ((len(self.content[block])*font_width)<=((block_width*line_width)/2))
      if list_info_length==2:
        test_height=font_height<=(self.height*(line_height))
        test_width= (len(self.content[block]*font_width)<=((block_width*line_width)/2))
      if list_info_length==1: 
        test_height= font_height<=(self.height*(line_height))
        test_width= (len(self.content[block]*font_width)<=(block_width*line_width))

      if test_height & test_width:
        string+='#'+self.name+block+'{position:absolute;\nmargin-left:'+\
                 str(margin_left)+'px;\nmargin-top:'+str(margin_top)+'px;\n}\n'              
        line.addBlockInfo(self.name+block)
      else: # we add question.png because the size of the block is not enough
        if ((self.width*line_width>=15) & (self.height*line_height>=15)): 
          matrix_data= matrix_picture[(block,list_info_length)]
          left = matrix_data['left']
          top = matrix_data['top']
          if left == 0:
            margin_left=0
          else:
           margin_left=round(((block_width*line_width)/left)-(15/left))
          if top==0:
            margin_top=0  
          else:
            margin_top=round(((self.height*(line_height-10))/top)-(15/top))
          if block=='center' and list_info_length==3:
            margin_left=round(((block_width*line_width)/left)-(15/left))
            margin_top=round(((self.height*(line_height-10))/top)-(font_height))
          if block=='center' and list_info_length==2:  
            margin_top=round(((self.height*(line_height-10))/top)-(font_height/top))    
          if already==0 or block=='center':
            string+='#'+self.name+block+'{position:absolute;\nmargin-left:'+str(margin_left)+\
                    'px;\nmargin-top:'+str(margin_top)+'0px;\n}'  
            block_disp=self.name+block
            already=1
    return string
    
  def get_error_message(self,err_type):
    return 'incorrect block'
PlanningBoxWidgetInstance = PlanningBoxWidget()        
          
class PlanningBox(ZMIField):
    meta_type = "PlanningBox"
    widget = PlanningBoxWidgetInstance
    validator = PlanningBoxValidatorInstance
    security = ClassSecurityInfo()
    security.declareProtected('Access contents information', 'get_value')
    def get_value(self, id, **kw):
      if id == 'default' and kw.get('render_format') in ('list', ):
        return self.widget.render(self, self.generate_field_key() , None , 
                                  kw.get('REQUEST'), render_format=kw.get('render_format'))
      else:
        return ZMIField.get_value(self, id, **kw)

    def render_css(self, value=None, REQUEST=None):      
      return self.widget.render_css(self,'',value,REQUEST)
