
ENABLE_PATCH = True
try:
  import sklearn
  #from sklearn.externals import joblib
  #from sklearn.externals.joblib.parallel import Parallel
  from joblib.parallel import Parallel
except ImportError:
  ENABLE_PATCH = False

if ENABLE_PATCH:
  from zLOG import LOG, WARNING

  def _print(self, msg, msg_args):    
    msg = msg % msg_args    
    LOG('Parallel._print', WARNING, '[%s]: %s\n' % (self, msg))  


  Parallel._print = _print
