##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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
from SelectionTool import makeTreeList
from Selection import Selection, DomainSelection
import OFS
from AccessControl import ClassSecurityInfo
from zLOG import LOG
from copy import copy
from Acquisition import aq_base, aq_inner, aq_parent, aq_self

from Products.Formulator.Form import BasicForm

from Products.ERP5Type.Utils import getPath
from Products.ERP5Type.Document import newTempBase
from Products.CMFCore.utils import getToolByName


class PlanningBoxValidator(Validator.StringBaseValidator):
    def validate(self, field, key, REQUEST):
        list_value={}
        try:
          for lang in list_value.keys():
            list_value[lang] = int(list_value[lang])
        except ValueError:
            self.raise_error('not an integer', field)
        return list_value
   
PlanningBoxValidatorInstance=PlanningBoxValidator()        

def createLineObject(meta_types,selection,selection_name,field,REQUEST,list_method,
                     here,report_root_list,y_axis_width,width_line,space_line,
                     height_global_div,height_header,height_axis_x,form,current_top,portal_types):
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
    #add **************
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
      except:
        pass
    #add ****************
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
  report_tree_list = makeTreeList(here, form, None,selection_report_path,None,0, 
                                  selection_report_current, form.id, selection_name, 
                                  report_depth,is_report_opened, sort_on=selection.sort_on)
  
  if report_depth is not None:
    report_list = map(lambda s:s[0].getRelativeUrl(), report_tree_list)
    selection.edit(report_list=report_list)
  report_sections = []
  
  list_object = []
  nbr_line=0
  object_list=[]    
  indic_line=0 
  index_line = 0  
  for s in report_tree_list:      
    selection.edit(report = s.getSelectDomainDict())            
    
    if s.getIsPureSummary():
      original_select_expression = kw.get('select_expression')
      kw['select_expression'] = select_expression
      selection.edit( params = kw )
      if original_select_expression is None:
        del kw['select_expression']
      else:
        kw['select_expression'] = original_select_expression
    
    if s.getIsPureSummary():
      stat_result = {}
      index = 1
      report_sections += [s]
      nbr_line+=1       
    else:
      # Prepare query
      selection.edit( params = kw )
      if list_method not in (None, ''):
        selection.edit(exception_uid_list=s.getExceptionUidList())
        object_list = selection(method = list_method, context=here, REQUEST=REQUEST)
      else:
        object_list = here.portal_selections.getSelectionValueList(selection_name,
                                                          context=here, REQUEST=REQUEST)
      
    
    selection.edit(report=None)
  index = 0

  # we start to build our line object structure right here.
  #for x in report_sections:
  #  print x.getObject().getTitle()  
  for l in report_sections:
    stat_result = {}
    stat_context = l.getObject().asContext(**stat_result)
    stat_context.domain_url = l.getObject().getRelativeUrl()
    stat_context.absolute_url = lambda x: l.getObject().absolute_url()     
    url=getattr(stat_context,'domain_url','')
    if l.getDepth() == 0:
      paternity = 0
      if len(l.getObject().objectValues())!=0:
        paternity = 1
    
      height=(height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))/float(nbr_line)
      line = Line(title=l.getObject().getTitle(),
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
      while l.getDepth() == report_sections[index-current_index].getDepth():
        current_index += 1
      if report_sections[index-current_index].getDepth() == 0:
        current_top=list_object[len(list_object)-1].createLineChild(report_sections,field,
                                current_top,y_axis_width,width_line,space_line,height_global_div,
                                height_header,height_axis_x,nbr_line,index,url)
        
      else : # in this case wee add a soon to a soon
        depth=0 
        current_soon=list_object[len(list_object)-1]
        while depth != (l.getDepth()-1):
          current_soon=list_object[len(list_object)-1].soon[len(list_object[len(list_object)-1].soon)-1]
          depth+=1
        current_top=current_soon.createLineChild(report_sections,field,current_top,y_axis_width,
                                                 width_line,space_line,height_global_div,height_header
                                                ,height_axis_x,nbr_line,index,url)    
    index += 1
    indic_line+=1
  return (list_object,nbr_line,report_sections)

    
def createGraphicCall(current_line,graphic_call):
  """ create html code of children used by graphic library to know which block can be moved"""
  
  for i in current_line.soon:
    for j in i.content:
      if j.types=='activity':
        graphic_call+='\"'+j.name+'\",'
      elif j.types=='info':
        graphic_call+='\"'+j.name+'\"+NO_DRAG,'   
    if i.soon!=[]: # case of a soon which has soons...
      graphic_call+=createGraphicCall(i,graphic_call)        
  return graphic_call
  
  
class PlanningBoxWidget(Widget.Widget):
    property_names = Widget.Widget.property_names +\
                     ['height_header', 'height_global_div','height_axis_x', 'width_line','space_line'
                     ,'list_method','report_tree','report_root_list','selection_name','portal_types',
                     'meta_types','sort','title_line','y_unity','y_axis_width','y_range','x_range',
                     'x_axis_script_id','x_start_bloc','x_stop_bloc','y_axis_method','info_center',
                     'info_topleft','info_topright','info_backleft','info_backright','security_index']
    
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
                                
                                
    report_tree = fields.CheckBoxField('report_tree',
                                 title='Report Tree',
                                 description=('Report Tree'),
                                 default='',
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
                                 default='',
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
                                default=5,
                                required=0) 
 
    x_range = fields.StringField('x_range',
                                 title='range of X-Axis:',
                                 description=('Nature of the subdivisions of X-Axes, not Required'),
                                 default='Day',
                                 required=0)	
 
    x_axis_script_id = fields.StringField('x_axis_script_id',
                                 title='script for building the X-Axis:',
                                 description=('script for building the X-Axis'),
                                 default='',
                                 required=0)	

    x_start_bloc = fields.StringField('x_start_bloc',
                                 title='specific method which fetches the data for the beginning of a block:',
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
                                 title='specific method of data type for creating Y-Axis',
                                 description=('Method for building Y-Axis'
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
                                description=("This variable is used because the rounds of each web browser seem to work differently"),
                                default=2,
                                required=0) 	 
                                                                                       
    def render_css(self, field, key, value, REQUEST):
  
        # DATA DEFINITION #############################################
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
        report_tree = field.get_value('report_tree')
        report_root_list = field.get_value('report_root_list')
        y_axis_method=field.get_value('y_axis_method')
        script=getattr(here,field.get_value('x_axis_script_id'),None)
        #info inside a block
        info_center = field.get_value('info_center')
        info_topleft = field.get_value('info_topleft')        
        info_topright = field.get_value('info_topright')
        info_backleft = field.get_value('info_backleft')
        info_backright = field.get_value('info_backright')
        #*******
        object_start_method_id = field.get_value('x_start_bloc')
        object_stop_method_id= field.get_value('x_stop_bloc')
        form = field.aq_parent
        sort = field.get_value('sort')   
        x_occurence=[] # contains datas of start and stop of each block like
                       # this [ [ [x1,x2],[x1,x2] ],[ [x1,x2],[x1,x2] ],.....] 
                       #it is not directly coordinate but datas.                    
        x_axe=[] # will contain what wee need to display in X-axis. contains: 
                 #(data used for construction, display of x-axis)
        yrange=[] # we store the value in Y-axis of each block 
        nbr=1
        y_max=1      
        current_top=height_header
        total=[]
        list_object=[] #in this list we store all the objects of type Line
        giant_string='' #will contain all the html code.
        report_sections=[]
        # END DATA DEFINITION ##########################################                        
        # we fetch fold/unfold datas ######################
        
        #here.portal_selections.setSelectionFor(selection_name, None)#uncoment to put selection to null
        selection = here.portal_selections.getSelectionFor(selection_name, REQUEST=REQUEST)
        default_params = {}
        if selection is None:
          selection = Selection(params=default_params, default_sort_on = sort)
        #domain_list = list(selection.getDomainList())
        #here.portal_selections.setSelectionFor(selection_name, selection, REQUEST=REQUEST)
        else:
          selection.edit(default_sort_on = sort)
          selection.edit(sort_on = sort)       
        here.portal_selections.setSelectionFor(selection_name, selection, REQUEST=REQUEST)
        ########################
        
        #we build line ***************************
        (list_object,nbr_line,report_sections)=createLineObject(meta_types,selection,selection_name
                                                                ,field,REQUEST,list_method,here,report_root_list,
                                                                y_axis_width,width_line,space_line,height_global_div,
                                                                height_header,height_axis_x,form,current_top,portal_types)
        
        # end build line ####################################################
        
         #we build x_occurence (used for the range in x-Axis ##################################
        for o in report_sections: 
          method_start = getattr(o.getObject(),object_start_method_id,None)
          method_stop= getattr(o.getObject(),object_stop_method_id,None)
          block_begin = method_start()
          if method_stop!=None:
            block_stop= method_stop()
          else:
            block_stop=None
          x_occurence.append([block_begin,block_stop])
        x_axe=script(x_occurence,x_range) #we call this script for the range in X-Axis
        ##################################################     
         
        # we add mobile block to the line object ###################################
        indic_line=0 
        while indic_line != len(report_sections):
          for o in list_object:
            if o.title == report_sections[indic_line].getObject().getTitle():
              if list_object != [] and report_sections[indic_line].getDepth()==0:
                o.insertActivityBlock(report_sections[indic_line].getObject(),object_start_method_id,
                                      object_stop_method_id,x_axe,field,info_center,info_topright,info_topleft,
                                      info_backleft,info_backright)                                                      
                break
          indic_line+=1
        # #############################################################
        # at this point list_object contains our tree of datas. Then we add others objects for the graphic.

        #one constructs the vertical dotted line **********************
        marge_left=y_axis_width+width_line/float(len(x_axe[1]))
        for i in list_object:
          i.appendVerticalDottedLine(x_axe,width_line,marge_left)
        #*************************************************************    

            
        #one constructs the maximum horizontal dotted line 10px under the top of the line***************
        maximum_y=y_max
        marge_top=10 
        if y_range!=0:  
          for i in list_object:  
            i.appendHorizontalDottedLine(marge_top,maximum_y,height_global_div,height_header,
                                         height_axis_x,nbr_line,y_range,y_max,current_section)
            #end construct of horizontal dotted line ********************************************************
   

        # we construct y-axis   ******************************
        way=[]    
        y=[]
        level=0
        current_top=height_header
        idx=0
        for i in list_object:
          current_top=i.buildYtype(way,y,level,y_axis_width,height_global_div,height_header,
                                   height_axis_x,nbr_line,current_top,space_line,y_max,y_range,
                                   y_unity,selection_name,form)  
          
          height=((height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))/float(nbr_line))+space_line
          current_top=y[len(y)-1].top+height
          idx+=1
        list_object=y+list_object #we need to add the y-axis block at the beginning of our structure
                                  #otherwise the display is not correct
        #************************end construct y-axis 	 

        
        #build X axis ########################################
        list_object.append(Line('','axis_x',y_axis_width,width_line,height_axis_x,current_top-space_line)) 
        list_object[len(list_object)-1].createXAxis(x_axe,width_line,y_axis_width)
       #***************************
        x_subdivision=width_line/float(len(x_axe[1]))
        SESSION = REQUEST.SESSION
        SESSION.set('total',list_object)  
        SESSION.set('width_line',width_line) 
        SESSION.set('height_global', height_global_div)
        SESSION.set('y_axis_width', y_axis_width)
        SESSION.set('report_tree',report_tree)
        SESSION.set('report_root_list',report_root_list)
        SESSION.set('selection_name',selection_name)
        SESSION.set('title',title)
        for i in list_object:
          giant_string+=i.render_css(y_axis_width,security_index,x_subdivision)   
        return giant_string
      
        
                
       
    def render(self,field, key, value, REQUEST):
        here = REQUEST['here']
        portal_url= here.portal_url()
        SESSION = REQUEST.SESSION
        total = SESSION.get('total')  
        width_line=SESSION.get('width_line')
        height_global_div=SESSION.get('height_global')
        y_axis_width=SESSION.get('y_axis_width')
        report_tree=SESSION.get('report_tree')
        report_root_list=SESSION.get('report_root_list')
        selection_name=SESSION.get('selection_name')
        title=SESSION.get('title')
        giant_string='<input type=\"hidden\" name=\"list_selection_name\" value='+selection_name+' />\n'
        """giant_string+='<div id=\"global_block\" style=\"position:absolute;width:'+str(width_line+y_axis_width)\
                      +'px;height:'+str(height_global_div)+'px;background:#d5e6de;margin-left:-99px;\
                      border-style:solid;border-color:#000000;border-width:1px;margin-top:px\">\n'""" 
        
        giant_string+='<div id=\"global_block\" style=\"position:absolute;width:'+str(width_line+y_axis_width)\
                      +'px;height:'+str(height_global_div)+'px;background:#d5e6de;margin-left:-2px;\
                      border-style:solid;border-color:#000000;border-width:1px;margin-top:-1px\">\n'
        
        #header of the graphic******************************************
        giant_string+='<div id=\"header\" style=\"position:absolute;width:'+str(width_line+y_axis_width)+\
                      'px;height:'+str(height_global_div)+'px;background:#d5e6de;margin-left:0px;\
                       border-style:solid;border-color:#000000;border-width:1px;margin-top:1px\">\
                       <table><tr><td><h3><u>'+title+'</h3></u></td><td>'
        ##########################report tree
        if report_tree:
          selection = here.portal_selections.getSelectionFor(selection_name, REQUEST=REQUEST)
          selection_report_path = selection.getReportPath()

          report_tree_options = ''
          for c in report_root_list:
            if c[0] == selection_report_path:
              report_tree_options += """<option selected value="%s">%s</option>\n""" % (c[0], c[1])
            else:
              report_tree_options += """<option value="%s">%s</option>\n""" % (c[0], c[1])
          report_popup = """<select name="report_root_url"
onChange="submitAction(this.form,'%s/portal_selections/setReportRoot')">
        %s</select></td></tr></table></div>""" % (here.getUrl(),report_tree_options)
          giant_string += report_popup
        else:
          report_popup = ''
        ######################################

        for i in range(0,len(total)):
          giant_string+=total[i].render(portal_url,y_axis_width)    
      ###################"  
    
        giant_string+='<div id=\"lefttop\" style=\"position:absolute;width:5px;height:5px;background:#a45d10\"></div>\n'
        giant_string+='<div id=\"righttop\" style=\"position:absolute;width:5px;height:5px;background:#a45d10"></div>\n'
        giant_string+='<div id=\"rightbottom\" style=\"position:absolute;width:5px;height:5px;background:#a45d10\"></div>\n'
        giant_string+='<div id=\"leftbottom\" style=\"position:absolute;width:5px;height:5px;background:#a45d10\"></div>\n'
        giant_string+='<script type=\"text/javascript\">\n SET_DHTML('
        
        
        for i in range(0,len(total)):
          graphic_call=''
          for j in total[i].content:
            if j.types=='activity':
              giant_string+='\"'+j.name+'\",'
            elif j.types=='info':
              giant_string+='\"'+j.name+'\"+NO_DRAG,'
      
          current_object=total[i]

          if current_object.soon!=[]:  
            giant_string+=createGraphicCall(current_object,graphic_call)     
      
        giant_string+='\"lefttop\"+CURSOR_NW_RESIZE, \"righttop\"+CURSOR_NE_RESIZE, \"rightbottom\"+CURSOR_SE_RESIZE,\
                       \"leftbottom\"+CURSOR_SW_RESIZE);\n'
        giant_string+='</script>\n </div> '
        return giant_string  
#***************************************************          
          


# class line **************************************
class Line:
  def __init__(self,title='',name='',begin=0,width=0,height=0,top=0,color='',soon=None,y_type='none',paternity=0,url=''):  
    if soon is None:
     soon = []
    self.title=title
    self.name=name
    self.begin=begin
    self.width=width
    self.height=height
    self.top=top
    self.content=[]
    self.color=color
    self.soon=soon
    self.y_type=y_type
    self.paternity=paternity
    self.url=url
   

  def render(self,portal_url,y_axis_width):
    """ creates "pure" html code of the line, its Block, its soon """
    html_render='<div id=\"'+self.name+'\"></div>\n'
    for j in self.content:
      if j.types=='activity':
        #checks if the block is too large for the end of the line if it is the case, one cuts the block
        if ((j.width*self.width)+(self.begin+j.begin*self.width)>self.width+y_axis_width): 
          html_render+='<div id=\"'+j.name+'\" ondblclick=\"showGrips()\" onclick=\"dd.elements.'\
                       +j.name+'.resizeTo('+str(round(j.width*self.width))+','+ str(j.height*(self.height-10))+') \">'
        elif ((self.begin+j.begin*self.width) < self.begin): #checks if the block starts before the beginning of the line
          html_render+='<div id=\"'+j.name+'\" ondblclick=\"showGrips()\" onclick=\"if (dd.elements.'\
                       +j.name+'.moved==0){dd.elements.'+j.name+'.moveBy('+str(round(j.begin*self.width))\
                       +',0);dd.elements.'+j.name+'.resizeTo('+str(round(j.width*self.width))+','\
                       + str(j.height*(self.height-10))+');dd.elements.'+j.name+'.moved=1} \">'  
                       # "done" is used because otherwise everytime we move the block it will execute moveby()
        else:
          html_render+='<div id=\"'+j.name+'\" ondblclick=\"showGrips()\">'      
        # we add info Block inside the div thanks to the render method of the Block class
        html_render+=j.render(self.width,self.height,portal_url,self.begin,y_axis_width,self)      
        html_render+='</div>\n'
      elif j.types!='info':
        html_render+='<div id=\"'+j.name+'\">'+str(j.text)+'</div>\n'      

    if self.soon!=[]:
      for i in self.soon:
        html_render+=i.render(portal_url,y_axis_width)      
    return html_render    
    
    
  def render_css(self,y_axis_width,security_index,x_subdivision):
    css_render='#'+self.name+'{position:absolute;\nborder-style:solid;\nborder-color:#53676e;\nborder-width:1px;\n'
    if self.color!='':
      css_render+='background:'+str(self.color)+';\n'
    css_render+='height:'+str(self.height)+'px;\n'
    css_render+='margin-left:'+str(self.begin)+'px;\n'
    css_render+='margin-top:'+str(self.top)+'px;\n'

    if self.y_type=='father1':
      css_render+='border-bottom-width:0px;'
    elif self.y_type=='soon1':
      css_render+='border-top-width:0px;\nborder-bottom-width:0px;\n'    
    elif self.y_type=='soon2':
      css_render+='border-top-width:0px;'
    css_render+='width:'+str(self.width)+'px;\n}'
    
    for j in self.content: #we generate block's css
      if j.types=='activity':
        css_render+='#'+j.name+'{position:absolute;\nbackground:#bdd2e7;\nborder-style:solid;\
                    \nborder-color:#53676e;\nborder-width:1px;\n'
        css_render+='height:'+str((j.height*(self.height-10))-security_index)+'px;\n' 
        #-10 because wee don't want a block sticked to border-top of the line
        
        if ((self.begin+j.begin*self.width) < self.begin): 
        #checks if the block starts before the beginning of the line
          css_render+='margin-left:'+str(self.begin)+'px;\n' 
          css_render+='width:'+str((j.width*self.width+j.begin*self.width))+'px;\n' 
        #checks if the block is too large for the end of the line. if it is the case, one cuts the block  
        elif ((j.width*self.width)+(self.begin+j.begin*self.width)>self.width+y_axis_width): 
          css_render+='width:'+str(round(j.width*self.width)-((self.begin+j.begin*self.width+j.width*self.width)
                      -(self.width+y_axis_width)))+'px;\n'

          css_render+='margin-left:'+str(round(self.begin+j.begin*self.width))+'px;\n' 
        else:  
          css_render+='width:'+str(round(j.width*self.width))+'px;\n'
          css_render+='margin-left:'+str(round(self.begin+j.begin*self.width))+'px;\n' 

        css_render+='margin-top:'+str(self.top+10+j.marge_top*(self.height-10))+'px;}\n'  
        css_render+=j.render_css(self.width,self.height,self,y_axis_width)  # we add info Block inside the div       
        
      elif j.types=='text_x' : 
        css_render+='#'+j.name+'{position:absolute;\nborder-style:solid;\nborder-color:#53676e;\nborder-width:1px;\n'
        css_render+='margin-left:'+str(j.begin)+'px;\n' 
        css_render+='margin-top:'+str(round(1+self.top+self.height/2))+'px;}\n'
        
      elif j.types=='text_y':
        css_render+='#'+j.name+'{position:absolute;\nborder-style:solid;\nborder-color:#53676e;\nborder-width:1px;\n'
        css_render+='margin-left:'+str(self.width/4)+'px;\n' 
        css_render+='margin-top:'+str(round(1+self.top+self.height/2))+'px;\n'
        css_render+='border-width:0px;}\n'


      elif j.types=='vertical_dotted':
        css_render+='#'+j.name+'{position:absolute;\nborder-style:dotted;\nborder-color:#53676e;\
                    \nborder-left-width:1px;\nborder-right-width:0px;\nborder-top-width:0px;\nborder-bottom-width:0px;\n'
        css_render+='margin-left:'+str(j.begin)+'px;\n' 
        css_render+='height:'+str(self.height)+'px;\n'
        css_render+='margin-top:'+str(1+round(self.top))+'px;}\n' 

      elif j.types=='horizontal_dotted': 
        css_render+='#'+j.name+'{position:absolute;\nborder-style:dotted;\nborder-color:#53676e;\
                    \nborder-left-width:0px;\nborder-right-width:0px;\nborder-top-width:1px;\nborder-bottom-width:0px;\n'
        css_render+='margin-left:'+str(self.begin)+'px;\n' 
        css_render+='height:1px;\n'
        css_render+='margin-top:'+str(self.top+j.marge_top)+'px;' 
        css_render+='width:'+str(self.width)+'px;}\n'

      elif j.types=='y_coord':
        css_render+='#'+j.name+'{position:absolute;\nborder-style:solid;\nborder-color:#53676e;\
                    \nfont-size:9px;\nborder-width:0px;\n'
        #x5 because this is the appropriate width for our font (9px), maybee need to be parameter            
        css_render+='margin-left:'+str(self.width-(len(j.text)*5))+'px;\n' 
        css_render+='margin-top:'+str(self.top+j.marge_top)+'px;}\n'

      elif j.types=='vertical':
        css_render+='#'+j.name+'{position:absolute;\nborder-style:solid;\nborder-color:#53676e;\
                    \nborder-left-width:1px;\nborder-right-width:0px;\nborder-top-width:0px;\nborder-bottom-width:0px;\n'
        css_render+='margin-left:'+str((self.width/4)+j.begin)+'px;\n'
        css_render+='height:'+str(j.height)+'px;\n'
        css_render+='margin-top:'+str(round(self.top)-self.height/2+13)+'px;}\n'

      elif j.types=='horizontal':
        css_render+='#'+j.name+'{position:absolute;\nborder-style:solid;\nborder-color:#53676e;\
                    \nborder-left-width:0px;\nborder-right-width:0px;\nborder-top-width:1px;\nborder-bottom-width:0px;\n'
        css_render+='margin-left:'+str((self.width/4)+j.begin)+'px;\n'
        css_render+='width:16px;\n'
        css_render+='height:1px; \n'
        css_render+='margin-top:'+str(round(1+self.top+self.height/2))+'px;}\n'
    
    if self.soon!=[]:
      for i in self.soon:
        css_render+=i.render_css(y_axis_width,security_index,x_subdivision);

    return css_render      

    

  def addBlock(self,name,block):
    self.content.append(Block('activity',name,block[0],block[1],block[2],'',block[3],block[4]))
    
  def addBlockInfo(self,name):
    self.content.append(Block('info',name,0,0,0,''))
    
  def addBlockTextY(self,name,text):
    self.content.append(Block('text_y',name,0,0,0,text))  
  
  def addBlockCoordY(self,name,text,marge_top):
    self.content.append(Block('y_coord',name,0,0,0,text,{},marge_top))  
    
  def addBlockTextX(self,name,begin,text):
    self.content.append(Block('text_x',name,begin,0,0,text))    
    
  def addBlockDottedVert(self,name,begin):
    self.content.append(Block('vertical_dotted',name,begin,0,0,''))  
    
  def addBlockDottedHoriz(self,name,marge_top):
    self.content.append(Block('horizontal_dotted',name,0,0,0,'',{},marge_top))   
  
  def addBlockVertical(self,name,marge_top,height,marge_left):
     self.content.append(Block('vertical',name,marge_left,0,height,'',{},marge_top)) 
     
  def addBlockHorizontal(self,name,marge_top,height,marge_left):
     self.content.append(Block('horizontal',name,marge_left,0,height,'',{},marge_top))    
         

 
      
    
  def appendVerticalDottedLine(self,x_axe,width_line,marge_left):
    current_marge=marge_left
    indic=0
    for j in x_axe[1]:
      nameblock='Block_vert_'+self.name+str(indic)
      self.addBlockDottedVert(nameblock,current_marge)
      current_marge+=width_line/float(len(x_axe[1]))   
      indic+=1
      
    if self.soon!=[]:
      for i in self.soon:
        i.appendVerticalDottedLine(x_axe,width_line,marge_left) 
      
 

 
  def buildYtype(self,way,y,level,y_axis_width,height_global_div,height_header,
                 height_axis_x,nbr_line,current_top,space_line,y_max,y_range,
                 y_unity,selection_name,form): 
    """ used for determining the type of each part of y axis taking into account father and children
       'way' is a list whichs allows to determinate if the current block is a type 'soon1' or 'soon2' """
    report_url=self.url
    if level==0:
      name='axis'+str(self.name)
      if self.soon!=[]:
        y.append(Line('',name,1,y_axis_width,
                ((height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))/float(nbr_line)),
                current_top,'',[],'father1'))
      else:
        y.append(Line('',name,1,y_axis_width,((height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))
                 /float(nbr_line)),current_top,'',[],'father2'))
        
      if self.paternity==1:
        if self.soon!=[]:
          y[len(y)-1].addBlockTextY('ytext'+name,str(3*'&nbsp '*level)+'<a href="portal_selections/foldReport?report_url='\
                                    +report_url+'&form_id='+form.id+'&list_selection_name='+selection_name+'">-'+self.title+'</a>')
        else:
          y[len(y)-1].addBlockTextY('ytext'+name,str(3*'&nbsp '*level)+'<a href="portal_selections/unfoldReport?report_url='\
                                    +report_url+'&form_id='+form.id+'&list_selection_name='+selection_name+'">+'+self.title+'</a>')
          

      else:
        y[len(y)-1].addBlockTextY('ytext'+name,str(3*'&nbsp '*level)+self.title)
      
      #one constructs the indicators
      if y_range!=0:
        y[len(y)-1].createIndicators(y_unity,y_range,y_max,height_global_div,height_header,height_axis_x,nbr_line)
      
      if self.soon!=[]:
        level+=1
        for j in range(0,len(self.soon)):
          if j==(len(self.soon)-1):
            way.append(1)
          else:
            way.append(0)
          current_top+=((height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))/float(nbr_line))  
         
          current_top=self.soon[j].buildYtype(way,y,level,y_axis_width,height_global_div,height_header,
                                              height_axis_x,nbr_line,current_top,space_line,y_max,y_range,
                                              y_unity,selection_name,form)
          del way[len(way)-1]
  
    else:
      if self.soon!=[]:
        name=str(self.name)
        for num in way:
          name=name+str(num)
        y.append(Line('',name,1,y_axis_width,((height_global_div-height_header-height_axis_x)/float(nbr_line))
                      ,current_top,'',[],'soon1'))

        if self.paternity==1:
          if self.soon!=[]:
            y[len(y)-1].addBlockTextY('ytext'+name,str(3*'&nbsp '*level)+\
                                      '<a href="portal_selections/foldReport?report_url='+report_url+'&form_id='\
                                      +form.id+'&list_selection_name='+selection_name+'">-'+self.title+'</a>')
          else:
            y[len(y)-1].addBlockTextY('ytext'+name,str(3*'&nbsp '*level)+\
                                      '<a href="portal_selections/unfoldReport?report_url='+report_url+'&form_id='\
                                      +form.id+'&list_selection_name='+selection_name+'">+'+self.title+'</a>') 
        else:
          y[len(y)-1].addBlockTextY('ytext'+name,str(3*'&nbsp '*level)+self.title)

        # one constructs the stick
        y[len(y)-1].addBlockVertical('stickVer'+name,current_top-
                                    ((height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))/float(nbr_line)),
                                    (height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))/float(nbr_line),3*level*5-18) 
                                     #5 is the width of the standart font, maybe a future parameter
        y[len(y)-1].addBlockHorizontal('stickHor'+name,current_top-
                                    ((height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))/float(nbr_line)),
                                    (height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))/float(nbr_line),3*level*5-18) 
        
        #one constructs the indicators
        if y_range!=0:
          y[len(y)-1].createIndicators(y_unity,y_range,y_max,height_global_div,height_header,height_axis_x,nbr_line)
        level+=1
        for j in range(0,len(self.soon)):
          current_top+=((height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))/float(nbr_line))
          if j==(len(self.soon)-1):
            way.append(1)
          else:
            way.append(0)
          current_top=self.soon[j].buildYtype(way,y,level,y_axis_width,height_global_div,height_header,
                                              height_axis_x,nbr_line,current_top,space_line,y_max,y_range,
                                              y_unity,selection_name,form)
          del way[len(way)-1]
  
      else:
        name=str(self.name)
        test='true'
        for num in way:
          name=name+str(num)
          if num==0:
            test='false'
        if test=='true':
          y.append(Line('',name,1,y_axis_width,((height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))/float(nbr_line)),current_top,'',[],'soon2'))
        else:
          y.append(Line('',name,1,y_axis_width,((height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))/float(nbr_line)),current_top,'',[],'soon1'))
          

        if self.paternity==1:
          if self.soon!=[]:
            y[len(y)-1].addBlockTextY('ytext'+name,str(3*'&nbsp '*level)+'<a href="portal_selections/foldReport?report_url='+report_url+'&form_id='+form.id+'&list_selection_name='+selection_name+'">-'+self.title+'</a>')
          else:
            y[len(y)-1].addBlockTextY('ytext'+name,str(3*'&nbsp '*level)+'<a href="portal_selections/unfoldReport?report_url='+report_url+'&form_id='+form.id+'&list_selection_name='+selection_name+'">+'+self.title+'</a>')
            
        else:
          y[len(y)-1].addBlockTextY('ytext'+name,str(3*'&nbsp '*level)+self.title)  
  
        # one constructs the sticks
        y[len(y)-1].addBlockVertical('stickVer'+name,current_top-((height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))/float(nbr_line)),
                                     (height_global_div-height_header-height_axis_x)/float(nbr_line),3*level*5-18)  
        y[len(y)-1].addBlockHorizontal('stickHor'+name,current_top-((height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))/float(nbr_line)),
                                       (height_global_div-height_header-height_axis_x)/float(nbr_line),3*level*5-18) 
        
        #one constructs the indicators   
        if y_range!=0:
          y[len(y)-1].createIndicators(y_unity,y_range,y_max,height_global_div,height_header,height_axis_x,nbr_line)
    return current_top      


  def createIndicators(self,y_unity,y_range,y_max,height_global_div,height_header,height_axis_x,nbr_line):
    #one constructs the indicators
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
 ###############################
    

  def appendHorizontalDottedLine(self,marge_top,maximum_y,height_global_div,height_header,height_axis_x,nbr_line,y_range,y_max): 
    current_top=marge_top
    max_y=maximum_y
    indic=0
    while max_y>=0:
      nameblock='Block_hor_'+self.name+str(indic)
      self.addBlockDottedHoriz(nameblock,current_top) 
      max_y=max_y-(y_max/float((y_range-1)))  #-1 because we don't want a dotted line on the X-axis
      current_top+=(((height_global_div-height_header-height_axis_x)/float(nbr_line))-marge_top)/y_range #10px under the top of the line . float is important here! """ 
      indic+=1
    if self.soon!=[]:
      for i in self.soon:
        i.appendHorizontalDottedLine(marge_top,maximum_y,height_global_div,height_header,height_axis_x,nbr_line,y_range,y_max)
    
     
  def appendActivityBlock(self,list_block):
    indic=0
    for data_block in list_block:
      self.addBlock('ActivityBlock_'+self.name+'_'+str(indic),data_block)
      indic+=1
  

  def createXAxis(self,x_axe,width_line,y_axis_width):
    marge_left=y_axis_width
    indic1=0
    for i in x_axe[1]:
      nameblock='block_'+self.name+str(indic1)
      self.addBlockTextX(nameblock,marge_left,i)
      indic1+=1  
      marge_left+=width_line/float(len(x_axe[1]))
        
  def addSoon(self,soon):
    self.soon.append(soon)       

    
  def createLineChild(self,report_section,field,current_top,y_axis_width,width_line,space_line,height_global_div,height_header,height_axis_x,nbr_line,current_index,url): 

    if len(report_section[current_index].getObject().objectValues())!=0:
      paternity=1
    else:
      paternity=0   
    soon=Line(title=str(report_section[current_index].getObject().getTitle()),name=self.name+'s'+str(current_index) ,begin=y_axis_width,width=width_line,height=(height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))/float(nbr_line),top=current_top,color='#ffffff',paternity=paternity,url=url) 

    if (current_index+1)<=(len(report_section)-1): 
     if report_section[current_index+1].getDepth() == 0:
       current_top=current_top+((height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))/float(nbr_line))+space_line       
     else:
       current_top=current_top+((height_global_div-height_header-height_axis_x-((nbr_line-1)*space_line))/float(nbr_line))
    self.addSoon(soon)                
    return current_top 

    
    
  def insertActivityBlock(self,line_content,object_start_method_id,object_stop_method_id,
                          x_axe,field,info_center,info_topright,info_topleft,info_backleft,
                          info_backright):
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
    if backright!=None: info['botright']=str(backright()) 
    marge=0
    method_start = getattr(line_content,object_start_method_id,None)  
    method_stop= getattr(line_content,object_stop_method_id,None)
    
    block_begin = method_start()
    list_block=[]
    if method_stop!=None:
      block_stop= method_stop()
    else:
      block_stop=None
    if isinstance(block_begin,DateTime):    
        if round(block_begin-DateTime(x_axe[0][0]))!=0:
          block_left=float(round(block_begin-DateTime(x_axe[0][0])))/round(DateTime(x_axe[0][len(x_axe[0])-1])-DateTime(x_axe[0][0]))
        else:
          block_left=0
        if block_stop-DateTime(x_axe[0][0])!=0:            
          block_right=float(round(block_stop-DateTime(x_axe[0][0])))/round(DateTime(x_axe[0][len(x_axe[0])-1])-DateTime(x_axe[0][0]))
        else:
          block_right=0                   
        list_block.append([block_left,block_right-block_left,0.75,info,0.25])
    else:
      for i in x_axe[0]:
        if block_begin==i:
          list_block.append([marge,(block_stop-block_begin)/(float(len(x_axe[0]))),0.75,info,0.25])   
        # 0.75(height) need to be defined        
        marge+=1/float(len(x_axe[0])) 
    
    if list_block!=[]:
      self.appendActivityBlock(list_block) 
      
    if self.soon!=[]:
      soon_line= line_content.objectValues()
      print soon_line
      indic=0
      while indic != len(soon_line):
        indic2=0
        for s in soon_line:
          if s.getTitle() == self.soon[indic].title:
            self.soon[indic].insertActivityBlock(s,object_start_method_id,object_stop_method_id,
                                               x_axe,field,info_center,info_topright,info_topleft,
                                               info_backleft,info_backright)
        indic+=1
        
    
