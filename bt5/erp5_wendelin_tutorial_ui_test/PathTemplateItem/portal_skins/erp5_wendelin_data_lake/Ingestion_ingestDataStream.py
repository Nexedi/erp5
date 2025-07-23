"""Create ingestion with data from stream"""
portal = context.getPortalObject()
request = portal.REQUEST

index = reference.index('-')
stream_reference = reference
ingestion_reference = reference[:index] + '.' + reference[index+1:len(reference)]
context.log("stream_reference = ", stream_reference)
context.log("ingestion_reference = ", ingestion_reference)
context.log("index = ", index)

request.environ['REQUEST_METHOD'] = 'POST'
request.set('reference', ingestion_reference)
request.set('data_chunk', portal.data_stream_module.get(stream_reference).getData())
portal.portal_ingestion_policies.default.ingest()
return 'Data ingested'
