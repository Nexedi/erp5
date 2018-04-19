import datetime
import json
import traceback
import time
import requests
from functools import wraps
from uritemplate import expand

import slapos.slap
from slapos.slap import SoftwareProductCollection
from requests.exceptions import HTTPError
from ..taskdistribution import SAFE_RPC_EXCEPTION_LIST
from . import logger

# max time to instance changing state: 3 hour
MAX_INSTANCE_TIME = 60*60*3

SOFTWARE_PRODUCT_NAMESPACE = "product."

SOFTWARE_STATE_UNKNOWN = "SOFTWARE_STATE_UNKNOWN"
SOFTWARE_STATE_INSTALLING = "SOFTWARE_STATE_INSTALLING"
SOFTWARE_STATE_INSTALLED = "SOFTWARE_STATE_INSTALLED"
SOFTWARE_STATE_DESTROYING = "SOFTWARE_STATE_DESTROYING"

INSTANCE_STATE_UNKNOWN = "INSTANCE_STATE_UNKNOWN"
INSTANCE_STATE_STARTING = "INSTANCE_STATE_STARTING"
INSTANCE_STATE_STARTED = "started"
INSTANCE_STATE_STARTED_WITH_ERROR = "INSTANCE_STATE_STARTED_WITH_ERROR"
INSTANCE_STATE_STOPPING = "INSTANCE_STATE_STOPPING"
INSTANCE_STATE_STOPPED = "stopped"
INSTANCE_STATE_DESTROYED = "destroyed"

TESTER_STATE_INITIAL = "TESTER_STATE_INITIAL"
TESTER_STATE_NOTHING = "TESTER_STATE_NOTHING"
TESTER_STATE_SOFTWARE_INSTALLED = "TESTER_STATE_SOFTWARE_INSTALLED"
TESTER_STATE_INSTANCE_INSTALLED = "TESTER_STATE_INSTANCE_INSTALLED"
TESTER_STATE_INSTANCE_STARTED = "TESTER_STATE_INSTANCE_STARTED"
TESTER_STATE_INSTANCE_UNINSTALLED = "TESTER_STATE_INSTANCE_UNINSTALLED"


# Simple decorator to prevent raise due small
# network failures.
def retryOnNetworkFailure(func,
    _except_list = SAFE_RPC_EXCEPTION_LIST + (
      HTTPError, slapos.slap.ConnectionError),
    ):
  def wrapper(*args, **kw):
    retry_time = 64
    while True:
      try:
        return func(*args, **kw)
      except _except_list:
        traceback.print_exc()

      print 'Network failure. Retry method %s in %i seconds' % (func, retry_time)
      time.sleep(retry_time)
      retry_time = min(retry_time*1.5, 640)

  return wraps(func)(wrapper)


