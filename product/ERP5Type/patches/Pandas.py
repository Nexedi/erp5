import numpy as np

try:
  import pandas as pd
except ImportError:
  pass
else:
  _pd_to_records = pd.DataFrame.to_records
  def DataFrame_to_records(*args, **kwargs):
    record = _pd_to_records(*args, **kwargs)
    record.dtype = np.dtype([(str(k), v) for k, v in record.dtype.descr])
    return record
  pd.DataFrame.to_records = DataFrame_to_records
