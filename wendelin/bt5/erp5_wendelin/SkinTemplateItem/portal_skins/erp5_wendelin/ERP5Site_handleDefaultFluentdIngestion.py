"""
  Example of ingesting data in ERP5 coming from fluentd.
  Fluentd sends to us a JSON dictionary using msgpack protocol.
  In this implementation we find respective Data Stream and simply
  append data there. We save raw JSON dictionary as string.
  Ingestion Policy -> Data Supply -> Data Supply Line -> Sensor
                                                      -> Data Stream
"""
from DateTime import DateTime
from zExceptions import NotFound
from Products.ZSQLCatalog.SQLCatalog import ComplexQuery
from Products.ZSQLCatalog.SQLCatalog import Query
   

now = DateTime()
request = context.REQUEST
portal_catalog = context.portal_catalog

reference = request.get('reference')
data_chunk = request.get('data_chunk')

if data_chunk is not None and reference is not None:
  # here we rely that fluentd will pass to us its tag which we use
  # as reference but we can extract it sometimes from sensor data
  # it thus depends on sensor and the fluentd topography
  query=ComplexQuery(Query(portal_type = 'Data Supply'),
                     Query(reference = reference),
                     Query(validation_state = 'validated'),
                     Query( **{'delivery.stop_date':now,  'range': 'min'}),
                     Query( **{'delivery.start_date':now,  'range': 'max'}),
                     logical_operator="AND")
  data_supply = portal_catalog.getResultValue(query=query)

  #context.log(data_supply)
  # we can have multiple lines for each sensor and we filter out by reference
  # XXX: in future we will use Predicates to find already generated
  # Data Ingestion (Movements)
  if data_supply is not None:
    for data_supply_line in data_supply.objectValues():
      sensor = data_supply_line.getSourceValue()
      if sensor is not None and sensor.getReference() == reference:
        # Sensor is defined as destination
        data_stream = data_supply_line.getDestinationValue()
        break

    #context.log(sensor)
    #context.log(data_stream)
    if data_stream is not None:
      pretty_data_chunk_list = []
      data_chunk_list = context.unpack(data_chunk)

      for data_chunk in data_chunk_list:
        pretty_data = str(data_chunk[1])
        pretty_data_chunk_list.append(pretty_data)
      data = ''.join(pretty_data_chunk_list)

      # append data
      data_stream.appendData(data)

      #context.log("Appended %s bytes to %s (%s, %s, %s)"   
      #              %(len(data), reference, data_supply, sensor, data_stream))
      # XXX: open question -> we do not store the act of ingestion.
      # one way is to have a business process for who's "ingestion" 
      # trade_phase / state we generate simulation movements and respective 
      # objects in data_ingestion_module. We can use same approach and same 
      # business process for analytics stage (just different trade_state / phase)?
      # JP: we should use this approach at a later stage
      # this approach can be hooked through interaction workflow on data stream
    else:
      raise NotFound('No data stream configuration found.')      
  else:
    raise NotFound('No data supply configuration found.')
else:
  raise NotFound('No data or any configuration found.')
