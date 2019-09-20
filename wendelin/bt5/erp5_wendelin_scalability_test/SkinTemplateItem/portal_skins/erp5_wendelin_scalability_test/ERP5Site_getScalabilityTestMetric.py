import json
from DateTime import DateTime

portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

now = DateTime()
now_minus_6 = now - 1.0/24/60*6
now_minus_1 = now - 1.0/24/60*1

catalog_kw = {'creation_date': {'query': (now_minus_6, now_minus_1), 'range': 'minmax'}, 
              #'validation_state': 'validated'
              }

data_stream_count = len(portal_catalog(portal_type="Data Stream", **catalog_kw))
data_stream_per_hour = 60 * data_stream_count / 5

return json.dumps({"data_stream_per_hour" : data_stream_per_hour})
