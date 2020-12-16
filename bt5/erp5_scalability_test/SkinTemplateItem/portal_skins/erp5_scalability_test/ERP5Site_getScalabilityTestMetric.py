import json
from DateTime import DateTime
now = DateTime()
now_minus_6 = now - 1.0/24/60*6
now_minus_1 = now - 1.0/24/60*1
catalog_kw = {'creation_date': {'query': (now_minus_6, now_minus_1), 'range': 'minmax'}, 'validation_state': 'validated'}
portal = context.getPortalObject()
portal_catalog = portal.portal_catalog
person_count = len(portal_catalog(portal_type="Person", **catalog_kw))
catalog_kw = {'creation_date': {'query': (now_minus_6, now_minus_1), 'range': 'minmax'}, 'simulation_state': 'planned'}
sale_order_count = len(portal_catalog(portal_type="Sale Order", **catalog_kw))
person_per_hour = 60*person_count/5
sale_order_per_hour = 60*sale_order_count/5
return json.dumps({"person_per_hour" : person_per_hour, "sale_order_per_hour": sale_order_per_hour})
