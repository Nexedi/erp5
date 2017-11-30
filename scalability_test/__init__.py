import os.path
import json

class ERP5_scalability():

  def getTestList(self):
    return ['createPerson']

  def getTestPath(self):
    return 'examples/'

  def getUsersFilePath(self):
    return 'examples/scalabilityUsers'

  def getUserQuantity(self, test_number):
    return [20, 30, 40, 50, 75][test_number]

  # Test duration in seconds
  def getTestDuration(self, test_number):
    return 40*self.getUserQuantity(test_number)

  def getTestRepetition(self, test_number):
    return 3

  def getScalabilityTestUrl(self, instance_information_dict):
    erp5_address = instance_information_dict["zope-address"]
    return "http://%s/erp5" % erp5_address

  def getScalabilityTestMetricUrl(self, instance_information_dict, **kw):
    metrics_url = "http://%s:%s@%s/erp5" % (instance_information_dict['user'],
                                    instance_information_dict['password'],
                                    instance_information_dict['zope-address'])
    return metrics_url + "/ERP5Site_getScalabilityTestMetric"

  def getScalabilityTestOutput(self, metric_list):
    if not metric_list: return None
    output_json = json.loads(metric_list[0])
    for metric in metric_list:
      metric_json = json.loads(metric)
      if metric_json["person_per_hour"] > output_json["person_per_hour"]:
        output_json = metric_json
    return "Person: %s doc/hour; SaleOrder: %s doc/hour;" % (
            str(output_json["person_per_hour"]), str(output_json["sale_order_per_hour"]))

  def getBootstrapScalabilityTestUrl(self, instance_information_dict, count=0, **kw):
    bootstrap_url = "http://%s:%s@%s/erp5" % (instance_information_dict['user'],
                                    instance_information_dict['password'],
                                    instance_information_dict['zope-address'])
    bootstrap_url += "/ERP5Site_bootstrapScalabilityTest"
    bootstrap_url += "?user_quantity=%i" % self.getUserQuantity(count)
    return bootstrap_url