class SlapOSMasterCommunicator(object):
  latest_state = None

  def __init__(self, slap, slap_supply, slap_order, url):
    self.slap = slap
    self.slap_order = slap_order
    self.slap_supply = slap_supply
    self.hateoas_navigator = self.slap._hateoas_navigator
    self.hosting_subscription_url = None

    if url is not None and \
      url.startswith(SOFTWARE_PRODUCT_NAMESPACE):

      product = SoftwareProductCollection(logger, self.slap)
      try:
        url = product.__getattr__(url[len(SOFTWARE_PRODUCT_NAMESPACE):])
      except AttributeError as e:
        logger.warning('Error on get software release: %s ', e.message)

    self.url = url  

  @retryOnNetworkFailure
  def _supply(self, state="available"):
    if self.computer_guid is None:
      logger.info('Nothing to supply for %s.', self.name)
      return None
    logger.info('Supply %s@%s', self.url, self.computer_guid)
    return self.slap_supply.supply(self.url, self.computer_guid, state)

  @retryOnNetworkFailure
  def _request(self, state, instance_title=None, request_kw=None, shared=False, software_type="RootSoftwareInstance"):
    if instance_title is not None:
      self.name = instance_title 
    if request_kw is not None:
      if isinstance(request_kw, basestring) or \
        isinstance(request_kw, unicode):
        self.request_kw = json.loads(request_kw)
      else:
        self.request_kw = request_kw
    if self.request_kw is None:
      self.request_kw = {}
    logger.info('Request %s@%s: %s', self.url, self.name, state)
    self.latest_state = state
    return self.slap_order.request(
            software_release=self.url,
            software_type=software_type,
            partition_reference=self.name,
            shared=shared,
            state=state,
            **self.request_kw)

  def isInstanceRequested(self, instance_title):
    hateoas = getattr(self.slap, '_hateoas_navigator', None)
    return instance_title in hateoas.getHostingSubscriptionDict()

  @retryOnNetworkFailure
  def _hateoas_getComputer(self, reference):
    root_document = self.hateoas_navigator.getRootDocument()
    search_url = root_document["_links"]['raw_search']['href']

    getter_link = expand(search_url, { 
      "query": "reference:%s AND portal_type:Computer" % reference, 
      "select_list": ["relative_url"],
      "limit": 1})

    result = self.hateoas_navigator.GET(getter_link)
    content_list = json.loads(result)['_embedded']['contents']

    if len(content_list) == 0:
      raise Exception('No Computer found.')

    computer_relative_url = content_list[0]["relative_url"]
    
    getter_url = self.hateoas_navigator.getDocumentAndHateoas(
      computer_relative_url)

    return json.loads(self.hateoas_navigator.GET(getter_url))
    
 
  @retryOnNetworkFailure
  def getSoftwareInstallationList(self, computer_guid=None):
    # XXX Move me to slap.py API
    computer = self._hateoas_getComputer(computer_guid) if computer_guid else self._hateoas_getComputer(self.computer_guid)

    # Not a list ?
    action = computer['_links']['action_object_slap']

    if action.get('title') == 'getHateoasSoftwareInstallationList':
      getter_link = action['href']
    else:
      raise Exception('No Link found found.')

    result = self.hateoas_navigator.GET(getter_link)
    return json.loads(result)['_links']['content']


  @retryOnNetworkFailure
  def getSoftwareInstallationNews(self, computer_guid=None):
    getter_link = None
    for si in self.getSoftwareInstallationList(computer_guid):
      if si["title"] == self.url:
        getter_link = si["href"]
        break

    # We could not find the document, so it is probably too soon.
    if getter_link is None:
      return ""
    
    result = self.hateoas_navigator.GET(getter_link)
    action_object_slap_list = json.loads(result)['_links']['action_object_slap']

    for action in action_object_slap_list:
      if action.get('title') == 'getHateoasNews':
        getter_link = action['href']
        break
    else:
      raise Exception('getHateoasNews not found.')

    result = self.hateoas_navigator.GET(getter_link)
    if len(json.loads(result)['news']) > 0:
      return json.loads(result)['news'][0]["text"]
    return ""

  @retryOnNetworkFailure
  def getInstanceUrlList(self):
    if self.hosting_subscription_url is None:
      hosting_subscription_dict = self.hateoas_navigator._hateoas_getHostingSubscriptionDict()
      for hs in hosting_subscription_dict:
        if hs['title'] == self.name:
          self.hosting_subscription_url = hs['href'] 
          break 

    if self.hosting_subscription_url is None:
      return None

    return self.hateoas_navigator.getHateoasInstanceList(
            self.hosting_subscription_url)

  @retryOnNetworkFailure
  def getNewsFromInstance(self, url):
    result = self.hateoas_navigator.GET(url)
    result = json.loads(result)
    if result['_links'].get('action_object_slap', None) is None:
      return None

    object_link = self.hateoas_navigator.hateoasGetLinkFromLinks(
       result['_links']['action_object_slap'], 'getHateoasNews')
    
    result = self.hateoas_navigator.GET(object_link)
    return json.loads(result)['news']

  @retryOnNetworkFailure
  def getInformationFromInstance(self, url):
    result = self.hateoas_navigator.GET(url)
    result = json.loads(result)
    if result['_links'].get('action_object_slap', None) is None:
      print result['links']
      return None

    object_link = self.hateoas_navigator.hateoasGetLinkFromLinks(
       result['_links']['action_object_slap'], 'getHateoasInformation')

    result = self.hateoas_navigator.GET(object_link)
    return json.loads(result)

  def _getSoftwareState(self, computer_guid=None):
    if self.computer_guid is None:
      return SOFTWARE_STATE_INSTALLED

    message = self.getSoftwareInstallationNews(computer_guid)
    logger.info(message)
    if message.startswith("#error no data found"):
      return SOFTWARE_STATE_UNKNOWN

    if message.startswith('#access software release'):
      return SOFTWARE_STATE_INSTALLED

    if message.startswith('#error'):
      return SOFTWARE_STATE_INSTALLING

    return SOFTWARE_STATE_UNKNOWN

  @retryOnNetworkFailure
  def getRSSEntryFromMonitoring(self, base_url):
    if base_url is None:
      return {}

    feed_url = base_url + '/monitor-public/rssfeed.html'
    d = feedparser.parse(feed_url)

    if len(d.entries) > 0:
      return {"date": d.entries[0].published,
              "message": d.entries[0].description,
              "title" : d.entries[0].title}
    return {}

  @retryOnNetworkFailure
  def _getInstanceState(self):
    latest_state = self.latest_state
    logger.info('latest_state = %r', latest_state)

    if latest_state is None:
      return INSTANCE_STATE_UNKNOWN

    message_list = []
    try:
      for instance in self.getInstanceUrlList():
        news = self.getNewsFromInstance(instance["href"])
        information = self.getInformationFromInstance(instance["href"])
        state = INSTANCE_STATE_UNKNOWN
        monitor_information_dict = {}

        info_created_at = "-1"
        is_slave = information['slave']
        if is_slave:
          if (information["connection_dict"]) > 0:
            state =  INSTANCE_STATE_STARTED
        else:
          # not slave
          instance_state = news[0]
          if instance_state.get('created_at', '-1') != "-1":
            # the following does NOT take TZ into account
            created_at = datetime.datetime.strptime(instance_state['created_at'], 
              '%a, %d %b %Y %H:%M:%S %Z')
            gmt_now = datetime.datetime(*time.gmtime()[:6])

            info_created_at = '%s (%d)' % (
               instance_state['created_at'], (gmt_now - created_at).seconds)

            if instance_state['text'].startswith('#access'):
              state =  INSTANCE_STATE_STARTED

            if instance_state['text'].startswith('#access Instance correctly stopped'):
              state =  INSTANCE_STATE_STOPPED

            if instance_state['text'].startswith('#destroy'):
              state = INSTANCE_STATE_DESTROYED

            if instance_state['text'].startswith('#error'):
              state = INSTANCE_STATE_STARTED_WITH_ERROR

        if state == INSTANCE_STATE_STARTED_WITH_ERROR:
          # search for monitor url
          monitor_v6_url = information["connection_dict"].get("monitor_v6_url")
          try:
            monitor_information_dict = self.getRSSEntryFromMonitoring(monitor_v6_url)
          except Exception:
            logger.exception('Unable to download promises for: %s', instance["title"])
            logger.error(traceback.format_exc())
            monitor_information_dict = {"message": "Unable to download"}

        message_list.append({
          'title': instance["title"],
          'slave': is_slave,
          'news': news[0],
          'information': information,
          'monitor': monitor_information_dict,
          'state': state
        })

    except slapos.slap.ServerError:
      logger.error('Got an error requesting partition for its state')
      return INSTANCE_STATE_UNKNOWN
    except Exception:
      logger.error("ERROR getting instance state")
      return INSTANCE_STATE_UNKNOWN

    started = 0
    stopped = 0
    self.message_history.append(message_list)
    for instance in message_list:
      if not instance['slave'] and \
        instance['state'] in (INSTANCE_STATE_UNKNOWN, INSTANCE_STATE_STARTED_WITH_ERROR):
        return instance['state']
      elif not instance['slave'] and instance['state'] == INSTANCE_STATE_STARTED:
        started = 1
      elif not instance['slave'] and instance['state'] == INSTANCE_STATE_STOPPED:
        stopped = 1

      if instance['slave'] and instance['state'] == INSTANCE_STATE_UNKNOWN:
        return instance['state']

    if started and stopped:
      return INSTANCE_STATE_STOPPED
      return INSTANCE_STATE_UNKNOWN

    if started:
      return INSTANCE_STATE_STARTED

    if stopped:
      return INSTANCE_STATE_STOPPED

  @retryOnNetworkFailure
  def _waitInstance(self, instance_title, state, max_time=MAX_INSTANCE_TIME):
    """
    Wait for 'max_time' an instance specific state
    """
    logger.info("Waiting for instance state: %s", state)
    start_time = time.time()
    while (not self._getInstanceState() == state
           and (max_time > (time.time()-start_time))):
      logger.info("Instance(s) not in %s state yet.", state)
      logger.info("Current state: %s", self._getInstanceState())
      time.sleep(15)
    if (time.time()-start_time) > max_time:
      error_message = "Instance '%s' not '%s' after %s seconds" %(instance_title, state, str(time.time()-start_time))
      return {'error_message' : error_message}
    logger.info("Instance correctly '%s' after %s seconds.", state, time.time() - start_time)
    return {'error_message' : None}

