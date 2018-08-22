##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
#                Aurelien Calonne <aurel@nexedi.com>
#                 Mohamadou Mbengue <mayoro@nexedi.com>
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

from App.Extensions import getBrain
from lxml import etree

SEPARATOR = '\n'

NodeBrain = getBrain('TioSafeBrain', 'Node', reload=1)
ResourceBrain = getBrain('TioSafeBrain', 'Resource', reload=1)
TransactionBrain = getBrain('TioSafeBrain', 'Transaction', reload=1)
LastIdBrain = getBrain('TioSafeBrain', 'LastId', reload=1)

class Transaction(TransactionBrain):
  """
    This class allows to build the TioSafe XML of a Sale Order and to sync.
  """
  __allow_access_to_unprotected_subobjects__ = 1

  def __init__(self, object_type, context, **kw):
    TransactionBrain.__init__(self, object_type, context, **kw)


  def _asXML(self):
    transaction = etree.Element('transaction', type="Payment Transaction")
    integration_site = self.getIntegrationSite()

    # marker for checking property existency
    MARKER = object()
    # Generate the title using the reference and the origin of the transaction
    self.reference = self.id
    self.stop_date = self.start_date
    
    # list of possible tags for a payment transaction
    tag_list = (
        'title', 'start_date', 'stop_date', 'reference',
    )
    self._setTagList(self, transaction, tag_list)
    self._setTagList(self, transaction, ['category', ], SEPARATOR)

        
    # transaction the movement list
    movement_list = []

    method_id = self.getPortalType().replace(' ', '')
    portal_type = self.getPortalType().replace(' ', '_').lower()
    module_id = "%s_module" %(portal_type)
    
    module = getattr(integration_site, module_id)

    getter_line_method = getattr(
        module,
        'get%sLineList' % (method_id,),
        MARKER,
    )

    if getter_line_method is not MARKER:
      # browse each transaction lines, build the sort element and set data
      parameter_kw = {'%s_id' % portal_type: str(self.getId()), }
      for line in getter_line_method(**parameter_kw):
        key_list = ['id', 'gross_price']
        value_list = [getattr(line, x, '') for x in key_list]
        movement_dict = {'context': line,}
        # set to None the '' value of the list
        for k, v in zip(key_list, value_list):
          movement_dict[k] = v or None

        gross_price = movement_dict['gross_price'].replace(",", ".");
        movement_dict['price'] = float(gross_price)
        
        movement_list.append(movement_dict)
           

    # the second part build the XML of the transaction
    # browse the ordered movement list and build the movement list as a result
    # the xml through of the line data in the dict
    for movement_dict in movement_list:
      movement = etree.SubElement(transaction, 'movement')
      # set arrow list on the movement
      #if movement_dict.get("context", None) is not None:
      #  self._setArrowTagList(movement_dict['context'], movement)
      # if exist the following tags in the line dict, add them in the xml
      tag_list = ('price',)
      for tag in tag_list:
        if tag in movement_dict:
          if movement_dict[tag] is not None:
            element = etree.SubElement(movement, tag)
            if tag == "price":
              element.text = "%.2f" % (float(movement_dict.get(tag, 0.0)),)
            else:
              element.text = movement_dict[tag]
      # add the categories to the movement
      for category_value in movement_dict.get('category', []):
        category = etree.SubElement(movement, 'category')
        category.text = category_value


    return etree.tostring(transaction, pretty_print=True, encoding='utf-8')
