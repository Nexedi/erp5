"""
This script will return all Data streams for Data set
"""
catalog_kw = {'portal_type': 'Data Ingestion Line',
              'aggregate_uid': data_set_uid,
              'limit': limit,
              }
data_ingestion_line_list = context.portal_catalog(**catalog_kw)
if data_ingestion_line_list:
  data_ingestion_uid_list = [x.uid for x in data_ingestion_line_list]
  catalog_kw = {'portal_type': 'Data Stream',
                'aggregate__related__uid': data_ingestion_uid_list,
                'validation_state':'validated',
                'select_list': ['reference', 'relative_url', 'versioning.size', 'versioning.version'],
                }
  return context.getPortalObject().portal_catalog(**catalog_kw)
return data_ingestion_line_list