class SlapOSTester(SlapOSMasterCommunicator):

  def __init__(self,
              name,
              slap,
              slap_order,
              slap_supply,
              url, # software release url
              computer_guid=None, # computer for supply if desired
              request_kw=None
          ):
    super(SlapOSTester, self).__init__(
      slap, slap_supply, slap_order, url)

    self.name = name
    self.computer_guid = computer_guid

    if isinstance(request_kw, str) or \
      isinstance(request_kw, unicode):
      self.request_kw = json.loads(request_kw)
    else:
      self.request_kw = request_kw
    self.message_history = []

  def getInfo(self):
    info = ""
    info += "Software Release URL: %s\n" % (self.url)
    if self.computer_guid is not None:
      info += "Supply requested on: %s\n" % (self.computer_guid)
    info += "Instance Requested (Parameters): %s\n" % self.request_kw
    return info

  def supply(self, software_path=None, computer_guid=None, state="available"):
    if software_path is not None:
      self.url = software_path
    if computer_guid is not None:
      self.computer_guid = computer_guid
    self._supply(state)

  def requestInstanceStart(self, instance_title=None, request_kw=None, shared=False, software_type="RootSoftwareInstance"):
    self.instance = self._request(INSTANCE_STATE_STARTED, instance_title, request_kw, shared, software_type)

  def requestInstanceStop(self, instance_title=None, request_kw=None, shared=False, software_type="RootSoftwareInstance"):
    self._request(INSTANCE_STATE_STOPPED, instance_title, request_kw, shared, software_type)

  def requestInstanceDestroy(self, instance_title=None, request_kw=None, shared=False):
    if not instance_title:
      instance_title = self.name
    self.destroyInstance(instance_title)

  def waitInstanceStarted(self, instance_title):
    error_message = self._waitInstance(instance_title, INSTANCE_STATE_STARTED)["error_message"]
    if error_message is not None:
      logger.error(error_message)
      logger.error("Instance '%s' will be stopped and test aborted.", instance_title)
      self.requestInstanceStop()
      time.sleep(60)
      raise ValueError(error_message)

  def waitInstanceStopped(self, instance_title):
    error_message = self._waitInstance(instance_title, INSTANCE_STATE_STOPPED)["error_message"]
    if error_message is not None:
      logger.error(error_message)
      raise ValueError(error_message)

  def waitInstanceDestroyed(self, instance_title):
    error_message = self._waitInstance(instance_title, INSTANCE_STATE_DESTROYED)["error_message"]
    if error_message is not None:
      logger.error(error_message)
      raise ValueError(error_message)

  def getMasterFrontendDict(self):
    def getInstanceGuid():
      try:
        return self.instance.getInstanceGuid()
      except:
        return None
    frontend_master_ipv6 = None
    instance_guid = None
    for instance in self.getInstanceUrlList():
      if instance["title"] == "Monitor Frontend apache-frontend-1":
        try:
          information = self.getInformationFromInstance(instance["href"])
          frontend_master_ipv6 = information['parameter_dict']['url']
        except Exception as e:
          pass
    start_time = time.time()
    while not getInstanceGuid() and time.time()-start_time < 60*5:
      sleep(60)
    return {'instance_guid' : getInstanceGuid(), 'frontend_master_ipv6' : frontend_master_ipv6}

  # XXX TODO
  # In the future, this should allow customization so each project to be tested parses its own information,
  # probably in the test suite definition class
  def getInstanceUrlDict(self):
    frontend_url_list = []
    for instance in self.getInstanceUrlList():
      information = self.getInformationFromInstance(instance["href"])
      if "frontend-" in instance["title"]:
        try:
          # TODO: this should get "secure_access" value (https). Until having a
          # valid certificate, the "site_url" (http) will be used.
          frontend = [instance["title"].replace("frontend-", ""),
                      information["connection_dict"]["site_url"]]
          frontend_url_list.append(frontend)
        except Exception as e:
          logger.info("Frontend url not generated yet for instance: " + instance["title"])
          pass
      if instance["title"] == self.name:
        try:
          connection_json = json.loads(information["connection_dict"]["_"])
          user = connection_json["inituser-login"]
          password = connection_json["inituser-password"]
        except Exception as e:
          raise ValueError("user and password not found in connection parameters. Error while instantiating?")
    return {'user' : user, 'password' : password, 'frontend-url-list' : frontend_url_list }

  def destroyInstance(self, instance_title):
    self.name = instance_title
    if self.getInstanceUrlList():
      for instance in self.getInstanceUrlList():
        if instance["title"] != instance_title:
          self._request(INSTANCE_STATE_DESTROYED, instance["title"])
        else:
          root_instance = instance
      logger.info("Going to destroy root partition: " + str(instance_title))
      self._request(INSTANCE_STATE_DESTROYED, root_instance["title"])
    else:
      logger.info("Instance not found")

