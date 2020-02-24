# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#               Aurelien Calonne <aurel@nexedi.com>
#               Hervé Poulain <herve@nexedi.com>
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

import os
import subprocess
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG, ERROR
from lxml import etree
from StringIO import StringIO
from Products.ERP5Type.tests.runUnitTest import tests_home
from difflib import unified_diff

class testTioSafeMixin(ERP5TypeTestCase):
  """ This class provides the main generics elements of test. """

  def getSynchronizationTool(self):
    """ return the tool """
    return self.portal.portal_synchronizations

  def getBusinessTemplateList(self):
    """ Return the list of BT required by unit tests. """
    return (
        'erp5_core_proxy_field_legacy',
        'erp5_full_text_mroonga_catalog',
        'erp5_base',
        'erp5_pdm',
        'erp5_simulation',
        'erp5_trade',
        # 'erp5_accounting',
        # 'erp5_invoicing',
        # 'erp5_simplified_invoicing',
        'erp5_syncml',
        'erp5_item',
        'erp5_tiosafe_core',
        'erp5_tiosafe_test',
        # 'erp5_tiosafe_accounting',
        # 'erp5_tiosafe_prestashop',
        # 'erp5_oauth',
    )

  def beforeTearDown(self):
    """ Call the methods which remove all created elements. """
    # remove the main elements, person, account
    if getattr(self, "not_removable_id_list", None) is None:
      self.not_removable_id_list = []
    for module_id in ["person_module", "product_module", "sale_order_module"]:
      module = getattr(self.portal, module_id)
      module.manage_delObjects([x for x in module.objectIds() if x not in self.not_removable_id_list])

    # delete the category integration mapping of the full integration site
    for integration_site in self.portal.portal_integrations.contentValues():
      self.deleteMapping(integration_site)

    # reset the pub/sub
    for sync in self.portal.portal_synchronizations.contentValues():
      if sync.getPortalType() == 'Publication':
        sync.resetSubscriberList()
      else:
        sync.resetSignatureList()
        sync.resetAnchorList()

    # drop the prestashop tables
    self.loadSQLDump(
        self.portal.erp5_sql_connection,
        'dump/prestashop/dump_99_drop_tables.sql',
    )
    self.tic()

  def makeFilePath(self, file_path):
    """ This method allows to build a file path to work with the file. """
    return '%s/%s' % (os.path.dirname(__file__), file_path)

  def loadSQLDump(self, connection, file_path):
    """ This methods allows to generate a database dump. """
    file = open(self.makeFilePath(file_path), 'r')
    sql = file.read().replace(';', ';\0')
    connection.manage_test(sql)

  def executeQuery(self, connection, query):
    """
      This method execute an SQL query in the database. These two elements are
      give as parameters.
    """
    connection.manage_test(query)

  def executePHP(self, integration_site, file_path, **kw):
    """ Execute a php script with the parameter given through kw. """
    # Build the args of the php command
    php_args = '$_GET["site_path"] = "%s";' % integration_site.getRelativeUrl()
    for key, value in kw.items():
      php_args += '$_GET["%s"] = "%s";' % (key, value)
    php_args += 'include("%s");' % self.makeFilePath(file_path)
    # Execute the php command and return the result
    process = subprocess.Popen(
        ['php', '-r', php_args, ],
        stdout=subprocess.PIPE,
    )
    return process.stdout.read()

  def login(self):
    acl_users = self.portal.acl_users
    acl_users._doAddUser('TioSafeUser', 'TioSafeUserPassword', ['Manager'], [])
    user = acl_users.getUserById('TioSafeUser').__of__(acl_users)
    newSecurityManager(None, user)

  def updateSynchronizationObjects(self):
    """ Change the url string of publication & subscription for tests """
    sync_server_path = "file://%s/sync_server" % tests_home
    sync_client_path = "file://%s/sync_client" % tests_home
    portal_sync = self.getSynchronizationTool()

    for pub in portal_sync.objectValues(portal_type="SyncML Publication"):
      pub.edit(
          url_string=sync_server_path,
          subscription_url_string=sync_server_path,
      )
    for sub in portal_sync.objectValues(portal_type="SyncML Subscription"):
      sub.edit(
          url_string=sync_server_path,
          subscription_url_string=sync_client_path,
          user_id='TioSafeUser',
          password='TioSafeUserPassword',
      )

  def synchronize(self, publication, subscription):
    """ This method allows to run the synchronization. """
    portal_sync = self.getSynchronizationTool()
    # To simulate sync which works by networks, the unittest will use file.
    # The XML frames will be exchange by file.
    # Reset files because we work on synchronization by this way.
    # Reset Publication URL
    file = open(subscription.getUrlString()[len('file:/'):], 'w')
    file.write('')
    file.close()
    # Reset Subscription URL
    file = open(subscription.getSubscriptionUrlString()[len('file:/'):], 'w')
    file.write('')
    file.close()
    self.tic()
    # Number of message exchange during synchronization
    nb_message = 1
    # Run synchronization
    result = portal_sync.SubSync(subscription.getPath())
    while result['has_response'] == 1:
      portal_sync.PubSync(publication.getPath())
      self.commit()
      LOG("COMMIT", 300, "COMMIT")
      self.tic()
      result = portal_sync.SubSync(subscription.getPath())
      self.commit()
      LOG("COMMIT", 300, "COMMIT")
      self.tic()
      nb_message += 1 + result['has_response']
    return nb_message

  def loadSync(self, sync_list=None, **kw):
    """ This method allows to call sync on each element of a list. """
    # ZopeTestCase._print('\nSynchronize Persons and Products\n')
    for module in sync_list:
      LOG('Synchronization... ', 0, str(module.getId()))
      self.synchronize(
          publication=module.getSourceSectionValue(),
          subscription=module.getDestinationSectionValue(),
      )

  def getConnectionPlugin(self, site, plugin_type=None):
    """
    Return a specific conneciton plugin
    """
    # XXX-AUREL implement type when needed
    if plugin_type is not None:
      raise NotImplementedError
    return site.objectValues(portal_type=['Web Service Connector',])[0]

  def createMapping(self, integration_site=None, title=None, path=None,
      source_reference=None, destination_reference=None):
    """
      This method allows to declare a mapping through the elements give as
      parameters in the integration site a mapping with the corresponding ERP5
      category.
    """
    # XXX-Aurel why don't we use the dict pass as parameter ?
    base = integration_site
    path_list = path.split('/')
    keyword = {}
    for link in path_list:
      if getattr(base, link, None) is not None:
        base = getattr(base, link, None)
      else:
        keyword['portal_type'] = 'Integration Category Mapping'
        keyword['title'] = title
        keyword['id'] = link
        keyword['source_reference'] = source_reference
        if base == integration_site:
          keyword['portal_type'] = 'Integration Base Category Mapping'
          keyword['destination_reference'] = destination_reference
          if len(path_list) != 1:
            continue
        else:
          keyword['destination_reference'] = base.getDestinationReference() + "/" + destination_reference
        # create the mapping
        base.newContent(**keyword)

  def initMapping(self, integration_site=None):
    """ This method create the mapping in the integration site. """
    # integration site mapping
    if integration_site is not None and \
        integration_site.getPortalType() == 'Integration Site':
      # think to order the list of creation of mappings
      mapping_dict_list = [
          { 'title': 'Country',
            'path': 'Country',
            'source_reference': 'Country',
            'destination_reference': 'region', },
          { 'title': 'France',
            'path': 'Country/France',
            'source_reference': 'France',
            'destination_reference': 'france', },
          { 'title': 'Allemagne',
            'path': 'Country/Allemagne',
            'source_reference': 'Allemagne',
            'destination_reference': 'europe/western_europe/allemagne', },
          { 'title': 'Taille du Ballon',
            'path': 'TailleduBallon',
            'source_reference': 'Taille du Ballon',
            'destination_reference': 'ball_size', },
          { 'title': 's4',
            'path': 'TailleduBallon/s4',
            'source_reference': 's4',
            'destination_reference': 'x4', },
          { 'title': 's5',
            'path': 'TailleduBallon/s5',
            'source_reference': 's5',
            'destination_reference': 'x5', },
          { 'title': 's6',
            'path': 'TailleduBallon/s6',
            'source_reference': 's6',
            'destination_reference': 'x6', },
          { 'title': 'Couleur',
            'path': 'Couleur',
            'source_reference': 'Couleur',
            'destination_reference': 'colour', },
          { 'title': 'Blanc',
            'path': 'Couleur/Blanc',
            'source_reference': 'Blanc',
            'destination_reference': 'white', },
          { 'title': 'Noir',
            'path': 'Couleur/Noir',
            'source_reference': 'Noir',
            'destination_reference': 'black', },
          { 'title': 'Rouge',
            'path': 'Couleur/Rouge',
            'source_reference': 'Rouge',
            'destination_reference': 'red', },
          { 'title': 'Payment Mode',
            'path': 'PaymentMode',
            'source_reference': 'Payment Mode',
            'destination_reference': 'payment_mode', },
          { 'title': 'CB',
            'path': 'PaymentMode/CB',
            'source_reference': 'CB',
            'destination_reference': 'cb', },
          { 'title': 'Cheque',
            'path': 'PaymentMode/Cheque',
            'source_reference': 'Cheque',
            'destination_reference': 'cb', },
      ]
      # browses the list of categories dict
      for mapping in mapping_dict_list:
        self.createMapping(integration_site=integration_site, **mapping)

    self.tic()

  def deleteMapping(self, integration_site):
    """ Remove the category integration mapping of integration site. """
    for category in integration_site.contentValues(
        portal_type='Integration Base Category Mapping'):
      integration_site.manage_delObjects(category.getId())

  def checkTioSafeXML(self, plugin_xml=None, tiosafe_xml=None, xsd_path=None):
    """
      This methods allows to check the xmls with the xsd and to check that
      the two xml are the same.
    """
    self.assertTrue(self.validateXMLSchema(plugin_xml, xsd_path))
    self.assertTrue(self.validateXMLSchema(tiosafe_xml, xsd_path))
    try:
      self.assertEqual(plugin_xml, tiosafe_xml)
    except AssertionError:
      diff = "\n"
      for x in unified_diff(plugin_xml.split('\n'), tiosafe_xml.split('\n'), "plugin", "tiosafe", lineterm=''):
        diff += "%s\n" %(x)
      raise AssertionError, diff

  def validateXMLSchema(self, xml, file_path):
    """ This method allows to check and validate the schema of an xml. """
    file = open(self.makeFilePath(file_path) ,'r')
    xml_schema = ''.join(file.readlines())
    xml_schema = StringIO(xml_schema)
    xml_schema = etree.parse(xml_schema)
    xml_schema = etree.XMLSchema(xml_schema)
    xml = etree.XML(xml)
    validated = xml_schema.validate(xml)
    if validated is False:
      LOG("validateXMLSchema failed with", ERROR, "%s" %(xml_schema.error_log.filter_from_errors()[0]))
    return validated

