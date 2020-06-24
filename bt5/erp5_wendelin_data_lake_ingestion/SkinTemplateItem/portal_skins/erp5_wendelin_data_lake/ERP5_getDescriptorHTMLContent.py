from Products.ZSQLCatalog.SQLCatalog import Query, SimpleQuery, ComplexQuery

portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

query = ComplexQuery(Query(simulation_state='stopped'),
                     Query(simulation_state='delivered'),
                     logical_operator="OR")
ing_dict = {
  "query": query,
  "portal_type": "Data Ingestion",
  "reference": reference}
ingestions = portal_catalog(**ing_dict)
if len(ingestions) == 1:
  data_ingestion = ingestions[0]
elif len(ingestions) == 0:
  ing_dict = {
    "simulation_state": "started",
    "portal_type": "Data Ingestion",
    "id": "%END",
    "reference": reference}
  single_started_ingestions = portal_catalog(**ing_dict)
  if len(single_started_ingestions) == 1:
    return '{"metadata":"Metadata not ready yet, please wait some minutes."}'
  else:
    context.logEntry("ERROR getting Data Ingestion of file %s. The file does not have a unique data ingestion in correct state." % reference)
    return '{"metadata":"No metadata available for this type of file yet"}'
else:
  context.logEntry("ERROR getting Data Ingestion of file %s. The file does not have a unique data ingestion in correct state." % reference)
  return '{"metadata":"No metadata available for this type of file yet"}'

try:
  if data_ingestion is None or data_ingestion.getSimulationState() != 'delivered':
    return '{"metadata":"Metadata not ready yet, please wait some minutes."}'

  query = Query(portal_type="Data Analysis", reference=reference)
  result_list = portal_catalog(query=query, sort_on=(('id', 'DESC', 'int'),))
  if len(result_list) == 0:
    return '{"metadata":"Metadata not ready yet, please wait some minutes."}'
  data_analysis = result_list[0]
  if data_analysis.getSimulationState() != 'stopped':
    return '{"metadata":"Metadata not ready yet, please wait some minutes."}'

  content = None
  try:
    url = 'data_descriptor_module/' + data_ingestion.getId()
    data_descriptor = context.restrictedTraverse(url)
  except Exception as e:
    # backward compatibility
    context.logEntry("ERROR while looking for data descriptor with id %s (reference: %s) : %s" % (str(data_ingestion.getId()), data_ingestion.getReference(), str(e)))
    query = Query(portal_type="Data Descriptor")
    data_descriptor = None
    for document in portal_catalog(query=query):
      if document.reference == reference:
        data_descriptor = document
    if data_descriptor is None:
      return '{"metadata":"No metadata descriptor found for this file"}'

  content = data_descriptor.getTextContent()
  if content is not None:
    return content
  else:
    return '{"metadata":"No metadata available for this type of file yet"}'

except Exception as e:
  context.logEntry("Error getting data descriptor content: " + str(e))
  return '{"metadata":"No metadata descriptor found for this file"}'
