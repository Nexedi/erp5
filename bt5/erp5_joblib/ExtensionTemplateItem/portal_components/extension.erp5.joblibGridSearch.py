import time

import numpy as np

from Products.ERP5Type.Log import log
import sklearn
from sklearn.externals import joblib
from sklearn.externals.joblib.parallel import parallel_backend
from sklearn.datasets import load_digits
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV


def test(self, active_process_path):
  digits = load_digits()
  X, y = digits.data, digits.target

  param_grid = {
    'C': np.logspace(-10, 10, 3),
    'gamma': np.logspace(-10, 10, 3),
    'tol': [1e-4]
  }

  clf = GridSearchCV(SVC(), param_grid=param_grid, verbose=10)
  active_process = self.portal_activities.unrestrictedTraverse(active_process_path)
  with parallel_backend('CMFActivity', n_jobs=2, active_process=active_process):
    tic = time.time()
    clf.fit(X, y)
  log("I am here", time.time()-tic)
  return 'ok', sklearn.__version__, joblib.__version__, time.time() - tic
  