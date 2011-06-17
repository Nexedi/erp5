# -*- coding: utf-8 -*-
## Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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

"""
ERP portal_synchronizations tool.
"""

from Products.ERP5Type.Tool.BaseTool import BaseTool
from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.ERP5Type import Permissions
from AccessControl.SecurityManagement import newSecurityManager
from Products.PluggableAuthService.interfaces.plugins import\
     IAuthenticationPlugin
from Products.ERP5Type.Globals import InitializeClass
import urllib
import urllib2
import httplib
import socket
import os
import commands
import random
from DateTime import DateTime
from zLOG import LOG, DEBUG, INFO, WARNING
from urlparse import urlparse

from Products.ERP5SyncML.SyncMLConstant import SYNCML_NAMESPACE, NSMAP,\
     NULL_ANCHOR, ACTIVITY_PRIORITY, MAX_LEN, MAX_OBJECTS,\
     REPLACE_ACTION, ADD_ACTION
from Products.ERP5SyncML.XMLSyncUtils import getConduitByName,\
     getAlertCodeFromXML, checkAlert, getMessageIdFromXml,\
     resolveSyncmlStatusCode, resolveSyncmlAlertCode, getSyncBodyStatusList,\
     xml2wbxml, wbxml2xml, encode, decode, cutXML, checkFinal\
     ,getSubscriptionUrlFromXML, getDataSubNode, getDataText,\
     setRidWithMap

from base64 import b16decode, b16encode

from lxml.builder import ElementMaker
from lxml.etree import Element
from lxml import etree
parser = etree.XMLParser(remove_blank_text=True)
E = ElementMaker(namespace=SYNCML_NAMESPACE, nsmap=NSMAP)


# Logging channel definitions
import logging
# Main logging channel
syncml_logger = logging.getLogger('ERP5SyncML')

# Direct logging to "[instancehome]/log/ERP5SyncML.log", if this directory exists.
# Otherwise, it will end up in root logging facility (ie, event.log).
from App.config import getConfiguration
instancehome = getConfiguration().instancehome
if instancehome is not None:
  log_directory = os.path.join(instancehome, 'log')
  if os.path.isdir(log_directory):
    from Signals import Signals
    from ZConfig.components.logger.loghandler import FileHandler
    log_file_handler = FileHandler(os.path.join(log_directory, 'ERP5SyncML.log'))
    # Default zope log format string borrowed from
    # ZConfig/components/logger/factory.xml, but without the extra "------"
    # line separating entries.
    log_file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s", "%Y-%m-%dT%H:%M:%S"))
    Signals.registerZopeSignals([log_file_handler])
    syncml_logger.addHandler(log_file_handler)
    syncml_logger.propagate = 0


class TimeoutHTTPConnection(httplib.HTTPConnection):
  """
  Custom Classes to set timeOut on handle sockets
  """
  def connect(self):
    httplib.HTTPConnection.connect(self)
    self.sock.settimeout(3600)

class TimeoutHTTPHandler(urllib2.HTTPHandler):
  def http_open(self, req):
    return self.do_open(TimeoutHTTPConnection, req)

def hexdump(raw=''):
  """
  this function is used to display the raw in a readable format :
  it display raw in hexadecimal format and display too the printable 
  characters (because if not printable characters are printed, it makes 
  terminal display crash)
  """
  buf = ""
  line = ""
  start = 0
  done = False
  while not done:
    end = start + 16
    max = len(str(raw))
    if end > max:
      end = max
      done = True
    chunk = raw[start:end]
    for i in xrange(len(chunk)):
      if i > 0:
        spacing = " "
      else:
        spacing = ""
      buf += "%s%02x" % (spacing, ord(chunk[i]))
    if done:
      for i in xrange(16 - (end % 16)):
        buf += "   "
    buf += "  "
    for c in chunk:
      val = ord(c)
      if val >= 33 and val <= 126:
        buf += c
      else:
        buf += "."
    buf += "\n"
    start += 16
  return buf

class SynchronizationTool(BaseTool):
  """
    This tool implements the synchronization algorithm
  """


  id           = 'portal_synchronizations'
  meta_type    = 'ERP5 Synchronizations'
  portal_type  = 'Synchronization Tool'

  security = ClassSecurityInfo()

  # Do we want to use emails ?
  #email = None
  email = 1
  same_export = 1

  security.declareProtected(Permissions.AccessContentsInformation,
      'getConflictList')
  def getConflictList(self, context=None):
    """
    Retrieve the list of all conflicts
    Here the list is as follow :
    [conflict_1,conflict2,...] where conflict_1 is like:
    ['publication',publication_id,object.getPath(),property_id,
    publisher_value,subscriber_value]
    """
    conflict_list = []
    for publication in self.searchFolder(portal_type='SyncML Publication'):
      for result in publication.searchFolder(
                                            portal_type='SyncML Subscription'):
        subscriber = result.getObject()
        sub_conflict_list = subscriber.getConflictList()
        for conflict in sub_conflict_list:
          if context is None or conflict.getOriginValue() == context:
            conflict_list.append(conflict.__of__(subscriber))
    for result in self.searchFolder(portal_type='SyncML Subscription'):
      subscription = result.getObject()
      sub_conflict_list = subscription.getConflictList()
      #LOG('SynchronizationTool.getConflictList, sub_conflict_list', DEBUG,
          #sub_conflict_list)
      for conflict in sub_conflict_list:
        if context is None or conflict.getOriginValue() == context:
          conflict_list.append(conflict.__of__(subscription))
    return conflict_list

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDocumentConflictList')
  def getDocumentConflictList(self, context=None):
    """
    Retrieve the list of all conflicts for a given document
    Well, this is the same thing as getConflictList with a path
    """
    return self.getConflictList(context)


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSynchronizationState')
  def getSynchronizationState(self, context):
    """
    context : the context on which we are looking for state

    This functions have to retrieve the synchronization state,
    it will first look in the conflict list, if nothing is found,
    then we have to check on a publication/subscription.

    This method returns a mapping between subscription and states

    JPS suggestion:
      path -> object, document, context, etc.
      type -> '/titi/toto' or ('','titi', 'toto') or <Base instance 1562567>
      object = self.resolveContext(context) (method to add)

    """
    path = self.resolveContext(context)
    conflict_list = self.getConflictList()
    state_list= []
    #LOG('getSynchronizationState', DEBUG, 'path: %s' % str(path))
    for conflict in conflict_list:
      if conflict.getOrigin() == path:
        #LOG('getSynchronizationState', DEBUG, 'found a conflict: %s' % str(conflict))
        state_list.append([conflict.getSubscriber(), 'conflict'])
    for domain in self.searchFolder():
      destination = domain.getSource()
      #LOG('getSynchronizationState', TRACE, 'destination: %s' % str(destination))
      j_path = '/'.join(path)
      #LOG('getSynchronizationState', TRACE, 'j_path: %s' % str(j_path))
      if destination in j_path:
        o_id = j_path[len(destination)+1:].split('/')[0]
        #LOG('getSynchronizationState', TRACE, 'o_id: %s' % o_id)
        if domain.getPortalType() == 'SyncML Publication':
          subscriber_list = [result.getObject() for result in\
                        domain.searchFolder(portal_type='SyncML Subscription')]
        else:
          subscriber_list = [domain]
        #LOG('getSynchronizationState, subscriber_list:', TRACE, subscriber_list)
        for subscriber in subscriber_list:
          gid = subscriber.getGidFromObject(context)
          signature = subscriber.getSignatureFromGid(gid)
          #XXX check if signature could be not None ...
          if signature is not None:
            state = signature.getValidationState()
            found = False
            # Make sure there is not already a conflict giving the state
            for state_item in state_list:
              if state_item[0] == subscriber:
                found = True
                break
            if not found:
              state_list.append([subscriber, state])
    return state_list

  security.declareProtected(Permissions.ModifyPortalContent,
                            'applyPublisherValue')
  def applyPublisherValue(self, conflict):
    """
      after a conflict resolution, we have decided
      to keep the local version of an object
    """
    object = conflict.getOriginValue()
    subscriber = conflict.getSubscriber()
    # get the signature:
    #LOG('p_sync.applyPublisherValue, subscriber: ', DEBUG, subscriber)
    gid = subscriber.getGidFromObject(object)
    signature = subscriber.getSignatureFromGid(gid)
    signature.delConflict(conflict)
    if not signature.getConflictList():
      signature.resolveConflictWithMerge()

  security.declareProtected(Permissions.ModifyPortalContent,
                            'applyPublisherDocument')
  def applyPublisherDocument(self, conflict):
    """
    apply the publisher value for all conflict of the given document
    """
    subscriber = conflict.getSubscriber()
    for c in self.getConflictList(conflict.getOriginValue()):
      if c.getSubscriber() == subscriber:
        #LOG('applyPublisherDocument, applying on conflict: ', DEBUG, conflict)
        c.applyPublisherValue()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPublisherDocumentPath')
  def getPublisherDocumentPath(self, conflict):
    """
    apply the publisher value for all conflict of the given document
    """
    return conflict.getOrigin()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPublisherDocument')
  def getPublisherDocument(self, conflict):
    """
    apply the publisher value for all conflict of the given document
    """
    publisher_object_path = self.getPublisherDocumentPath(conflict)
    #LOG('getPublisherDocument publisher_object_path', TRACE, publisher_object_path)
    publisher_object = self.unrestrictedTraverse(publisher_object_path)
    return publisher_object

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSubscriberDocumentVersion')
  def getSubscriberDocumentVersion(self, conflict, docid):
    """
    Given a 'conflict' and a 'docid' refering to a new version of a
    document, applies the conflicting changes to the document's new
    version. By so, two differents versions of the same document will be
    available.
    Thus, the manager will be able to open both version of the document
    before selecting which one to keep.
    """
    subscriber = conflict.getSubscriber()
    publisher_object = conflict.getOrigineValue()
    publisher_xml = self.getXMLObject(
                       object=publisher_object,
                       xml_mapping=subscriber.getXmlBindingGeneratorMethodId())
    directory = publisher_object.aq_parent
    object_id = docid
    if object_id in directory.objectIds():
      directory._delObject(object_id)
      # Import the conduit and get it
      conduit_name = subscriber.getConduitModuleId()
      conduit = getConduitByName(conduit_name)
      conduit.addNode(xml=publisher_xml, object=directory,
                      object_id=object_id,
                      signature=conflict.getParentValue())
      subscriber_document = directory._getOb(object_id)
      for c in self.getConflictList(conflict.getOriginValue()):
        if c.getSubscriber() == subscriber:
          c.applySubscriberValue(object=subscriber_document)
      return subscriber_document

  def _getCopyId(self, object):
    directory = object.aq_inner.aq_parent
    if directory.getId() != 'portal_repository':
      object_id = object.getId() + '_conflict_copy'
      if object_id in directory.objectIds():
        directory._delObject(object_id)
    else:
      repotool = directory
      docid, rev = repotool.getDocidAndRevisionFromObjectId(object.getId())
      new_rev = repotool.getFreeRevision(docid) + 10 # make sure it's not gonna provoke conflicts
      object_id = repotool._getId(docid, new_rev)
    return object_id

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSubscriberDocumentPath')
  def getSubscriberDocumentPath(self, conflict):
    """
    apply the publisher value for all conflict of the given document
    """
    subscriber = conflict.getSubscriber()
    publisher_object = conflict.getOriginValue()
    conduit_name = subscriber.getConduitModuleId()
    conduit = getConduitByName(conduit_name)
    publisher_xml = conduit.getXMLFromObjectWithId(publisher_object,
                       xml_mapping=subscriber.getXmlBindingGeneratorMethodId(),
                       context_document=subscriber.getPath())
    directory = publisher_object.aq_inner.aq_parent
    object_id = self._getCopyId(publisher_object)
    # Import the conduit and get it
    conduit.addNode(xml=publisher_xml, object=directory, object_id=object_id,
                    signature=conflict.getParentValue())
    subscriber_document = directory._getOb(object_id)
    subscriber_document._conflict_resolution = 1
    for c in self.getConflictList(conflict.getOriginValue()):
      if c.getSubscriber() == subscriber:
        c.applySubscriberValue(object=subscriber_document)
    copy_path = subscriber_document.getPhysicalPath()
    return copy_path

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSubscriberDocument')
  def getSubscriberDocument(self, conflict):
    """
    apply the publisher value for all conflict of the given document
    """
    subscriber_object_path = self.getSubscriberDocumentPath(conflict)
    subscriber_object = self.unrestrictedTraverse(subscriber_object_path)
    return subscriber_object

  security.declareProtected(Permissions.ModifyPortalContent,
                            'applySubscriberDocument')
  def applySubscriberDocument(self, conflict):
    """
    apply the subscriber value for all conflict of the given document
    """
    # XXX-AUREL : when we solve one conflict, it solves all conflicts related
    # to the same object ? is it the wanted behaviour ?
    subscriber = conflict.getSubscriber()
    for c in self.getConflictList(conflict.getOriginValue()):
      if c.getSubscriber() == subscriber:
        c.applySubscriberValue()

  security.declareProtected(Permissions.ModifyPortalContent,
                            'applySubscriberValue')
  def applySubscriberValue(self, conflict, object=None):
    """
      after a conflict resolution, we have decided
      to keep the local version of an object
    """
    solve_conflict = 1
    if object is None:
      object = conflict.getOriginValue()
    else:
      # This means an object was given, this is used in order
      # to see change on a copy, so don't solve conflict
      solve_conflict = False
    subscriber = conflict.getSubscriber()
    # get the signature:
    gid = subscriber.getGidFromObject(object)
    signature = subscriber.getSignatureFromGid(gid)
    # Import the conduit and get it
    conduit_name = subscriber.getConduitModuleId()
    conduit = getConduitByName(conduit_name)
    conduit.updateNode(xml=conflict.getDiffChunk(), object=object, force=True, signature=signature)
    if solve_conflict:
      signature.delConflict(conflict)
      if not signature.getConflictList():
        signature.resolveConflictWithMerge()

  #security.declareProtected(Permissions.ModifyPortalContent,
      #'managePublisherValue')
  #def managePublisherValue(self, subscription_url, property_id, object_path,
      #RESPONSE=None):
    #"""
    #Do whatever needed in order to store the local value on
    #the remote server

    #Suggestion (API)
      #add method to view document with applied xupdate
      #of a given subscriber XX
      #(ex. viewSubscriberDocument?path=ddd&subscriber_id=dddd)
      #Version=Version CPS
    #"""
    ## Retrieve the conflict object
    ##LOG('manageLocalValue', DEBUG, '%s %s %s' % (str(subscription_url),
                                          ##str(property_id),
                                          ##str(object_path)))
    #for conflict in self.getConflictList():
      #if conflict.getPropertyId() == property_id:
        #if '/'.join(conflict.getObjectPath()) == object_path:
          #if conflict.getSubscriber().getSubscriptionUrlString() == subscription_url:
            #conflict.applyPublisherValue()
    #if RESPONSE is not None:
      #RESPONSE.redirect('manageConflicts')

  #security.declareProtected(Permissions.ModifyPortalContent, 
      #'manageSubscriberValue')
  #def manageSubscriberValue(self, subscription_url, property_id, object_path, 
      #RESPONSE=None):
    #"""
    #Do whatever needed in order to store the remote value locally
    #and confirmed that the remote box should keep it's value
    #"""
    ##LOG('manageLocalValue', DEBUG, '%s %s %s' % (str(subscription_url),
                                          ##str(property_id),
                                          ##str(object_path)))
    #for conflict in self.getConflictList():
      #if conflict.getPropertyId() == property_id:
        #if '/'.join(conflict.getObjectPath()) == object_path:
          #if conflict.getSubscriber().getSubscriptionUrlString() == subscription_url:
            #conflict.applySubscriberValue()
    #if RESPONSE is not None:
      #RESPONSE.redirect('manageConflicts')

  #security.declareProtected(Permissions.ModifyPortalContent,
      #'manageSubscriberDocument')
  #def manageSubscriberDocument(self, subscription_url, object_path):
    #"""
    #"""
    #for conflict in self.getConflictList():
      #if '/'.join(conflict.getObjectPath()) == object_path:
        #if conflict.getSubscriber().getSubscriptionUrlString() == subscription_url:
          #conflict.applySubscriberDocument()
          #break
    #self.managePublisherDocument(object_path)

  #security.declareProtected(Permissions.ModifyPortalContent, 
      #'managePublisherDocument')
  #def managePublisherDocument(self, object_path):
    #"""
    #"""
    #retry = True
    #while retry:
      #retry = False
      #for conflict in self.getConflictList():
        #if '/'.join(conflict.getObjectPath()) == object_path:
          #conflict.applyPublisherDocument()
          #retry = True
          #break

  def resolveContext(self, context):
    """
    We try to return a path (like ('','erp5','foo') from the context.
    Context can be :
      - a path
      - an object
      - a string representing a path
    """
    if context is None:
      return context
    elif isinstance(context, tuple):
      return context
    elif isinstance(context, tuple):
      return tuple(context.split('/'))
    else:
      return context.getPhysicalPath()

  security.declarePublic('sendResponse')
  def sendResponse(self, to_url=None, from_url=None, sync_id=None, xml=None,
      domain=None, send=1, content_type='application/vnd.syncml+xml'):
    """
    We will look at the url and we will see if we need to send mail, http
    response, or just copy to a file.
    """
