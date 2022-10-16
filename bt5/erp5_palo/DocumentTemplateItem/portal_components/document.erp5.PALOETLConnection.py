##############################################################################
#
# Copyright (c) 2015 Nexedi SA and Contributors. All Rights Reserved.
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

import suds
import six.moves.urllib.request
import ssl
import lxml.etree

from AccessControl import ClassSecurityInfo

from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type import Permissions

from suds.transport.https import HttpAuthenticated

class HTTPAuthenticatedUnverifiedSSL(HttpAuthenticated):
  def u2handlers(self):
    handlers = [ six.moves.urllib.request.HTTPSHandler(context=ssl._create_unverified_context()) ]
    handlers.extend(HttpAuthenticated.u2handlers(self))
    return handlers

class PALOETLConnection(XMLObject):
  """Connects to PALO ETL Server.

  A typical session to load the OLAP database should be:

  Upload your project file. This can be done only once.
  >>> palo.uploadProject(project_id, xml)

  Execute an ETL job and print status at the end:

  >>> execution_id = palo.addExecution(project_id, job_id)
  >>> palo.runExecution(execution_id)
  >>> while True:
  ...   status = palo.getExecutionStatus(execution_id)
  ...   if status != 'Running':
  ...     break
  ...   time.sleep(1) # You better spawn another activity here.
  >>> print palo.getExecutionLog(execution_id)

  """
  meta_type = 'ERP5 PALO ETL Connection'
  portal_type = 'PALO ETL Connection'

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _getSudsClient(self):
    # maybe client can be cached as a _v_ attribute. For now, we do not care about performance.
    if "ignore ssl certificate check":
      client = suds.client.Client(self.getUrlString(), transport=HTTPAuthenticatedUnverifiedSSL())
    else:
      client = suds.client.Client(self.getUrlString())
    if "fix service location":
      # XXX The axis2 generated webservice only supports http on port 8080.
      # It seems to be using an old and buggy version of axis2.
      # Easiest workaround is to force the port (in WSDL terminology) location.
      # for a WSDL url like "https://[ip]:port/etlserver/services/ETL-Server?wsdl" it will be https://[ip]:port/etlserver/services/ETL-Server.ETL-ServerHttpSoap11Endpoint/
      assert self.getUrlString().endswith('?wsdl')
      port_url = '%s.ETL-ServerHttpSoap11Endpoint/' % (self.getUrlString()[:-5])
      client.wsdl.services[0].setlocation(port_url)
    return client

  def uploadProject(self, project_xml):
    # Read the name attribute from xml
    root = lxml.etree.fromstring(project_xml.encode('utf8'))
    project_id = root.get('name')
    ret, = self._getSudsClient().service.addComponents(project_id, project_xml)
    if not ret.valid:
      raise RuntimeError(ret.errorMessage)
    return ret

  def addExecution(self, project_id, job_id='default'):
    ret = self._getSudsClient().service.addExecution('%s.jobs.%s' % (project_id, job_id))
    if ret.errors:
      raise RuntimeError(ret.errorMessage)
    return ret.id

  def runExecution(self, execution_id):
    ret = self._getSudsClient().service.runExecution(execution_id)
    if ret.errors:
      raise RuntimeError(ret.errorMessage)
    return ret.id

  def getExecutionStatus(self, execution_id, waitForTermination=False):
    ret = self._getSudsClient().service.getExecutionStatus(id=execution_id, waitForTermination=waitForTermination)
    if ret.errors:
      raise RuntimeError(ret.errorMessage)
    return ret.status

  def getExecutionLog(self, execution_id, log_type='?', timestamp=0):
    ret = self._getSudsClient().service.getExecutionLog(
      execution_id, type=log_type, timestamp=timestamp)
    if not ret.valid:
      raise RuntimeError(ret.errorMessage)
    return ret.result

