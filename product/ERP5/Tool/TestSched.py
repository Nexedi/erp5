
from threading import Thread, Event

class Scheduler:
  """
    Step 1: use lists

    Step 2: add some object related dict which prevents calling twice the same method

    Step 3: add some time information for deferred execution

    Step 4: use MySQL as a way to store events (with locks)

    Step 5: use periodic Timer to wakeup Scheduler

    Step 6: add multiple threads on a single Scheduler

    Step 7: add control thread to kill "events which last too long"

    Some data:

    - reindexObject = 50 ms

    - calling a MySQL read = 0.7 ms

    - calling a simple method by HTTP = 30 ms

    - calling a complex method by HTTP = 500 ms

    References:

    http://www.mysql.com/doc/en/InnoDB_locking_reads.html
    http://www.python.org/doc/current/lib/thread-objects.html
  """

  def __init__(self):
    self.is_alive = 1
    self.queue = []
    self.wakeup_event = Event()
    self.thread = Thread(target = self.run)
    self.thread.start()

  def queueMessage(self, m):
    self.queue.append(m)
    self.wakeup_event.set()

  def dequeueMessage(self):
    m = self.queue[0]
    m()
    del self.queue[0]

  def run(self):
    while self.is_alive:
      if self.main():
        self.sleep()
        self.wait()

  def wait(self):
    self.wakeup_event.wait()

  def sleep(self):
    self.wakeup_event.clear()

  def wakeup(self):
    self.wakeup_event.set()

  def terminate(self):
    self.is_alive = 0

  def main(self):
    if len(self.queue) is 0:
      return 1 # Sleep
    else:
      self.dequeueMessage()
      return 0

main_scheduler = Scheduler()

class Message:
  def __init__(self, object, method_id, *args, **kw):
    self.object = object
    self.method_id = method_id
    self.args = args
    self.kw = kw
    # User Info ?

  def __call__(self):
    getattr(self.object,self.method_id)(*self.args, **self.kw)

class Method:

  def __init__(self, passive_self, method_id):
    self.passive_self = passive_self
    self.method_id = method_id

  def __call__(self, *args, **kw):
    m = Message(self.passive_self, self.method_id, *args, **kw)
    main_scheduler.queueMessage(m)

class ActiveObject:

  def __init__(self, passive_self):
    self.__dict__['passive_self'] = passive_self

  def __getattr__(self, id):
    return Method(self.__dict__['passive_self'], id)

class Test:

  toto = 0
  active_wrapper = None

  def incToto(self, v, foo=0):
    self.toto = self.toto + v + foo

  def activate(self):
    if self.active_wrapper is None: self.active_wrapper = ActiveObject(self)
    return self.active_wrapper

o = Test()
a = o.activate()

# Test
print 'Begin', o.toto
o.incToto(1)
print 'Inc Result +1', o.toto
o.activate().incToto(2)
print 'Active Inc Result +2', o.toto
o.activate().incToto(3, foo=100)
print 'Active Inc Result +3 foo', o.toto
#main_scheduler.dequeueMessage()
#print 'Dequeu Result', o.toto
#main_scheduler.dequeueMessage()
#print 'Dequeu Result', o.toto
# while o.toto < 100:
#   print 'Run', o.toto
# print 'Run', o.toto
# print 'Run', o.toto
#main_scheduler.terminate()