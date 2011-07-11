import json
import threading
import os

class DummyTaskDistributionTool(object):

  def __init__(self):
    self.lock = threading.Lock()

  def createTestResult(self, name, revision, test_name_list, allow_restart,
      *args):
    self.test_name_list = list(test_name_list)
    return None, revision

  def updateTestResult(self, name, revision, test_name_list):
    self.test_name_list = list(test_name_list)
    return None, revision

  def startUnitTest(self, test_result_path, exclude_list=()):
    self.lock.acquire()
    try:
      for i, test in enumerate(self.test_name_list):
        if test not in exclude_list:
          del self.test_name_list[i]
          return None, test
    finally:
      self.lock.release()

  def stopUnitTest(self, test_path, status_dict):
    pass

def jsondump(obj, fp):
  json.dump(obj, fp, indent=4, sort_keys=True)

class JSONFSTaskDistributionTool(object):
  """Uses directory to store information"""
  def __init__(self, directory):
    if not os.path.isdir(directory):
      raise ValueError('Directory %r does not exists.' % directory)
    self.directory = os.path.abspath(directory)
    self.lock = threading.Lock()
    self.file_index = 1

  def createTestResult(self, name, revision, test_name_list, allow_restart,
      *args):
    jsondump(dict(name=name, revision=revision, test_name_list=test_name_list,
      allow_restart=allow_restart, args=args),
      open(os.path.join(self.directory, 'createTestResult.json'), 'w'))
    self.test_name_list = list(test_name_list)
    return self.directory, revision

  def updateTestResult(self, name, revision, test_name_list):
    raise NotImplementedError

  def startUnitTest(self, test_result_path, exclude_list=()):
    self.lock.acquire()
    try:
      for i, test in enumerate(self.test_name_list):
        if test not in exclude_list:
          jsondump(dict(test_result_path=test_result_path,
            exclude_list=exclude_list,),
            open(os.path.join(self.directory, 'startUnitTest.%s.json' % test),
                'w'))
          del self.test_name_list[i]
          return test, test
    finally:
      self.lock.release()

  def stopUnitTest(self, test_path, status_dict):
    jsondump(dict(test_path=test_path, status_dict=status_dict),
        open(os.path.join(self.directory, 'stopUnitTest.%s.json' % test_path),
        'w'))
