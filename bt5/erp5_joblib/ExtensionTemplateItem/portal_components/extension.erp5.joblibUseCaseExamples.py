##############################################################################
#
# Copyright (c) 2017 Nexedi SARL and Contributors. All Rights Reserved.
#          Hardik Juneja <hardik.juneja@nexedi.com>
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

import time
import six
import numpy as np

from copy import copy
from math import sqrt

from erp5.component.module.Log import log
from Products.CMFActivity.ActiveResult import ActiveResult
from sklearn.base import clone
from sklearn.utils import check_random_state
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
if six.PY2:
  from sklearn.externals import joblib
  from sklearn.externals.joblib.parallel import parallel_backend, Parallel, delayed
else:
  import joblib
  from joblib.parallel import parallel_backend, Parallel, delayed
from sklearn.datasets import load_digits
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV

#
# Example: simple sqrt calculator
#

def example_simple_function(self, active_process_path):
  """ simple function to calculate sqrt
  """
  active_process = self.portal_activities.unrestrictedTraverse(active_process_path)

  # Use CMFActivity as a backend for joblob
  with parallel_backend('CMFActivity', active_process=active_process):
    result = Parallel(n_jobs=2, pre_dispatch='all', timeout=30, verbose=30)(delayed(sqrt)(i**2) for i in range(5))

  # Set result value and an id to the active result and post it
  result = ActiveResult(result=result)
  active_process.postResult(result)
  log("joblib activity result", result)
  return result

#
# Example: random forest function
#

def combine(all_ensembles):
  final_ensemble = copy(all_ensembles[0])
  final_ensemble.estimators_ = []

  for ensemble in all_ensembles:
    final_ensemble.estimators_ += ensemble.estimators_

  return final_ensemble

def train_model(model, X, y, sample_weight=None, random_state=None):
  model.set_params(random_state=random_state)
  if sample_weight is not None:
    model.fit(X, y, sample_weight=sample_weight)
  else:
    model.fit(X, y)

  return model

def grow_ensemble(base_model, X, y, sample_weight=None, n_estimators=1,
          n_jobs=1, random_state=None):
  random_state = check_random_state(random_state)
  max_seed = np.iinfo('uint32').max
  random_states = random_state.randint(max_seed + 1, size=n_estimators)
  results = joblib.Parallel(n_jobs=n_jobs)(
    joblib.delayed(train_model)(
      clone(base_model), X, y,
      sample_weight=sample_weight, random_state=rs)
    for rs in random_states)

  return combine(results)

def example_random_forest_function(self, active_process_path):
  digits = load_digits()

  X_train, X_test, y_train, y_test = train_test_split(
    digits.data, digits.target, random_state=0)

  # Create an active process
  active_process = self.portal_activities.unrestrictedTraverse(active_process_path)

  # Use CMFActivity as a backend for joblib
  with parallel_backend('CMFActivity', n_jobs=2, active_process=active_process):
    final_model = grow_ensemble(RandomForestClassifier(), X_train, y_train,
                                n_estimators=10, n_jobs=2, random_state=42)
  score = final_model.score(X_test, y_test)

  # Set result value and an id to the active result and post it
  result = ActiveResult(result=score, signature=123)
  active_process.postResult(result)
  log('ok', len(final_model.estimators_))
  return 'ok', len(final_model.estimators_), score

#
# Example: grid search function
#

def example_grid_search_function(self, active_process_path):
  digits = load_digits()
  X, y = digits.data, digits.target

  param_grid = {
    'C': np.logspace(-10, 10, 3),
    'gamma': np.logspace(-10, 10, 3),
    'tol': [1e-4]
  }
  X = np.ascontiguousarray(X)
  y = np.ascontiguousarray(y)
  clf = GridSearchCV(SVC(), param_grid=param_grid, verbose=10)
  active_process = self.portal_activities.unrestrictedTraverse(active_process_path)
  tic = time.time()
  with parallel_backend('CMFActivity', n_jobs=2, active_process=active_process):
    clf.fit(X, y)
  return 'ok', joblib.__version__, time.time() - tic

