from sklearn.externals.joblib.parallel import parallel_backend, Parallel, delayed
from Products.ERP5Type.Log import log
from Products.CMFActivity.ActiveResult import ActiveResult
import time
from math import sqrt

def abc(num):
  time.sleep(5)
  return sqrt(num)

def test(self, active_process_path):
  active_process = self.portal_activities.unrestrictedTraverse(active_process_path)

  with parallel_backend('CMFActivity', active_process=active_process):
    result = Parallel(n_jobs=2, timeout=30, verbose=30)(delayed(abc)(i**2) for i in range(4))
  
  log("I am here", result)
  return result