#*************************************************   
    
# class block ***********************************     
class Block:
  def __init__(self,types,name,begin,width=0,height=0,text='',content={},marge_top=0):
    self.types=types
    self.name=name
    self.begin=begin
    self.width=width
    self.height=height
    self.text=text
    self.content=content #stores info block in a dictionnary
    self.marge_top=marge_top
    # self.color=color need to be implemented in the future!
    
  def render(self,line_width,line_height,portal_url,line_begin,y_axis_width,line):
    """used for inserting text in a block. one calculates how to organise the space.
    one defines a width and height parameter (in pixel) which can be 
    changed (depends on the size and the font used)
    one fetches content which is a dictionnary like 
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
      block_width=self.width*line_width-((line_begin+self.begin*line_width+self.width*line_width)-(line_width+y_axis_width))
      block_width=block_width/line_width
    else:
      block_width=self.width
    return self.buildInfoBlockBody(line_width,block_width,font_width,line_height,font_height,line,portal_url) # NEED TO BE TESTED !!!
    
  def render_css(self,line_width,line_height,line,y_axis_width):
    string=''
    font_height=10
    font_width=6
    line_begin=line.begin
    if ((line_begin+self.begin*line_width) < line_begin): #checks if the block starts before the beginning of the line
      block_width=self.width+self.begin
    elif ((self.width*line_width)+(line_begin+self.begin*line_width)>line_width+y_axis_width): #checks if the block is too large for the end of the line. if it is the case, one cuts the block
      block_width=self.width*line_width-((line_begin+self.begin*line_width+self.width*line_width)-(line_width+y_axis_width))
      block_width=block_width/line_width
    else:
      block_width=self.width
    
    return self.buildInfoBlockCss(font_height,line_height,block_width,line_width,font_width,line)   # NEED TO BE TESTED!!
    
  #************************************************************************      
  def addInfoCenter(self,info): #add info in the top left corner of a block    
    self.content['center']=info  
    
  def addInfoTopLeft(self,info): #add info in the top left corner of a block    
    self.content['topleft']=info
  
  def addInfoTopRight(self,info): #add info in the top right corner of a block    
    self.content['topright']=info
  
  def addInfoBottomLeft(self,info): #add info in the bottom left corner of a block    
    self.content['botleft']=info
  
  def addInfoBottomRight(self,info): #add info in the bottom right corner of a block    
    self.content['botright']=info
   
    
  # ****************************************     
  def buildInfoBlockBody(self,line_width,block_width,font_width,line_height,font_height,line,portal_url):
    """ create the body of the html for displaying info inside a block"""
    string=''
    already=0
    block_name=''
    length_list_info=0
    info=''
    for i in self.content:
      if self.content[i]!=None:
        length_list_info += 1
    
    for i in self.content:
      if length_list_info==5:
        test_height= font_height<=((self.height*line_height)/3)
        test_width= ((len(self.content[i])*font_width)<=((block_width*line_width)/3))
      if length_list_info==4 or length_list_info==3:
        if i=='topright':
          print '--------'
          print self.name
          print line_height
        test_height= font_height<=((self.height*line_height)/2)
        test_width= ((len(self.content[i])*font_width)<=((block_width*line_width)/2))
        if i=='topright':
          print test_height
          print test_width 
          print '---------'
     
      if length_list_info==2:
        test_height=font_height<=(self.height*line_height)
        test_width= (len(self.content[i]*font_width)<=((block_width*line_width)/2))
      if length_list_info==1: 
        test_height= font_height<=(self.height*line_height)
        test_width= (len(self.content[i]*font_width)<=(block_width*line_width))   

      if test_height & test_width:
        string+='<div id=\"'+self.name+i+'\"><a href=\"'+portal_url+'/'+line.url+'\">'+ self.content[i]
        string+='</a href></div>\n' 
      else: #one adds interogation.png  
        if ((self.width*line_width>=15) & (self.height*line_height>=15)): 
          info+=self.content[i]+'|'
          if already==0 or i=='center':
            block_name=self.name+i
            already=1
             
    if already==1:
      string+='<div id=\"'+block_name+'\" title=\"'+info+'\"><a href=\"'+portal_url+'/'+line.url+'\"><img src=\"'+portal_url+'/images/question.png\" height=\"15\" width=\"15\"></a href> '
      string+='</div>\n'   
         
    return string     
  #**************************************************

#*******************************************    
  def buildInfoBlockCss(self,font_height,line_height,block_width,line_width,font_width,line):
    """use for creating css code when one needs to add info inside a block"""
    string=''
    already=0
    list_info_length = 0 #counts number of info inside a block(between 0 and 5)
    for j in self.content:
      if  self.content[j]!= None:
        list_info_length += 1 
    if list_info_length ==0:return ''

    matrix = {('center',5):{'left':2,'top':2},('center',4):{'left':0,'top':0},('center',3):{'left':2,'top':2},('center',2):{'left':2,'top':2},
    ('center',1):{'left':2,'top':2},
    ('topright',5):{'left':1.01,'top':0},('topright',4):{'left':1.01,'top':0},('topright',3):{'left':1.01,'top':0},('topright',2):{'left':1.01,'top':2},('topright',1):{'left':1.01,'top':0},
    ('topleft',5):{'left':0,'top':0},('topleft',4):{'left':1,'top':1},('topleft',3):{'left':0,'top':0},('topleft',2):{'left':0,'top':0},('topleft',1):{'left':0,'top':0},
    ('botleft',5):{'left':0,'top':1},('botleft',4):{'left':0,'top':1},('botleft',3):{'left':0,'top':1},('botleft',2):{'left':0,'top':1},('botleft',1):{'left':0,'top':1},
    ('botright',5):{'left':1.01,'top':1.1},('botright',4):{'left':1.01,'top':1.1},('botright',3):{'left':1.01,'top':1.1},('botright',2):{'left':1.01,'top':1.1},('botright',1):{'left':1.01,'top':1.1}
    }
    
    matrix_picture = {('center',5):{'left':2,'top':2},('center',4):{'left':0,'top':0},
    ('center',3):{'left':2,'top':2},('center',2):{'left':0,'top':2},('center',1):{'left':2,'top':2},
    ('topright',5):{'left':1,'top':0},('topright',4):{'left':1,'top':0},('topright',3):{'left':1,'top':0},('topright',2):{'left':1,'top':2},('topright',1):{'left':0,'top':0},
    ('topleft',5):{'left':0,'top':0},('topleft',4):{'left':1,'top':1},('topleft',3):{'left':0,'top':0},('topleft',2):{'left':0,'top':0},('topleft',1):{'left':0,'top':0},
    ('botleft',5):{'left':0,'top':1},('topleft',4):{'left':0,'top':1},('botleft',3):{'left':0,'top':1},('botleft',2):{'left':0,'top':1},('botleft',1):{'left':0,'top':1},
    ('botright',5):{'left':1,'top':1},('botright',4):{'left':0,'top':0},('botright',3):{'left':0,'top':0},('botright',2):{'left':0,'top':0},('botright',1):{'left':1,'top':1}
    }  
    idx= 0
    margin_left=0
    margin_top=0
   
    for i in self.content:         
      matrix_data = matrix[(i,list_info_length)]
      left = matrix_data['left']
      top= matrix_data['top']
      if left == 0:
        margin_left=0
      else:
        margin_left = round(((block_width*line_width)/left)-(font_width*len(self.content[i]))/left)  
      if top==0:
        margin_top=0  
      else:
        margin_top = round(((self.height*(line_height-10))/top)-(font_height/top))

      if list_info_length==5:
        test_height= font_height<=((self.height*line_height)/3)
        test_width= ((len(self.content[i])*font_width)<=((block_width*line_width)/3))
      if list_info_length==4 or list_info_length==3:
        if i=='topright':
          print '********'
          print self.name
          print line_height
        test_height= font_height<=((self.height*line_height)/2)
        test_width= ((len(self.content[i])*font_width)<=((block_width*line_width)/2))
        if i=='topright':
          print test_height,test_width
          print '********'
      if list_info_length==2:
        test_height=font_height<=(self.height*line_height)
        test_width= (len(self.content[i]*font_width)<=((block_width*line_width)/2))
      if list_info_length==1: 
        test_height= font_height<=(self.height*line_height)
        test_width= (len(self.content[i]*font_width)<=(block_width*line_width))

      if test_height & test_width:
        string+='#'+self.name+i+'{position:absolute;\nmargin-left:'+str(margin_left)+'px;\nmargin-top:'+str(margin_top)+'px;\n}\n'              
        line.addBlockInfo(self.name+i)
      else: # we add question.png because the size of the block is not enough
        if ((self.width*line_width>=15) & (self.height*line_height>=15)): 
          matrix_data= matrix_picture[(i,list_info_length)]
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
          if i=='center' and list_info_length==3:
            margin_left=round(((block_width*line_width)/left)-(15/left))  
            margin_top=round(((self.height*(line_height-10))/top)-(font_height/top))
          if i=='center' and list_info_length==2:  
            margin_top=round(((self.height*(line_height-10))/top)-(font_height/top))    
          if already==0 or i=='center':
            string+='#'+self.name+i+'{position:absolute;\nmargin-left:'+str(margin_left)+'px;\nmargin-top:'+str(margin_top)+'0px;\n}'  
            block_disp=self.name+i
            already=1
    return string  
 #####################################################
 
 
            
PlanningBoxWidgetInstance = PlanningBoxWidget()        
 
          
class PlanningBox(ZMIField):
    meta_type = "PlanningBox"
    widget = PlanningBoxWidgetInstance
    validator = PlanningBoxValidatorInstance
    security = ClassSecurityInfo()
    security.declareProtected('Access contents information', 'get_value')
    def get_value(self, id, **kw):
      if id == 'default' and kw.get('render_format') in ('list', ):
        return self.widget.render(self, self.generate_field_key() , None , kw.get('REQUEST'), render_format=kw.get('render_format'))
      else:
        return ZMIField.get_value(self, id, **kw)

    def render_css(self, value=None, REQUEST=None):
      return self.widget.render_css(self,'',value,REQUEST)
              