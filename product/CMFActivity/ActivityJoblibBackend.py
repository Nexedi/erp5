##############################################################################
#
# Copyright (c) 2016 Nexedi SA and Contributors. All Rights Reserved.
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
ENABLE_JOBLIB = True

import copy
import hashlib
import sys
import time

from zLOG import LOG, INFO, WARNING
from ZODB.POSException import ConflictError

try:
  from sklearn.externals.joblib import register_parallel_backend
  from sklearn.externals.joblib.parallel import ParallelBackendBase, parallel_backend
  from sklearn.externals.joblib.parallel import FallbackToBackend, SequentialBackend
  from sklearn.externals.joblib._parallel_backends import SafeFunction
  from sklearn.externals.joblib.my_exceptions import TransportableException, WorkerInterrupt
  from sklearn.externals.joblib.format_stack import format_exc
except ImportError:
  LOG("CMFActivityBackend", WARNING, "CLASS NOT LOADED!!!")
  ENABLE_JOBLIB = False

if ENABLE_JOBLIB:
  
  # this is improvisation of 
  # http://stackoverflow.com/questions/5884066/hashing-a-python-dictionary/8714242#8714242
  def make_hash(o):
    """
    Makes a hash from a dictionary, list, tuple or set to any level, that contains
    only other hashable types (including any lists, tuples, sets, and
    dictionaries).
    """
 
    if (callable(o) and o.__name__):
      return hash(o.__name__)

    if isinstance(o, (set, tuple, list)):
      return hash(tuple([make_hash(e) for e in o]))
  
    elif not isinstance(o, dict):
      try:
        return hash(o)
      except TypeError:
        return hash(int(hashlib.md5(o).hexdigest(), 16))
    new_o = copy.deepcopy(o)
    for k, v in new_o.items():
      new_o[k] = make_hash(v)
    return hash(tuple(frozenset(sorted(new_o.items()))))

  class MySafeFunction(SafeFunction):
    """Wrapper around a SafeFunction that catches any exception
  
    The exception can be handled in CMFActivityResult.get
    """
    def __init__(self, *args, **kwargs):
      super(MySafeFunction, self).__init__(*args, **kwargs)
      self.batch = args[0]
    def __call__(self, *args, **kwargs):
      try:
        return super(MySafeFunction, self).__call__(*args, **kwargs)
      except Exception as exc:
        return exc

  class CMFActivityResult(object):
    def __init__(self, active_process, active_process_sig, callback):
      self.active_process = active_process
      self.active_process_sig = active_process_sig
      self.callback = callback
 
    def get(self, timeout=None):
      if self.active_process.getResult(self.active_process_sig) is None:
        raise ConflictError
      result = self.active_process.getResult(self.active_process_sig).result

      # TODO raise before or after the callback?
      if isinstance(result, Exception):
        raise result
      if self.callback is not None:
        self.callback(result)
      return result

  class CMFActivityBackend(ParallelBackendBase):
    def __init__(self, *args, **kwargs):
      self.count = 1
      self.active_process = kwargs['active_process']

    def effective_n_jobs(self, n_jobs):
      """Dummy implementation to prevent n_jobs <=0

      and allow (sequential) n_jobs=1 and n_jobs != 1 (parallel) behaviour
      """
      if n_jobs == 0:
        raise ValueError('n_jobs == 0 in Parallel has no meaning')
      return abs(n_jobs)

    def apply_async(self, batch, callback=None):
      """Schedule a func to be run"""
      portal_activities = self.active_process.portal_activities
      active_process_id = self.active_process.getId()
      joblib_result = None
      sig = make_hash(batch.items[0])

      if not self.active_process.getResult(sig):
        joblib_result = portal_activities.activate(activity='SQLJoblib',
          tag="joblib_%s" % active_process_id,
          signature=sig,
          active_process=self.active_process).Base_callSafeFunction(sig, MySafeFunction(batch))
      if joblib_result is None:
        joblib_result = CMFActivityResult(self.active_process, sig, callback)
      return joblib_result

    def configure(self, n_jobs=1, parallel=None, **backend_args):
      """Reconfigure the backend and return the number of workers. This
      makes it possible to reuse an existing backend instance for successive
      independent calls to Parallel with different parameters."""
      LOG("CMFActivityBackend", INFO, 'n_jobs={}'.format(n_jobs))
      LOG("CMFActivityBackend", INFO, 'parallel={}'.format(parallel))

      if n_jobs == 1:
        raise FallbackToBackend(SequentialBackend())

      self.parallel = parallel
      return self.effective_n_jobs(n_jobs)

    def abort_everything(self, ensure_ready=True):
      # All jobs will be aborted here while they are still processing our backend
      if ensure_ready:
        self.configure(n_jobs=self.parallel.n_jobs, parallel=self.parallel,
                        **self.parallel._backend_args)
      return

  register_parallel_backend('CMFActivity', CMFActivityBackend)
  
else:
  class CMFActivityBackend(object):
    pass

