import json
import os
import threading

# Per-user publish/subscribe relay, started as a background thread inside
# one designated Zope worker process (selected by instance parameters, see
# NOTIFICATION_RELAY_ENABLE in the process environment). Built entirely on
# gevent's own explicit API (WSGIServer, Queue) - gevent.monkey.patch_all()
# is never called, so nothing outside this thread's own gevent hub is
# affected; the rest of this Zope process keeps its normal OS-thread
# semantics, exactly like the existing NEO/ZEO client code already does.

_state = {'started': False}
_state_lock = threading.Lock()

_registry_lock = threading.Lock()
_registry = {}  # user_id -> list of gevent.queue.Queue

HEARTBEAT_SECONDS = 15


def _subscribe(user_id):
  from gevent.queue import Queue
  queue = Queue()
  with _registry_lock:
    _registry.setdefault(user_id, []).append(queue)
  return queue


def _unsubscribe(user_id, queue):
  with _registry_lock:
    waiter_list = _registry.get(user_id)
    if waiter_list and queue in waiter_list:
      waiter_list.remove(queue)
      if not waiter_list:
        del _registry[user_id]


def _publish(user_id, payload):
  with _registry_lock:
    waiter_list = list(_registry.get(user_id, ()))
  for queue in waiter_list:
    queue.put(payload)
  return len(waiter_list)


def _checkRelayKey(environ):
  expected = os.environ.get('NOTIFICATION_RELAY_KEY') or None
  if not expected:
    return True
  return environ.get('HTTP_X_RELAY_KEY') == expected


def _subscribeStream(user_id):
  from gevent.queue import Empty
  queue = _subscribe(user_id)
  try:
    while True:
      try:
        payload = queue.get(timeout=HEARTBEAT_SECONDS)
      except Empty:
        yield b': heartbeat\n\n'
      else:
        yield ('data: %s\n\n' % json.dumps(payload)).encode('utf-8')
  finally:
    _unsubscribe(user_id, queue)


def _handlePublish(environ, start_response, user_id):
  try:
    length = int(environ.get('CONTENT_LENGTH') or 0)
  except ValueError:
    length = 0
  body = environ['wsgi.input'].read(length) if length else b''
  try:
    payload = json.loads(body or b'{}')
  except ValueError:
    start_response('400 Bad Request', [('Content-Type', 'application/json')])
    return [b'{"error":"invalid JSON body"}']
  delivered = _publish(user_id, payload)
  start_response('200 OK', [('Content-Type', 'application/json')])
  return [json.dumps({'subscriber_count': delivered}).encode('utf-8')]


def _wsgiApp(environ, start_response):
  if not _checkRelayKey(environ):
    start_response('403 Forbidden', [('Content-Type', 'application/json')])
    return [b'{"error":"invalid or missing X-Relay-Key"}']

  method = environ.get('REQUEST_METHOD')
  path = environ.get('PATH_INFO', '')

  if method == 'GET' and path.startswith('/subscribe/'):
    user_id = path[len('/subscribe/'):]
    if user_id and '/' not in user_id:
      start_response('200 OK', [
          ('Content-Type', 'text/event-stream'),
          ('Cache-Control', 'no-cache'),
          ('X-Accel-Buffering', 'no'),
      ])
      return _subscribeStream(user_id)

  if method == 'POST' and path.startswith('/publish/'):
    user_id = path[len('/publish/'):]
    if user_id and '/' not in user_id:
      return _handlePublish(environ, start_response, user_id)

  start_response('404 Not Found', [('Content-Type', 'application/json')])
  return [b'{"error":"not found"}']


def _serveForever(host, port):
  from gevent.pywsgi import WSGIServer
  WSGIServer((host, port), _wsgiApp).serve_forever()


def startNotificationRelayIfConfigured(self):
  # type: (Any) -> None
  if _state['started']:
    return
  with _state_lock:
    if _state['started']:
      return
    _state['started'] = True
    if os.environ.get('NOTIFICATION_RELAY_ENABLE', '').lower() not in ('1', 'true', 'yes'):
      return
    port = int(os.environ.get('NOTIFICATION_RELAY_PORT', '9247'))
    host = os.environ.get('NOTIFICATION_RELAY_HOST', '::')
    relay_thread = threading.Thread(
        target=_serveForever, args=(host, port), name='notification-relay')
    relay_thread.daemon = True
    relay_thread.start()
