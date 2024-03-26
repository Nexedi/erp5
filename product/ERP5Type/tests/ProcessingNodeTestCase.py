# -*- coding: utf-8 -*-
import abc
import errno, logging, mock, os, socket, time
import itertools
from threading import Thread
import six
if six.PY2:
  from UserDict import IterableUserDict as UserDict
else:
  from collections import UserDict
import transaction
from Testing import ZopeTestCase
from zope.globalrequest import setRequest
from ZODB.POSException import ConflictError
from zLOG import LOG, ERROR
from Products.CMFActivity.Activity.Queue import VALIDATION_ERROR_DELAY
import App.config
from ExtensionClass import pmc_init_of
from Products.ERP5Type.tests.utils import \
  addUserToDeveloperRole, DummyMailHostMixin, parseListeningAddress
from Products.CMFActivity.ActivityTool import getCurrentNode


class DictPersistentWrapperMetaClass(abc.ABCMeta):
  def __new__(cls, name, base, d):
    def wrap(attr):
      wrapped = getattr(base[0], attr)
      def wrapper(self, *args, **kw):
        self._persistent_object._p_changed = 1
        return wrapped(self, *args, **kw)
      wrapper.__name__ = attr
      return wrapper
    for attr in ('clear', 'setdefault', 'update', '__setitem__', '__delitem__'):
      d[attr] = wrap(attr)
    return super(
      DictPersistentWrapperMetaClass, cls).__new__(cls, name, base, d)


@six.add_metaclass(DictPersistentWrapperMetaClass)
class DictPersistentWrapper(UserDict, object):

  def __init__(self, dict, persistent_object):
    self.data = dict
    self._persistent_object = persistent_object


def patchActivityTool():
  """Redefine several methods of ActivityTool for unit tests
  """
  from Products.CMFActivity.ActivityTool import ActivityTool
  def patch(function):
    name = function.__name__
    orig_function = getattr(ActivityTool, name)
    setattr(ActivityTool, '_orig_' + name, orig_function)
    setattr(ActivityTool, name, function)
    function.__doc__ = orig_function.__doc__
    # make life easier when inspecting the wrapper with ipython
    function._original = orig_function

  # When a ZServer can't be started, the node name ends with ':' (no port).
  @patch
  def _isValidNodeName(self, node_name):
    return True

  # Divert location to register processing and distributing nodes.
  # Load balancing is configured at the root instead of the activity tool,
  # so that additional can register even if there is no portal set up yet.
  # Properties at the root are:
  # - 'test_processing_nodes' to list processing nodes
  # - 'test_distributing_node' to select the distributing node
  @patch
  def getNodeDict(self):
    app = self.getPhysicalRoot()
    if getattr(app, 'test_processing_nodes', None) is None:
      app.test_processing_nodes = {}
    return DictPersistentWrapper(app.test_processing_nodes, app)

  @patch
  def getDistributingNode(self):
    return getattr(self.getPhysicalRoot(), 'test_distributing_node', '')

  # A property to catch setattr on 'distributingNode' would not work
  # because self would lose all acquisition wrappers.
  class SetDistributingNodeProxy(object):
    def __init__(self, ob):
      self._ob = ob
    def __getattr__(self, attr):
      m = getattr(self._ob, attr).__func__
      return lambda *args, **kw: m(self, *args, **kw)
  @patch
  def manage_setDistributingNode(self, distributingNode, REQUEST=None):
    proxy = SetDistributingNodeProxy(self)
    proxy._orig_manage_setDistributingNode(distributingNode, REQUEST=REQUEST)
    self.getPhysicalRoot().test_distributing_node = proxy.distributingNode

  # When there is more than 1 node, prevent the distributing node from
  # processing activities.
  @patch
  def tic(self, processing_node=1, force=0):
    processing_node_list = self.getProcessingNodeList()
    if len(processing_node_list) > 1 and \
       getCurrentNode() == self.getDistributingNode():
      # Sleep between each distribute.
      time.sleep(0.3)
      transaction.commit()
      transaction.begin()
    else:
      self._orig_tic(processing_node, force)


def Application_resolveConflict(self, old_state, saved_state, new_state):
  """Solve conflicts in case several nodes register at the same time
  """
  new_state = new_state.copy()

  test_distributing_node_set = {
      old_state.pop('test_distributing_node', ''),
      saved_state.pop('test_distributing_node', ''),
      new_state.pop('test_distributing_node', '')}
  test_distributing_node_set.discard('')
  new_state['test_distributing_node'] = ''
  if test_distributing_node_set:
    if len(test_distributing_node_set) != 1:
      raise ConflictError
    new_state['test_distributing_node'] = test_distributing_node_set.pop()

  old, saved, new = [set(state.pop('test_processing_nodes', {}).items())
                     for state in (old_state, saved_state, new_state)]
  # The value of these attributes don't have proper __eq__ implementation.
  for attr in '__before_traverse__', '__before_publishing_traverse__':
    del old_state[attr], saved_state[attr]
  if sorted(old_state.items()) != sorted(saved_state.items()):
    raise ConflictError
  new |= saved - old
  new -= old - saved
  new_state['test_processing_nodes'] = nodes = dict(new)
  if len(nodes) != len(new):
    raise ConflictError
  return new_state

