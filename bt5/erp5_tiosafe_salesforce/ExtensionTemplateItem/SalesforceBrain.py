##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Herve Poulain <herve@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

import TioSafeBrain
from Acquisition import aq_base
from lxml import etree
from zLOG import LOG

# ---------- SF ---------- #
class SalesforceBrain(TioSafeBrain):

  # Salesforce need to another way to put arrows
  def _setArrowTag(self, document=None, xml=None, source_tag='source',
      destination_tag='destination', category=''):
    """ This method build the XML of the arrow. """
    # only work on the data of the document and not on its parent's data
    document = aq_base(document)

    # create the arrow tag and set if exist source and destination
    arrow = etree.SubElement(xml, 'arrow', type=category)
    arrow_list = [(source_tag, 'source'), (destination_tag, 'destination')]
    for prop, tag in arrow_list:
      if getattr(document, prop, None) is not None:
        etree.SubElement(arrow, tag).text = getattr(document, source_tag)


class SalesforceNodeBrain(SalesforceBrain):
  """
    This class allows to build the TioSafe XML of a Salesforce Node.
  """
  __allow_access_to_unprotected_subobjects__ = 1

  def _asXML(self):
    node_type = self.context.getDestinationObjectType()
    if node_type == 'Account':
      node_type = 'Organisation'
    node = etree.Element('node', type=node_type)

    # list of possible tags for a node
    tag_list = (
        'title', 'firstname', 'lastname', 'email', 'phone', 'fax',
        'birthday', 'reference', 'description', 'relation',
    )
    # FIXME-Generic: Duplication of the following code
    for tag in tag_list:
      if not getattr(self, tag, None):
        try:
          delattr(self, tag)
        except AttributeError:
          # it means that the attribute does not exists
          pass
    self._setTagList(self, node, tag_list)
    self._setTagList(self, node, ['category', ], SEPARATOR)

    # check non property existency
    tag_list = ('street', 'zip', 'city', 'country', )
    # FIXME-Generic: Duplication of the following code
    for tag in tag_list:
      if not getattr(self, tag, None):
        try:
          delattr(self, tag)
        except AttributeError:
          # it means that the attribute does not exists
          pass
    check_list = [getattr(self, tag, None) for tag in tag_list]
    if None in check_list:
      LOG("Can not set address, %s doesn't provided full elements" % self.title, 300, "")
      pass
    else:
      address = etree.SubElement(node, 'address')
      self._setTagList(self, address, tag_list)

    xml = etree.tostring(node, pretty_print=True, encoding='utf-8')
    LOG("SalesforceNodeBrain asXML returns : %s" % (xml, ), 300, "")
    return xml


class SalesforceResourceBrain(SalesforceBrain):
  """
    This class allows to build the TioSafe XML of a Salesforce Node.
  """
  __allow_access_to_unprotected_subobjects__ = 1

  def _asXML(self):
    resource_type = self.context.getDestinationObjectType()
    node = etree.Element('node', type=resource_type)

    # list of possible tags for a node
    tag_list = (
      'title', 'reference', 'sale_price', 'purchase_price', 'ean13',
      'description',
    )
    # FIXME-Generic: Duplication of the following code
    for tag in tag_list:
      if not getattr(self, tag, None):
        try:
          delattr(self, tag)
        except AttributeError:
          # it means that the attribute does not exists
          pass
    self._setTagList(self, node, tag_list)
    self._setTagList(self, node, ['category', ], SEPARATOR)

    xml = etree.tostring(node, pretty_print=True, encoding='utf-8')
    LOG("SalesforceResourceBrain asXML returns : %s" % (xml, ), 300, "")
    return xml


