##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#               Guy Oswald OBAMA <guy@nexedi.com>
#               thomas <thomas@nexedi.com>
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

# This code is under refactoring. This code will change in near future
# with a lot of cleanups. This is stored only for a temporary purpose.
# Do not rely on the real implementation. It is assumed that the code is
# improved and modified significantly by thomas.

from Products.PythonScripts.Utility import allow_class
from ZPublisher.HTTPRequest import FileUpload
from xml.dom.ext.reader import PyExpat
from xml.dom import Node, minidom
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, get_request
from zipfile import ZipFile, ZIP_DEFLATED
from StringIO import StringIO
from zLOG import LOG
import imghdr
import random
import getopt, sys, os
from urllib import quote



class ScribusParser:
  """
  Parses a Scribus file with PDF-elements inside
  """
  
  #declare security
  security = ClassSecurityInfo()
  
  
  security.declarePublic('getObjectTooltipProperty')
  def getObjectTooltipProperty(self, check_key, default_value, object_name, object_dict):
    """
    check if 'check_key' exists in 'object_dict' and has a value
    if true, then returns this value, else returns 'default_value' and log 'object_name'
    """
    #return object_dict.get(check_key, None) or default_value
    if object_dict.has_key(check_key):
      # 'check_key' exists
      if len(object_dict[check_key]) != 0:
        # check_key corresponding value is not null
        # returning this value
        return object_dict[check_key]
      else:
        # check_key is null, logging and asigning default value
        print "    > " + str(object_name) + " has an invalid '" + str(check_key) \
        + "' : using default = " + str(default_value)
        LOG("WARNING : " + str(object_name),0,"invalid " + str(check_key) \
        + ": using " + str(default_value))
        return default_value
    else:
      # check_key is null, logging and asigning default value
      print "    > " + str(object_name) + " has no '" + str(check_key) \
      + "' : using default = " + str(default_value)
      LOG("WARNING : " + str(object_name),0,"no " + str(check_key) \
      + ": using " + str(default_value))
      return default_value
    

  security.declarePublic('getStringInt')
  def getStringInt(self,input_string):
    """
    convert a string containing an integer or a long number
    into an integer, as should do the int() function (if it
    was not crashing when trying to do such a convertion).
    This function is used to convert position and size values
    to integers to prevent script from crashing.
    """
    return int(input_string.split('.')[0])

  
  security.declarePublic('getXmlObjectProperties')
  def getXmlObjectsProperties(self, xml_string):
    """
    takes a string containing a whole document and returns
    a full dict of 'PAGE', containing a dict of 'PAGEOBJECT',
    containing a dict of all the relative attributes
    """
    
    #ERP5 access_type
    #Create the PyExpat reader
    print "\n => ScibusParser.getXmlObjectProperties"
    print " > create reader"
    LOG("ScribusUtils",1,"create reader")
    reader = PyExpat.Reader()
    
    # Create DOM tree from the xml string
    print " > create DOM tree"
    dom_tree = reader.fromString(xml_string)
    #dom_tree = minidom.parse(xml_string)
    
    ##External script acces_type
    ## testing procedure outside erp5. Put these lines in comment if this
    ## module is called inside erp5.
    #print " => opening socket..."
    #sock = open(xml_string)
    #print " => reading the whole file..."
    #dom_tree = minidom.parse(sock)
    #print " => closing socket..."
    #sock.close()
    
    # creating the root from the input file
    # does not depend on the kind of access (w or w/o erp5)
    dom_root = dom_tree.documentElement
    
    #making a listing of all the PAGE object
    print " > making listing of all PAGE objects"
    page_list = dom_root.getElementsByTagName("PAGE")
        
    returned_page_dict = {}
    
    #for each PAGE object, searching for PAGEOBJECT
    for page in page_list:

      
      # getting page number
      # parsing method from the previous ScribusUtils
      page_number = -1
      for attribute in page.attributes:
        node_name = str(attribute.nodeName)
        node_value = str(attribute.nodeValue)
        if node_name == 'NUM':
          page_number = node_value
        
      print "  > PAGE NUM=" + str(page_number)
      
      # making a listing of all PAGEOBJECT in a specified PAGE
      page_object_list = page.getElementsByTagName("PAGEOBJECT")
      
      # initialising global output dictionary containing pages of elements
      returned_page_object_dict = {}
      
      # for each PAGEOBJECT, building dict with atributes
      for page_object in page_object_list:
          
        # initialising 
        returned_page_object = {}
        field_name = None

        #iterating PAGEOBJECT attributes
        #old parsing method emlployed also here
        for attribute in page_object.attributes:
          node_name = str(attribute.nodeName)
          node_value = str(attribute.nodeValue)
          
          
        #iterating through PAGEOBJECT attributes
        #for attribute in page_object.attributes.keys():
        #  node_name  = str(attribute)
        #  node_value = str(page_object.attributes[attribute].value)
        
        
          if node_name == 'ANNAME':
            if node_value != '':
              #if 'PAGEOBJECT' contains an attribute 'ANNAME' not null then
              #this value is considered as the 'PAGEOBJECT' name
              field_name = node_value.replace(' ','_')
          else:
              #for others attributes, just adding them to the dictionary as
              #standard attributes
              returned_page_object[node_name] = node_value
          
        if field_name != None:
          #if 'PAGEOBJECT' has a valid name, then adding it to the global
          #dictionary containing all the 'PAGEOBJECT' of the 'PAGE'
          returned_page_object_dict[field_name] = returned_page_object
          print "    > PAGEOBJECT = " + str(field_name)
            
      #after having scanned all 'PAGEOBJECT' from a 'PAGE', adding the
      #relatives information to the list of 'PAGE' before going to the next one
      #in case the page is not empty
      if len(returned_page_object_dict) != 0: 
        returned_page_dict[page_number] = returned_page_object_dict

    print "=> end ScribusParser.getXmlObjectProperties"
    return returned_page_dict   



   
  security.declarePublic('getPropertiesConversion')
  def getPropertiesConversion(self, text_page_dict):
    """
    takes a dict generated from 'getXmlObjectsProperties' method and returns a
    dict of PAGE including a list with usefull 'PAGEOBJECT' attributes updated
    with standard attributes and special informations contained in the
    'ANTOOLTIP' attribute.
    
    usefull attributes are
    - position & size
    - type & inputformat (for erp5 and html)
    - creation order (using 'nb' property)
    - erp5 relative position (left, right, etc.)
    - title information
    - other properties (read_only, multiline, etc.)
    - etc.
    
    for each PAGE, all PAGEOBJECT are sorted according to their creation order
    'nb'
    """

    print "\n  => ScribusParser.getPropertiesConversion"
    returned_page_dict = {}
    
    # declaring ScribusParser object to run other functions
    sp = ScribusParser()
  
    
    for page_number in text_page_dict.keys():
      # iterating through 'PAGE' object of the document
      # id = page_number
      # content = page_content
      page_content = text_page_dict[page_number]
      
      print " => PAGE = " + str(page_number)
      
      # declaring special lists used to generate nb for all objects
      # this 'nb' property is usefull to define the object creation order
      # all objects are sorted (has nb / has no nb) and all objects without
      # nb attribte are added t othe end of the 'has nb' list
      nb_property_nbkey_list = []
      nb_property_nonbkey_list = []
      
      # declaring output object
      returned_object_dict = {}
      
      # if page_content.haskey('my_fax_field')
      # print "my_fax_field"
      for object_name in page_content.keys():
        # iterating through 'PAGEOBJECT' of the page
        # id = object_name
        # content = object_content
        object_content = page_content[object_name]

        print "  => PAGEOBJECT = " + str(object_name)
        # recovering other attributes from 'ANTOOLTIP'
        text_tooltipfield_properties = object_content['ANTOOLTIP']
        #declaring output file
        tooltipfield_properties_dict = {}
        #splitting the different attributes
        tooltipfield_properties_list = text_tooltipfield_properties.split('#')
        
        print "      " + str(tooltipfield_properties_list)
        
        
        
        # test if first argument is nb according to previous naming-conventions
        # i.e composed of three digits without id 'nb:' written
        if  str(tooltipfield_properties_list[0]).isdigit():
          # first value of tooltilfield is digit : assuming this is an creation-order
          # information compliant with the previous naming convention
          # modifying this field to make it compatible with new convention
          print "        => first element = " +  str(tooltipfield_properties_list[0] + " is digit...")
          LOG("WARNING : " + str(object_name),0,"out-of-date naming convention found" \
             + "for tooltipfield, please check naming_conventions")
          temp_nb = tooltipfield_properties_list[0]
          # deleting actual entry
          tooltipfield_properties_list.remove(temp_nb)
          # adding new entry to the list
          temp_nb_text = "nb:" + str(temp_nb)
          tooltipfield_properties_list.append(temp_nb_text)
          # end of translating work to get new standard compliant code
        for tooltipfield_property in tooltipfield_properties_list:
          #printing each property before spliting
          print "         " + str(tooltipfield_property)
          # splitting attribute_id / attribute_value
          tooltipfield_properties_split = tooltipfield_property.split(':')
          if len(tooltipfield_properties_split) == 2:
            tooltipfield_id = tooltipfield_properties_split[0]
            tooltipfield_value = tooltipfield_properties_split[1]
            # making dictionary from 'ANTOOLTIP' attributes
            tooltipfield_properties_dict[tooltipfield_id] = tooltipfield_value
        # end of 'ANTOOLTIP' parsing
        
        
        
        # getting usefull attributes from scribus 'PAGEOBJECT' and 'ANTOOLTIP'
        # --------------------------------------------------------------------
        object_properties = {}
          
        # getting object position and size
        object_properties['position_x'] = sp.getObjectTooltipProperty('XPOS','0',object_name,object_content)
        object_properties['position_y'] = sp.getObjectTooltipProperty('YPOS','0',object_name,object_content)
        object_properties['size_x'] = sp.getObjectTooltipProperty('WIDTH','100',object_name,object_content)
        object_properties['size_y'] = sp.getObjectTooltipProperty('HEIGHT','17',object_name,object_content)
        # converting values to integer-compliant to prevent errors when using them
        object_properties['position_x'] = str(float(object_properties['position_x']))
        object_properties['position_x'] = str(sp.getStringInt(object_properties['position_x']))
        object_properties['position_y'] = str(sp.getStringInt(object_properties['position_y']))
        object_properties['size_x'] = str(sp.getStringInt(object_properties['size_x']))
        object_properties['size_y'] = str(sp.getStringInt(object_properties['size_y']))
        
        
        # getting object title
        # object title can only be user-specified in the 'tooltip' dict
        object_properties['title'] = sp.getObjectTooltipProperty('title', object_name, object_name, tooltipfield_properties_dict)
          
        
        # getting object order position for erp5 form
        temp_order = sp.getObjectTooltipProperty('order','none',object_name,tooltipfield_properties_dict)
        if temp_order not in  ['left','right']:
          # temp_order invalid
          # trying to get it from document
          if sp.getStringInt(object_properties['position_x']) > 280.0 :
            temp_order = 'right'
          else :
            temp_order = 'left'
        object_properties['order'] =  temp_order

        
        
        
        # getting special ANFLAG sub-properties
        temp_ANFLAG = long(sp.getObjectTooltipProperty('ANFLAG','0',object_name,object_content))
        # initialising results
        anflag_properties = {}
        anflag_properties['noScroll'] = 0
        anflag_properties['noSpellCheck'] = 0
        anflag_properties['editable'] = 0
        anflag_properties['password'] = 0
        anflag_properties['multiline'] = 0
        anflag_properties['noExport'] = 0
        anflag_properties['required'] = 0
        anflag_properties['readOnly'] = 0
        # analysing result
        print "      => ANFLAG = " + str(object_content['ANFLAG'])
        if temp_ANFLAG - 8388608 >= 0:
          # substracting value
          temp_ANFLAG = temp_ANFLAG - long(8388608)
          # 'do not scroll' field
          # adding property
          anflag_properties['noscroll'] = 1
        if temp_ANFLAG - 4194304 >= 0:
          temp_ANFLAG = temp_ANFLAG - 4194304
          # 'do not spell check' field
          anflag_properties['noSpellCheck'] = 1
        if temp_ANFLAG - 262144 >= 0:
          temp_ANFLAG = temp_ANFLAG - 262144
          # 'editable' field
          anflag_properties['editable'] = 1
        if temp_ANFLAG - 8192 >= 0:
          temp_ANFLAG = temp_ANFLAG - 8192
          # 'password' field
          anflag_properties['password'] = 1
        if temp_ANFLAG - 4096 >= 0:
          temp_ANFLAG = temp_ANFLAG - 4096
          # 'multiline' field
          anflag_properties['multiline'] = 1
        if temp_ANFLAG - 4 >= 0:
          temp_ANFLAG = temp_ANFLAG - 4
          # 'do not export data' field
          anflag_properties['noExport'] = 1
        if temp_ANFLAG - 2 >= 0:
          temp_ANFLAG = temp_ANFLAG - 2
          # 'required field
          anflag_properties['required'] = 1
        if temp_ANFLAG == 1:
          # 'read only" field
          anflag_properties['readOnly'] = 1
        

        # getting maximum number of caracters the field can hold
        # note : only for textfields
        object_properties['maximum_input'] = sp.getObjectTooltipProperty('ANMC','0',object_name,object_content)
        print "      => MaxInput = %s" % object_properties['maximum_input']
        
        # getting object type :
        # first checking for user-specified type in 'tooltip' properties
        if tooltipfield_properties_dict.has_key('type'):
          # 'type' id in tooltip : using it and ignoring other 'type' information
          # in scribus properties
          object_properties['type'] = tooltipfield_properties_dict['type']
        # if no user-specified type has been found, trying to find scribus-type  
        elif object_content.has_key('ANTYPE'):
          # from scribus type (selected in the scribus PDF-form properties)
          object_type = str(object_content['ANTYPE'])
          if object_type == '2':
            #type 2 = PDF-Button
            object_properties['type'] = 'Button'
          elif object_type == '3':
            #type 3 = PDF-Text : Stringfield by default
            object_properties['type'] = 'StringField'
            if anflag_properties['multiline'] == 1:
              # Stringfield is multiline, converting to TextAreaField
              object_properties['type'] = 'TextAreaField'
            elif object_content.has_key('ANFORMAT'):
              object_format = str(object_content['ANFORMAT'])
              # checking kind of Stringfield
              if object_format == '1':
                #type is number
                object_properties['type'] = 'IntegerField'
              elif object_format == '2':
                #type is percentage
                object_properties['type'] = 'FloatField'
              elif object_format == '3':
                #type is date
                object_properties['type'] = 'DateTimeField'
              elif object_format == '4':
                #type is time
                object_properties['type'] = 'DateTimeField'
          elif object_type == '4':
            # type 4 = PDF-Checkbox
            object_properties['type'] = 'CheckBoxField'
          elif object_type == '5':
            # type 5 = PDF-Combobox
            object_properties['type'] = 'ComboBox'
          elif object_type == '6':
            # type 6 = PDF-ListBox
            object_properties['type'] = 'ListBox'
        else:
          # object type not found in user-properties neither in document-properties
          # logging and initialising with default type
          LOG("WARNING : " + str(object_name),0,"no 'type' found, please check your document properties or use 'tooltips' properties")
          print "      => no type specified : assuming default = StringField" 
          object_properties['type'] = 'StringField'
        print "      type = " + str(object_properties['type'])
        
          
        # getting 'required' property
        # first checking from user data in 'tooltip'
        temp_required = sp.getObjectTooltipProperty('required','none',object_name,tooltipfield_properties_dict)
        if  temp_required == 'none':
          # no 'required' property in 'tooltip'
          # cheking global PAGEOBJECT properties for 'required' (found in anflag)
          temp_required = anflag_properties['required']
        object_properties['required'] = temp_required
        
          
        # getting type properties for special types
        # checkbox objects belongs to a group of checkbox
        if str(object_properties['type']) == 'CheckBox' :
          # checking if THIS checkbox is in a group
          object_properties['group'] = sp.getObjectTooltipProperty('group', '0', object_name, tooltipfield_properties_dict)
          print "      group = " + str(object_properties['group'])
          
            
        #object is listbox, and listbox have several possible values
        if str(object_properties['type']) == 'ListBox' :
          #checking if this listbox has different possible values
          object_properties['items'] = sp.getObjectTooltipProperty('items', '', object_name, tooltipfield_properties_dict)
          
             
        #object is datetimefield and need several informations
        if str(object_properties['type']) == 'DateTimeField':
          #checking if field has inpu_order property
          object_properties['input_order'] = sp.getObjectTooltipProperty('input_order','day/month/year',object_name,tooltipfield_properties_dict)
          #
          #checking if field has date_only property
          object_properties['date_only'] = sp.getObjectTooltipProperty('date_only','1',object_name,tooltipfield_properties_dict)   
          
            
        # object is relationstringfield and ned some informations
        # FIXME : quelle est la valeur par defaut pour des champs de ce type ?
        if str(object_properties['type']) == 'RelationStringField':
          object_properties['base_category'] = sp.getObjectTooltipProperty('base_category','0',object_name,tooltipfield_properties_dict)
          object_properties['catalog_index'] = sp.getObjectTooltipProperty('catalog_index','0',object_name,tooltipfield_properties_dict)
          object_properties['default_module'] = sp.getObjectTooltipProperty('default_module','0',object_name,tooltipfield_properties_dict)
          
        
          
        # getting creation order from 'tooltip' properties
        # used to create ERP5 objects in a special order
        if tooltipfield_properties_dict.has_key('nb') and str(tooltipfield_properties_dict['nb']).isdigit():
          # object has a nb properties containing its creation position
          # adding the object in the ordered list
          nb_value = int(tooltipfield_properties_dict['nb'])
          print "      =>'nb' property specified : using it to order PAGEOBJECT elements"
          # iterating through existing list to find right position
          # before inserting value
          if len(nb_property_nbkey_list) == 0:
            print "    => 'nb' list empty : adding without sorting"
            # list is empty : adding value without sort
            nb_property_nbkey_list.insert(0,(nb_value,object_name))
          elif nb_property_nbkey_list[len(nb_property_nbkey_list)-1][0] <= nb_value:
            print "    => 'nb' end : adding at the end"
            # last element is smaller than new element : adding at the end
            nb_property_nbkey_list.append((nb_value,object_name))
          else:
            print "    => checking for place to add the element"
            # searching where to insert the element in the ordered list
            for temp_key in range(len(nb_property_nbkey_list)):
              temp_value = nb_property_nbkey_list[temp_key][0]
              temp_content = nb_property_nbkey_list[temp_key][1]
              print "      @" + str(temp_key) + " temp=" + str(temp_value) + "/" + str(nb_value)
              if nb_value < temp_value:
                #first position where actual 'nb' is smaller than temp 'nb'
                # inserting new couple (nb_value,object_name) here
                print "      inserting here : " + str(temp_value) + "/" + str(nb_value)
                nb_property_nbkey_list.insert(temp_key,(nb_value,object_name))
                # element has been insered , no need to continue the search => breaking
                break
        else:
          # object has no nb property. logging and adding it to the list of
          # nb-less objects. Script will automatically find a 'nb' value for this element
          LOG("WARNING : " + str(object_name),0,"no 'nb' defined : finding a free slot")
          print "      => no 'nb' property specified : post-processing will try to define one"
          nb_property_nonbkey_list.append(object_name)
          
        # adding current object with its relative properties to the dict
        # before going to the next page_object
        returned_object_dict[object_name] = object_properties
        
        
      # final processing before returning full page with modified
      # page_object_properties : setting 'nb' property to all objects
      # without user-specified 'nb' property
      for object_name in nb_property_nonbkey_list:
        # listing all objects with no 'nb' declared
        # defining final position in output list : absolute pos + relative pos
        object_position = len(nb_property_nbkey_list) + 1 
        # and addind it to the end of the final nb-list
        # to give them a 'nb' property
        nb_property_nbkey_list.append((object_position,object_name))
      print "  => final sorting before returning value, " + str(len(nb_property_nbkey_list)) + " elements"
      # now all page_object are referenced in the list, we just need to sort
      # the elements in the good order. for that a new list of objects is needed
      returned_object_list = []
      for nb_ind in range(len(nb_property_nbkey_list)):
        # iterating through final nb-list
        # getting list-object information
        (nb_key, nb_value) = nb_property_nbkey_list[nb_ind]
        # setting object's 'nb' property
        returned_object_dict[nb_value]['nb'] = nb_ind + 1
        # add the object at the end of the new list
        returned_object_list.append((nb_value,returned_object_dict[nb_value]))
        LOG("INFO : " + str(nb_value),0,"creation order =" + str(nb_ind))
        print "    > " + str(nb_value) + " has nb:" + str(nb_ind)
      
        
        
      # adding returned list of object to the page dict
      # before going to the next page
      returned_page_dict[page_number] = returned_object_list
      
      
    
    # returning final dict containing all the modified data
    print "  => end ScribusParser.getPropertiesConversion"
    return returned_page_dict
   
        
  security.declareProtected('Import/Export objects', 'getContentFile')
  def getContentFile(self, file_descriptor):
    """ Get file content """
    return file_descriptor.read()
  
InitializeClass(ScribusParser)
allow_class(ScribusParser)  