from OFS.Application import Application
Application._p_resolveConflict = Application_resolveConflict


class ProcessingNodeTestCase(ZopeTestCase.TestCase):
  """Minimal ERP5 TestCase class to process activities

  When a processing node starts, the portal may not exist yet, or its name is
  unknown, so an additional 'test_portal_name' property at the root is set by
  the node running the unit tests to tell other nodes on which portal activities
  should be processed.
  """
  _server_address = None # (host, port) of the http server if it was started, None otherwise

  @staticmethod
  def startHTTPServer(verbose=False):
    """Start HTTP Server in background"""
    if ProcessingNodeTestCase._server_address is None:
      from Products.ERP5Type.tests.runUnitTest import log_directory
      log = os.path.join(log_directory, "Z2.log")
      message = "Running %s server at %s:%s\n"
      if True:
        from Products.ERP5.bin.zopewsgi import app_wrapper, createServer
        sockets = []
        server_type = 'HTTP'
        zserver = os.environ.get('zserver')
        try:
          for ip, port in parseListeningAddress(zserver):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
              s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
              s.bind((ip, port))
              s.listen(0)
            except socket.error as e:
              s.close()
              if e.args[0] != errno.EADDRINUSE:
                raise
              if zserver:
                raise RuntimeError(str(e))
            else:
              if sockets:
                webdav_ports = port,
              else:
                webdav_ports = ()
              sockets.append(s)
              if verbose:
                ZopeTestCase._print(message % (server_type, ip, port))
              if webdav_ports:
                break
              server_type = 'WebDAV'
        except RuntimeError as e:
          ZopeTestCase._print('Could not start %s server: %s\n'
            % (server_type, e))
        if sockets:
          logger = logging.getLogger("access")
          logger.addHandler(logging.FileHandler(log))
          logger.propagate = False
          hs = createServer(
            app_wrapper(
              large_file_threshold=10<<20,
              webdav_ports=webdav_ports),
            logger,
            sockets=sockets)
          ProcessingNodeTestCase._server = hs
          ProcessingNodeTestCase._server_address = hs.addr
          ProcessingNodeTestCase._server_thread = t = Thread(
            target=hs.run,
            name='ProcessingNodeTestCase.startHTTPServer')
          t.setDaemon(1)
          t.start()
      from Products.CMFActivity import ActivityTool
      # Reset, in case that getServerAddress was already called,
      # in which case, the value was ('', '')
      if ActivityTool._server_address:
        if ActivityTool.currentNode == ActivityTool._server_address:
          ActivityTool.currentNode = None
        ActivityTool._server_address = None
    return ProcessingNodeTestCase._server_address
  startZServer = startHTTPServer # BBB

  @staticmethod
  def stopHTTPServer():
    if ProcessingNodeTestCase._server_address is not None:
      ProcessingNodeTestCase._server_address = None
      ProcessingNodeTestCase._server.close()
      ProcessingNodeTestCase._server_thread.join(5)

  def _registerNode(self, distributing, processing):
    """Register node to process and/or distribute activities"""
    try:
      activity_tool = self.portal.portal_activities
    except AttributeError:
      from Products.CMFActivity.ActivityTool import ActivityTool
      activity_tool = ActivityTool().__of__(self.app)
    currentNode = getCurrentNode()
    if distributing:
      activity_tool.manage_setDistributingNode(currentNode)
    elif currentNode == activity_tool.getDistributingNode():
      activity_tool.manage_setDistributingNode('')
    if processing:
      activity_tool.manage_addToProcessingList((currentNode,))
    else:
      activity_tool.manage_delNode((currentNode,))

  @classmethod
  def unregisterNode(cls):
    if cls._server_address is not None:
      self = cls('unregisterNode')
      self.app = self._app()
      self._registerNode(distributing=0, processing=0)
      transaction.commit()
      self._close()

  def assertNoPendingMessage(self):
    """Get the last error message from error_log"""
    message_list = self.portal.portal_activities.getMessageList()
    if message_list:
      error_message = 'These messages are pending: %r' % [
          ('/'.join(m.object_path), m.method_id, m.processing_node, m.retry)
          for m in message_list]
      error_log = self.portal.error_log._getLog()
      if len(error_log):
        error_message += '\nLast error message:' \
                         '\n%(type)s\n%(value)s\n%(tb_text)s' \
                         % error_log[-1]
      self.fail(error_message)

  def abort(self):
    transaction.begin()
    # Consider reaccessing the portal to trigger a call to ERP5Site.__of__

  def commit(self):
    transaction.commit()
    self.abort()

  def tic(self, verbose=0, stop_condition=lambda message_list: False, delay=30*60):
    """Execute pending activities.

    This method executes activities until all messages are executed successfully,
    or at least execution of one message was marked as failed, in this case a
    RuntimeError exception will be raised.

    `stop_condition` can be a function that will be called between each iteration
    with the list of pending messages and return True to stop execution, or False
    to continue.

    If the total time spent processing activities exceeded `delay` seconds (default
    30 minutes), then the processing is interrupted and `tic` raise a RuntimeError
    exception.
    """
    transaction.commit()
    # Some tests like testDeferredStyle require that we use self.getPortal()
    # instead of self.portal in order to setup current skin.
    portal_activities = self.getPortal().portal_activities
    if 1:
      if verbose:
        ZopeTestCase._print('Executing pending activities ...')
        old_message_count = 0
      start = time.time()
      deadline = start + delay # This prevents an infinite loop.
      getMessageList = portal_activities.getMessageList
      message_list = getMessageList()
      message_count = len(message_list)
      for call_count in itertools.count():
        if not message_count or stop_condition(message_list):
          break
        if verbose and old_message_count != message_count:
          ZopeTestCase._print(' %i' % message_count)
          old_message_count = message_count
        portal_activities.process_timer(None, None)
        message_list = getMessageList()
        message_count = len(message_list)
        if time.time() >= deadline or message_count and any(x.processing_node == -2
                                              for x in message_list):
          # We're about to raise RuntimeError, but maybe we've reached
          # the stop condition, so check just once more:
          if stop_condition(message_list):
            break
          error_message = 'tic is looping forever. '
          try:
            self.assertNoPendingMessage()
          except AssertionError as e:
            error_message += str(e)
          raise RuntimeError(error_message)
        # This give some time between messages
        if call_count % 10 == 0:
          portal_activities.timeShift(3 * VALIDATION_ERROR_DELAY)
      if verbose:
        ZopeTestCase._print(' done (%.3fs)\n' % (time.time() - start))
    self.abort()

  def getOtherZopeNodeList(self, node_count=2):
    """Wait for at least `node_count` (including the current node) to be
    registered on portal activities and return the list of their node ids.

    This aborts current transaction.
    """
    for i in range(60):
      node_list = list(self.portal.portal_activities.getProcessingNodeList())
      if len(node_list) >= node_count:
        node_list.remove(getCurrentNode())
        return node_list
      self.abort()
      time.sleep(i * 0.1)
    self.fail(
        "No other activity node registered, make sure you are using"
        " --activity_node=%s command line flag" % node_count)

  def afterSetUp(self):
    """Initialize a node that will only process activities"""
    self.startHTTPServer()
    # Make sure to still have possibilities to edit components
    addUserToDeveloperRole('ERP5TypeTestCase')
    from Zope2.custom_zodb import cluster
    self._registerNode(distributing=not cluster, processing=1)
    self.commit()

  def _setUpDummyMailHost(self):
    """Replace Original Mail Host by Dummy Mail Host in a non-persistent way
    """
    cls = self.portal.MailHost.__class__
    if not issubclass(cls, DummyMailHostMixin):
      cls.__bases__ = (DummyMailHostMixin,) + cls.__bases__
      pmc_init_of(cls)

  def _restoreMailHost(self):
    """Restore original Mail Host
    """
    if self.portal is not None:
      cls = self.portal.MailHost.__class__
      if cls.__bases__[0] is DummyMailHostMixin:
        cls.__bases__ = cls.__bases__[1:]
        pmc_init_of(cls)

  def processing_node(self):
    """Main loop for nodes that process activities"""
    setRequest(self.app.REQUEST)
    try:
      while True:
        time.sleep(.3)
        transaction.begin()
        try:
          portal = self.portal = self.app[self.app.test_portal_name]
        except (AttributeError, KeyError):
          continue
        self._setUpDummyMailHost()
        if portal.portal_activities.isSubscribed():
          try:
            portal.portal_activities.process_timer(None, None)
          except Exception:
            LOG('Invoking Activity Tool', ERROR, '', error=True)
    except KeyboardInterrupt:
      pass

  def timerserver(self):
    """Main loop using timer server.
    """
    import Products.TimerService

    # AlarmTool uses alarmNode='' as a way to bootstrap an alarm node, but
    # during these tests we don't want the first node to start executing
    # alarms directly, because this usually cause conflicts when other
    # nodes register.
    with mock.patch(
      'Products.ERP5.Tool.AlarmTool.AlarmTool.getAlarmNode',
      return_value='bootstrap_disabled_in_test'):

      timerserver_thread = None
      try:
        while True:
          time.sleep(.3)
          transaction.begin()
          try:
            self.portal = self.app[self.app.test_portal_name]
          except (AttributeError, KeyError):
            continue
          self._setUpDummyMailHost()
          if not timerserver_thread:
            timerserver_thread = Products.TimerService.timerserver.TimerServer.TimerServer(
              module='Zope2',
              interval=0.1,
            )
      except KeyboardInterrupt:
        pass
