# -*- coding: utf-8 -*-
"""
 Wendelin extension code to forward data to another wendelin instance.
"""
import base64
import urllib
import urllib2

def IngestionPolicy_forward(self, reference, data_chunk):
  configuration_dict = self.IngestionPolicy_getWendelinRelayConfigurationDict()
  if not configuration_dict["wendelin_url"]:
    return
  data = urllib.urlencode({'data_chunk': data_chunk})
  url = "%s/%s/ingest?reference=%s" %(configuration_dict["wendelin_url"],
                                      self.getRelativeUrl(),
                                      reference)
  request = urllib2.Request(url, data)
  base64string = base64.encodestring('%s:%s' % (
    configuration_dict["username"],
    configuration_dict["password"])).replace('\n', '')
  request.add_header("Authorization", "Basic %s" % base64string)
  urllib2.urlopen(request, timeout=configuration_dict["timeout"])