class SalesforceTicketBrain(SalesforceBrain):
  """ Build the brain for the Tickets """
  __allow_access_to_unprotected_subobjects__ = 1

  def _asXML(self):
    transaction_type = self.context.getDestinationObjectType()
    transaction = etree.Element('transaction', type=transaction_type)
    integration_site = self.getIntegrationSite()

    get_arrow_list = [
        ('source_ownership', integration_site.person_module, 'person_id'),
        ('destination_ownership', integration_site.person_module, 'person_id'),
        ('source_accounting', integration_site.organisation_module, 'organisation_id'),
        ('destination_accounting', integration_site.organisation_module, 'organisation_id'),
        ('source', integration_site.campaign_module, 'campaign_id'),
        ('destination', integration_site.campaign_module, 'campaign_id'),
    ]
    for tag, method, parameter in get_arrow_list:
      if not getattr(self, tag, None):
        try:
          delattr(self, tag)
        except AttributeError:
          pass
      else:
        parameter_kw = {parameter: getattr(self, tag)}
        try:
          setattr(self, tag, method(**parameter_kw)[0].getGid())
        except:
          setattr(self, tag, "What is %s" % (getattr(self, tag), ))
    # list of possible tags for a sale order
    tag_list = (
        'title', 'start_date', 'stop_date', 'reference', 'currency',
        'causality', 'description',
    )
    # FIXME-Generic: Duplication of the following code
    for tag in tag_list:
      if not getattr(self, tag, None):
        try:
          delattr(self, tag)
        except AttributeError:
          # it means that the attribute does not exists
          pass
    # set tag on the transaction
    self._setTagList(self, transaction, tag_list)
    self._setTagList(self, transaction, ['category', ], SEPARATOR)

    try:
      self._setArrowTagList(self, transaction)
    except ValueError:
      # A mapping must be missing
      return None

    xml = etree.tostring(transaction, pretty_print=True, encoding='utf-8')
    LOG("SalesforceTicketBrain asXML returns : %s" % (xml, ), 300, "")
    return xml


class SalesforceEventBrain(SalesforceBrain):
  """ Build the brain for events """
  __allow_access_to_unprotected_subobjects__ = 1

  def _asXML(self):
    transaction_type = self.context.getDestinationObjectType()
    transaction = etree.Element('transaction', type=transaction_type)
    integration_site = self.getIntegrationSite()

    get_arrow_list = [
        ('source_ownership', integration_site.person_module, 'person_id'),
        ('destination_ownership', integration_site.person_module, 'person_id'),
        ('source_accounting', integration_site.organisation_module, 'organisation_id'),
        ('destination_accounting', integration_site.organisation_module, 'organisation_id'),
        ('source', integration_site.person_module, 'person_id'),
        ('destination', integration_site.person_module, 'person_id'),
    ]
    for tag, method, parameter in get_arrow_list:
      if not getattr(self, tag, None):
        try:
          delattr(self, tag)
        except AttributeError:
          pass
      else:
        parameter_kw = {parameter: getattr(self, tag)}
        try:
          setattr(self, tag, method(**parameter_kw)[0].getGid())
        except:
          setattr(self, tag, "What is %s" % (getattr(self, tag), ))

    # specific work on causality, it could be :
    #   - account
    #   - sale opporttunity
    #   - campaign
    #   - case
    #   - or customer object
    if getattr(self, 'causality', None):
      method_getter_list = [
          (integration_site.organisation_module, 'organisation_id'),
          (integration_site.sale_opportunity_module, 'sale_opportunity_id'),
          (integration_site.campaign_module, 'campaign_id'),
      ]
      object_list = []
      for method, parameter in method_getter_list:
        parameter_dict = { parameter: self.causality, }
        object_list += method(**parameter_dict)

      if len(object_list) == 1:
        self.causality = object_list[0].getGid()
      else:
        pass
    else:
      try:
        delattr(self, 'causality')
      except AttributeError:
        pass

    # list of possible tags for a sale order
    tag_list = (
        'title', 'start_date', 'stop_date', 'reference', 'currency',
        'causality', 'description',
    )
    self._setTagList(self, transaction, tag_list)
    self._setTagList(self, transaction, ['category', ], SEPARATOR)

    # set arrow list
    try:
      self._setArrowTagList(self, transaction)
    except ValueError:
      # A mapping must be missing
      return None

    xml = etree.tostring(transaction, pretty_print=True, encoding='utf-8')
    LOG("SalesforceEventBrain asXML returns : %s" % (xml, ), 300, "")
    return xml

