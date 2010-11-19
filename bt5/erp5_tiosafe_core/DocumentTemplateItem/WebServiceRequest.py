##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5TioSafe.Utils import EchoDictTarget
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from App.Extensions import getBrain
from lxml import etree
from zLOG import LOG, ERROR, INFO
from Products.ERP5Type.Tool.WebServiceTool import ConnectionError


ID_SEPARATOR="-"

class WebServiceRequest(XMLObject, ZopePageTemplate):
  # CMF Type Definition
  meta_type = 'ERP5 Web Service Request'
  portal_type = 'Web Service Request'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Reference
                    , PropertySheet.SimpleItem
                    , PropertySheet.Arrow
                    , PropertySheet.Data
                    , PropertySheet.WebServiceRequest
                      )

  isIndexable = 0
  content_type="text/html"

  def getIntegrationSite(self,):
    """
    return integration site if the wsr
    """
    # XXX this must become a caching method later
    if getattr(self, "integration_site", None) is not None:
      if not isinstance(getattr(self, "integration_site"), str):
        self.integration_site = None
    if getattr(self, "integration_site", None) is None:
      parent = self.getParentValue()
      while parent.getPortalType() != "Integration Site":
        parent = parent.getParentValue()
      self.integration_site = parent.getPath()
    return self.getPortalObject().portal_integrations.restrictedTraverse(self.integration_site)

  def edit(self, **kw):
    """
    Override the edit method to register page template values
    """
    if kw.get('data'):
      self.pt_edit(text=kw['data'], content_type=kw['content_type'])
    return self._edit(**kw)

  def getIDParameterName(self):
    """
    Return the parameter name used for id
    """
    if self.getDestinationObjectType():
      return "%s_id" %(self.getDestinationObjectType().replace(" ", "_").lower())
    else:
      return "id"

  def __call__(self, context_document=None, test_mode=False, **kw):
    """
    Make this object callable. It will call the method defined in reference using
    the web service connector it is related to
    """
    if kw.has_key("id"):
      kw[self.getIDParameterName()] = str(kw.pop("id"))

    sub_id = None
    if kw.has_key(self.getIDParameterName()) and ID_SEPARATOR in kw[self.getIDParameterName()]:
      kw[self.getIDParameterName()], sub_id = kw[self.getIDParameterName()].split(ID_SEPARATOR)

    object_list = []
    method_name = self.getReference()
    try:
      connection = self.getSourceValue().getConnection()
    except AttributeError:
      LOG("__call__ of %s" %(self.getPath(),), ERROR,
          "Error on getting connection, connector is %s" %(self.getSourceValue(),))
      connection = None
    if connection is None:
      if test_mode:
        self._edit(last_request_parameter=str(kw),
                   last_request_result="",
                   last_request_path="",
                   last_request_error="No connection available, connector is %s" %(self.getSourceValue(),))
        return []
      else:
        raise ValueError, "No connection available"

    # Add specific parameters defined on integration site
    site = self.getIntegrationSite()
    if site.getLanguage():
      kw['language'] = site.getLanguage()

    if site.getStartDate():
      kw['start_date'] = site.getStartDate()

    if site.getStopDate():
      kw['stop_date'] = site.getStopDate()

      
    # Render page template content
    if getattr(self, "data", None) and len(self.data):
      #LOG("passing options %s to self %s" %(kw, self.getPath()), 300, "CALL")
      pt_data = self.pt_render(extra_context={'options': kw, })
      pt_data = pt_data.replace('\n', '')
      kw = {'data': pt_data}

    # transforms parameters
    #LOG("before transformation of params %s" %(kw), 300, self.getPath())
    new_kw = kw.copy()
    args = []
    if self.getDestination():
      for k,v in kw.iteritems():
        new_key = site.getMappingFromProperty(self.getDestinationValue(), k)
        new_kw.pop(k)
        if new_key is None:
          # Some web service does not need explicit parameters
          args.append(v)
        else:
          new_kw[new_key] = v

    kw = new_kw
    #LOG("calling with params args = %s, kw = %s" %(args, kw), 300, self.getPath())
    error = None
    # Call the method
    try:
      url, xml = getattr(connection, method_name)(*args, **kw)
    except ConnectionError, msg:
      if test_mode:
        error = msg
        url = connection.url
        xml = ""
      else:
        raise


    # Register information for testing/debug purposes
    if test_mode:
      self._edit(last_request_parameter="args = %s, kw = %s" %(str(args), str(kw)),
                 last_request_result=xml,
                 last_request_path=url,
                 last_request_error=error)

    def getSubMappingObject(object, parser_dict):
      for mapping in object.objectValues():
        if mapping.getPortalType() == "Integration Property Mapping":
          parser_dict[str(mapping.getSourceReference())] = (mapping.getDestinationReference(), False)
        # else:
        #   # Sub mapping
        #   parser_dict[str(mapping.getSourceReference())] = (mapping.getDestinationReference(), True)
        #   getSubMappingObject(mapping, parser_dict)

    # Parse the result
    if self.getDestination():
      parser_dict = {str(self.getDestinationValue().getSourceReference()) : (self.getDestinationValue().getDestinationReference(), True)}
      getSubMappingObject(self.getDestinationValue(), parser_dict)
    else:
      return []


    if type(xml) == list:
      result_list = self.parse_dict(parser_dict, xml)
    else:
      parser = etree.XMLParser(target = EchoDictTarget(parser_dict))
      # FIXME: About prestashop sync, '&' and '&' char in xml cause problem
      # xml = xml.replace('&', '')
      #LOG("got XML from WSR %s = %s" %(method_name, xml), 300, "will call parser with %s" %(parser_dict))
      result_list = []
      try:
        result_list = etree.XML(xml, parser,)
      except etree.XMLSyntaxError:
        LOG("WebServiceRequest", ERROR, "Bad XML returned by request %s with kw = %s, xml = %s" %(self.getPath(), kw, xml))
        if test_mode:
          self._edit(last_request_error="Bad XML returned by request, impossible to parse it")
        else:
          raise ValueError, "Bad XML returned by request %s with kw = %s, xml = %s" %(self.getPath(), kw, xml)

    brain = getBrain(self.brain_class_file, self.brain_class_name, reload=1)

    script_id = self.getBrainBuilderScript(None)
    if script_id is not None:
      brain_builder_script = getattr(self, script_id, None)
    else:
      brain_builder_script = None
    if brain_builder_script is not None:
      for result in result_list:
        object_list.extend(brain_builder_script(result, brain))
      if sub_id:
        object_list = [object_list[int(sub_id)-1],]
    else:
      for result in result_list:
        #LOG("initialising brain", INFO, "data is %s" %(result))
        obj = brain(context=self,
                    object_type=self.getDestinationObjectType(),
                    **result)
        object_list.append(obj)

    return object_list

  def __getitem__(self, item):
    """
    Simulate the traversable behaviour by retrieving the item through
    the web service
    """
    # build parameter name
    kw = {self.getIDParameterName() : str(item), }
    object_list = self(**kw)
    if len(object_list) == 1:
      return object_list[0]
    else:
      raise KeyError, "Item %s does not exists call by Web Service Request %s with params %s return %d results" % (item,
                                                                                                                   self.getTitle(),
                                                                                                                   kw,
                                                                                                                   len(object_list))

  def parse_dict(self, parser_dict, dict_list):
    """ Render the dict list mapped by the parser dict. """
    # TODO: This parser method must be defined in the Web Service Connector
    data_list = []
    for dictionnary in dict_list:
      property_dict = {}
      for k, v in dictionnary.items():
        k = parser_dict.get(k)
        if k is not None:
          k = k[0]
          property_dict[k] = unicode(v)
      data_list.append(property_dict)
    return data_list