##     LOG('sendResponse, domain.getPath(): ', INFO, domain.getPath())
##     LOG('sendResponse, to_url: ', INFO, to_url)
##     LOG('sendResponse, from_url: ', INFO, from_url)
##     LOG('sendResponse, sync_id: ', INFO, sync_id)
##     LOG('sendResponse, xml: \n', INFO, xml)
    if content_type == 'application/vnd.syncml+wbxml':
      xml = xml2wbxml(xml)
      #LOG('sendHttpResponse, xml after wbxml: \n', DEBUG, hexdump(xml))
    if domain is not None:
      gpg_key = domain.getGpgPublicKey()
      if gpg_key:
        filename = str(random.randrange(1,2147483600)) + '.txt'
        decrypted = file('/tmp/%s' % filename,'w')
        decrypted.write(xml)
        decrypted.close()
        (status,output)=commands.getstatusoutput('gzip /tmp/%s' % filename)
        (status,output)=commands.getstatusoutput('gpg --yes --homedir \
            /var/lib/zope/Products/ERP5SyncML/gnupg_keys -r "%s" -se \
            /tmp/%s.gz' % (gpg_key,filename))
        # LOG('sendResponse, gpg output:', DEBUG, output)
        encrypted = file('/tmp/%s.gz.gpg' % filename,'r')
        xml = encrypted.read()
        encrypted.close()
        commands.getstatusoutput('rm -f /tmp/%s.gz' % filename)
        commands.getstatusoutput('rm -f /tmp/%s.gz.gpg' % filename)
    if send:
      if isinstance(to_url, str):
        scheme = urlparse(to_url)[0]
        # XXX-Aurel a mapping between protocol-method should be
        # done instead of treating everything here
        if scheme in ('http', 'https'):
          if domain.getPortalType() == 'SyncML Publication' and not\
                                                 domain.getIsActivityEnabled():
            # not use activity
            # XXX Make sure this is not a problem
            return None
          #use activities to send send an http response
          #LOG('sendResponse, will start sendHttpResponse, xml', INFO, '')
          self.activate(activity='SQLQueue',
                        tag=domain.getId(),
                        priority=ACTIVITY_PRIORITY).sendHttpResponse(
                                              sync_id=sync_id,
                                              to_url=to_url,
                                              xml=xml,
                                              domain_path=domain.getPath(),
                                              content_type=content_type)
        elif scheme in ('file',):
          filename = to_url[len('file:/'):]
          stream = file(filename, 'w')
          stream.write(xml)
          stream.close()
          # we have to use local files (unit testing for example
        elif scheme in ('mailto',):
          # we will send an email
          to_address = to_url[len('mailto:'):]
          from_address = from_url[len('mailto:'):]
          self.sendMail(from_address, to_address, sync_id, xml)
        else:
          LOG("sendResponse", WARNING, "Unknown scheme %s for response %s : %s - %s" %(domain.getPath(),
                                                                                       scheme, to_url, xml))
    return xml

  security.declarePrivate('sendHttpResponse')
  def sendHttpResponse(self, to_url=None, sync_id=None, xml=None,
                       domain_path=None,
                       content_type='application/vnd.syncml+xml'):
    domain = self.unrestrictedTraverse(domain_path)
    #LOG('sendHttpResponse, starting with domain:', INFO, domain)
    if domain is not None:
      if domain.getPortalType() == 'SyncML Publication' and not\
                                                 domain.getIsActivityEnabled():
        return xml
    # Retrieve the proxy from os variables
    proxy_url = ''
    if os.environ.has_key('http_proxy'):
      proxy_url = os.environ['http_proxy']
    #LOG('sendHttpResponse, proxy_url:', DEBUG, proxy_url)
    if proxy_url !='':
      proxy_handler = urllib2.ProxyHandler({"http" :proxy_url})
    else:
      proxy_handler = urllib2.ProxyHandler({})
    pass_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    auth_handler = urllib2.HTTPBasicAuthHandler(pass_mgr)
    proxy_auth_handler = urllib2.ProxyBasicAuthHandler(pass_mgr)
    opener = urllib2.build_opener(proxy_handler, proxy_auth_handler,
        auth_handler, TimeoutHTTPHandler)
    urllib2.install_opener(opener)
    to_encode = {}
    to_encode['text'] = xml
    to_encode['sync_id'] = sync_id
    headers = {'User-Agent':'ERP5SyncML', 'Content-Type':content_type}

    #XXX bad hack for synchronization with erp5
    # because at this time, when we call the readResponse method, we must
    # encode the data with urlencode if we want the readResponse method to
    # receive the data's in parameters.
    # All this should be improved to not use urlencode in all cases.
    # to do this, perhaps use SOAP :
    #  - http://en.wikipedia.org/wiki/SOAP
    #  - http://www.contentmanagementsoftware.info/zope/SOAPSupport
    #  - http://svn.zope.org/soap/trunk/

    if domain.getIsSynchronizedWithErp5Portal():
      #LOG('Synchronization with another ERP5 instance ...', INFO, 'to_encode = %s' %(to_encode))
      if to_url.find('readResponse')<0:
        to_url = to_url + '/portal_synchronizations/readResponse'
      encoded = urllib.urlencode(to_encode)
      data = encoded
      request = urllib2.Request(url=to_url, data=data)
    else:
      #XXX only to synchronize with other server than erp5 (must be improved):
      # XXX-AUREL : head is an undefined variable here !!!
      data = head+xml
      request = urllib2.Request(to_url, data, headers)

    try:
      url_file = urllib2.urlopen(request)
##       LOG("sendHttpResponse, sent to url %s :" % to_url, INFO, data)
##       LOG('sendHttpResponse, url_file', INFO, (url_file))
      result = url_file.read()
    except socket.error, msg:
      self.activate(activity='SQLQueue',
                    tag=domain.getId(),
                    priority=ACTIVITY_PRIORITY).sendHttpResponse(
                                                  to_url=to_url,
                                                  sync_id=sync_id,
                                                  xml=xml,
                                                  domain_path=domain.getPath(),
                                                  content_type=content_type)
      LOG('sendHttpResponse, socket ERROR:', INFO, msg)
      LOG('sendHttpResponse, url, data', INFO, (to_url, data))
      return
    except urllib2.URLError, msg:
      LOG("sendHttpResponse, can't open url %s :" % to_url, INFO, msg)
      LOG('sendHttpResponse, to_url, data', INFO, (to_url, data))
      return

    if domain is not None:
      if domain.getPortalType() == 'SyncML Subscription' and not\
                                                 domain.getIsActivityEnabled():
        #if we don't use activity :
        if result:
          self.readResponse(sync_id=sync_id, text=result)
    return result

  security.declareProtected(Permissions.ManagePortal, 'sync')
  def sync(self):
    """
    This will try to synchronize every subscription
    XXX Should not be used
    """
    for subscription in self.getSubscriptionList():
      #user_id = subscription.getZopeUser()
      #uf = self.getPortalObject().acl_users
      #user = uf.getUserById(user_id).__of__(uf)
      #newSecurityManager(None, user)
      subscription.activate(activity='SQLQueue',
                            tag=subscription.getId(),
                            priority=ACTIVITY_PRIORITY
                                ).SubSync(subscription.getPath())

  security.declarePublic('readResponse')
  def readResponse(self, text='', sync_id=None, to_url=None, from_url=None):
    """
    We will look at the url and we will see if we need to send mail, http
    response, or just copy to a file.
    """
##     LOG('readResponse, text:', INFO, text)
##     LOG('readResponse, hexdump(text) :', INFO, hexdump(text))
    syncml_logger.info('readResponse to_url %s' %(to_url,))
    syncml_logger.info('readResponse from_url %s' %(from_url,))
    syncml_logger.info('readResponse sync_id %s' %(sync_id,))
    status_code = None
    if text:
      # XXX We will look everywhere for a publication/subsription with
      # the id sync_id, this is not so good, but there is no way yet
      # to know if we will call a publication or subscription XXX