class SoftwareReleaseTester(SlapOSTester):
  deadline = None

  def __init__(self,
              name,
              slap,
              slap_order,
              slap_supply,
              url, # software release url
              computer_guid=None, # computer for supply if desired
              request_kw=None,
              software_timeout=3600,
              instance_timeout=3600,
          ):
    super(SoftwareReleaseTester, self).__init__(
      name, slap, slap_order, slap_supply, url, computer_guid, request_kw)

    self.state = TESTER_STATE_INITIAL
    self.transition_dict = {
      # step function
      # delay
      # next_state
      # software_state
      # instance_state
      TESTER_STATE_INITIAL: (
        lambda t: None,
        None,
        TESTER_STATE_NOTHING,
        None,
        None,
      ),
      TESTER_STATE_NOTHING: (
        lambda t: t._supply("available"),
        int(software_timeout),
        request_kw is None and TESTER_STATE_INSTANCE_UNINSTALLED or \
            TESTER_STATE_SOFTWARE_INSTALLED,
        SOFTWARE_STATE_INSTALLED,
        None,
      ),
      TESTER_STATE_SOFTWARE_INSTALLED: (
        lambda t: t._request(INSTANCE_STATE_STARTED),
        int(instance_timeout),
        TESTER_STATE_INSTANCE_STARTED,
        None,
        INSTANCE_STATE_STARTED,
      ),
      TESTER_STATE_INSTANCE_STARTED: (
        lambda t: t._request(INSTANCE_STATE_DESTROYED),
        int(1200),
        TESTER_STATE_INSTANCE_UNINSTALLED,
        None,
        INSTANCE_STATE_STOPPED,
      ),
      TESTER_STATE_INSTANCE_UNINSTALLED: (
        lambda t: t._supply(INSTANCE_STATE_DESTROYED),
        int(1200),
        None,
        None,
        None,
      ),
     }

  def __repr__(self):
      deadline = self.deadline
      if deadline is not None:
          deadline -= time.time()
          deadline = '+%is' % (deadline, )
      return '<%s(state=%s, deadline=%s) at %x>' % (
          self.__class__.__name__, self.state, deadline, id(self))

  def getFormatedLastMessage(self):
    if len(self.message_history) == 0:
      return "No message"

    summary = "Summary about the test. Instance List and Status:\n"
    message = "Last information about the tester:\n"
    if self.message_history[-1] is not None:
      message_list = self.message_history[-1]
      for entry in message_list:
        summary += "%s %s -> %s\n" % (
          entry['title'], entry["slave"] and "(slave)" or "", entry['state'])
        for prop in entry:
          if prop != "information":
            message += "%s = %s\n" % (prop, json.dumps(entry[prop], indent=2))
          
        message += "=== connection_dict === \n%s\n" % (
          json.dumps(entry["information"]["connection_dict"], indent=2))
        message += "\n"
        message += "=== parameter_dict === \n%s\n" % (
          json.dumps(entry["information"]["parameter_dict"], indent=2))
        message += "\n"
      message += "="*79
      message += "\n\n\n"
 
    return summary + message

  @retryOnNetworkFailure
  def teardown(self):
    """
    Interrupt a running test sequence, putting it in idle state.
    """
    logger.info('Invoking TearDown for %s@%s', self.url, self.name)
    if self.request_kw is not None:
       self._request(INSTANCE_STATE_DESTROYED)
    if self.computer_guid is not None:
      self._supply(INSTANCE_STATE_DESTROYED)
    self.state = TESTER_STATE_INSTANCE_UNINSTALLED

  def tic(self, now):
    """
    Check for missed deadlines (-> test failure), conditions for moving to
    next state, and actually moving to next state (executing its payload).
    """
    logger.debug('TIC')
    deadline = self.deadline

    if deadline < now and deadline is not None:
      raise TestTimeout(self.state)

    _, _, next_state, software_state, instance_state = self.transition_dict[
        self.state]

    if (software_state is None or
          software_state == self._getSoftwareState()) and (
          instance_state is None or
          instance_state == self._getInstanceState()):

      logger.debug('Going to state %s (%r)', next_state, instance_state)
      if next_state is None:
        return None

      self.state = next_state
      stepfunc, delay, _, _, _ = self.transition_dict[next_state]
      self.deadline = now + delay
      stepfunc(self)
    return self.deadline
