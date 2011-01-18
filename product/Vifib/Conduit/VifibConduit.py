# -*- coding: utf-8 -*-

#from zLOG import LOG, INFO
#import xml_marshaller
from lxml import etree
parser = etree.XMLParser(remove_blank_text=True)


class VifibConduit:
  """This conduit is used to synchronize tiosafe packing list and erp5"""  

  def __init__(self):
    pass

  def convertToXml(self, xml):
    """
    if xml is a string, convert it in a node
    """
    if xml is None: return None
    if isinstance(xml, (str, unicode)):
      if isinstance(xml, unicode):
        xml = xml.encode('utf-8')
      #LOG('VifibCounduit', INFO, '%s' % xml, error=True)
      xml = etree.XML(xml, parser=parser)
    #if we have the xml from the node erp5 we just take the subnode
    if xml.xpath('local-name()') == 'erp5':
      xml = xml[0]
    return xml



  def addNode(self, object=None, xml=None):
    """
      This method create an object
    """
    #LOG('VifibConduit-check-3', INFO, '%s' % xml, error=True)
    xml = self.convertToXml(xml)
    tags_text = {} 
    #fill up a dict with (tag - text) pairs
    for element in xml.iter():
      tags_text[element.tag] = element.text
    #retrieve the packing list module
    sale_packing_list_portal_type = 'Sale Packing List'
    sale_packing_list_module = \
    object.getPortalObject().getDefaultModule(sale_packing_list_portal_type)    
    #We create the new packing list
     
    usage_report_sale_packing_list_document = \
        sale_packing_list_module.newContent(
        portal_type = 'Sale Packing List',
      )
    
    usage_report_sale_packing_list_document.confirm()
    usage_report_sale_packing_list_document.start()
    #Note inverted time and date---remember to correct in slapreport 
    usage_report_sale_packing_list_document.edit(
      start_date=tags_text['time'],
      start_time=tags_text['date'],
      memory=tags_text['Memory'],
      cpu_time=tags_text['CpuTime'],
      cpu_percent=tags_text['CPU'],
      rss=tags_text['RSS'],
    )
    
    return usage_report_sale_packing_list_document

    #software_release_module_id = object.getDefaultModuleId(portal_type = 'Sale Packing List') 
    #software_release_module_id = self.portal.restrictedTraverse(software_release_module_id)    
    #software_release = software_release_module.newContent(portal_type = 'Sale Packing List')
