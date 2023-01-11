##############################################################################
#
# Copyright (c) 2002-2023 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################
import msgpack
import random
import string
import pandas as pd
import numpy as np
import math
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class Test(ERP5TypeTestCase):
  """
  A Sample Test Class
  """

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    # here, you can create the categories and objects your test will depend on
    self.bucket_data = ["timestamp (ms);latitude (°);longitude (°);AMSL (m);rel altitude (m);yaw (°);ground speed (m/s);climb rate (m/s)\n 16.666666666666668;45.6403;14.264800000000008;660.46;65.668;0;16.666666666666668;0\n 33.333333333333336;45.64030377777778;14.264800000000008;660.46;65.668;3.5083546492674384e-15;16.666666666666668;0\n 50;45.64030720137322;14.264799927891772;660.5773939615947;65.78539396159465;-0.669850845047716;15.10512978394417;7.043637695678324\n 66.66666666666667;45.640310624266725;14.264799783685163;660.6947879231893;65.9027879231893;-1.3397016900954353;15.10512978394417;7.043637695678324\n 83.33333333333334;45.64031404599047;14.264799567399876;660.812181884784;66.02018188478394;-2.0095525351431416;15.105129783944166;7.043637695678324\n 100.00000000000001;45.640317466076766;14.264799279065471;660.9295758463786;66.13757584637858;-2.6794033801908608;15.105129783944168;7.043637695678324\n 116.66666666666669;45.640320884058156;14.264798918721397;661.0469698079733;66.25496980797323;-3.3492542252385813;15.105129783944165;7.043637695678322\n 133.33333333333334;45.64032429946747;14.264798486416822;661.1643637695679;66.37236376956787;-4.019105070286313;15.105129783944168;7.043637695678324\n 150;45.640327711837884;14.26479798221095;661.2817577311625;66.48975773116251;-4.688955915334046;15.105129783944168;7.043637695678324", 
                        {"message":"timestamp (ms);latitude (°);longitude (°);AMSL (m);rel altitude (m);yaw (°);ground speed (m/s);climb rate (m/s)\n 16.666666666666668;45.6403;14.264800000000008;660.46;65.668;0;16.666666666666668;0\n 33.333333333333336;45.64030377777778;14.264800000000008;660.46;65.668;3.5083546492674384e-15;16.666666666666668;0\n 50;45.64030720137322;14.264799927891772;660.5773939615947;65.78539396159465;-0.669850845047716;15.10512978394417;7.043637695678324\n 66.66666666666667;45.640310624266725;14.264799783685163;660.6947879231893;65.9027879231893;-1.3397016900954353;15.10512978394417;7.043637695678324\n 83.33333333333334;45.64031404599047;14.264799567399876;660.812181884784;66.02018188478394;-2.0095525351431416;15.105129783944166;7.043637695678324\n 100.00000000000001;45.640317466076766;14.264799279065471;660.9295758463786;66.13757584637858;-2.6794033801908608;15.105129783944168;7.043637695678324\n 116.66666666666669;45.640320884058156;14.264798918721397;661.0469698079733;66.25496980797323;-3.3492542252385813;15.105129783944165;7.043637695678322\n 133.33333333333334;45.64032429946747;14.264798486416822;661.1643637695679;66.37236376956787;-4.019105070286313;15.105129783944168;7.043637695678324\n 150;45.640327711837884;14.26479798221095;661.2817577311625;66.48975773116251;-4.688955915334046;15.105129783944168;7.043637695678324"
                },{"message":"timestamp (ms);latitude (°);longitude (°);AMSL (m);rel altitude (m);yaw (°);ground speed (m/s);climb rate (m/s)\n 16.666666666666668;45.6403;14.264800000000008;660.46;65.668;0;16.666666666666668;0\n 33.333333333333336;45.64030377777778;14.264800000000008;660.46;65.668;3.5083546492674384e-15;16.666666666666668;0\n 50;45.64030720137322;14.264799927891772;660.5773939615947;65.78539396159465;-0.669850845047716;15.10512978394417;7.043637695678324\n 66.66666666666667;45.640310624266725;14.264799783685163;660.6947879231893;65.9027879231893;-1.3397016900954353;15.10512978394417;7.043637695678324\n 83.33333333333334;45.64031404599047;14.264799567399876;660.812181884784;66.02018188478394;-2.0095525351431416;15.105129783944166;7.043637695678324\n 100.00000000000001;45.640317466076766;14.264799279065471;660.9295758463786;66.13757584637858;-2.6794033801908608;15.105129783944168;7.043637695678324\n 116.66666666666669;45.640320884058156;14.264798918721397;661.0469698079733;66.25496980797323;-3.3492542252385813;15.105129783944165;7.043637695678322\n 133.33333333333334;45.64032429946747;14.264798486416822;661.1643637695679;66.37236376956787;-4.019105070286313;15.105129783944168;7.043637695678324\n 150;45.640327711837884;14.26479798221095;661.2817577311625;66.48975773116251;-4.688955915334046;15.105129783944168;7.043637695678324", "filepath":"Test"
                },{"message":"timestamp (ms);latitude (°);longitude (°);AMSL (m);rel altitude (m);yaw (°);ground speed (m/s);climb rate (m/s)\n 16.666666666666668;45.6403;14.264800000000008;660.46;65.668;0;16.666666666666668;0\n 33.333333333333336;45.64030377777778;14.264800000000008;660.46;65.668;3.5083546492674384e-15;16.666666666666668;0\n 50;45.64030720137322;14.264799927891772;660.5773939615947;65.78539396159465;-0.669850845047716;15.10512978394417;7.043637695678324\n 66.66666666666667;45.640310624266725;14.264799783685163;660.6947879231893;65.9027879231893;-1.3397016900954353;15.10512978394417;7.043637695678324\n 83.33333333333334;45.64031404599047;14.264799567399876;660.812181884784;66.02018188478394;-2.0095525351431416;15.105129783944166;7.043637695678324\n 100.00000000000001;45.640317466076766;14.264799279065471;660.9295758463786;66.13757584637858;-2.6794033801908608;15.105129783944168;7.043637695678324\n 116.66666666666669;45.640320884058156;14.264798918721397;661.0469698079733;66.25496980797323;-3.3492542252385813;15.105129783944165;7.043637695678322\n 133.33333333333334;45.64032429946747;14.264798486416822;661.1643637695679;66.37236376956787;-4.019105070286313;15.105129783944168;7.043637695678324\n 150;45.640327711837884;14.26479798221095;661.2817577311625;66.48975773116251;-4.688955915334046;15.105129783944168;7.043637695678324", "filepath":""
                },{"message":"timestamp (ms);latitude (°);longitude (°);AMSL (m);rel altitude (m);yaw (°);ground speed (m/s);climb rate (m/s)\n 16.666666666666668;45.6403;14.264800000000008;660.46;65.668;0;16.666666666666668;0\n 33.333333333333336;45.64030377777778;14.264800000000008;660.46;65.668;3.5083546492674384e-15;16.666666666666668;0\n 50;45.64030720137322;14.264799927891772;660.5773939615947;65.78539396159465;-0.669850845047716;15.10512978394417;7.043637695678324\n 66.66666666666667;45.640310624266725;14.264799783685163;660.6947879231893;65.9027879231893;-1.3397016900954353;15.10512978394417;7.043637695678324\n 83.33333333333334;45.64031404599047;14.264799567399876;660.812181884784;66.02018188478394;-2.0095525351431416;15.105129783944166;7.043637695678324\n 100.00000000000001;45.640317466076766;14.264799279065471;660.9295758463786;66.13757584637858;-2.6794033801908608;15.105129783944168;7.043637695678324\n 116.66666666666669;45.640320884058156;14.264798918721397;661.0469698079733;66.25496980797323;-3.3492542252385813;15.105129783944165;7.043637695678322\n 133.33333333333334;45.64032429946747;14.264798486416822;661.1643637695679;66.37236376956787;-4.019105070286313;15.105129783944168;7.043637695678324\n 150;45.640327711837884;14.26479798221095;661.2817577311625;66.48975773116251;-4.688955915334046;15.105129783944168;7.043637695678324", "Not a real key":""
                },
                  {"message":"timestamp (ms);latitude (°);longitude (°);AMSL (m);rel altitude (m);yaw (°);ground speed (m/s);climb rate (m/s)\n 16.666666666666668;45.6403;14.264800000000008;660.46;65.668;0;16.666666666666668;0\n 33.333333333333336;45.64030377777778;14.264800000000008;660.46;65.668;3.5083546492674384e-15;16.666666666666668;0\n 50;45.64030720137322;14.264799927891772;660.5773939615947;65.78539396159465;-0.669850845047716;15.10512978394417;7.043637695678324\n 66.66666666666667;45.640310624266725;14.264799783685163;660.6947879231893;65.9027879231893;-1.3397016900954353;15.10512978394417;7.043637695678324\n 83.33333333333334;45.64031404599047;14.264799567399876;660.812181884784;66.02018188478394;-2.0095525351431416;15.105129783944166;7.043637695678324\n 100.00000000000001;45.640317466076766;14.264799279065471;660.9295758463786;66.13757584637858;-2.6794033801908608;15.105129783944168;7.043637695678324\n 116.66666666666669;45.640320884058156;14.264798918721397;661.0469698079733;66.25496980797323;-3.3492542252385813;15.105129783944165;7.043637695678322\n 133.33333333333334;45.64032429946747;14.264798486416822;661.1643637695679;66.37236376956787;-4.019105070286313;15.105129783944168;7.043637695678324\n 150;45.640327711837884;14.26479798221095;661.2817577311625;66.48975773116251;-4.688955915334046;15.105129783944168;7.043637695678324", "filepath":"simulation_log_D0_(14.0, 10.0).log"}]
    portal = self.getPortalObject()
    
    self.column_names = ["timestamp (ms)","latitude (°)","longitude (°)","AMSL (m)","rel altitude (m)","yaw (°)","ground speed (m/s)","climb rate (m/s)"]
    self.wrong_column_names = ["timestamp (ms)","latit(°)","°","AL (m)","rel alie (m)","ya ()","ground speed ()"]

  def create_random_name(self):
    return "simulation_log_D0_"+str((random.uniform(5,20), random.uniform(5,20)))+".log"

  def create_random_dataframe_string(self, column_names):
    l = []
    nr_lines = random.randint(10,100) # We have files with somewhere like 18k lines. But we could also reduce them here, just to save space
    timestamp = sorted([random.uniform(1,100) for _ in range(nr_lines)]) #We only go up to 100, because otherwise it is possible that the smallest timestamp in the mock simulation is larger than the largest timestamp in the mock real data.
    x = [[random.uniform(-100,100) if name !="timestamp (ms)" else timestamp[i] for name in column_names] for i in range(nr_lines)]
    x.insert(0, column_names)
    for line in x:
      l.append(";".join(map(str, line)))
    
    return "\n".join(l)

    
  def create_random_data_msg(self, column_names):
    return {"message": self.create_random_dataframe_string(column_names), "filepath": self.create_random_name()}
  
    

  def randomword(self, length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

  def create_random_wrong_dataframe(self, column_names):
    l = []
    nr_lines = random.randint(10,100) # We have files with somewhere like 18k lines. But we could also reduce them here, just to save space
    timestamp = sorted([random.uniform(1,100) for _ in range(nr_lines)]) #We only go up to 100, because otherwise it is possible that the smallest timestamp in the mock simulation is larger than the largest timestamp in the mock real data.
    x = [[self.randomword(5) if name !="timestamp (ms)" else self.randomword(5) for name in column_names] for _ in range(nr_lines)]
    x.insert(0, column_names)
    for line in x:
      l.append(";".join(map(str, line)))
    
    return "\n".join(l)
    
  def create_random_wrong_data_msg_list(self, column_names, wrong_column_names):
    return [{"message": self.create_random_dataframe_string(column_names), "filepath": "Wrong Filepath Name but correct data"},
            {"message": self.create_random_data_msg(wrong_column_names), "filepath": self.create_random_name()},
            {"message": self.create_random_wrong_dataframe(column_names), "filepath": self.create_random_name()}]

  def checkCorrectName(self, data_bucket_stream, name):
    self.assertNotEquals(data_bucket_stream.get(name), None)
    return name
  def stepCallAnalyses(self):
    self.portal.portal_alarms.wendelin_handle_analysis.activeSense()
    self.tic()
    self.portal.portal_alarms.wendelin_handle_analysis.activeSense()
    self.tic()

  def stepIngestSimDroneData(self, ingestion_policy, tag, data):
    """
      Ingest some data
    """
    document_to_delete_list = []
    data_ingestion = self.portal.portal_catalog.getResultValue(
        portal_type = "Data Array")

    request = self.portal.REQUEST
    
    # simulate fluentd by setting proper values in REQUEST
    request.environ['REQUEST_METHOD'] = 'POST'
    data_chunk = msgpack.packb([0, data], use_bin_type=True)
    request.set('reference', tag)
    request.set('data_chunk', data_chunk)
    ingestion_policy.ingest()
    self.tic()

    # check that new data ingestion was correctly created
    data_ingestion = self.portal.portal_catalog.getResultValue(
        portal_type = "Data Ingestion",
        specialise_uid = self.portal.data_supply_module.drone_simulation.getUid(),
        reference = 'drone_simulation')

    self.assertNotEquals(data_ingestion, None)
    
    #self.document_to_delete_list.append(data_ingestion)
    return data_ingestion
  
  def stepIngestRealDroneData(self, ingestion_policy, tag, data):
    """
      Ingest some data
    """
    request = self.portal.REQUEST
    
    # simulate fluentd by setting proper values in REQUEST
    request.environ['REQUEST_METHOD'] = 'POST'
    data_chunk = msgpack.packb([0, data], use_bin_type=True)
    request.set('reference', tag)
    request.set('data_chunk', data_chunk)
    ingestion_policy.ingest()
    self.tic()

    # check that new data ingestion was correctly created
    data_ingestion = self.portal.portal_catalog.getResultValue(
        portal_type = "Data Ingestion",
        specialise_uid = self.portal.data_supply_module.drone_real.getUid(),
        reference = 'drone_real')

    self.assertNotEquals(data_ingestion, None)
    
    #self.document_to_delete_list.append(data_ingestion)
    return data_ingestion
  
  def test_01_CorrectSimIngestion(self):
    portal = self.getPortalObject()
    ingestion_policy = portal.portal_ingestion_policies.default
    
    self.tic()
    #ingest sim data
    tag_bin = "drone_simulation.sample-drone-raw-data"
    # First we will ingest some predetermined data
    for item in self.bucket_data:
      bin_chunk = item
      data_ingestion_bin = self.stepIngestSimDroneData(ingestion_policy,
                                             tag_bin,
                                             bin_chunk)
    # Now we generate some random mock data as well
    bin_chunk = self.create_random_data_msg(self.column_names)
    data_ingestion_bin = self.stepIngestSimDroneData(ingestion_policy,
                                             tag_bin,
                                             bin_chunk)
    self.tic()
    bin_line = None
    for line in data_ingestion_bin.objectValues(
        portal_type = "Data Ingestion Line"):
      if line.getReference() == "bucket_stream":
        bin_line = line
    """
    What do we actually want to check here? Probably only need to check that the data is not beeing ingested
    Or we just start it and the test will only fail if the programm throws an error
    """
    # check line for binary data
    self.assertNotEquals(bin_line, None)
    self.assertEquals(bin_line.getQuantity(), 1)
    self.assertEquals(bin_line.getResource(), 
      'data_product_module/drone_raw_data')
    
    destination_data_stream_bucket = bin_line.getAggregateDataBucketStreamValue()
    self.assertNotEquals(destination_data_stream_bucket, None)
    self.assertNotEquals(destination_data_stream_bucket.getBucketByKey(bin_chunk["filepath"]), None)
    self.assertIn(bin_chunk["message"], destination_data_stream_bucket.getBucketByKey(bin_chunk["filepath"]))
  
    self.stepCallAnalyses()
  
   
    data_transformation = portal.portal_catalog.getResultValue(
                                   portal_type = 'Data Transformation',
                                   reference = 'convert-drone-raw-data',
                                   validation_state = 'validated')
    self.assertNotEqual(None, data_transformation)

    data_analysis = portal.portal_catalog.getResultValue(
                                   portal_type = 'Data Analysis',
                                   reference = 'drone_simulation',
                                   specialise_uid = data_transformation.getUid(),
                                   simulation_state = 'started')
    self.assertNotEqual(None, data_analysis)
    
    for data_analysis_line in data_analysis.objectValues():
      reference = data_analysis_line.getReference()
      if reference == 'in_stream':
        data_stream = data_analysis_line.getAggregateValueList(portal_type= "Data Bucket Stream")[0]
        self.assertIn(bin_chunk["filepath"], data_stream.getKeyList())
        
      if reference == 'out_array':
        data_array = data_analysis_line.getAggregateValueList(portal_type = 'Data Array')[0]
        zarray = data_array.getArray()
        self.assertNotEquals(zarray, None)
    
  def test_02_WrongSimIngestion(self):
    portal = self.getPortalObject()
    ingestion_policy = portal.portal_ingestion_policies.default
    
    self.tic()
    #ingest sim data
    tag_bin = "drone_simulation.sample-drone-raw-data"
    data_list = self.create_random_wrong_data_msg_list(self.column_names, self.wrong_column_names)
    for item in data_list:
      bin_chunk = item
      data_ingestion_bin = self.stepIngestSimDroneData(ingestion_policy,
                                             tag_bin,
                                             bin_chunk)
      self.tic()
      bin_line = None
      for line in data_ingestion_bin.objectValues(
          portal_type = "Data Ingestion Line"):
        if line.getReference() == "bucket_stream":
          bin_line = line
        
    # check line for binary data
      self.assertNotEquals(bin_line, None)
      self.assertEquals(bin_line.getQuantity(), 1)
      self.assertEquals(bin_line.getResource(), 
        'data_product_module/drone_raw_data')
    
      destination_data_stream_bucket = bin_line.getAggregateDataBucketStreamValue()
      self.assertNotEquals(destination_data_stream_bucket, None)
      if bin_chunk["filepath"] != "Wrong Filepath Name but correct data":
        try:
          _ = destination_data_stream_bucket.getBucketByKey(bin_chunk["filepath"])
        except:
          continue
      self.assertNotEquals(destination_data_stream_bucket.getBucketByKey(bin_chunk["filepath"]), None)
      self.assertIn(bin_chunk["message"], destination_data_stream_bucket.getBucketByKey(bin_chunk["filepath"]))
  

      self.stepCallAnalyses()
  
   
      data_transformation = portal.portal_catalog.getResultValue(
                                   portal_type = 'Data Transformation',
                                   reference = 'convert-drone-raw-data',
                                   validation_state = 'validated')
      self.assertNotEqual(None, data_transformation)

      data_analysis = portal.portal_catalog.getResultValue(
                                   portal_type = 'Data Analysis',
                                   reference = 'drone_simulation',
                                   specialise_uid = data_transformation.getUid(),
                                   simulation_state = 'started')
      self.assertNotEqual(None, data_analysis)
    
      for data_analysis_line in data_analysis.objectValues():
        reference = data_analysis_line.getReference()
        if reference == 'in_stream':
          data_stream = data_analysis_line.getAggregateValueList(portal_type= "Data Bucket Stream")[0]
          self.assertIn(bin_chunk["filepath"], data_stream.getKeyList())
        
        if reference == 'out_array':
          data_array = data_analysis_line.getAggregateValueList(portal_type = 'Data Array')[0]
          zarray = data_array.getArray()
          self.assertNotEquals(zarray, None)
    
    
  def test_03_RealIngestion(self):
    portal = self.getPortalObject()
    ingestion_policy = portal.portal_ingestion_policies.default
    self.tic()

    #ingest real data
    tag_bin = "drone_real.bouncy_flight_mavsdk_raw_data"
    for item in self.bucket_data:
      bin_chunk = item
      data_ingestion_bin = self.stepIngestRealDroneData(ingestion_policy,
                                             tag_bin,
                                             bin_chunk)
    self.tic()
    
    bin_line = None
    for line in data_ingestion_bin.objectValues(
        portal_type = "Data Ingestion Line"):
      if line.getReference() == "bucket_stream":
        bin_line = line
        
    # check line for binary data
    self.assertNotEquals(bin_line, None)
    self.assertEquals(bin_line.getQuantity(), 1)
    self.assertEquals(bin_line.getResource(), 
      'data_product_module/bouncy_flight_mavsdk_raw_data')
    
    destination_data_stream_bucket = bin_line.getAggregateDataBucketStreamValue()
    self.assertNotEquals(destination_data_stream_bucket, None)

    for i in ["Test","","simulation_log_D0_(14.0, 10.0).log"]:
      self.assertEquals(
            destination_data_stream_bucket.getBucketByKey(i), \
            self.bucket_data[0])

    self.stepCallAnalyses()
  
    # find resampling data transformation and its data analayze
    data_transformation = portal.portal_catalog.getResultValue(
                                   portal_type = 'Data Transformation',
                                   reference = 'convert-drone-raw-real-data',
                                   validation_state = 'validated')
    self.assertNotEqual(None, data_transformation)

    data_analysis = portal.portal_catalog.getResultValue(
                                   portal_type = 'Data Analysis',
                                   reference = 'drone_real',
                                   specialise_uid = data_transformation.getUid(),
                                   simulation_state = 'started')
    self.assertNotEqual(None, data_analysis)
    
    for data_analysis_line in data_analysis.objectValues():
      reference = data_analysis_line.getReference()
      if reference == 'in_stream':
        data_stream = data_analysis_line.getAggregateValueList(portal_type= "Data Bucket Stream")[0]
        self.assertSetEqual(set(data_stream.getKeyList()), set(["","Test","simulation_log_D0_(14.0, 10.0).log"]))
        
      if reference == 'out_array':
        data_array = data_analysis_line.getAggregateValueList(portal_type = 'Data Array')[0]
        zarray = data_array.getArray()
        self.assertNotEquals(zarray, None)
  def test_04_ScoreCalculation(self):
    # Sim flights
    data_transformation_sim_flight = self.portal.portal_catalog.getResultValue(
                                   portal_type = 'Data Transformation',
                                   reference = 'convert-drone-raw-real-data',
                                   validation_state = 'validated')


    data_analysis_sim_flight = self.portal.portal_catalog.getResultValue(
                                   portal_type = 'Data Analysis',
                                   reference = 'drone_real',
                                   specialise_uid = data_transformation_sim_flight.getUid(),
                                   simulation_state = 'started')

    zarray_sim_flight = None
    for data_analysis_line in data_analysis_sim_flight.objectValues():
      reference = data_analysis_line.getReference()

      if reference == 'out_array':
        data_array_sim_flight = data_analysis_line.getAggregateValueList(portal_type = 'Data Array')[0]
        zarray_sim_flight = data_array_sim_flight
        data_array_line_names_sim_flight_list = list(zarray_sim_flight)

    test_sim_data = zarray_sim_flight.get("simulation_log_D0_(14.0, 10.0).log").getArray()
    test_sim_dataframe = pd.DataFrame(data=test_sim_data, columns=["timestamp (ms)","latitude ()","longitude ()","AMSL (m)","rel altitude (m)","yaw ()","ground speed (m/s)","climb rate (m/s)"])
      
      
    # Sim flights after score 
    data_transformation_sim_flight_score = self.portal.portal_catalog.getResultValue(
                                 portal_type = 'Data Transformation',
                                 reference = 'create-score-list-array',
                                 validation_state = 'validated')
    data_analysis_sim_flight_score = self.portal.portal_catalog.getResultValue(
                                   portal_type = 'Data Analysis',
                                   reference = 'drone_simulation',
                                   specialise_uid = data_transformation_sim_flight_score.getUid(),
                                   simulation_state = 'started')

    zarray_sim_flight_score = None
    for data_analysis_line in data_analysis_sim_flight_score.objectValues():
      reference = data_analysis_line.getReference()

      if reference == 'out_array_scores':
        data_array_sim_flight_score = data_analysis_line.getAggregateValueList(portal_type = 'Data Array')[0]
        zarray_sim_flight_score = data_array_sim_flight_score
        data_array_line_names_sim_flight_score_list = list(zarray_sim_flight_score)

    test_sim_score_data = zarray_sim_flight_score.getArray()

    test_sim_score_dataframe = pd.DataFrame.from_records(test_sim_score_data[:].copy())
    
    # Determine if there are duplicates
    self.assertEqual(len(test_sim_score_dataframe["name"]), len(test_sim_score_dataframe["name"].unique()))
   
    optimal_flight = test_sim_score_dataframe[test_sim_score_dataframe["name"]=="simulation_log_D0_(14.0, 10.0).log"]

    # Check that the score is 1 everytwhere for this one instance
    self.assertTrue(not optimal_flight[optimal_flight["climb_rate_reciprocal"] == 1].empty)
    self.assertTrue(not optimal_flight[optimal_flight["ground_speed_reciprocal"] == 1].empty)
    self.assertTrue(not optimal_flight[optimal_flight["ASML_reciprocal"] == 1].empty)
    self.assertTrue(not optimal_flight[optimal_flight["distance_reciprocal"] == 1].empty)
    
    # Check if the scores are (approximately) correct (floating point errors can not be avoided)
    for flight_name in test_sim_score_dataframe["name"]:
      flight_dataframe = test_sim_score_dataframe[test_sim_score_dataframe["name"] == flight_name]
      # Because we can be sure that each flight_dataframe is only one row (because each simulation is represented with exactly one row), we can use .item()
      self.assertAlmostEqual((flight_dataframe["climb_rate_reciprocal"] + flight_dataframe["ground_speed_reciprocal"] + flight_dataframe["ASML_reciprocal"] + flight_dataframe["distance_reciprocal"]).item()/4,
                            flight_dataframe["score_reciprocal"].item())
      
  def test_05_RecalculateScores(self):
    data_transformation = self.portal.portal_catalog.getResultValue(
                                 portal_type = 'Data Transformation',
                                 reference = 'recalculate-score-list-array',
                                 validation_state = 'validated')
    self.assertNotEqual(data_transformation, None)
    
    self.stepCallAnalyses()

    data_analysis = self.portal.portal_catalog.getResultValue(
                                   portal_type = 'Data Analysis',
                                   reference = 'drone_simulation',
                                   specialise_uid = data_transformation.getUid(),
                                   simulation_state = 'started')
    self.assertNotEqual(data_analysis, None)

    zarray = None
    for data_analysis_line in data_analysis.objectValues():
      reference = data_analysis_line.getReference()

      if reference == 'out_array_scores':
        data_array = data_analysis_line.getAggregateValueList(portal_type = 'Data Array')[0]
        zarray = data_array
        data_array_line_names_sim_flight_score_list = list(zarray)

    self.assertNotEqual(zarray.getArray(), None)
    recalculated_scores = pd.DataFrame.from_records(zarray.getArray()[:].copy())
    
    # Determine if there are nan values
    self.assertFalse(math.isnan(recalculated_scores["iteration"].max()))