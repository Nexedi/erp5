# -*- coding: utf-8 -*
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Cedric de Saint Martin <cedric.dsm@tiolive.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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

"""Vifib and Slapgrid interaction scenarios"""
import os
import random
import shutil
import signal
import stat
import subprocess
import glob
import re
import xmlrpclib
from DateTime import DateTime
from StringIO import StringIO
from supervisor.xmlrpc import SupervisorTransport

from Testing.ZopeTestCase import _print
import Products.ERP5Type.tests.ERP5TypeLiveTestCase
from Products.ERP5Type.tests.ERP5TypeLiveTestCase import ERP5TypeLiveTestCase
reload(Products.ERP5Type.tests.ERP5TypeLiveTestCase)
ERP5TypeLiveTestCase = Products.ERP5Type.tests.ERP5TypeLiveTestCase.\
     ERP5TypeLiveTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
import transaction

class SubprocessTimeout(Exception):
  pass

def subprocess_timeout_handler(signum, frame):
  raise SubprocessTimeout('Break by %s' % signum)

class TestManualDefaultSetup(ERP5TypeLiveTestCase):
  """Tests default manual setup and slapgrid result"""
  computer_module_portal_type = 'Computer Module'
  computer_partition_portal_type = 'Computer Partition'
  computer_portal_type = 'Computer'
  document_module_portal_type = 'Document Module'
  file_portal_type = 'File'
  hosting_subscription_module_portal_type = 'Hosting Subscription Module'
  hosting_subscription_portal_type = 'Hosting Subscription'
  internet_protocol_address_portal_type = 'Internet Protocol Address'
  purchase_packing_list_portal_type = "Purchase Packing List"
  purchase_packing_list_line_portal_type = "Purchase Packing List Line"
  sale_packing_list_line_portal_type = 'Sale Packing List Line'
  sale_packing_list_module_portal_type = 'Sale Packing List Module'
  sale_packing_list_portal_type = 'Sale Packing List'
  service_module_portal_type = 'Service Module'
  service_portal_type = 'Service'
  software_instance_module_portal_type = 'Software Instance Module'
  software_instance_portal_type = 'Software Instance'
  software_product_portal_type= 'Software Product'
  software_release_module_portal_type = 'Software Release Module'
  software_release_portal_type = 'Software Release'
  usage_report_portal_type = 'Usage Report'

  def afterSetUp(self):
    # validate needed rules
    self.cleanup_list = []
    #self.validateRules()
    self.login("devel")

  def beforeTearDown(self):
    #self.cleanupGarbage()
    pass#transaction.commit()

  def collectGarbage(self, document):
    """Keeps a list of documents to erase at the end of the test
    """
    self.cleanup_list.append(document)

  def cleanupGarbage(self):
    if getattr(self, 'cleanup_list', None) is None:
      return
    for document in self.cleanup_list:
      parent = document.getParentValue()
      document_id = document.getId()
      #if document_id in parent.objectIds():
      parent.manage_delObjects(ids=[document_id])

  #
  # Helper methods
  #
  def defineIds(self):
    """Generates need ids, names and path in order them to be unique"""
    self.tmp_directory = "/tmp"
    try:
      self.tmp_directory = os.environ['TMP']
    except KeyError:
      pass
    self.computer_guid = '%s%s' % ('testslapgrid', #self.id().replace('__', ''),
          int(random.random() * 100000000))
    self.partition_id = '%spart' % self.computer_guid
    self.ip_address = '127.0.0.1'
    self.tcp_port = "1234"
    self.udp_port = "1234"
    self.python_binary = "/home/nexediadmin/python2.6/parts/python2.6/bin/python2.6"
    self.vifib_product_directory = '/home/nexediadmin/vifib-devel-instance/'\
        'buildbot/Products/Vifib/'
    self.working_directory = os.path.join(self.tmp_directory, self.computer_guid)
    self.slapgrid_buildout_directory = os.path.join(self.working_directory,
        'slapgrid_buildout')
    self.buildout_binary = os.path.join(self.slapgrid_buildout_directory,
        'bin', 'buildout')
    self.slapgrid_binary = os.path.join(self.slapgrid_buildout_directory,
        'bin', 'slapgrid')
    self.bootstrap_py_file = os.path.join(self.vifib_product_directory, 'tests',
        'test_data', 'bootstrap.py')
    self.slapgrid_buildout_cfg_file = os.path.join(self.vifib_product_directory,
        'tests', 'test_data', 'slapgrid.buildout.cfg')
    self.software_root_directory = os.path.join(self.working_directory,
        'software_root')
    self.instance_root_directory = os.path.join(self.working_directory,
        'instance_root')
    self.computer_partition_directory = os.path.join(
        self.instance_root_directory, self.partition_id)
    self.supervisor_socket = os.path.join(self.instance_root_directory,
        'supervisor.sock')
  
  def createTestSequenceAndPlay(self, sequence_string):
    """Creates a test sequence, try to play it, then clean up directories"""
    sequence_list = SequenceList()
    sequence_list.addSequenceString(sequence_string)
    try:
      sequence_list.play(self)
    finally:
      if os.path.exists(self.working_directory):
        if os.path.exists(self.supervisor_socket):
          self.shutdownSupervisor()
        if os.environ.get('SLAP_TEST_KEEP_WORKDIR', 'false').lower() != 'true':
          try:
            shutil.rmtree(self.working_directory)
          except OSError:
            shutil.rmtree(self.working_directory)
        else:
          _print('Working directory %r kept.'% self.working_directory)
          
  def appendAggregateToDocument(self, sequence, document_id, append_id):
    document = sequence.get(document_id)
    append = sequence.get(append_id)
    document.edit(
        aggregate_list=document.getAggregateList() + [append.getRelativeUrl()]
    )

  def prepareDirectoryStructure(self):
    """Simulates human which prepares directory structure on server"""
    # first level of working directory - test environment specific
    os.mkdir(self.working_directory)
    # directory where slapgrid will be installed by buildout
    os.mkdir(self.slapgrid_buildout_directory)
    # directory which will be used by slapgrid software
    os.mkdir(self.software_root_directory)
    # directory which will be used by slapgrid instance
    os.mkdir(self.instance_root_directory)
    # and system administrator is responsible for creating computer partition
    os.mkdir(self.computer_partition_directory)
    os.chmod(self.computer_partition_directory, 0750)

  def callAndPrint(self, command_list, remove_from_env=None, asserts=True,
      **subprocess_kwargs):
    _print('\nInvoking %r:\n'%command_list)
    try:
      signal.signal(signal.SIGALRM, subprocess_timeout_handler)
      signal.alarm(int(os.environ.get('SLAP_TEST_SUBPROCESS_TIMEOUT', 300)))
    except ValueError:
      _print('\nCould not set signal.alarm.')
    if remove_from_env is not None:
      subprocess_kwargs['env'] = self.getCleanedEnviron(remove_from_env)
    try:
      subprocess_kwargs.update(stdout=subprocess.PIPE,
          stderr=subprocess.STDOUT)
      popen = subprocess.Popen(command_list, **subprocess_kwargs)
      result = popen.communicate()[0]
      _print(result)
    finally:
      try:
        signal.alarm(0)
      except ValueError:
        pass
    if asserts:
      self.assertEqual(0, popen.returncode,
        'Command %r failed with message:\n%s' % (command_list, result))

  def getCleanedEnviron(self, to_remove_list):
    current_env = os.environ.copy()
    for k in to_remove_list:
      current_env.pop(k, None)
    return current_env

  def bootstrapSlapgridBuildout(self):
    command_list = [self.python_binary, '-S', self.bootstrap_py_file, '-d',
        '-c', self.slapgrid_buildout_cfg_file, 'buildout:directory=%s'%
        self.slapgrid_buildout_directory]
    self.callAndPrint(command_list, cwd=self.slapgrid_buildout_directory,
      remove_from_env=['SOFTWARE_HOME', 'PYTHONPATH',
          'ZOPE_HOME', 'CLIENT_HOME'])

  def runSlapgridBuildout(self):
    command_list = [self.python_binary, '-S', self.buildout_binary, '-U', '-c',
      self.slapgrid_buildout_cfg_file,
      'buildout:directory=%s'% self.slapgrid_buildout_directory,
      'buildout:find-links=%s' % 'https://nexedivifib1.dyn.majimoto.net:40443/'\
          'erp5/web_site_module/erpypi/']
    self.callAndPrint(command_list, remove_from_env=[
      'SOFTWARE_HOME', 'PYTHONPATH', 'ZOPE_HOME', 'CLIENT_HOME'])

  def shutdownSupervisor(self):
    xmlrpclib.ServerProxy('http://127.0.0.1', SupervisorTransport('', '',
      'unix://%s' % self.supervisor_socket)).supervisor.shutdown()

  #
  # Steps
  #
  def stepRunSlapgrid(self, sequence=None):
    """Runs slapgrid binary

    On purpose python environment and site is imported.
    slapgrid shall work correctly in such case and it is its job to clean
    python before running buildout or external python binaries.

    Note: Unfortunately ERP5 tests runs with heavily modified environment and
          it is *just* impossible to run print 'hello world' in different
          python (as PYTHONPATH is set to python2.4 and slapgrid shall run with
          python2.6).
    """
    command_list = [self.slapgrid_binary,
      '--software-root', self.software_root_directory,
      '--instance-root', self.instance_root_directory,
      '--master-url', self.portal.portal_slap.absolute_url(),
      '--computer-id', sequence.get('computer').getReference(),
      '--supervisord-socket', self.supervisor_socket]
    self.callAndPrint(command_list, remove_from_env=[
      'SOFTWARE_HOME', 'PYTHONPATH', 'ZOPE_HOME', 'CLIENT_HOME'])

  def stepRunSlapgridWithoutAssert(self, sequence=None):
    """Runs slapgrid binary

    On purpose python environment and site is imported.
    slapgrid shall work correctly in such case and it is its job to clean
    python before running buildout or external python binaries.

    Note: Unfortunately ERP5 tests runs with heavily modified environment and
          it is *just* impossible to run print 'hello world' in different
          python (as PYTHONPATH is set to python2.4 and slapgrid shall run with
          python2.6).
    """
    command_list = [self.slapgrid_binary,
      '--software-root', self.software_root_directory,
      '--instance-root', self.instance_root_directory,
      '--master-url', self.portal.portal_slap.absolute_url(),
      '--computer-id', sequence.get('computer').getReference(),
      '--supervisord-socket', self.supervisor_socket]
    return self.callAndPrint(command_list, remove_from_env=[
        'SOFTWARE_HOME', 'PYTHONPATH', 'ZOPE_HOME',
        'CLIENT_HOME'], asserts=False)

  def stepPrepareTestingEnvironment(self, sequence=None):
    self.prepareDirectoryStructure()
    self.bootstrapSlapgridBuildout()
    self.runSlapgridBuildout()

  def stepCreateSoftwareReleaseFile(self, sequence=None):
    module = self.portal.getDefaultModule(
        portal_type=self.document_module_portal_type)
    software_release_file=module.newContent(
        portal_type=self.file_portal_type,
        title='testVifibSlapgrid')
    self.cleanup_list.append(software_release_file)
    sequence.edit(software_release_file=software_release_file)

  def stepCreateSoftwareTemplateFile(self, sequence=None):
    module = self.portal.getDefaultModule(
        portal_type=self.document_module_portal_type)
    software_template_file = module.newContent(
      portal_type=self.file_portal_type,
      title='testVifibSlapgrid')
    self.cleanup_list.append(software_template_file)
    sequence.edit(software_template_file=software_template_file)

  def stepLoadSoftwareTemplateFile(self, sequence=None):
    software_template_file = sequence.get('software_template_file')
    software_template_file.edit(source_reference='%s-template.cfg' \
        % self.computer_guid,
       version='1',
       file=StringIO(str("""[buildout]
parts =
  dummy-software-instance

[dummy-software-instance]
recipe = collective.recipe.template
input = inline:
  #! /bin/sh
  exec ${source_location}/bin/slapmonitor ${source_location}/bin/dummy-software
output = ${target_location}/bin/run
mode = 755
""")))

  def stepSetReferenceOnSoftwareTemplateFile(self, sequence=None):
    software_template_file = sequence.get('software_template_file')
    software_template_file.edit(reference=self.computer_guid + \
        "_template")

  def stepLoadSoftwareReleaseFile(self, sequence=None):
    software_release_file = sequence.get('software_release_file')
    software_template_file = sequence.get('software_template_file')
    host_pattern = re.compile('^(?:f|ht)tp(?:s)?\://([^/]+)')
    hostname = host_pattern.findall(software_template_file.getAbsoluteUrl())[0]
    software_template_file_uri = 'https://%s/erp5/web_site_module/erpypi/' \
        '%s-1.cfg' % (hostname, software_template_file.getReference())
    content = """[buildout]
parts =
  dummy-software
  dummy-software-template
  slap-monitor
# slap monitor shall be took from trunk
find-links =
  https://nexedivifib1.dyn.majimoto.net:40443/erp5/web_site_module/erpypi/slapos.slapmonitor-0.0.6dev.tar.gz

[dummy-software]
recipe = collective.recipe.template
input = inline:
  #!/bin/sh
  while :; do
    echo "This is dummy software"
    sleep 5
  done

output = ${buildout:bin-directory}/dummy-software
mode = 755

[dummy-software-template]
recipe = hexagonit.recipe.download
url = @DUMMY_SOFTWARE_TEMPLATE@
download-only = true
destination = ${buildout:directory}
filename = template.cfg

[slap-monitor]
recipe = zc.recipe.egg:scripts
eggs =
  slapos.slapmonitor
""".replace('@DUMMY_SOFTWARE_TEMPLATE@', software_template_file_uri)
    source_reference = '%s.cfg' % self.computer_guid
    software_release_file.edit(file=content, source_reference=source_reference,
        version='1')

  def stepLoadEmptySoftwareReleaseFile(self, sequence=None):
    software_release_file = sequence.get('software_release_file')
    content = StringIO(str("""[buildout]
parts = empty_parts

[empty_parts]
recipe = collective.recipe.template
input = inline:
  #!/bin/sh
  sleep 5
output = /dev/null"""))
    source_reference = '%s.cfg' % self.computer_guid
    software_release_file.edit(source_reference= source_reference,
        file=content, version='1')
    content.close()

  def stepLoadTrappedSoftwareReleaseFile(self, sequence=None):
    software_release_file = sequence.get('software_release_file')
    content = StringIO(str(""))
    source_reference = '%s.cfg' % self.computer_guid
    software_release_file.edit(source_reference= source_reference,
        file=content)
    content.close()

  def stepSetReferenceOnSoftwareReleaseFile(self, sequence=None):
    software_release_file = sequence.get('software_release_file')
    software_release_file.edit(reference=self.computer_guid + \
        "_software_release_file")

  def stepPublishSoftwareTemplateFile(self, sequence=None):
    software_template_file = sequence.get('software_template_file')
    software_template_file.publish()

  def stepPublishSoftwareReleaseFile(self, sequence=None):
    software_release_file = sequence.get('software_release_file')
    software_release_file.publish()

  def stepCreateSoftwareAvailabilityService(self, sequence=None):
    software_availability_service = self.portal.restrictedTraverse(
        self.portal.portal_preferences.getPreferredSoftwareSetupResource())
    sequence.edit(software_availability_service=software_availability_service)

  def stepCreateInstanceSetupService(self, sequence=None):
    instance_setup_service = self.portal.restrictedTraverse(
        self.portal.portal_preferences.getPreferredInstanceSetupResource())
    sequence.edit(instance_setup_service=instance_setup_service)

  def stepCreateInstanceHostingService(self, sequence=None):
    instance_hosting_service = self.portal.restrictedTraverse(
        self.portal.portal_preferences.getPreferredInstanceHostingResource())
    sequence.edit(instance_hosting_service=instance_hosting_service)

  def stepCreateInstanceDestroyService(self, sequence=None):
    instance_destroy_service = self.portal.restrictedTraverse(
        self.portal.portal_preferences.getPreferredInstanceCleanupResource())
    sequence.edit(instance_destroy_service=instance_destroy_service)

  def stepCreateSoftwareRelease(self, sequence=None):
    module = self.portal.getDefaultModule(
        portal_type=self.software_release_module_portal_type)
    software_release = module.newContent(
        portal_type=self.software_release_portal_type,
        title='testVifibSlapgrid Software Release')
    self.cleanup_list.append(software_release)
    sequence.edit(software_release=software_release)

  def stepSetSoftwareReleaseUri(self, sequence=None):
    software_release = sequence.get('software_release')
    software_release_file = sequence.get('software_release_file')
    host_pattern = re.compile('^(?:f|ht)tp(?:s)?\://([^/]+)')
    hostname = host_pattern.findall(software_release_file.getAbsoluteUrl())[0]
    software_release_uri = 'https://%s/erp5/web_site_module/erpypi/%s-1.cfg' % (
        hostname, software_release_file.getReference())
    software_release.edit(url_string=software_release_uri)

  def stepSetAggregateToSoftwareRelease(self, sequence=None):
    software_product = self.portal.portal_catalog(
      id='test_software_product',
      portal_type=self.software_product_portal_type)[0].getObject()
    sequence.edit(software_product=software_product)
    self.appendAggregateToDocument(sequence, 'software_release',
        'software_product')
        
  def stepPublishSoftwareRelease(self, sequence=None):
    software_release = sequence.get('software_release')
    software_release.publish()

  def stepCreateComputer(self, sequence=None):
    module = self.portal.getDefaultModule(
        portal_type=self.computer_module_portal_type)
    computer = module.newContent(portal_type=self.computer_portal_type,
        title='testVifibSlapgrid')
    self.cleanup_list.append(computer)
    sequence.edit(computer=computer)

  def stepSetReferenceOnComputer(self, sequence=None):
    computer = sequence.get('computer')
    computer.edit(reference=self.computer_guid)

  def stepCreateComputerPartition(self, sequence=None):
    computer = sequence.get('computer')
    computer_partition = computer.newContent(
        portal_type=self.computer_partition_portal_type)
    self.cleanup_list.append(computer_partition)
    sequence.edit(computer_partition=computer_partition)

  def stepValidateComputerPartition(self, sequence=None):
    computer_partition = sequence.get('computer_partition')
    computer_partition.validate()
    # Mark newly created computer partition as free by default
    computer_partition.markFree()

  def stepSetReferenceOnComputerPartition(self, sequence=None):
    computer_partition = sequence.get('computer_partition')
    computer_partition.edit(reference=self.partition_id)

  def stepCreateInternetProtocolAddress(self, sequence=None):
    computer = sequence.get('computer_partition')
    internet_protocol_address = computer.newContent(
        portal_type=self.internet_protocol_address_portal_type,
        ip_address='127.0.0.1',
        network_interface='eth0')
    self.cleanup_list.append(internet_protocol_address)
    sequence.edit(internet_protocol_address=internet_protocol_address)

  def stepSetIpAndTcpPortAndUdpPortOnInternetProtocolAddress(self,
      sequence=None):
    internet_protocol_address = sequence.get('internet_protocol_address')
    internet_protocol_address.edit(ip_address=self.ip_address,
        tcp_port_number=self.tcp_port,
        udp_port_number=self.udp_port,
        id='default_network_address')

  def stepValidateComputer(self, sequence=None):
    computer = sequence.get('computer')
    computer.validate()
    self.assertEqual('validated', computer.getValidationState())

  def stepTerminateSoftwareInstance(self, sequence=None):
    software_instance = sequence.get('software_instance')
    software_instance.terminate()
    self.assertEqual('terminate_requested',
        software_instance.getRequestState())

  def stepCreateSoftwareInstance(self, sequence=None):
    module = self.portal.getDefaultModule(
        portal_type=self.software_instance_module_portal_type)
    software_instance = module.newContent(
      portal_type=self.software_instance_portal_type,
      title='testVifibSlapgrid')
    self.cleanup_list.append(software_instance)
    sequence.edit(software_instance=software_instance)
    
  def stepSetReferenceOnSoftwareInstance(self, sequence=None):
    software_instance = sequence.get('software_instance')
    software_instance.edit(reference='%s_softwareinstance' % self.computer_guid)

  def stepCreateHostingSubscription(self, sequence=None):
    module = self.portal.getDefaultModule(
        portal_type=self.hosting_subscription_module_portal_type)
    hosting_subscription = module.newContent(
      portal_type=self.hosting_subscription_portal_type,
      title='testVifibSlapgrid')
    self.cleanup_list.append(hosting_subscription)
    sequence.edit(hosting_subscription=hosting_subscription)

  def stepSetSoftwareInstanceMemcachedXml(self, sequence=None):
    software_instance = sequence.get('software_instance')
    software_instance.edit(text_content=self.software_instance_xml)

  def stepCreateSetupSalePackingList(self, sequence=None):
    module = self.portal.getDefaultModule(
        portal_type=self.sale_packing_list_module_portal_type)
    sale_packing_list = module.newContent(
      portal_type=self.sale_packing_list_portal_type)
    sale_packing_list.edit(title='testVifibSlapgrid Setup SPL')
    self.cleanup_list.append(sale_packing_list)
    sequence.edit(setup_sale_packing_list=sale_packing_list)

  def stepCreateSetupSalePackingListLine(self, sequence=None):
    sale_packing_list = sequence.get('setup_sale_packing_list')
    sale_packing_list_line = sale_packing_list.newContent(
      portal_type=self.sale_packing_list_line_portal_type)
    self.cleanup_list.append(sale_packing_list_line)
    sequence.edit(setup_sale_packing_list_line=sale_packing_list_line)

  def stepSetSetupSalePackingListLineInstanceSetupResource(self, sequence=None):
    sale_packing_list_line = sequence.get('setup_sale_packing_list_line')
    instance_setup_service = sequence.get('instance_setup_service')
    sale_packing_list_line.edit(resource_value=instance_setup_service)
    self.assertNotEqual(None, instance_setup_service)

  def stepAppendSetupSalePackingListLineComputerPartitionAggregate(self,
      sequence=None):
    self.appendAggregateToDocument(sequence, 'setup_sale_packing_list_line',
        'computer_partition')

  def stepAppendSetupSalePackingListLineSoftwareInstanceAggregate(self,
      sequence=None):
    self.appendAggregateToDocument(sequence, 'setup_sale_packing_list_line',
        'software_instance')

  def stepAppendSetupSalePackingListLineSoftwareReleaseAggregate(self,
      sequence=None):
    self.appendAggregateToDocument(sequence, 'setup_sale_packing_list_line',
        'software_release')

  def stepAppendSetupSalePackingListLineHostingSubscriptionAggregate(self,
      sequence=None):
    self.appendAggregateToDocument(sequence, 'setup_sale_packing_list_line',
        'hosting_subscription')

  def stepConfirmSetupSalePackingList(self, sequence=None):
    sale_packing_list = sequence.get('setup_sale_packing_list')
    sale_packing_list.portal_workflow.doActionFor(sale_packing_list,
        'confirm_action')
    self.assertEqual('confirmed', sale_packing_list.getSimulationState())

  def stepStopSetupSalePackingList(self, sequence=None):
    sale_packing_list = sequence.get('setup_setup_sale_packing_list')
    sale_packing_list.stop()
    self.assertEqual('stopped',
        sale_packing_list.getSimulationState())

  def stepSetStartDateOnSetupSalePackingList(self, sequence=None):
    sale_packing_list = sequence.get('setup_sale_packing_list')
    sale_packing_list.edit(start_date=DateTime())

  def stepCreateHostingSalePackingList(self, sequence=None):
    module = self.portal.getDefaultModule(
        portal_type=self.sale_packing_list_module_portal_type)
    sale_packing_list = module.newContent(
      portal_type=self.sale_packing_list_portal_type,
      title='testVifibSlapgrid Hosting SPL')
    self.cleanup_list.append(sale_packing_list)
    sequence.edit(hosting_sale_packing_list=sale_packing_list)

  def stepCreateHostingSalePackingListLine(self, sequence=None):
    sale_packing_list = sequence.get('hosting_sale_packing_list')
    sale_packing_list_line = sale_packing_list.newContent(
      portal_type=self.sale_packing_list_line_portal_type)
    self.cleanup_list.append(sale_packing_list_line)
    sequence.edit(hosting_sale_packing_list_line=sale_packing_list_line)

  def stepSetHostingSalePackingListLineInstanceHostingResource(self,
      sequence=None):
    sale_packing_list_line = sequence.get('hosting_sale_packing_list_line')
    instance_hosting_service = sequence.get('instance_hosting_service')
    sale_packing_list_line.edit(resource_value=instance_hosting_service)
    self.assertNotEqual(None, instance_hosting_service)

  def stepAppendHostingSalePackingListLineComputerPartitionAggregate(self,
      sequence=None):
    self.appendAggregateToDocument(sequence, 'hosting_sale_packing_list_line',
        'computer_partition')

  def stepAppendHostingSalePackingListLineSoftwareInstanceAggregate(self,
      sequence=None):
    self.appendAggregateToDocument(sequence, 'hosting_sale_packing_list_line',
        'software_instance')

  def stepAppendHostingSalePackingListLineSoftwareReleaseAggregate(self,
      sequence=None):
    self.appendAggregateToDocument(sequence, 'hosting_sale_packing_list_line',
        'software_release')

  def stepAppendHostingSalePackingListLineHostingSubscriptionAggregate(self,
      sequence=None):
    self.appendAggregateToDocument(sequence, 'hosting_sale_packing_list_line',
        'hosting_subscription')

  def stepConfirmHostingSalePackingList(self, sequence=None):
    sale_packing_list = sequence.get('hosting_sale_packing_list')
    sale_packing_list.confirm()
    self.assertEqual('confirmed', sale_packing_list.getSimulationState())

  def stepStopHostingSalePackingList(self, sequence=None):
    sale_packing_list = sequence.get('hosting_sale_packing_list')
    sale_packing_list.stop()
    self.assertEqual('stopped',
        sale_packing_list.getSimulationState())

  def stepSetStartDateOnHostingSalePackingList(self, sequence=None):
    sale_packing_list = sequence.get('hosting_sale_packing_list')
    sale_packing_list.edit(start_date=DateTime())

  def stepCreateDestroySalePackingList(self, sequence=None):
    module = self.portal.getDefaultModule(
        portal_type=self.sale_packing_list_module_portal_type)
    sale_packing_list = module.newContent(
      portal_type=self.sale_packing_list_portal_type,
      title='testVifibSlapgrid Destroy SPL')
    self.cleanup_list.append(sale_packing_list)
    sequence.edit(destroy_sale_packing_list=sale_packing_list)

  def stepCreateDestroySalePackingListLine(self, sequence=None):
    sale_packing_list = sequence.get('destroy_sale_packing_list')
    sale_packing_list_line = sale_packing_list.newContent(
      portal_type=self.sale_packing_list_line_portal_type)
    self.cleanup_list.append(sale_packing_list_line)
    sequence.edit(destroy_sale_packing_list_line=sale_packing_list_line)

  def stepSetDestroySalePackingListLineInstanceDestroyResource(self,
      sequence=None):
    sale_packing_list_line = sequence.get('destroy_sale_packing_list_line')
    instance_destroy_service = sequence.get('instance_destroy_service')
    sale_packing_list_line.edit(resource_value=instance_destroy_service)
    self.assertNotEqual(None, instance_destroy_service)

  def stepAppendDestroySalePackingListLineComputerPartitionAggregate(self,
      sequence=None):
    self.appendAggregateToDocument(sequence, 'destroy_sale_packing_list_line',
        'computer_partition')

  def stepAppendDestroySalePackingListLineSoftwareInstanceAggregate(self,
      sequence=None):
    self.appendAggregateToDocument(sequence, 'destroy_sale_packing_list_line',
        'software_instance')

  def stepAppendDestroySalePackingListLineSoftwareReleaseAggregate(self,
      sequence=None):
    self.appendAggregateToDocument(sequence, 'destroy_sale_packing_list_line',
        'software_release')

  def stepAppendDestroySalePackingListLineHostingSubscriptionAggregate(self,
      sequence=None):
    self.appendAggregateToDocument(sequence, 'destroy_sale_packing_list_line',
        'hosting_subscription')

  def stepConfirmDestroySalePackingList(self, sequence=None):
    sale_packing_list = sequence.get('destroy_sale_packing_list')
    sale_packing_list.confirm()
    self.assertEqual('confirmed', sale_packing_list.getSimulationState())

  def stepSetStartDateOnDestroySalePackingList(self, sequence=None):
    sale_packing_list = sequence.get('destroy_sale_packing_list')
    sale_packing_list.edit(start_date=DateTime())

  def stepCreatePurchasePackingList(self, sequence=None, 
                         sequence_list=None, **kw):
    """
    Create an purchase packing list document.
    """
    module = self.portal.getDefaultModule(
        portal_type=self.purchase_packing_list_portal_type)
    order = module.newContent(
        portal_type=self.purchase_packing_list_portal_type,
        title='testVifibSlapgrid')
    self.cleanup_list.append(order)
    sequence.edit(purchase_packing_list=order)

  def stepCreatePurchasePackingListLine(self, sequence=None, 
                         sequence_list=None, **kw):
    """
    Create an purchase packing list line document.
    """
    order = sequence.get("purchase_packing_list")
    line = order.newContent(
        portal_type=self.purchase_packing_list_line_portal_type)
    self.cleanup_list.append(line)
    sequence.edit(purchase_packing_list_line=line)

  def stepSetPurchasePackingListLineSoftwareResource(self, sequence=None):
    purchase_list_line = sequence.get('purchase_packing_list_line')
    service = sequence.get('software_availability_service')
    purchase_list_line.edit(resource_value=service)
    self.assertNotEqual(None, service)

  def stepSetPurchasePackingListLineAggregate(self, sequence=None, 
                         sequence_list=None, **kw):
    """
    Associate a computer and a software release to the purchase packing list
    line.
    """
    line = sequence.get("purchase_packing_list_line")
    line.edit(
        aggregate_uid_list=[sequence.get('computer').getUid(),
                            sequence.get('software_release').getUid()]
        )

  def stepConfirmPurchasePackingList(self, sequence=None, 
                         sequence_list=None, **kw):
    """
    Confirm the purchase packing list
    """
    order = sequence.get("purchase_packing_list")
    order.portal_workflow.doActionFor(order, 'confirm_action')

  #
  # Assertions
  #
  def stepAssertSoftwareInstanceExternalStateIsStarted(self, sequence=None):
    software_instance = sequence.get('software_instance')
    self.assertEqual('started', software_instance.getExternalState())

  def getPermissionString(self, path):
    return oct(stat.S_IMODE(os.stat(path).st_mode))

  def stepAssertClientGeneratedFileListPermissions(self, sequence=None):
    incorrect_permission_list = []
    # XXX-Luke: Is check software_root_directory really needed?

    # check instance_root_directory
    for directory in os.listdir(self.instance_root_directory):
      if os.path.samefile(os.path.join(self.instance_root_directory,
        directory), self.computer_partition_directory):
        continue
      for walk_tuple in os.walk(os.path.join(self.instance_root_directory,
        directory)):
        path = walk_tuple[0]
        permission = self.getPermissionString(path)
        if permission not in ('0600', '0700'):
          incorrect_permission_list.append('%s:%s'%(path, permission))

    self.assertEqual([], incorrect_permission_list,
        'Insecure file permissions:\n%s' % '\n'.join(
          incorrect_permission_list))

  def _assertPathExistence(self, parent, path_list):
    non_existing_path_list = []
    for path in path_list:
      path = os.path.join(parent, path)
      if not os.path.exists(path):
        non_existing_path_list.append(path)
    self.assertEqual([], non_existing_path_list,
        'Missing paths:\n%s\n' % '\n'.join(non_existing_path_list))

  def stepAssertClientSoftwareReleaseInstalled(self, sequence=None):
    software_root_directory_list = os.listdir(self.software_root_directory)
    self.assertEqual(1, len(software_root_directory_list))

    software_release_directory = [d for d in software_root_directory_list
        if not d.endswith('bin')][0]
    software_release_directory = os.path.join(self.software_root_directory,
        software_release_directory)
    self._assertPathExistence(software_release_directory,
        ['bin/dummy-software', 'bin/slapmonitor', 'template.cfg'])

  def stepAssertClientComputerPartitionInstalled(self, sequence=None):
    self._assertPathExistence(self.computer_partition_directory,
        ['buildout.cfg', 'bin/run'])

  def stepAssertUsageReport(self, sequence=None):
    computer_partition = sequence.get('computer_partition')
    usage_report_list = computer_partition.getCausalityRelatedValueList(
        portal_type=self.usage_report_portal_type)
    self.assertEqual(1, len(usage_report_list))
    usage_report = usage_report_list[0]
    delivery_line_list = usage_report.getAggregateRelatedValueList(
        portal_type=self.sale_packing_list_line_portal_type)
    self.assertEqual(1, len(delivery_line_list))
    delivery_line = delivery_line_list[0]
    self.assertEqual('started', delivery_line.getSimulationState())
    # XXX-Luke: To assert resource it have to be unhardcoded

  def stepAssertClientComputerPartitionIsNotRunning(self, sequence=None):
    computer_partition = sequence.get('computer_partition')
    server_proxy = xmlrpclib.ServerProxy('http://127.0.0.1',
        SupervisorTransport('', '', 'unix://%s' % self.supervisor_socket))
    supervisor_state = server_proxy.supervisor.getProcessInfo(
        computer_partition.getReference())
    self.assertEqual('STOPPED', supervisor_state['statename'])

  def stepAssertClientComputerPartitionIsRunning(self, sequence=None):
    computer_partition = sequence.get('computer_partition')
    server_proxy = xmlrpclib.ServerProxy('http://127.0.0.1',
        SupervisorTransport('', '', 'unix://%s' % self.supervisor_socket))
    supervisor_state = server_proxy.supervisor.getProcessInfo(
        computer_partition.getReference())
    self.assertEqual('RUNNING', supervisor_state['statename'])

  def stepAssertComputerPartitionIsAssigned(self, sequence=None):
    """Checks if current computer partition is not empty"""
    self.assertNotEqual([], glob.glob(self.computer_partition_directory))

  def stepAssertComputerPartitionIsNotAssigned(self, sequence=None):
    """Checks if current computer partition is empty"""
    self.assertEqual([], glob.glob(self.computer_partition_directory))

  def stepAssertComputerPartitionIsCleaned(self, sequence=None):
    """Checks if current computer partition is empty"""
    self.assertEqual([], glob.glob(os.path.join(
        self.computer_partition_directory, '*')))

  def stepAssertSoftwareReleaseErrorReported(self, sequence=None):
    #We test here that software Release Error exist in ERP5
    computer = sequence.get('computer')
    #Now we are testing if External Workflows is in error state
    #self.assertEqual("error", computer.getSlapState())
    last_history_action = computer.portal_workflow.getInfoFor(ob=computer,
        name='history', wf_id='computer_slap_interface_workflow')[-1]['action']
    self.assertEqual(last_history_action, 
        'report_software_release_installation_error')

  def stepAssertSoftwareInstanceErrorReported(self, sequence=None):
    software_instance = sequence.get('software_instance')
    #self.assertEqual("error", software_instance.getSlapState())
    last_history_action = software_instance.portal_workflow.getInfoFor(
        ob=software_instance, name='history',
        wf_id='software_instance_slap_interface_workflow')[-1]['action']
    self.assertEqual(last_history_action, 'report_computer_partition_error')

  def stepCrash(self, sequence):
    """Debugging purpose, stop test"""
    raise OSError()

  #
  # Tests
  #
  def testSlapgridHandlesInstanceState(self):
    """Testing if slapgrid correctly handles partition states.
    Use case : 
    - create a Software release profile which informs the test runner when
      start/stop argument is passed to the wrapper.
    - create all needed objects in ERP5 (as done in "test")
    - change the instance state in ERP5 to start
    - check that the wrapper returns the expected value
    - change the instance state in ERP5 to stop
    - check that the wrapper returns the expected value
    - change the instance state in ERP5 to start
    - check that the wrapper returns the expected value
    - change the instance state in ERP5 to stop
    - check that the wrapper returns the expected value
    - change the instance state in ERP5 to terminated
    - check that slapgrid cleans the computer partition 
    - configure a new software instance
    - check that the computer partition is assigned to this new instance
    - configure a third new software instance
    - check that the computer partition is not assigned to this new instance
    """
    self.defineIds()
    self.software_instance_xml = """<?xml version="1.0" encoding="utf-8"?>
<instance>
<parameter id="memcached_tcp_port">9998</parameter>
<parameter id="memcached_udp_port">9998</parameter>
<parameter id="memcached_host">127.0.0.1</parameter>
<parameter id="memcached_memory_size">2</parameter>
</instance>"""
    sequence_string = """
      Tic
      CreateSoftwareAvailabilityService
      CreateInstanceSetupService
      CreateInstanceHostingService
      CreateInstanceDestroyService
      CreateSoftwareTemplateFile
      LoadSoftwareTemplateFile
      SetReferenceOnSoftwareTemplateFile
      PublishSoftwareTemplateFile
      CreateSoftwareReleaseFile
      LoadSoftwareReleaseFile
      PublishSoftwareReleaseFile
      CreateSoftwareRelease
      SetReferenceOnSoftwareReleaseFile
      SetSoftwareReleaseUri
      SetAggregateToSoftwareRelease
      PublishSoftwareRelease
      CreateComputer
      SetReferenceOnComputer
      ValidateComputer
      Tic
      CreateComputerPartition
      SetReferenceOnComputerPartition
      CreateInternetProtocolAddress
      Tic
      SetIpAndTcpPortAndUdpPortOnInternetProtocolAddress
      ValidateComputerPartition
      CreateHostingSubscription
      CreateSoftwareInstance
      SetReferenceOnSoftwareInstance
      SetSoftwareInstanceMemcachedXml
      CreateSetupSalePackingList
      CreateSetupSalePackingListLine
      SetSetupSalePackingListLineInstanceSetupResource
      AppendSetupSalePackingListLineComputerPartitionAggregate
      AppendSetupSalePackingListLineSoftwareInstanceAggregate
      AppendSetupSalePackingListLineSoftwareReleaseAggregate
      AppendSetupSalePackingListLineHostingSubscriptionAggregate
      ConfirmSetupSalePackingList
      SetStartDateOnSetupSalePackingList
      CreatePurchasePackingList
      CreatePurchasePackingListLine
      SetPurchasePackingListLineSoftwareResource
      SetPurchasePackingListLineAggregate
      ConfirmPurchasePackingList
      Tic
      CreateHostingSalePackingList
      CreateHostingSalePackingListLine
      SetHostingSalePackingListLineInstanceHostingResource
      AppendHostingSalePackingListLineComputerPartitionAggregate
      AppendHostingSalePackingListLineSoftwareInstanceAggregate
      AppendHostingSalePackingListLineSoftwareReleaseAggregate
      AppendHostingSalePackingListLineHostingSubscriptionAggregate
      ConfirmHostingSalePackingList
      SetStartDateOnHostingSalePackingList
      Tic
      PrepareTestingEnvironment
      RunSlapgrid
      AssertClientComputerPartitionIsRunning
      Tic
      RunSlapgrid
      AssertClientComputerPartitionIsRunning
      StopHostingSalePackingList
      Tic
      RunSlapgrid
      AssertClientComputerPartitionIsNotRunning
      CreateHostingSalePackingList
      CreateHostingSalePackingListLine
      SetHostingSalePackingListLineInstanceHostingResource
      AppendHostingSalePackingListLineComputerPartitionAggregate
      AppendHostingSalePackingListLineSoftwareInstanceAggregate
      AppendHostingSalePackingListLineSoftwareReleaseAggregate
      AppendHostingSalePackingListLineHostingSubscriptionAggregate
      ConfirmHostingSalePackingList
      SetStartDateOnHostingSalePackingList
      Tic
      RunSlapgrid
      AssertClientComputerPartitionIsRunning
      StopHostingSalePackingList
      Tic
      RunSlapgrid
      AssertClientComputerPartitionIsNotRunning
      CreateDestroySalePackingList
      CreateDestroySalePackingListLine
      SetDestroySalePackingListLineInstanceDestroyResource
      AppendDestroySalePackingListLineComputerPartitionAggregate
      AppendDestroySalePackingListLineSoftwareInstanceAggregate
      AppendDestroySalePackingListLineSoftwareReleaseAggregate
      AppendDestroySalePackingListLineHostingSubscriptionAggregate
      ConfirmDestroySalePackingList
      SetStartDateOnDestroySalePackingList
      Tic
      RunSlapgrid
      AssertComputerPartitionIsCleaned
      Tic
    """
    self.createTestSequenceAndPlay(sequence_string)

  def testManualDefaultSetup(self):
    """Manual default setup of slapgrid"""
    self.defineIds()
    self.software_instance_xml = """<instance>
  <parameter id="memcached_tcp_port">98076</parameter>
  <parameter id="memcached_udp_port">98076</parameter>
  <parameter id="memcached_host">127.0.0.1</parameter>
  <parameter id="memcached_memory_size">2</parameter>
</instance>"""
    sequence_string = """
      Tic
      CreateSoftwareAvailabilityService
      CreateInstanceSetupService
      CreateInstanceHostingService
      CreateInstanceDestroyService
      CreateSoftwareTemplateFile
      LoadSoftwareTemplateFile
      SetReferenceOnSoftwareTemplateFile
      PublishSoftwareTemplateFile
      CreateSoftwareReleaseFile
      SetReferenceOnSoftwareReleaseFile
      LoadSoftwareReleaseFile
      PublishSoftwareReleaseFile
      CreateSoftwareRelease
      SetSoftwareReleaseUri
      SetAggregateToSoftwareRelease
      PublishSoftwareRelease
      CreateComputer
      SetReferenceOnComputer
      ValidateComputer
      Tic
      CreateComputerPartition
      SetReferenceOnComputerPartition
      CreateInternetProtocolAddress
      Tic
      SetIpAndTcpPortAndUdpPortOnInternetProtocolAddress
      ValidateComputerPartition
      CreateHostingSubscription
      CreateSoftwareInstance
      SetReferenceOnSoftwareInstance
      SetSoftwareInstanceMemcachedXml
      CreateSetupSalePackingList
      CreateSetupSalePackingListLine
      SetSetupSalePackingListLineInstanceSetupResource
      AppendSetupSalePackingListLineComputerPartitionAggregate
      AppendSetupSalePackingListLineSoftwareInstanceAggregate
      AppendSetupSalePackingListLineSoftwareReleaseAggregate
      AppendSetupSalePackingListLineHostingSubscriptionAggregate
      Tic
      ConfirmSetupSalePackingList
      SetStartDateOnSetupSalePackingList
      CreatePurchasePackingList
      CreatePurchasePackingListLine
      SetPurchasePackingListLineSoftwareResource
      SetPurchasePackingListLineAggregate
      ConfirmPurchasePackingList
      Tic
      PrepareTestingEnvironment
      RunSlapgrid
      AssertClientSoftwareReleaseInstalled
      AssertClientComputerPartitionInstalled
      AssertClientGeneratedFileListPermissions
      AssertClientComputerPartitionIsNotRunning
      CreateHostingSalePackingList
      CreateHostingSalePackingListLine
      SetHostingSalePackingListLineInstanceHostingResource
      AppendHostingSalePackingListLineComputerPartitionAggregate
      AppendHostingSalePackingListLineSoftwareInstanceAggregate
      AppendHostingSalePackingListLineSoftwareReleaseAggregate
      AppendHostingSalePackingListLineHostingSubscriptionAggregate
      ConfirmHostingSalePackingList
      SetStartDateOnHostingSalePackingList
      Tic
      RunSlapgrid
      AssertClientComputerPartitionIsRunning
      AssertUsageReport
      AssertSoftwareInstanceExternalStateIsStarted
    """
    self.createTestSequenceAndPlay(sequence_string)

  def testSlapgridTrappedSoftwareRelease(self):
    """Create a Software Release buildout profile which fails when running.
       - create all needed objects in ERP5 (as done in the Luke's test),
       - when running slapgrid, check that the error was correctly
         reported in ERP5 (in the Supply).
    """
    self.defineIds()
    self.software_instance_xml = "<instance></instance>"
    sequence_string = """
      Tic
      CreateSoftwareAvailabilityService
      CreateInstanceSetupService
      CreateInstanceHostingService
      CreateInstanceDestroyService
      CreateSoftwareTemplateFile
      LoadSoftwareTemplateFile
      SetReferenceOnSoftwareTemplateFile
      PublishSoftwareTemplateFile
      CreateSoftwareReleaseFile
      SetReferenceOnSoftwareReleaseFile
      LoadTrappedSoftwareReleaseFile
      PublishSoftwareReleaseFile
      CreateSoftwareRelease
      SetSoftwareReleaseUri
      SetAggregateToSoftwareRelease
      PublishSoftwareRelease
      CreateComputer
      SetReferenceOnComputer
      ValidateComputer
      Tic
      CreateComputerPartition
      SetReferenceOnComputerPartition
      CreateInternetProtocolAddress
      Tic
      SetIpAndTcpPortAndUdpPortOnInternetProtocolAddress
      ValidateComputerPartition
      CreateHostingSubscription
      CreateSoftwareInstance
      SetReferenceOnSoftwareInstance
      SetSoftwareInstanceMemcachedXml
      CreateSetupSalePackingList
      CreateSetupSalePackingListLine
      SetSetupSalePackingListLineInstanceSetupResource
      AppendSetupSalePackingListLineComputerPartitionAggregate
      AppendSetupSalePackingListLineSoftwareInstanceAggregate
      AppendSetupSalePackingListLineSoftwareReleaseAggregate
      AppendSetupSalePackingListLineHostingSubscriptionAggregate
      ConfirmSetupSalePackingList
      SetStartDateOnSetupSalePackingList
      CreatePurchasePackingList
      CreatePurchasePackingListLine
      SetPurchasePackingListLineSoftwareResource
      SetPurchasePackingListLineAggregate
      ConfirmPurchasePackingList
      Tic
      CreateHostingSalePackingList
      CreateHostingSalePackingListLine
      SetHostingSalePackingListLineInstanceHostingResource
      AppendHostingSalePackingListLineComputerPartitionAggregate
      AppendHostingSalePackingListLineSoftwareInstanceAggregate
      AppendHostingSalePackingListLineSoftwareReleaseAggregate
      AppendHostingSalePackingListLineHostingSubscriptionAggregate
      ConfirmHostingSalePackingList
      SetStartDateOnHostingSalePackingList
      Tic
      PrepareTestingEnvironment
      RunSlapgridWithoutAssert
      Tic
      AssertSoftwareReleaseErrorReported
    """
    self.createTestSequenceAndPlay(sequence_string)

  def testSlapgridEmptySoftwareRelease(self):
    """Create a Software Release buildout profile which does nothing during
       installation. It's instanciation template should fails when running.
       - create all needed objects in ERP5 (as done in the Luke's test)
       - when running slapgrid, check that the error was correctly reported
         in ERP5 (in the Software Instance)
    """
    self.defineIds()
    self.software_instance_xml = "<instance></instance>"
    sequence_string = """
      Tic
      CreateSoftwareAvailabilityService
      CreateInstanceSetupService
      CreateInstanceHostingService
      CreateInstanceDestroyService
      CreateSoftwareTemplateFile
      LoadSoftwareTemplateFile
      SetReferenceOnSoftwareTemplateFile
      PublishSoftwareTemplateFile
      CreateSoftwareReleaseFile
      SetReferenceOnSoftwareReleaseFile
      LoadEmptySoftwareReleaseFile
      PublishSoftwareReleaseFile
      CreateSoftwareRelease
      SetSoftwareReleaseUri
      SetAggregateToSoftwareRelease
      PublishSoftwareRelease
      CreateComputer
      SetReferenceOnComputer
      ValidateComputer
      Tic
      CreateComputerPartition
      SetReferenceOnComputerPartition
      CreateInternetProtocolAddress
      Tic
      SetIpAndTcpPortAndUdpPortOnInternetProtocolAddress
      ValidateComputerPartition
      CreateHostingSubscription
      CreateSoftwareInstance
      SetReferenceOnSoftwareInstance
      SetSoftwareInstanceMemcachedXml
      CreateSetupSalePackingList
      CreateSetupSalePackingListLine
      SetSetupSalePackingListLineInstanceSetupResource
      AppendSetupSalePackingListLineComputerPartitionAggregate
      AppendSetupSalePackingListLineSoftwareInstanceAggregate
      AppendSetupSalePackingListLineSoftwareReleaseAggregate
      AppendSetupSalePackingListLineHostingSubscriptionAggregate
      ConfirmSetupSalePackingList
      SetStartDateOnSetupSalePackingList
      CreatePurchasePackingList
      CreatePurchasePackingListLine
      SetPurchasePackingListLineSoftwareResource
      SetPurchasePackingListLineAggregate
      ConfirmPurchasePackingList
      Tic
      CreateHostingSalePackingList
      CreateHostingSalePackingListLine
      SetHostingSalePackingListLineInstanceHostingResource
      AppendHostingSalePackingListLineComputerPartitionAggregate
      AppendHostingSalePackingListLineSoftwareInstanceAggregate
      AppendHostingSalePackingListLineSoftwareReleaseAggregate
      AppendHostingSalePackingListLineHostingSubscriptionAggregate
      ConfirmHostingSalePackingList
      SetStartDateOnHostingSalePackingList
      Tic
      PrepareTestingEnvironment
      RunSlapgridWithoutAssert
      Tic
      AssertSoftwareInstanceErrorReported
    """
    self.createTestSequenceAndPlay(sequence_string)
