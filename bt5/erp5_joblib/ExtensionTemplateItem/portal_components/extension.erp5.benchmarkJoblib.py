import time 
import random
import string
import transaction

def getRandomString():
  return '%s' %''.join([random.choice(string.ascii_letters + string.digits) \
    for n in xrange(4)])

def tend(self, path):
  active_process = self.portal_activities.unrestrictedTraverse(path)
  active_process.tend = time.time()
  dt = active_process.tend - active_process.tstart
  active_process.postResult(dt)

def example_bench_function(self, path):
  active_process = self.portal_activities.unrestrictedTraverse(path)

  reference = "energey_data_2" #'energey_data_%s' % getRandomString()

  self.portal_activities.activate(activity="SQLQueue", after_tag="DataStream_copyCSVToDataArray", active_process=active_process).Base_joblibLinearRegression(path, reference)

  # used to use stream and create/feed a data array

  # data_stream = self.data_stream_module.energey_data
  # data_stream_data = data_stream.getData()
  # data_array = self.data_array_module.newContent(
  #                       portal_type = 'Data Array', 
  #                       reference = reference)
  
  # data_stream.DataStream_transform(\
  #     # chunk_length = 	572344, \
  #     transform_script_id = 'DataStream_copyCSVToDataArray',
  #     data_array_reference = reference)
  
  # data_array.validate()
  # transaction.commit()

