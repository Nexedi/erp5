import threading

class DummyTaskDistributionTool(object):

  def __init__(self):
    self.lock = threading.Lock()

  def createTestResult(self, name, revision, test_name_list, allow_restart):
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