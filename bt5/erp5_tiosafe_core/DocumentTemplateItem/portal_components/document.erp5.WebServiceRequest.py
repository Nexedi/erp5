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
from erp5.component.module.TioSafeUtils import EchoDictTarget, NewEchoDictTarget
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
# pylint:disable=no-name-in-module
try: # BBB Zope 2.12
  from App.Extensions import getBrain
except ImportError:
  from Shared.DC.ZRDB.DA import getBrain
# pylint:enable=no-name-in-module
from lxml import etree
from zLOG import LOG, ERROR, INFO
from erp5.component.tool.WebServiceTool import ConnectionError
from Products.ERP5Type.Cache import CachingMethod
import six

if six.PY3:
  long = int

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
    def cached_getIntegrationSite(self):
      parent = self.getParentValue()
      while parent.getPortalType() != "Integration Site":
        parent = parent.getParentValue()
      return parent.getPath()

    cached_getIntegrationSite = CachingMethod(cached_getIntegrationSite,
                                   id="WebServiceRequest_getIntegrationSite",
                                   cache_factory="erp5_content_long")

    integration_site = cached_getIntegrationSite(self)
    return self.getPortalObject().portal_integrations.restrictedTraverse(integration_site)

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
    def cached_getIDParameterName(self):
      if self.getDestinationObjectType():
        return "%s_id" %(self.getDestinationObjectType().replace(" ", "_").lower())
      else:
        return "id"
    cached_getIDParameterName = CachingMethod(cached_getIDParameterName,
                                   id="WebServiceRequest_getIDParameterName",
                                   cache_factory="erp5_content_long")
    return cached_getIDParameterName(self)


  def __call__(self, context_document=None, test_mode=False, REQUEST=None, **kw):
    """
    Make this object callable. It will call the method defined in reference using
    the web service connector it is related to
    """
    if REQUEST is not None:
      return self.view()
    #LOG("_call__", 300, kw)
    if "id" in kw:
      kw[self.getIDParameterName()] = str(kw.pop("id"))

    sub_id = None
    if self.getIDParameterName() in kw and ID_SEPARATOR in kw[self.getIDParameterName()]:
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
        raise ValueError("No connection available")

    # Add specific parameters defined on integration site
    site = self.getIntegrationSite()
    if site.getLanguage():
      kw['language'] = site.getLanguage()

    if site.getStartDate():
      kw['start_date'] = site.getStartDate()

    if site.getStopDate():
      kw['stop_date'] = site.getStopDate()


    # Render page template content
    if self.hasData():
      #LOG("passing options %s to self %s" %(kw, self.getPath()), 300, "CALL")
      pt_data = self.pt_render(extra_context={'options': kw, })
      pt_data = pt_data.replace('\n', '')
      kw = {'data': pt_data}

    # transforms parameters
    #LOG("before transformation of params %s" %(kw), 300, self.getPath())
    new_kw = kw.copy()
    args = []
    if self.getDestination():
      for k,v in six.iteritems(kw):
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

    def callRequest(self, method_name, *args, **kw):
      connection = self.getSourceValue().getConnection()
      return getattr(connection, method_name)(*args, **kw)

    # cached_callRequest = CachingMethod(callRequest,
    #                                    id="WebServiceRequest_callRequest",
    #                                    cache_factory="erp5_content_short")

    # Call the method
    try:
      url, xml = callRequest(self, method_name, *args, **kw)
    except ConnectionError as msg:
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

    def buildParserDict(root_mapping):
      parser_dict = {}
      for mapping in root_mapping.contentValues():
        if len(mapping.contentValues()):
          sub_parser_dict = buildParserDict(mapping)
          parser_dict[mapping.getSourceReference()] = (mapping.getDestinationReference(), sub_parser_dict)
        else:
          parser_dict[mapping.getSourceReference()] = (mapping.getDestinationReference(), None)
      return parser_dict

    if self.hasDestination():
      sub_parser_dict = buildParserDict(self.getDestinationValue())
      parser_dict = {self.getDestinationValue().getSourceReference() : (self.getDestinationValue().getDestinationReference(), sub_parser_dict)}
    else:
      return []

    # Parse the result
    if self.getSourceValue().getParserMethodId():
      method = getattr(self, self.getSourceValue().getParserMethodId())
      result_list = method(result=xml, parser_dict=parser_dict)
    else:
      if type(xml) == list:
        result_list = self.parse_dict(parser_dict, xml)
      else:
        parser = etree.XMLParser(target = NewEchoDictTarget(parser_dict))
        # FIXME: About prestashop sync, '&' and '&' char in xml cause problem
        # xml = xml.replace('&', '')
        #LOG("got XML from WSR %s = %s" %(method_name, xml), 300, "will call parser with %s" %(parser_dict))
        result_list = []
        try:
          result_list = etree.XML(xml, parser,)
          #LOG("result_list = %r" %(result_list), 300, "")
        except etree.XMLSyntaxError:
          LOG("WebServiceRequest", ERROR, "Bad XML returned by request %s with kw = %s, xml = %s" %(self.getPath(), kw, xml))
          if test_mode:
            self._edit(last_request_error="Bad XML returned by request, impossible to parse it")
          else:
            raise ValueError("Bad XML returned by request %s with kw = %s, xml = %s" %(self.getPath(), kw, xml))

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
    try:
      long(item)
    except ValueError:
      raise KeyError("Item %s does not exists call by Web Service Request %s : not a long" % (item,
                                                                                               self.getTitle(),))
    kw = {self.getIDParameterName() : str(item), }
    object_list = self(**kw)
    if len(object_list) == 1:
      return object_list[0]
    else:
      raise KeyError("Item %s does not exists call by Web Service Request %s with params %s return %d results" % (item,
                                                                                                                   self.getTitle(),
                                                                                                                   kw,
                                                                                                                   len(object_list)))

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

