import os.path
import json

ZOPE_USER_FAMILY = "user"
ZOPE_ACTIVITIES_FAMILIY = "activities"
PERSON_KEY = "person_per_hour"
ORDER_KEY = "sale_order_per_hour"

class ERP5_scalability():

  def getTestList(self):
    return ['createPerson', 'createSaleOrder']

  def getTestPath(self):
    return 'example/'

  def getUsersFilePath(self):
    return 'example/scalabilityUsers'

  def getUserQuantity(self, test_number):
    return [8, 14, 20, 28, 36][test_number]

  def getTestDuration(self, test_number):
    return 60*10

  def getTestRepetition(self, test_number):
    return 3

  def getScalabilityTestUrl(self, instance_information_dict):
    for frontend in instance_information_dict['frontend-url-list']:
      if frontend[0] == ZOPE_USER_FAMILY:
        frontend_address = frontend[1]
        break
    return "%s/erp5" % (frontend_address)

  def getScalabilityTestMetricUrl(self, instance_information_dict, **kw):
    frontend_address = self.getScalabilityTestUrl(instance_information_dict)
    metrics_url = frontend_address.replace("://",
                    "://%s:%s@" % (instance_information_dict['user'],
                                   instance_information_dict['password']))
    return metrics_url + "/ERP5Site_getScalabilityTestMetric"

  def getBootstrapScalabilityTestUrl(self, instance_information_dict, count=0, **kw):
    frontend_address = self.getScalabilityTestUrl(instance_information_dict)
    bootstrap_url = frontend_address.replace("://",
                      "://%s:%s@" % (instance_information_dict['user'],
                                     instance_information_dict['password']))
    bootstrap_url += "/ERP5Site_bootstrapScalabilityTest"
    bootstrap_url += "?user_quantity=%i" % self.getUserQuantity(count)
    return bootstrap_url

  def getSiteAvailabilityUrl(self, instance_information_dict, **kw):
    frontend_address = self.getScalabilityTestUrl(instance_information_dict)
    site_url = frontend_address.replace("://",
                    "://%s:%s@" % (instance_information_dict['user'],
                                   instance_information_dict['password']))
    return site_url + "/ERP5Site_isReady"

  def getScalabilityTestOutput(self, metric_list):
    """
    From the list of metrics taken during a test run, select the best metric
    for the test output by a specific criteria
    """
    if not metric_list: return None
    output_json = json.loads(metric_list[0])
    for metric in metric_list:
      metric_json = json.loads(metric)
      if metric_json[PERSON_KEY] > output_json[PERSON_KEY]:
        output_json[PERSON_KEY] = metric_json[PERSON_KEY]
      if metric_json[ORDER_KEY] > output_json[ORDER_KEY]:
        output_json[ORDER_KEY] = metric_json[ORDER_KEY]
    return "Person: %s doc/hour; SaleOrder: %s doc/hour;" % (
            str(output_json[PERSON_KEY]), str(output_json[ORDER_KEY]))