##       LOG('readResponse, sync_id :', INFO, sync_id)
      gpg_key = ''
      # we are still anonymous at this time, use unrestrictedSearchResults
      # to fetch the Subcribers
      catalog_tool = self.getPortalObject().portal_catalog
      publication_list = catalog_tool.unrestrictedSearchResults(
                                              parent_uid=self.getUid(),
                                              portal_type='SyncML Publication',
                                              source_reference=sync_id,
                                              validation_state='validated')
      if publication_list:
        publication = publication_list[0].getObject()
        gpg_key = publication.getGpgPublicKey()
        domain = publication
      if not gpg_key:
        # Retrieve Subscription and login with intial user
        # Who start the process
        # sync_id parameter can be source_reference or destination_reference
        subscription_list = catalog_tool.unrestrictedSearchResults(
                                               parent_uid=self.getUid(),
                                               portal_type='SyncML Subscription',
                                               validation_state='validated')
        for subscription in subscription_list:
          subscription = subscription.getObject()
          if sync_id in (subscription.getSourceReference(),
                                       subscription.getDestinationReference()):
            gpg_key = subscription.getGpgPublicKey()
            domain = subscription
            user_id = domain.getProperty('zope_user')
            if user_id:
              ##LOG('readResponse, user :', DEBUG, user)
              user_folder = self.getPortalObject().acl_users
              user = user_folder.getUserById(user_id).__of__(user_folder)
              newSecurityManager(None, user)
      else:
        # decrypt the message if needed
        filename = str(random.randrange(1, 2147483600)) + '.txt'
        encrypted = file('/tmp/%s.gz.gpg' % filename,'w')
        encrypted.write(text)
        encrypted.close()
        (status, output) = commands.getstatusoutput('gpg --homedir \
            /var/lib/zope/Products/ERP5SyncML/gnupg_keys -r "%s"  --decrypt \
            /tmp/%s.gz.gpg > /tmp/%s.gz' % (gpg_key, filename, filename))
        # LOG('readResponse, gpg output:', INFO, output)
        (status,output)=commands.getstatusoutput('gunzip /tmp/%s.gz' % filename)
        decrypted = file('/tmp/%s' % filename,'r')
        text = decrypted.read()
        #LOG('readResponse, text:', INFO, text)
        decrypted.close()
        commands.getstatusoutput('rm -f /tmp/%s' % filename)
        commands.getstatusoutput('rm -f /tmp/%s.gz.gpg' % filename)
      # Get the target and then find the corresponding publication or
      # Subscription
      # LOG('type(text) : ', INFO, type(text))
      if domain is None:
        LOG('Impossible to find a publication or subscription for %s' %(sync_id,),
            WARNING, "Check that your pub/sub are validated and their source URI")
        return " "

      if domain.getContentType() == 'application/vnd.syncml+wbxml':
        text = wbxml2xml(text)
      syncml_logger.info('readResponse, text after wbxml : %s\n' %(text,))
      xml = etree.XML(text, parser=parser)
      url = '%s' % xml.xpath('string(/syncml:SyncML/syncml:SyncHdr/'\
                             'syncml:Target/syncml:LocURI)',
                             namespaces=xml.nsmap)
      # XXX-AUREL : the following part assumes that pub and sub have different
      # source_reference now since url can be the same
      # What is the gain in this ? If it has to remains like this, developper
      # must be informed not to waste time !!!
      for publication in self.searchFolder(portal_type='SyncML Publication',
                                           source_reference=sync_id,
                                           validation_state='validated'):
        if publication.getUrlString() == url:
          if publication.getIsActivityEnabled():
            #use activities to send SyncML data.
            publication.activate(activity='SQLQueue',
                                 tag=publication.getId(),
                                 priority=ACTIVITY_PRIORITY).PubSync(
                                                         publication.getPath(),
                                                         text)
            return ' '
          else:
            result = self.PubSync(publication.getPath(), xml)
            # Then encrypt the message
            xml = result['xml']
            if publication.getContentType() == 'application/vnd.syncml+wbxml':
              xml = xml2wbxml(xml)
            return xml
      for subscription in self.searchFolder(portal_type='SyncML Subscription',
                                            source_reference=sync_id,
                                            validation_state='validated'):
        if subscription.getSubscriptionUrlString() == url:
          subscription_path = subscription.getPath()
          self.activate(activity='SQLQueue',
                        tag=subscription.getId(),
                        priority=ACTIVITY_PRIORITY).SubSync(subscription_path,
                                                            text)
          return ' '
    # we use from only if we have a file
    elif isinstance(from_url, str):
      if from_url.find('file://') == 0:
        try:
          filename = from_url[len('file:/'):]
          stream = file(filename, 'r')
          xml = stream.read()
          # LOG('readResponse', DEBUG, 'file... msg: %s' % str(stream.read()))
        except IOError:
          LOG('readResponse, cannot read file: ', INFO, filename)
          xml = None
        if xml is not None and len(xml) == 0:
          xml = None
        return xml

  security.declareProtected(Permissions.ModifyPortalContent, 'PubSync')
  def PubSync(self, publication_path, msg=None, RESPONSE=None, subscriber=None):
    """
      This is the synchronization method for the server
    """
    LOG('PubSync', DEBUG, 'Starting... publication: %s' % (publication_path))
    # Read the request from the client
    publication = self.unrestrictedTraverse(publication_path)
    xml_client = msg
    if xml_client is None:
      xml_client = self.readResponse(from_url=publication.getUrlString(),
                                     sync_id=publication.getSourceReference())
    LOG('PubSync', DEBUG, 'Starting... msg: %s' % str(xml_client))
    result = None
    if xml_client is not None:
      if isinstance(xml_client, (str, unicode)):
        xml_client = etree.XML(xml_client, parser=parser)
      #FIXME to apply a DTD or schema
      if xml_client.xpath('local-name()') != "SyncML":
        LOG('PubSync', INFO, 'This is not a SyncML Message')
        raise ValueError, "Sorry, This is not a SyncML Message"
      alert_code = getAlertCodeFromXML(xml_client)
      category_tool = self.getPortalObject().portal_categories
      if alert_code:
        alert_code = [category.getId() for category in\
                      category_tool.syncml_alert_code.objectValues() if\
                      category.getReference() == alert_code][0]
      # Get informations from the header
      client_header = xml_client[0]
      #FIXME to apply a DTD or schema
      if client_header.xpath('local-name()') != "SyncHdr":
        LOG('PubSync', INFO, 'This is not a SyncML Header')
        raise ValueError, "Sorry, This is not a SyncML Header"
      subscription_url = getSubscriptionUrlFromXML(client_header)
      # Get the subscriber or create it if not already in the list
      subscriber = publication.getSubscriber(subscription_url)
      if subscriber is None:
        subscriber = publication.createUnrestrictedSubscriber(
                                  subscription_url_string=subscription_url,
                                  xml_binding_generator_method_id=\
                                  publication.getXmlBindingGeneratorMethodId(),
                                  conduit_module_id=\
                                              publication.getConduitModuleId(),
                                  list_method_id=publication.getListMethodId(),
                                  gid_generator_method_id=publication.getGidGeneratorMethodId(),
                                  source=publication.getSource(),
                                  syncml_alert_code=alert_code)
        # first synchronization
        result = self.PubSyncInit(publication=publication,
                                  xml_client=xml_client,
                                  subscriber=subscriber,
                                  sync_type=alert_code)
      elif checkAlert(xml_client) and alert_code in ('two_way', 'slow_sync',
                                                     'one_way_from_server',
                                                     'one_way_from_client',):
        subscriber.setXmlBindingGeneratorMethodId(
                                  publication.getXmlBindingGeneratorMethodId())
        subscriber.setConduitModuleId(publication.getConduitModuleId())
        result = self.PubSyncInit(publication=publication,
                                  xml_client=xml_client,
                                  subscriber=subscriber,
                                  sync_type=alert_code)
      elif not alert_code:
        #we log the user authenticated to do the synchronization with him
        if xml_client.xpath('string(/syncml:SyncML/syncml:SyncBody/'\
                            'syncml:Map)', namespaces=xml_client.nsmap):
          setRidWithMap(xml_client, subscriber)
        if subscriber.getAuthenticationState() == 'logged_in':
          uf = self.getPortalObject().acl_users
          authenticated_user = subscriber.getProperty('authenticated_user')
          user = uf.getUserById(authenticated_user).__of__(uf)
          newSecurityManager(None, user)
        result = self.PubSyncModif(publication, xml_client)
      elif alert_code in category_tool.syncml_alert_code.objectIds():
        raise NotImplementedError('ALert code not handled yet: %r' % alert_code)
      else:
        # Must return (405) Command not allowed
        raise NotImplementedError
    elif subscriber is not None:
      # This looks like we are starting a synchronization after
      # a conflict resolution by the user
      result = self.PubSyncInit(publication=publication,
                                xml_client=None,
                                subscriber=subscriber,
                                sync_type='two_way')
    return result

  security.declareProtected(Permissions.ModifyPortalContent, 'PubSyncInit')
  def PubSyncInit(self, publication=None, xml_client=None, subscriber=None,
      sync_type=None):
    """
      Read the client xml message
      Send the first XML message from the server
    """
    LOG('PubSyncInit', INFO,
        'Starting... publication: %s' % (publication.getPath()))
    #the session id is set at the same value of those of the client
    session_id = int(xml_client.xpath(
                      'string(/syncml:SyncML/syncml:SyncHdr/syncml:SessionID)',
                      namespaces=xml_client.nsmap))
    subscriber.setSessionId(session_id)
    #same for the message id
    message_id = getMessageIdFromXml(xml_client)
    subscriber.setMessageId(message_id)
    #at the begining of the synchronization the subscriber is not authenticated
    if subscriber.getAuthenticationState() == 'logged_in':
      subscriber.logout()
    #the last_message_id is 1 because the message that 
    #we are about to send is the message 1
    subscriber.initLastMessageId(1)

    alert = None
    # Get informations from the body
    if xml_client is not None: # We have received a message
      last_anchor = '%s' % xml_client.xpath('string(.//syncml:Alert/'\
                                            'syncml:Item/syncml:Meta/'\
                                            'syncml:Anchor/syncml:Last)',
                                            namespaces=xml_client.nsmap)
      next_anchor = '%s' % xml_client.xpath('string(.//syncml:Alert/'\
                                            'syncml:Item/syncml:Meta/'\
                                            'syncml:Anchor/syncml:Next)',
                                            namespaces=xml_client.nsmap)
      alert = checkAlert(xml_client)
      alert_code = getAlertCodeFromXML(xml_client)
      cred_node_list = xml_client.xpath('/syncml:SyncML/syncml:SyncHdr/'\
                                        'syncml:Cred',
                                        namespaces=xml_client.nsmap)

      #the source and the target of the subscriber are reversed compared 
      # to those of the publication :
      target_uri = '%s' % xml_client.xpath('string(//syncml:SyncBody/'\
                                           'syncml:Alert/syncml:Item/'\
                                           'syncml:Target/syncml:LocURI)',
                                           namespaces=xml_client.nsmap)
      subscriber.setSourceReference(target_uri)
      source_uri = '%s' % xml_client.xpath('string(//syncml:SyncBody/'\
                                           'syncml:Alert/syncml:Item/'\
                                           'syncml:Source/syncml:LocURI)',
                                           namespaces=xml_client.nsmap)
      subscriber.setDestinationReference(source_uri)

      cmd_id = 1 # specifies a SyncML message-unique command identifier
      #create element 'SyncML' with a default namespace
      xml = E.SyncML()
      # syncml header
      xml.append(self.SyncMLHeader(subscriber.getSessionId(),
        subscriber.getMessageId(),
        subscriber.getSubscriptionUrlString(),
        publication.getUrlString()))
      # syncml body
      sync_body = E.SyncBody()
      xml.append(sync_body)

      # at the begining, the code is initialised at UNAUTHORIZED
      auth_code = 'invalid_credentials'
      if not len(cred_node_list):
        auth_code = 'missing_credentials'
        LOG("PubSyncInit : there's no credential in the SyncML Message!!!", INFO,'return status 407 - %s' %(auth_code))
        # Prepare the xml message for the Sync initialization package
        sync_body.append(self.SyncMLChal(cmd_id, "SyncHdr",
                                         publication.getUrlString(),
                                         subscriber.getSubscriptionUrlString(),
                                         publication.getAuthenticationFormat(),
                                         publication.getAuthenticationType(),
                                         auth_code))
        cmd_id += 1
        # chal message
        xml_status, cmd_id = self.SyncMLStatus(
                                      xml_client,
                                      auth_code,
                                      cmd_id,
                                      next_anchor,
                                      subscription=subscriber)
        sync_body.extend(xml_status)
      else:
        # If slow sync, then resend everything
        if alert_code == resolveSyncmlAlertCode(self, 'slow_sync') and \
                                        subscriber.getNextAnchor() is not None:
          LOG('Warning !!!, reseting client synchronization for subscriber:', WARNING,
              subscriber.getPath())
          subscriber.resetAllSignatures()
          subscriber.resetAnchorList()

        # Check if the last time synchronization is the same as the client one
        if subscriber.getNextAnchor() != last_anchor:
          if not last_anchor:
            LOG('PubSyncInit', INFO, 'anchor null')
          else:
            message = '\nsubscriber.getNextAnchor:\t%s\nsubscriber.getLastAnchor:\t%s\
                  \nlast_anchor:\t\t\t%s\nnext_anchor:\t\t\t%s' % \
                  (subscriber.getNextAnchor(),
                    subscriber.getLastAnchor(),
                    last_anchor,
                    next_anchor)
            LOG('PubSyncInit Anchors', INFO, message)
        else:
          subscriber.setNextAnchor(next_anchor)
        cred_node = cred_node_list[0]
        meta_node = cred_node.xpath('syncml:Meta',
                                                 namespaces=cred_node.nsmap)[0]
        authentication_format = '%s' % meta_node.xpath('string(./*'\
                                                  '[local-name() = "Format"])',
                                                  namespaces=meta_node.nsmap)
        authentication_type = '%s' % meta_node.xpath('string(./*'\
                                                    '[local-name() = "Type"])',
                                                  namespaces=meta_node.nsmap)
        data = '%s' % cred_node.xpath('string(syncml:Data)',
                                      namespaces=cred_node.nsmap)

        if authentication_type == publication.getAuthenticationType():
          authentication_format = publication.getAuthenticationFormat()
          decoded = decode(authentication_format, data)
          if decoded and ':' in decoded:
            login, password = decoded.split(':')
            user_folder = self.getPortalObject().acl_users
            for plugin_name, plugin in user_folder._getOb('plugins')\
                                           .listPlugins(IAuthenticationPlugin):
              #LOG('PubSyncInit Authentication', INFO,
                  #'%r %s:%s' % (plugin, login, password))
              if plugin.authenticateCredentials(
                        {'login':login, 'password':password}) is not None:
                subscriber.login()
                LOG("PubSyncInit Authentication Accepted", INFO, '')
                auth_code = 'authentication_accepted'
                #here we must log in with the user authenticated :
                user = user_folder.getUserById(login).__of__(user_folder)
                newSecurityManager(None, user)
                subscriber._edit(authenticated_user=login)
                break
              else:
                # in all others cases, the auth_code is set to UNAUTHORIZED
                auth_code = 'invalid_credentials'
                LOG('PubSyncInit Authentication Failed !! with', INFO,
                    'login:%r' % (login,))

        # Prepare the xml message for the Sync initialization package
        if auth_code == 'authentication_accepted':
          xml_status, cmd_id = self.SyncMLStatus(xml_client, auth_code,
                                                 cmd_id, next_anchor,
                                                 subscription=subscriber)
          sync_body.extend(xml_status)
          # alert message
          sync_body.append(self.SyncMLAlert(cmd_id, sync_type,
                                            subscriber.getDestinationReference(),
                                            subscriber.getSourceReference(),
                                            subscriber.getLastAnchor(),
                                            next_anchor))
          cmd_id += 1

          subscriber.initialiseSynchronization()
        else:
          # chal message
          sync_body.append(self.SyncMLChal(cmd_id, "SyncHdr",
                                         publication.getUrlString(),
                                         subscriber.getSubscriptionUrlString(),
                                         publication.getAuthenticationFormat(),
                                         publication.getAuthenticationType(),
                                         auth_code))
          cmd_id += 1
          xml_status, cmd_id = self.SyncMLStatus(xml_client,
                                                 'missing_credentials', cmd_id,
                                                 next_anchor,
                                                 subscription=subscriber)
          sync_body.extend(xml_status)

    else:
      # We have started the sync from the server (may be for a conflict 
      # resolution)
      raise ValueError, "the syncml message is None. Maybe a synchronization \
          has been started from the server (forbiden)"
      # a synchronization is always starded from a client and can't be from
      # a server !
    sync_body.append(E.Final())
    xml_string = etree.tostring(xml, encoding='utf-8', pretty_print=True)
    if publication.getContentType() == 'application/vnd.syncml+wbxml':
      xml_string = xml2wbxml(xml_string)
    self.sendResponse(from_url=publication.getUrlString(),
                      to_url=subscriber.getSubscriptionUrlString(),
                      sync_id=subscriber.getDestinationReference(),
                      xml=xml_string, domain=publication,
                      content_type=publication.getContentType())

    return {'has_response': True, 'xml': xml_string}

  security.declareProtected(Permissions.ModifyPortalContent, 'PubSyncModif')
  def PubSyncModif(self, publication, xml_client):
    """
    The modidification message for the publication
    """
    return self.SyncModif(publication, xml_client)


  security.declareProtected(Permissions.ModifyPortalContent, 'SubSyncInit')
  def SubSyncInit(self, subscription):
    """
      Send the first XML message from the client
    """
    LOG('SubSyncInit',0,'starting....')
    cmd_id = 1 # specifies a SyncML message-unique command identifier
    subscription.createNewAnchor()
    subscription.initLastMessageId()

    # save the actual user to use it in all the session:
    user_id = getSecurityManager().getUser().getId()
    user_folder = self.getPortalObject().acl_users
    user = user_folder.getUserById(user_id)
    if user is None:
      raise ValueError, "Current logged user %s cannot be found in user folder, \
                 synchronization cannot work with this kind of user" %(user_id,)
    subscription._edit(zope_user=user_id)
    if subscription.getAuthenticationState() != 'logged_in':
      subscription.login()

    #create element 'SyncML'
    xml = E.SyncML()
    # syncml header
    xml.append(self.SyncMLHeader(subscription.incrementSessionId(),
                                 subscription.incrementMessageId(),
                                 subscription.getUrlString(),
                                 subscription.getSubscriptionUrlString(),
                                 source_name=subscription.getUserId()))

    # syncml body
    sync_body = E.SyncBody()
    xml.append(sync_body)

    subscription.initialiseSynchronization()

    # alert message
    sync_body.append(self.SyncMLAlert(cmd_id,
                                      subscription.getSyncmlAlertCode(),
                                      subscription.getDestinationReference(),
                                      subscription.getSourceReference(),
                                      subscription.getLastAnchor(),
                                      subscription.getNextAnchor()))
    cmd_id += 1
    syncml_put = self.SyncMLPut(cmd_id, subscription)
    if syncml_put is not None:
      sync_body.append(syncml_put)
      cmd_id += 1

    xml_string = etree.tostring(xml, encoding='utf-8', xml_declaration=True,
                                pretty_print=True)
    self.sendResponse(from_url=subscription.getSubscriptionUrlString(),
                      to_url=subscription.getUrlString(),
                      sync_id=subscription.getDestinationReference(),
                      xml=xml_string, domain=subscription,
                      content_type=subscription.getContentType())

    return {'has_response': True, 'xml': xml_string}

  security.declareProtected(Permissions.ModifyPortalContent, 'SubSync')
  def SubSync(self, subscription_path, msg=None, RESPONSE=None):
    """
      This is the synchronization method for the client
    """
    response = None #check if subsync replies to this messages
    subscription = self.unrestrictedTraverse(subscription_path)
    if msg is None and (subscription.getSubscriptionUrlString()).find('file') >= 0:
      msg = self.readResponse(sync_id=subscription.getDestinationReference(),
                              from_url=subscription.getSubscriptionUrlString())
    if msg is None:
      response = self.SubSyncInit(subscription)
    else:
      xml_client = msg
      if isinstance(xml_client, (str, unicode)):
        xml_client = etree.XML(xml_client, parser=parser)
      status_list = getSyncBodyStatusList(xml_client)
      if status_list:
        status_code_syncHdr = status_list[0]['code']
        LOG('SubSync status code : ', DEBUG, status_code_syncHdr)
        if status_code_syncHdr ==\
                      resolveSyncmlStatusCode(self, 'missing_credentials'):
          if xml_client.xpath('string(/syncml:SyncML/syncml:SyncBody/'\
                              'syncml:Status/syncml:Chal)',
                              namespaces=xml_client.nsmap):
            authentication_format = '%s' % xml_client.xpath(
                                      'string(//*[local-name() = "Format"])',
                                      namespaces=xml_client.nsmap)
            authentication_type = '%s' % xml_client.xpath(
                                      'string(//*[local-name() = "Type"])',
                                      namespaces=xml_client.nsmap)
            LOG('SubSync auth_required :', INFO,
                'format:%s, type:%s' % (authentication_format,
                                        authentication_type))
            subscription.setAuthenticationFormat(authentication_format)
            subscription.setAuthenticationType(authentication_type)
          else:
            raise ValueError, "Sorry, the server chalenge for an \
                authentication, but the authentication format is not find"

          LOG('SubSync', INFO, 'Authentication required')
          response = self.SubSyncCred(subscription, xml_client)
        elif status_code_syncHdr ==\
                        resolveSyncmlStatusCode(self, 'invalid_credentials'):
          LOG('SubSync', INFO, 'Bad authentication')
          return {'has_response': False, 'xml': xml_client}
        else:
          response = self.SubSyncModif(subscription, xml_client)
      else:
        response = self.SubSyncModif(subscription, xml_client)

    return response

  security.declareProtected(Permissions.ModifyPortalContent, 'SubSyncModif')
  def SubSyncModif(self, subscription, xml_client):
    """
      Send the client modification, this happens after the Synchronization
      initialization
    """
    return self.SyncModif(subscription, xml_client)

  security.declareProtected(Permissions.ModifyPortalContent, 'SyncModif')
  def SyncModif(self, domain, remote_xml):
    """
    Modification Message, this is used after the first
    message in order to send modifications.
    Send the server modification, this happens after the Synchronization
    initialization
    """
    has_response = False #check if syncmodif replies to this messages
    cmd_id = 1 # specifies a SyncML message-unique command identifier
    #LOG('SyncModif', DEBUG, 'Starting... domain: %s' % domain.getId())
    # Get informations from the header
    xml_header = remote_xml[0]
    #FIXME to apply a DTD or schema
    if xml_header.xpath('local-name()') != "SyncHdr":
      LOG('SyncModif', INFO, 'This is not a SyncML Header')
      raise ValueError, "Sorry, This is not a SyncML Header"

    subscriber = domain # If we are the client, this is fine
    simulate = False # used by applyActionList, should be False for client
    if domain.getPortalType() == 'SyncML Publication':
      subscription_url = getSubscriptionUrlFromXML(xml_header)
      subscriber = domain.getSubscriber(subscription_url)

    # We have to check if this message was not already, this can be dangerous
    # to update two times the same object
    message_id = getMessageIdFromXml(remote_xml)
    correct_message = subscriber.checkCorrectRemoteMessageId(message_id)
    if not correct_message: # We need to send again the message
      LOG('SyncModif, no correct message:', INFO, "sending again...")
      LOG('SyncModif message_id:', INFO, repr(message_id))
      last_xml = subscriber.getLastSentMessage()
      LOG("SyncModif last_xml :", INFO, last_xml)
      remote_xml = etree.tostring(remote_xml, encoding='utf-8',
                                  xml_declaration=True,
                                  pretty_print=True)
      LOG("SyncModif remote_xml :", INFO, remote_xml)
      if last_xml:
        has_response = True
        if domain.getPortalType() == 'SyncML Publication': # We always reply
          self.sendResponse(from_url=domain.getUrlString(),
                            to_url=subscriber.getSubscriptionUrlString(),
                            sync_id=subscriber.getDestinationReference(),
                            xml=last_xml,
                            domain=domain,
                            content_type=domain.getContentType())
        elif domain.getPortalType() == 'SyncML Subscription':
          self.sendResponse(from_url=domain.getSubscriptionUrlString(),
                            to_url=domain.getUrlString(),
                            sync_id=domain.getDestinationReference(),
                            xml=last_xml,
                            domain=domain,
                            content_type=domain.getContentType())
        else:
          raise ValueError('domain type not known %s' % domain.getPath())
      return {'has_response': has_response, 'xml': last_xml}
    subscriber.setLastSentMessage('')

    # First apply the list of status codes
    destination_waiting_more_data, has_status_list = self.applyStatusList(
                                                         subscriber=subscriber,
                                                         remote_xml=remote_xml)

    alert_code = getAlertCodeFromXML(remote_xml)
    # Import the conduit and get it
    conduit = getConduitByName(subscriber.getConduitModuleId())
    # Then apply the list of actions
    xml_confirmation_list, has_next_action, cmd_id = self.applyActionList(
                                                         cmd_id=cmd_id,
                                                         domain=domain,
                                                         subscriber=subscriber,
                                                         remote_xml=remote_xml,
                                                         conduit=conduit,
                                                         simulate=simulate)

    xml = E.SyncML()

    # syncml header
    if domain.getPortalType() == 'SyncML Publication':
      xml.append(self.SyncMLHeader(
                  subscriber.getSessionId(),
                  subscriber.incrementMessageId(),
                  subscriber.getSubscriptionUrlString(),
                  domain.getUrlString()))
    elif domain.getPortalType() == 'SyncML Subscription':
      xml.append(self.SyncMLHeader(
                  domain.getSessionId(), domain.incrementMessageId(),
                  domain.getUrlString(),
                  domain.getSubscriptionUrlString()))
    else:
      raise ValueError('domain not handled %r' % domain.getPath())
    # syncml body
    sync_body = E.SyncBody()
    xml.append(sync_body)

    xml_status, cmd_id = self.SyncMLStatus(
                                    remote_xml,
                                    'success',
                                    cmd_id,
                                    subscriber.getNextAnchor(),
                                    subscription=subscriber)
    sync_body.extend(xml_status)

    destination_url = ''
    # alert message if we want more data
    if destination_waiting_more_data:
      sync_body.append(self.SyncMLAlert(
                        cmd_id,
                        'partial_content',
                        subscriber.getTargetURI(),
                        subscriber.getSourceReference(),
                        subscriber.getLastAnchor(),
                        subscriber.getNextAnchor()))
    # Now we should send confirmations
    cmd_id_before_getsyncmldata = cmd_id
    cmd_id = cmd_id+1
    # XXX Not sure that reading getSyncMLData before sending
    # confimations is a good idea.
    # It means that synchronisations are crossed executed
    # It must be clarified and fixed.
    if domain.getIsActivityEnabled():
      #use activities to get SyncML data.
      remote_xml = etree.tostring(remote_xml, encoding='utf-8',
                                  xml_declaration=True, pretty_print=False)
      xml_tree = etree.tostring(xml, encoding='utf-8', xml_declaration=True,
                                pretty_print=False)
      xml_confirmation_list = [etree.tostring(xml, encoding='utf-8',\
                                              xml_declaration=True,\
                                              pretty_print=False) for xml in \
                                              xml_confirmation_list]
      domain.activate(activity='SQLQueue',
                      tag=domain.getId(),
                      priority=ACTIVITY_PRIORITY).activateSyncModif(
                      domain_relative_url=domain.getRelativeUrl(),
                      remote_xml=remote_xml,
                      xml_tree=xml_tree,
                      subscriber_relative_url=subscriber.getRelativeUrl(),
                      cmd_id=cmd_id,
                      xml_confirmation_list=xml_confirmation_list,
                      syncml_data_list=[],
                      cmd_id_before_getsyncmldata=cmd_id_before_getsyncmldata,
                      has_status_list=has_status_list,
                      has_response=has_response )
      return {'has_response': True, 'xml': ''}
    else:
      result = self.getSyncMLData(domain=domain,
                             remote_xml=remote_xml,
                             subscriber=subscriber,
                             cmd_id=cmd_id,
                             xml_confirmation_list=xml_confirmation_list,
                             conduit=conduit,
                             maximum_object_list_len=None)
      syncml_data_list = result['syncml_data_list']
      xml_confirmation_list = result['xml_confirmation_list']
      cmd_id = result['cmd_id']
      return self.sendSyncModif(syncml_data_list, cmd_id_before_getsyncmldata,
                                subscriber, domain, xml_confirmation_list,
                                remote_xml, xml, has_status_list,
                                has_response)

  security.declarePrivate('applyStatusList')
  def applyStatusList(self, subscriber=None, remote_xml=None):
    """
    This read a list of status list (ie syncml confirmations).
    This method have to change status codes on signatures
    """
    status_list = getSyncBodyStatusList(remote_xml)
    has_status_list = False
    destination_waiting_more_data = False
    for status in status_list:
      if not status['code']:
        continue
      status_cmd = status['cmd']
      object_gid = status['source']
      if not object_gid:
        object_gid = status['target']
      status_code = status['code']
      signature = subscriber.getSignatureFromGid(object_gid)
      #if signature is None:
        ##the client give his id but not the gid
        #signature = subscriber.getSignatureFromRid(object_gid)
      #if signature is not None:
        #LOG('signature.getId()', 0, signature.getId())
        #LOG('signature.getReference()', 0, signature.getReference())
        #LOG('signature.getValidationState()', 0, signature.getValidationState())
        #LOG('status_cmd', 0, status_cmd)
        #LOG('status_code', 0, status_code)
      if status_cmd in ('Add', 'Replace',):
        has_status_list = True
        if status_code == resolveSyncmlStatusCode(self, 'partial_content'):
          destination_waiting_more_data = True
          signature.changeToPartial()
        elif status_code == resolveSyncmlStatusCode(self, 'conflict'):
          signature.changeToConflict()
        elif status_code == resolveSyncmlStatusCode(self,
                                               'conflict_resolved_with_merge'):
          # We will have to apply the update, and we should not care 
          # about conflicts, so we have to force the update
          signature.drift()
          signature.setForce(True)
        elif status_code in (resolveSyncmlStatusCode(self, 'success'),
                             resolveSyncmlStatusCode(self, 'item_added'),
                             resolveSyncmlStatusCode(self,
                             'conflict_resolved_with_client_command_winning')):#\
                          #and signature.getValidationState() != 'synchronized':
          signature.synchronize()
      elif status_cmd == 'Delete':
        has_status_list = True
        if status_code == resolveSyncmlStatusCode(self, 'success'):
          if signature is not None:
            subscriber._delObject(signature.getId())
    return destination_waiting_more_data, has_status_list

  security.declarePrivate('SyncMLChal')
  def SyncMLChal(self, cmd_id, cmd, target_ref, source_ref, auth_format,
      auth_type, auth_code):
    """
    This is used in order to ask crendentials
    """
    auth_code = resolveSyncmlStatusCode(self, auth_code)
    xml = (E.Status(
             E.CmdID('%s' % cmd_id),
             E.MsgRef('1'),
             E.CmdRef('0'),
             E.Cmd(cmd),
             E.TargetRef(target_ref),
             E.SourceRef(source_ref),
             E.Chal(
               E.Meta(
                 E.Format(auth_format, xmlns='syncml:metinf'),
                 E.Type(auth_type, xmlns='syncml:metinf')
                 )
               ),
            E.Data('%s' % auth_code)
            ))
    return xml

  security.declarePrivate('SyncMLAlert')
  def SyncMLAlert(self, cmd_id, sync_code, target, source, last_anchor,
                  next_anchor):
    """
      Since the Alert section is always almost the same, this is the
      way to set one quickly.
    """
    if isinstance(last_anchor, DateTime):
      last_anchor = last_anchor.strftime('%Y%m%dT%H%M%SZ')
    elif not last_anchor:
      last_anchor = NULL_ANCHOR
    if isinstance(next_anchor, DateTime):
      next_anchor = next_anchor.strftime('%Y%m%dT%H%M%SZ')
    elif not next_anchor:
      next_anchor = NULL_ANCHOR
    sync_code = resolveSyncmlAlertCode(self, sync_code)
    xml = (E.Alert(
            E.CmdID('%s' % cmd_id),
            E.Data(sync_code),
            E.Item(
              E.Target(
                E.LocURI(target)
                ),
              E.Source(
                E.LocURI(source)
                ),
              E.Meta(
                E.Anchor(
                  E.Last(last_anchor),
                  E.Next(next_anchor)
                  )
                )
              )
            ))
    return xml

  security.declarePrivate('SubSyncCred')
  def SubSyncCred(self, subscription, msg=None, RESPONSE=None):
    """
      This method send crendentials
    """
    cmd_id = 1 # specifies a SyncML message-unique command identifier
    #create element 'SyncML' with a default namespace
    xml = E.SyncML()
    # syncml header
    data = "%s:%s" % (subscription.getUserId(), subscription.getPassword())
    data = encode(subscription.getAuthenticationFormat(), data)
    xml.append(self.SyncMLHeader(
      subscription.incrementSessionId(),
      subscription.incrementMessageId(),
      subscription.getUrlString(),
      subscription.getSubscriptionUrlString(),
      source_name=subscription.getUserId(),
      dataCred=data,
      authentication_format=subscription.getAuthenticationFormat(),
      authentication_type=subscription.getAuthenticationType()))

    # syncml body
    sync_body = E.SyncBody()
    xml.append(sync_body)

    # alert message
    sync_body.append(self.SyncMLAlert(cmd_id,
                                      subscription.getSyncmlAlertCode(),
                                      subscription.getDestinationReference(),
                                      subscription.getSourceReference(),
                                      subscription.getLastAnchor(),
                                      subscription.getNextAnchor()))
    cmd_id += 1
    syncml_put = self.SyncMLPut(cmd_id, subscription)
    if syncml_put is not None:
      sync_body.append(syncml_put)
    sync_body.append(E.Final())
    xml_string = etree.tostring(xml, encoding='utf-8', xml_declaration=True,
                                pretty_print=True)
    self.sendResponse(from_url=subscription.getSubscriptionUrlString(),
                      to_url=subscription.getUrlString(),
                      sync_id=subscription.getDestinationReference(),
                      xml=xml_string, domain=subscription,
                      content_type=subscription.getContentType())

    return {'has_response': True, 'xml': xml_string}

  security.declarePrivate('SyncMLHeader')
  def SyncMLHeader(self, session_id, msg_id, target, source, target_name=None,
      source_name=None, dataCred=None, authentication_format='b64',
      authentication_type='syncml:auth-basic'):
    """
      Since the Header is always almost the same, this is the
      way to set one quickly.
    """
    xml = (E.SyncHdr(
            E.VerDTD('1.2'),
            E.VerProto('SyncML/1.2'),
            E.SessionID('%s' % session_id),
            E.MsgID('%s' % msg_id),
          ))
    target_node = E.Target(E.LocURI(target))
    if target_name:
      target_node.append(E.LocName(target_name.decode('utf-8')))
    xml.append(target_node)
    source_node = E.Source(E.LocURI(source))
    if source_name:
      source_node.append(E.LocName(source_name.decode('utf-8')))
    xml.append(source_node)
    if dataCred:
      xml.append(E.Cred(
                  E.Meta(E.Format(authentication_format, xmlns='syncml:metinf'),
                  E.Type(authentication_type, xmlns='syncml:metinf'),),
                  E.Data(dataCred)
                  ))
    return xml

  security.declarePrivate('SyncMLStatus')
  def SyncMLStatus(self, remote_xml, data_code, cmd_id, next_anchor,
                   subscription=None):
    """
    return a status bloc with all status corresponding to the syncml
    commands in remote_xml
    """
    #list of element in the SyncBody bloc
    sub_syncbody_element_list = remote_xml.xpath(
                                            '/syncml:SyncML/syncml:SyncBody/*',
                                            namespaces=remote_xml.nsmap)
    message_id = getMessageIdFromXml(remote_xml)
    status_list = []
    target_uri = '%s' % remote_xml.xpath('string(/syncml:SyncML/'\
                                         'syncml:SyncHdr/syncml:Target/'\
                                         'syncml:LocURI)',
                                         namespaces=remote_xml.nsmap)
    source_uri = '%s' % remote_xml.xpath('string(/syncml:SyncML/'\
                                         'syncml:SyncHdr/syncml:Source/'\
                                         'syncml:LocURI)',
                                         namespaces=remote_xml.nsmap)
    if isinstance(next_anchor, DateTime):
      next_anchor = next_anchor.strftime('%Y%m%dT%H%M%SZ')
    elif not next_anchor:
      next_anchor = NULL_ANCHOR
    if data_code != 'missing_credentials':
      xml = (E.Status(
               E.CmdID('%s' % cmd_id),
               E.MsgRef('%s' % message_id),
               E.CmdRef('0'),
               E.Cmd('SyncHdr'),
               E.TargetRef(target_uri),
               E.SourceRef(source_uri),
               E.Data(resolveSyncmlStatusCode(self, data_code)),
               ))
      cmd_id += 1
      status_list.append(xml)
    for sub_syncbody_element in sub_syncbody_element_list:
      if sub_syncbody_element.xpath('local-name()') not in\
                                                    ('Status', 'Final', 'Get'):
        nsmap = sub_syncbody_element.nsmap
        xml = (E.Status(
                 E.CmdID('%s' % cmd_id),
                 E.MsgRef('%s' % message_id),
                 E.CmdRef('%s' %\
                 sub_syncbody_element.xpath('string(.//syncml:CmdID)',
                                            namespaces=nsmap)),
                 E.Cmd('%s' % sub_syncbody_element.xpath('local-name()'))
                 ))
        cmd_id += 1
        #target_ref = sub_syncbody_element.xpath(
                                      #'string(.//syncml:Target/syncml:LocURI)',
                                      #namespaces=nsmap)
        #if target_ref:
          #xml.append(E.TargetRef('%s' % target_ref))
        #source_ref = sub_syncbody_element.xpath(
                                      #'string(.//syncml:Source/syncml:LocURI)',
                                      #namespaces=nsmap)
        #if source_ref:
          #xml.append(E.SourceRef('%s' % source_ref))
        target_ref = sub_syncbody_element.xpath(
                                      'string(.//syncml:Target/syncml:LocURI)',
                                      namespaces=nsmap)
        if target_ref:
          xml.append(E.SourceRef('%s' % target_ref))
        source_ref = sub_syncbody_element.xpath(
                                      'string(.//syncml:Source/syncml:LocURI)',
                                      namespaces=nsmap)
        if source_ref:
          xml.append(E.TargetRef('%s' % source_ref))
        if sub_syncbody_element.xpath('local-name()') == 'Add':
          xml.append(E.Data(resolveSyncmlStatusCode(self, 'item_added')))
        elif sub_syncbody_element.xpath('local-name()') == 'Alert' and \
            sub_syncbody_element.xpath('string(.//syncml:Data)',
                                       namespaces=nsmap) == \
            resolveSyncmlAlertCode(self, 'slow_sync'):
          xml.append(E.Data(resolveSyncmlStatusCode(self, 'refresh_required')))
        elif sub_syncbody_element.xpath('local-name()') == 'Alert':
          xml.append(E.Item(E.Data(E.Anchor(E.Next(next_anchor)))))
        else:
          xml.append(E.Data(resolveSyncmlStatusCode(self, 'success')))
        status_list.append(xml)
      #FIXME to do a test for Get
      if sub_syncbody_element.xpath('local-name()') == 'Get'\
          and subscription is not None:
        cmd_ref = '%s' % sub_syncbody_element.xpath('string(.//syncml:CmdID)',
                                                    namespaces=nsmap)
        syncml_result = self.SyncMLPut(
                                  cmd_id,
                                  subscription,
                                  markup='Results',
                                  cmd_ref=cmd_ref,
                                  message_id=message_id)
        if syncml_result is not None:
          status_list.append(syncml_result)
        cmd_id += 1

    return status_list, cmd_id

  security.declarePrivate('SyncMLPut')
  def SyncMLPut(self, cmd_id, subscription, markup='Put', cmd_ref=None,
      message_id=None):
    """
    this is used to inform the server of the CTType version supported
    but if the server use it to respond to a Get request, it's a <Result> markup
    instead of <Put>
    """
    conduit_name = subscription.getConduitModuleId()
    conduit = getConduitByName(conduit_name)
    xml = None
    #if the conduit support the SyncMLPut :
    if getattr(conduit, 'getCapabilitiesCTTypeList', None) is not None and \
       getattr(conduit, 'getCapabilitiesVerCTList', None) is not None and \
       getattr(conduit, 'getPreferedCapabilitieVerCT', None) is not None:
      xml = Element('{%s}%s' % (SYNCML_NAMESPACE, markup))
      xml.append(E.CmdID('%s' % cmd_id))
      if message_id:
        xml.append(E.MsgRef('%s' % message_id))
      if cmd_ref:
        xml.append(E.CmdRef('%s' % cmd_ref))
      xml.extend((E.Meta(E.Type('application/vnd.syncml-devinf+xml')),
                 E.Item(E.Source(E.LocURI('./devinf11')),
                 E.Data(E.DevInf(
                   E.VerDTD('1.1'),
                   E.Man('Nexedi'),
                   E.Mod('ERP5SyncML'),
                   E.OEM('Open Source'),
                   E.SwV('0.1'),
                   E.DevID(subscription.getSubscriptionUrlString()),
                   E.DevTyp('workstation'),
                   E.UTC(),
                   E.DataStore(E.SourceRef(subscription.getSourceReference()))
                   )
                 )
               )))
      data_store = xml.find('{%(ns)s}Item/{%(ns)s}Data/{%(ns)s}DevInf/{%(ns)s}DataStore' % {'ns': SYNCML_NAMESPACE})
      tx_element_list = []
      rx_element_list = []
      for type in conduit.getCapabilitiesCTTypeList():
        if type != 'text/xml':
          for x_version in conduit.getCapabilitiesVerCTList(type):
            rx_element_list.append(E.Rx(E.CTType(type), E.VerCT(x_version)))
            tx_element_list.append(E.Tx(E.CTType(type), E.VerCT(x_version)))
      rx_pref = Element('{%s}Rx-Pref' % SYNCML_NAMESPACE)
      rx_pref.extend((E.CTType(conduit.getPreferedCapabilitieCTType()),
                      E.VerCT(conduit.getPreferedCapabilitieVerCT())))
      data_store.append(rx_pref)
      data_store.extend(rx_element_list)
      tx_pref = Element('{%s}Tx-Pref' % SYNCML_NAMESPACE)
      tx_pref.extend((E.CTType(conduit.getPreferedCapabilitieCTType()),
                      E.VerCT(conduit.getPreferedCapabilitieVerCT())))
      data_store.append(tx_pref)
      data_store.extend(tx_element_list)
      data_store.append(E.SyncCap(
                          E.SyncType('2'),
                          E.SyncType('1'),
                          E.SyncType('4'),
                          E.SyncType('6')
                          ))
    return xml

  security.declarePrivate('getSyncMLData')
  def getSyncMLData(self, domain=None, remote_xml=None, cmd_id=0,
                    subscriber=None, xml_confirmation_list=None, conduit=None,
                    maximum_object_list_len=None, **kw):
    """
    This generate the syncml data message. This returns a string
    with all modification made locally (ie replace, add ,delete...)

    if object is not None, this usually means we want to set the
    actual xupdate on the signature.
    """
    # LOG('getSyncMLData starting...', INFO, "%s - %s" %(domain.getTitle(), domain.getPath()))
    if isinstance(conduit, str):
      conduit = getConduitByName(conduit)
    if xml_confirmation_list is None:
      xml_confirmation_list = []
    local_gid_list = []
    syncml_data_list = kw.get('syncml_data_list', [])
    result = {'finished': True}
    if isinstance(remote_xml, (str, unicode)):
      remote_xml = etree.XML(remote_xml, parser=parser)
    if domain.isOneWayFromServer() or subscriber.isOneWayFromClient():
      # Do not fill in object_path_list, client send nothing to server
      subscriber._edit(remaining_object_path_list=[])
    elif subscriber.getProperty('remaining_object_path_list') is None:
      object_list = domain.getObjectList()
      object_path_list = [x.getPath() for x in object_list]
      LOG("getSyncMLData", 300, "object path list got from %s is %s" %(domain, object_path_list))
      subscriber._edit(remaining_object_path_list=object_path_list)
      if conduit.getContentType() == 'text/vcard':
        # XXX This part should be handled by Conduit itself,
        # not by SynchronizationTool
        #here the method getGidFromObject don't return the good gid because
        #the conduit use the catalog to determine it and object are not yet
        #cataloged so if there is many times the same gid, we must count it
        gid_not_encoded_list = []
        for object in object_list:
          #LOG('getSyncMLData :', DEBUG, 'object:%s,  objectTitle:%s, local_gid_list:%s' % (object, object.getTitle(), local_gid_list))
          gid = b16decode(domain.getGidFromObject(object))
          if gid in gid_not_encoded_list:
            number = len([item for item in gid_not_encoded_list if item.startswith(gid)])
            if number:
              gid = '%s__%s' %  (gid, str(number+1))
          gid_not_encoded_list.append(gid)
          local_gid_list.append(b16encode(gid))
          #LOG('getSyncMLData :', DEBUG,'gid_not_encoded_list:%s, local_gid_list:%s, gid:%s' % (gid_not_encoded_list, local_gid_list, gid))
      else:
        local_gid_list = [domain.getGidFromObject(x) for x in object_list]
      # Objects to remove
      #LOG('getSyncMLData remove object to remove ...', DEBUG, '')
      for object_gid in subscriber.getGidList():
        if object_gid not in local_gid_list:
          # This is an object to remove
          signature = subscriber.getSignatureFromGid(object_gid)
          if signature.getValidationState() != 'partial':
            # If partial, then we have a signature but no local object
            rid = signature.getRid()
            syncml_data_list.append(self.deleteXMLObject(object_gid=object_gid,
                                                         rid=rid,
                                                         cmd_id=cmd_id))
            cmd_id += 1
            # Delete Signature if object does not exist anymore
            subscriber._delObject(object_gid)

    local_gid_list = []
    loop = 0
    for object_path in subscriber.getProperty('remaining_object_path_list'):
      if maximum_object_list_len is not None and\
                                               loop >= maximum_object_list_len:
        result['finished'] = False
        break
      #LOG('getSyncMLData object_path', INFO, object_path)
      object = self.getPortalObject().unrestrictedTraverse(object_path)
      gid = domain.getGidFromObject(object)
      if not gid:
        continue
      local_gid_list.append(gid)
      force = False
      #if ''.join(syncml_data_list).count('\n') < MAX_LINES and not \
          #object.getId().startswith('.'):
      if len(''.join(syncml_data_list)) < MAX_LEN:
        # If not we have to cut
        #LOG('getSyncMLData', INFO, 'object_path:%r' % (object_path,))
        #LOG('getSyncMLData', INFO, 'gid:%r' % (gid,))
        #LOG('getSyncMLData', INFO, 'xml_mapping:%r' %\
                                       #domain.getXmlBindingGeneratorMethodId())
        #LOG('getSyncMLData', INFO, 'code:%r' % getAlertCodeFromXML(remote_xml))
        #LOG('getSyncMLData', INFO, 'gid_list:%r' % local_gid_list)
        #LOG('getSyncMLData', INFO, 'subscriber.getGidList:%r' %\
                                                       #subscriber.getGidList())
        #LOG('getSyncMLData', INFO, 'hasSignature:%r' %\
                                           #subscriber.hasSignature(gid))
        #LOG('getSyncMLData', INFO, 'alert_code == slowsync:%r' %\
           #(getAlertCodeFromXML(remote_xml) == resolveSyncmlAlertCode(self,
                                                                 #'slow_sync')))
        signature = subscriber.getSignatureFromGid(gid)
        ## Here we first check if the object was modified or not by looking at dates
        #status = self.SENT
        more_data = False
        # For the case it was never synchronized, we have to send everything
        if signature is None or (not signature.hasData() and\
            signature.getValidationState() != 'partial') or\
            getAlertCodeFromXML(remote_xml) ==\
                                     resolveSyncmlAlertCode(self, 'slow_sync'):
          #LOG('getSyncMLData', DEBUG, 'Current object.getPath: %s' % object.getPath())
          xml_string = conduit.getXMLFromObjectWithId(object,
                                                      xml_mapping=\
                                       domain.getXmlBindingGeneratorMethodId(),
                                       context_document=subscriber.getPath())
          if signature is None:
            LOG("SynchronizationTool", 300, "creating a signature for gid = %s, path %s" %(gid, object.getPath()))
            signature = subscriber.newContent(portal_type='SyncML Signature',
                                              id=gid,
                                              reference=object.getPath(),
                                              temporary_data=xml_string)
          #if xml_string.count('\n') > MAX_LINES:
            #more_data = True
            #xml_string, rest_string = cutXML(xml_string)
            #signature.setPartialData(rest_string)
            #signature.setPartialAction(ADD_ACTION)
            #signature.changeToPartial()
          if xml_string and len(xml_string) > MAX_LEN:
            more_data = True
            xml_string, rest_string = cutXML(xml_string)
            signature.setPartialData(rest_string)
            signature.setPartialAction(ADD_ACTION)
            signature.changeToPartial()
          else:
            signature.setTemporaryData(xml_string)

          if xml_string:
            syncml_data_list.append(self.addXMLObject(cmd_id=cmd_id,
                                          object=object,
                                          gid=gid,
                                          xml_string=xml_string,
                                          more_data=more_data,
                                          media_type=conduit.getContentType()))
          cmd_id += 1
        elif signature.getValidationState() in ('not_synchronized',
                                                'synchronized',
                                               'conflict_resolved_with_merge'):
          # We don't have synchronized this object yet but it has a signature
          xml_object = conduit.getXMLFromObjectWithId(object,
                           xml_mapping=domain.getXmlBindingGeneratorMethodId(),
                           context_document=subscriber.getPath())
          #LOG('getSyncMLData', DEBUG, 'checkMD5: %s' % str(signature.checkMD5(xml_object)))
          #LOG('getSyncMLData', DEBUG, 'getStatus: %s' % str(signature.getStatus()))
          if signature.getValidationState() == 'conflict_resolved_with_merge':
            xml_confirmation_list.append(self.SyncMLConfirmation(
                                      cmd_id=cmd_id,
                                      source_ref=signature.getId(),
                                      sync_code='conflict_resolved_with_merge',
                                      cmd='Replace'))
          set_synchronized = True
          # LOG('signature.checkMD5(xml_object)', INFO, '%r' % signature.checkMD5(xml_object))
          if not signature.checkMD5(xml_object):
            #LOG("signature data is %r\n\nxml_object is %r\n\n\nXXXXXXXXXXXXX" %(signature.getData(), xml_object), 300, "")
            set_synchronized = False
            if conduit.getContentType() != 'text/xml':
              # If there is no xml, we re-send all the objects
              xml_string = xml_object
            else:
              # This object has changed on this side, we have to generate some xmldiff
              xml_object_with_gid = conduit.replaceIdFromXML(xml_object, 'gid',
                                                             gid)
              previous_xml_with_gid = conduit.replaceIdFromXML(
                                                           signature.getData(),
                                                           'gid', gid)
              xml_string = conduit.generateDiff(xml_object_with_gid,
                                                previous_xml_with_gid)
              #LOG('XMLSyncUtils diff:%s' % object.getPath(), INFO, xml_string)
              #if xml_string.count('\n') > MAX_LINES:
                ## This make comment fails, so we need to replace
                #more_data = True
                #xml_string, rest_string = cutXML(xml_string)
                #signature.setPartialData(rest_string)
                ##status = self.PARTIAL
                #signature.setPartialAction(REPLACE_ACTION)
                #signature.changeToPartial()
              if len(xml_string) > MAX_LEN:
                # This make comment fails, so we need to replace
                more_data = True
                xml_string, rest_string = cutXML(xml_string)
                signature.setPartialData(rest_string)
                #status = self.PARTIAL
                signature.setPartialAction(REPLACE_ACTION)
                if signature.getValidationState() != 'partial':
                  signature.changeToPartial()
            syncml_data_list.append(self.replaceXMLObject(
                                        cmd_id=cmd_id, object=object,
                                        gid=gid,
                                        xml_string=xml_string,
                                        more_data=more_data,
                                        media_type=conduit.getContentType()))
            cmd_id += 1
            signature.setTemporaryData(xml_object)
          # XXX getSyncMLData must not edit objects this is a read only
          # methods. The code below is probabbly disabled since
          # applyDiff is implemented on Signature
          # Now we can apply the xupdate from the subscriber
          subscriber_xupdate = signature.getSubscriberXupdate()
          #LOG('getSyncMLData subscriber_xupdate', INFO, subscriber_xupdate)
          if subscriber_xupdate is not None:
            # The modification in the xml from signature is compared and
            # updated with xml_xupdate from subscriber
            previous_xml_with_gid = conduit.replaceIdFromXML(
                                                           signature.getData(),
                                                           'gid', gid,
                                                           as_string=False)
            conduit.updateNode(xml=subscriber_xupdate, object=object,
                         previous_xml=previous_xml_with_gid,
                         force=(domain.getPortalType()=='SyncML Subscription'),
                         simulate=False,
                         signature=signature,
                         domain=domain)
            xml_object = conduit.getXMLFromObjectWithId(object,
                                                        xml_mapping=\
                                       domain.getXmlBindingGeneratorMethodId(),
                                       context_document=subscriber.getPath())
            signature.setTemporaryData(xml_object)
          if set_synchronized and\
                              signature.getValidationState() != 'synchronized':
            # We should not have this case when we are in CONFLICT_MERGE
            signature.synchronize()
        elif signature.getValidationState() ==\
                               'conflict_resolved_with_client_command_winning':
          # We have decided to apply the update
          # XXX previous_xml will be geXML instead of getTempXML because
          # some modification was already made and the update
          # may not apply correctly
          xml_update = signature.getPartialData()
          previous_xml_with_gid = conduit.replaceIdFromXML(signature.getData(),
                                                           'gid', gid,
                                                           as_string=False)
          conduit.updateNode(xml=xml_update, object=object,
                             previous_xml=previous_xml_with_gid, force=True,
                             gid=gid,
                             signature=signature,
                             domain=domain)
          xml_confirmation_list.append(self.SyncMLConfirmation(
                                  cmd_id=cmd_id,
                                  target_ref=gid,
                                  sync_code='conflict_resolved_with_client_command_winning',
                                  cmd='Replace'))
          signature.synchronize()
        elif signature.getValidationState() == 'partial':
          # Receive the chunk of partial xml
          if conduit.getContentType() != 'text/xml':
            xml_string = conduit.getXMLFromObjectWithId(object,
                                        xml_mapping=domain.getXmlBindingGeneratorMethodId(),
                                        context_document=subscriber.getPath())
          else:
            # Wrapp it into CDATA
            #xml_string = signature.getPartialData('')
            #if xml_string.count('\n') > MAX_LINES:
              #more_data = True
              #xml_string = signature.getFirstChunkPdata(MAX_LINES)
              #signature.changeToPartial()
            xml_string = signature.getPartialData('')
            if len(xml_string) > MAX_LEN:
              more_data = True
              xml_string = signature.getFirstPdataChunk(MAX_LEN)
              if signature.getValidationState() != 'partial':
                signature.changeToPartial()
            xml_string = etree.CDATA(xml_string.decode('utf-8'))
          #if signature.getValidationState() != 'partial':
            #signature.sent()
          if signature.getPartialAction() == REPLACE_ACTION:
            #rid = signature.getRid()
            # In first, we try with rid if there is one
            syncml_data_list.append(self.replaceXMLObject(
                                       cmd_id=cmd_id,
                                       object=object,
                                       gid=gid,
                                       #rid=rid,
                                       xml_string=xml_string,
                                       more_data=more_data,
                                       media_type=subscriber.getContentType()))
          elif signature.getPartialAction() == ADD_ACTION:
            #in fisrt, we try with rid if there is one
            syncml_data_list.append(self.addXMLObject(
                                        cmd_id=cmd_id,
                                        object=object,
                                        gid=gid,
                                        xml_string=xml_string,
                                        more_data=more_data,
                                        media_type=subscriber.getContentType()))
        if not more_data:
          subscriber.removeRemainingObjectPath(object_path)
      else:
        result['finished'] = True
        break
      loop += 1
    result['syncml_data_list'] = syncml_data_list
    result['xml_confirmation_list'] = xml_confirmation_list
    result['cmd_id'] = cmd_id
    return result

  security.declarePrivate('applyActionList')
  def applyActionList(self, domain=None, subscriber=None, cmd_id=0,
                      remote_xml=None, conduit=None, simulate=False):
    """
    This just look to a list of action to do, then id applies
    each action one by one, thanks to a conduit
    """
    xml_confirmation_list = []
    has_next_action = False
    gid_from_xml_list = []
    destination = domain.getSourceValue()
    # LOG('applyActionList args', INFO, 'domain : %s\n subscriber : %s\n cmd_id: %s'\
    #     % (domain.getPath(), subscriber.getPath(), cmd_id))
    #LOG('XMLSyncUtils applyActionList', DEBUG, self.getSyncActionList(remote_xml))
    for action in remote_xml.xpath('//syncml:Add|//syncml:Delete|'\
                              '//syncml:Replace', namespaces=remote_xml.nsmap):
      conflict_list = []
      status_code = 'success'
      # Thirst we have to check the kind of action it is

      # The rid is the Temporary GUID (SYNCML Protocol). the rid sent by the
      # client unlike gid. The rid is in MapItem for each Action Map it's the LocURI in
      # the action.
      gid = '%s' % action.xpath('string(.//syncml:Item/syncml:Source/'\
                                      'syncml:LocURI)',
                                      namespaces=action.nsmap)
      if not gid:
        gid = '%s' % action.xpath('string(.//syncml:Item/syncml:Target/'\
                                        'syncml:LocURI)',
                                        namespaces=action.nsmap)
      #The action delete hasn't need a gid and retrieve the gid of conduit for
      #object.
      if action.xpath('local-name()') != 'Delete':
        data_action = getDataSubNode(action)
        if conduit.getContentType() != 'text/xml':
          #data in unicode
          data_action = getDataText(action)
        if getattr(conduit, 'getGidFromXML', None) is not None:
          temp_gid = conduit.getGidFromXML(data_action, gid_from_xml_list)
          if temp_gid:
            gid_from_xml_list.append(temp_gid)
            gid = b16encode(temp_gid)
      #the rid unlike gid, it's the rid or gid (if rid == gid) will use for
      #retrieve object and send response to client
      signature = subscriber.getSignatureFromGid(gid)
      object = subscriber.getObjectFromGid(gid)
      LOG("gid is %s, found existing object = %s" %(gid, object), 300, "")
      object_id = domain.generateNewIdWithGenerator(object=destination, gid=gid)
      if signature is None:
        LOG("SynchronizationTool", 300, "creating a signature for gid = %s without ref" %(gid))
        signature = subscriber.newContent(portal_type='SyncML Signature',
                                          id=gid,
                                          content_type=conduit.getContentType()
                                         )
        if object is not None:
          LOG("SynchronizationTool", 300, "\tsetting ref %s" %(object.getPath()))
          signature.setReference(object.getPath())
      elif signature.getValidationState() == 'synchronized':
        signature.drift()
      force = signature.isForce()
      data_node = action.find('.//{%(ns)s}Item/{%(ns)s}Data'\
                                                    % {'ns': SYNCML_NAMESPACE})
      if data_node is not None:
        if len(data_node):
          data = etree.tostring(data_node[0])
        else:
          data = data_node.text or ''
      else:
        data = ''
      #LOG('applyActionList gid', 0, gid)
      #LOG('applyActionList data', 0, data)
      if not action.xpath('.//syncml:Item/syncml:MoreData',
                          namespaces=action.nsmap):
        # This is the last chunk of a partial xml
        # or this is just an entire data chunk
        data_subnode = None
        if signature.hasPartialData():
          # rebuild the entire data
          signature.appendPartialData(data)
          # fetch data as string
          data_subnode = signature.getPartialData()
          # clear partial data cache on Signature
          signature.setPartialData(None)
          #LOG('applyActionList', DEBUG, 'data_subnode: %s' % data_subnode)
          if conduit.getContentType() == 'text/xml':
            data_subnode = etree.XML(data_subnode, parser=parser)
        else:
          if conduit.getContentType() != 'text/xml':
            data_subnode = getDataText(action)
          else:
            data_subnode = getDataSubNode(action)
        if action.xpath('local-name()') == 'Add':
          # Then store the xml of this new subobject
          reset = False
          if object is None:
            add_data = conduit.addNode(xml=data_subnode,
                                       object=destination,
                                       object_id=object_id,
                                       signature=signature,
                                       domain=domain)
            conflict_list.extend(add_data['conflict_list'])
            # Retrieve directly the object from addNode
            object = add_data['object']
            if object is not None:
              signature.setReference(object.getPath())
          else:
            reset = True
            # Object was retrieved but need to be updated without recreated
            # usefull when an object is only deleted by workflow.
            if data_subnode is not None:
              actual_xml = conduit.getXMLFromObjectWithGid(object, gid,
                             xml_mapping=\
                             domain.getXmlBindingGeneratorMethodId(force=True),
                             context_document=subscriber.getPath())
              # use gid to compare because their ids can be different
              data_subnode = conduit.replaceIdFromXML(data_subnode, 'gid', gid)
              # produce xupdate
              data_subnode = conduit.generateDiff(data_subnode, actual_xml)
            conflict_list.extend(conduit.updateNode(
                                        xml=data_subnode,
                                        object=object,
                                        previous_xml=actual_xml,
                                        force=force,
                                        simulate=simulate,
                                        reset=reset,
                                        signature=signature,
                                        domain=domain))
            xml_object = conduit.getXMLFromObjectWithId(object,
                                       xml_mapping=\
                                       domain.getXmlBindingGeneratorMethodId(),
                                       context_document=subscriber.getPath())
            signature.setTemporaryData(xml_object)
          if object is not None:
            #LOG('applyActionList', DEBUG, 'addNode, found the object')
            if reset:
              #After a reset we want copy the LAST XML view on Signature.
              #this implementation is not sufficient, need to be improved.
              if not isinstance(xml_object, str):
                xml_object = etree.tostring(xml_object, encoding='utf-8',
                                            pretty_print=True)
            else: 
              xml_object = conduit.getXMLFromObjectWithId(object,
                                       xml_mapping=\
                                       domain.getXmlBindingGeneratorMethodId(),
                                       context_document=subscriber.getPath())
            #if signature.getValidationState() != 'synchronized':
            signature.synchronize()
            signature.setReference(object.getPath())
            signature.setData(xml_object)
            xml_confirmation_list.append(self.SyncMLConfirmation(
                                                        cmd_id=cmd_id,
                                                        cmd='Add',
                                                        sync_code='item_added',
                                                        remote_xml=action))
            cmd_id +=1
        elif action.xpath('local-name()') == 'Replace':
          #LOG('applyActionList', INFO, 'object: %s will be updated...' % str(object))
          if object is not None:
            #LOG('applyActionList', DEBUG, 'object: %s will be updated...' % object.id)
            signature = subscriber.getSignatureFromGid(gid)
            #LOG('applyActionList', DEBUG, 'previous signature: %s' % str(signature))
            previous_xml = signature.getData()
            if previous_xml:
              # can be None
              previous_xml = conduit.replaceIdFromXML(previous_xml, 'gid', gid)
            conflict_list += conduit.updateNode(xml=data_subnode,
                                                object=object,
                                                previous_xml=previous_xml,
                                                force=force,
                                                signature=signature,
                                                simulate=simulate,
                                                domain=domain)
            if previous_xml:
              # here compute patched data with given diff
              xml_object = conduit.applyDiff(previous_xml, data_subnode)
              xml_object = conduit.replaceIdFromXML(xml_object, 'id',
                                                    object.getId(),
                                                    as_string=True)
            elif conduit.getContentType() == 'text/xml':
              # no previous, this is the first synchronization
              # store xml view from object as it has been provided.
              xml_object = etree.tostring(data_subnode)
            else:
              xml_object = data_subnode
            signature.setTemporaryData(xml_object)
            if conflict_list:
              status_code = 'conflict'
              signature.changeToConflict()
              data_subnode_string = etree.tostring(data_subnode,
                                                   encoding='utf-8')
              signature.setPartialData(data_subnode_string)
            else: #if not simulate:
              signature.synchronize()
            xml_confirmation_list.append(self.SyncMLConfirmation(
                                                         cmd_id=cmd_id,
                                                         cmd='Replace',
                                                         sync_code=status_code,
                                                         remote_xml=action))
            cmd_id += 1
            if simulate:
              # This means we are on the publisher side and we want to store
              # the xupdate from the subscriber and we also want to generate
              # the current xupdate from the last synchronization
              if not isinstance(data_subnode, str):
                data_subnode = etree.tostring(data_subnode, encoding='utf-8')
              #LOG('applyActionList, subscriber_xupdate:', TRACE, data_subnode_string)
              signature.setSubscriberXupdate(data_subnode)

        elif action.xpath('local-name()') == 'Delete':
          #LOG("applyactionlist delete", INFO, "")
          object_id = signature.getId()
          #LOG('applyActionList Delete on : ', DEBUG, (signature.getId(), subscriber.getObjectFromGid(object_id)))
          if conduit.getContentType() != 'text/xml':
            data_subnode = getDataText(action)
          else:
            data_subnode = getDataSubNode(action)
          #LOG('applyActionList, object gid to delete :', INFO, subscriber.getObjectFromGid(object_id))
          document = subscriber.getObjectFromGid(object_id)
          if document is not None:
          #if the object exist:
            conduit.deleteNode(xml=data_subnode, object=destination,
                               object_id=document.getId(),
                               signature=signature,
                               domain=domain)
            subscriber._delObject(gid)
          xml_confirmation_list.append(self.SyncMLConfirmation(
                                                         cmd_id=cmd_id,
                                                         cmd='Delete',
                                                         sync_code=status_code,
                                                         remote_xml=action))
      else: # We want to retrieve more data
        if signature.getValidationState() != 'partial':
          signature.changeToPartial()
        signature.appendPartialData(data)
        #LOG('applyActionList', INFO, 'waiting more data for :%s' % signature.getId())
        #LOG('applyActionList', INFO, 'waiting more data for :%s' % object.getPath())
        #LOG('applyActionList', INFO, data)
        xml_confirmation_list.append(self.SyncMLConfirmation(
                                             cmd_id=cmd_id,
                                             cmd="%s" % action.xpath('name()'),
                                             sync_code=status_code,
                                             remote_xml=action))
      if conflict_list and signature is not None and\
                                  signature.getValidationState() != 'conflict':
        # We had a conflict
        signature.changeToConflict()

    return xml_confirmation_list, has_next_action, cmd_id

  security.declarePrivate('addXMLObject')
  def addXMLObject(self, **kw):
    """
      Add an object with the SyncML protocol
    """
    LOG("addXMLObject", INFO, "xml = %s" %(kw.get('xml_string', '')))
    return self._createAddOrReplaceNode('Add', **kw)

  security.declarePrivate('addXMLObject')
  def replaceXMLObject(self, **kw):
    """
      Replace an object with the SyncML protocol
    """
    LOG("replaceXMLObject", INFO, "xml = %s" %(kw.get('xml_string', '')))
    return self._createAddOrReplaceNode('Replace', **kw)

  def _createAddOrReplaceNode(self, id_tag, cmd_id=0, object=None,
                              xml_string=None, more_data=False, gid=None,
                              rid=None, media_type=None):
    """Mixin for addXMLObject() and replaceXMLObject()
    """
    data_node = E.Data()
    if media_type == 'text/xml':
      if isinstance(xml_string, str):
        data_node.append(etree.XML(xml_string, parser=parser))
      elif isinstance(xml_string, etree.CDATA):
        #xml_string could be Data element if partial XML
        data_node.text = xml_string
      else:
        data_node.append(xml_string)
    else:
      if isinstance(xml_string, etree.CDATA):
        data_node.text = xml_string
      else:
        cdata = etree.CDATA(xml_string.decode('utf-8'))
        data_node.text = cdata
    main_tag = Element('{%s}%s' % (SYNCML_NAMESPACE, id_tag))
    main_tag.append(E.CmdID('%s' % cmd_id))
    main_tag.append(E.Meta(E.Type(media_type)))
    main_tag.append(E.Item(E.Source(E.LocURI(gid)), data_node))
    if more_data:
      item_node = main_tag.find('{%s}Item' % SYNCML_NAMESPACE)
      item_node.append(E.MoreData())
    return etree.tostring(main_tag, encoding='utf-8', pretty_print=True)

  security.declarePrivate('deleteXMLObject')
  def deleteXMLObject(self, cmd_id=0, object_gid=None, rid=None):
    """
      Delete an object with the SyncML protocol
    """
    LOG("deleteXMLObject", INFO, "object_gid = %s" %(object_gid))
    if rid:
      elem_to_append = E.Target(E.LocURI('%s' % rid))
    else:
      elem_to_append = E.Source(E.LocURI('%s' % object_gid))
    xml = (E.Delete(
             E.CmdID('%s' % cmd_id),
             E.Item(
               elem_to_append
               )
             ))
    return etree.tostring(xml, encoding='utf-8', pretty_print=True)

  security.declarePrivate('SyncMLConfirmation')
  def SyncMLConfirmation(self, cmd_id=None, target_ref=None, cmd=None,
      sync_code=None, msg_ref=None, cmd_ref=None, source_ref=None,
      remote_xml=None):
    """
    This is used in order to confirm that an object was correctly
    synchronized
    """
    if remote_xml is not None:
      msg_id = '%s' % remote_xml.xpath('string(/syncml:SyncML/'\
                                        'syncml:SyncHdr/syncml:MsgID)',
                                        namespaces=remote_xml.nsmap)
      cmd_ref = '%s' % remote_xml.xpath('string(.//syncml:CmdID)',
                                        namespaces=remote_xml.nsmap)
      target_ref = '%s' % remote_xml.xpath('string(.//syncml:Target/'\
                                           'syncml:LocURI)',
                                           namespaces=remote_xml.nsmap)
      source_ref = '%s' % remote_xml.xpath('string(.//syncml:Source/'\
                                           'syncml:LocURI)',
                                           namespaces=remote_xml.nsmap)
    xml = E.Status()
    if cmd_id:
      xml.append(E.CmdID('%s' % cmd_id))
    if msg_ref:
      xml.append(E.MsgRef(msg_id))
    if cmd_ref:
      xml.append(E.CmdRef(cmd_ref))
    if cmd:
      xml.append(E.Cmd(cmd))
    if target_ref:
      xml.append(E.TargetRef(target_ref))
    if source_ref:
      xml.append(E.SourceRef(source_ref))
    if sync_code:
      xml.append(E.Data(resolveSyncmlStatusCode(self, sync_code)))
    return xml

  security.declarePrivate('sendSyncModif')
  def sendSyncModif(self, syncml_data_list, cmd_id_before_getsyncmldata,
                    subscriber, domain, xml_confirmation_list, remote_xml,
                    xml_tree, has_status_list, has_response):
    sync_body = xml_tree.find('SyncBody')
    if sync_body is None:
      sync_body = xml_tree.xpath('syncml:SyncBody',
                                 namespaces=xml_tree.nsmap)[0]
    if syncml_data_list:
      sync_node = E.Sync(E.CmdID('%s' % cmd_id_before_getsyncmldata))
      sync_body.append(sync_node)
      target_uri = subscriber.getDestinationReference()
      if target_uri:
        sync_node.append(E.Target(E.LocURI(target_uri)))
      source_uri = subscriber.getSourceReference()
      if source_uri:
        sync_node.append(E.Source(E.LocURI(source_uri)))
      for syncml_data in syncml_data_list:
        sync_node.append(etree.XML(syncml_data, parser=parser))
    for xml_confirmation in xml_confirmation_list:
      if isinstance(xml_confirmation, str):
        xml_confirmation = etree.XML(xml_confirmation, parser=parser)
      sync_body.append(xml_confirmation)

    sync_finished = False
    if domain.getPortalType() == 'SyncML Publication': # We always reply
      # When the publication receive the response Final and the modification 
      # data is finished so the publication send the tag "Final"
      if not remote_xml.xpath('string(/syncml:SyncML/syncml:SyncBody/'\
                              'syncml:Sync)', namespaces=remote_xml.nsmap)\
        and not xml_confirmation_list and not syncml_data_list\
        and checkFinal(remote_xml):
        sync_body.append(E.Final())
        sync_finished = True
      xml_string = etree.tostring(xml_tree, encoding='utf-8',
                                  pretty_print=True)
      subscriber.setLastSentMessage(xml_string)
      self.sendResponse(from_url=domain.getUrlString(),
                        to_url=subscriber.getSubscriptionUrlString(),
                        sync_id=subscriber.getDestinationReference(),
                        xml=xml_string,
                        domain=domain,
                        content_type=domain.getContentType())
      if sync_finished:
        LOG('this is the end of the synchronization session from PUB !!!',
            INFO, domain.getTitle())
        if subscriber.getAuthenticationState() == 'logged_in':
          subscriber.logout()
        if domain.getAuthenticationState() == 'logged_in':
          domain.logout()
        subscriber._edit(authenticated_user=None,
                         remaining_object_path_list=None)
      has_response = True
    elif domain.getPortalType() == 'SyncML Subscription':
      # the modification data is finished on the subscription so the tag
      # "Final" sent to the publication
      if not checkAlert(remote_xml) and not xml_confirmation_list\
                                                      and not syncml_data_list:
        sync_body.append(E.Final())
        sync_finished = True
      xml_string = etree.tostring(xml_tree, encoding='utf-8', pretty_print=True)
      if not sync_finished or not checkFinal(remote_xml):
        subscriber.setLastSentMessage(xml_string)
        self.sendResponse(
                  from_url=domain.getSubscriptionUrlString(),
                  to_url=domain.getUrlString(),
                  sync_id=domain.getDestinationReference(),
                  xml=xml_string, domain=domain,
                  content_type=domain.getContentType())
        has_response = True
      #When the receive the final element and the sub finished synchronization
      else:
        if domain.isOneWayFromServer() or subscriber.isOneWayFromClient():
          self.deleteRemainObjectList(domain, subscriber)
        has_response = False
        LOG('this is the end of the synchronization session from SUB !!!',
            INFO, domain.getTitle())
        if domain.getAuthenticationState() == 'logged_in':
          domain.logout()
        domain._edit(zope_user=None)
    return {'has_response': has_response, 'xml': xml_string}

  security.declareProtected(Permissions.ModifyPortalContent,
                            'deleteRemainObjectList')
  def deleteRemainObjectList(self, domain, subscriber):
    """
    This method allow deletion on not synchronized Objects at the end of Synchronization session.
    Usefull only after reseting in One Way Sync
    """
    object_list = domain.getObjectList()
    gid_list = [domain.getGidFromObject(x) for x in object_list]
    domain_path = domain.getPath()
    subscriber_path = subscriber.getPath()
    while len(gid_list):
      sliced_gid_list = [gid_list.pop() for i in gid_list[:MAX_OBJECTS]]
      #Split List Processing in activities
      self.activate(activity='SQLQueue',
                    tag=domain.getId(),
                    priority=ACTIVITY_PRIORITY)\
                                   .activateDeleteRemainObjectList(domain_path,
                                                               subscriber_path,
                                                               sliced_gid_list)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'activateDeleteRemainObjectList')
  def activateDeleteRemainObjectList(self, domain_path, subscriber_path, gid_list):
    """
    Execute Deletion in Activities
    """
    domain = self.unrestrictedTraverse(domain_path)
    subscriber = self.unrestrictedTraverse(subscriber_path)
    folder = domain.getSourceValue()
    conduit_name = subscriber.getConduitModuleId()
    conduit = getConduitByName(conduit_name)
    for gid in gid_list:
      if subscriber.getSignatureFromGid(gid) is None:
        object_id = b16decode(gid)
        conduit.deleteObject(object=folder, object_id=object_id)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'activateSyncModif')
  def activateSyncModif(self, **kw):
    domain = self.unrestrictedTraverse(kw['domain_relative_url'])
    subscriber = self.unrestrictedTraverse(kw['subscriber_relative_url'])
    conduit = subscriber.getConduitModuleId()
    result = self.getSyncMLData(domain=domain, subscriber=subscriber,
                                conduit=conduit,
                                maximum_object_list_len=MAX_OBJECTS, **kw)
    syncml_data_list = result['syncml_data_list']
    cmd_id = result['cmd_id']
    kw['syncml_data_list'] = syncml_data_list
    kw['cmd_id'] = cmd_id
    finished = result['finished']
    if not finished:
      domain.activate(activity='SQLQueue',
                      tag=domain.getId(),
                      priority=ACTIVITY_PRIORITY).activateSyncModif(**kw)
    else:
      cmd_id = result['cmd_id']
      cmd_id_before_getsyncmldata = kw['cmd_id_before_getsyncmldata']
      remote_xml = etree.XML(kw['remote_xml'], parser=parser)
      xml_tree = etree.XML(kw['xml_tree'], parser=parser)
      xml_confirmation_list = kw['xml_confirmation_list']
      has_status_list = kw['has_status_list']
      has_response = kw['has_response']
      return self.sendSyncModif(
                        syncml_data_list,
                        cmd_id_before_getsyncmldata,
                        subscriber,
                        domain,
                        xml_confirmation_list,
                        remote_xml,
                        xml_tree,
                        has_status_list,
                        has_response)

  security.declareProtected(Permissions.ModifyPortalContent, 'addNode')
  def addNode(self, conduit='ERP5Conduit', **kw):
    """
    """
    # Import the conduit and get it
    conduit_object = getConduitByName(conduit)
    return conduit_object.addNode(**kw)

InitializeClass( SynchronizationTool )
