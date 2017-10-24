from DateTime import DateTime
from Products.ERP5Type.DateUtils import addToDate
from Products.ZSQLCatalog.SQLCatalog import Query, SimpleQuery

portal_catalog = context.getPortalObject().portal_catalog

# search for dates older than one minute ago
# Only stop data ingestion of related resource is configured for batch
# ingestion
old_start_date = addToDate(DateTime(), {'minute' : -1})
start_date_query = Query(**{'delivery.start_date': old_start_date, 'range': 'ngt'})
kw_dict = {"query": start_date_query,
           "portal_type": "Data Ingestion",
           "simulation_state": "started",
           "use_relative_url": "use/big_data/ingestion/batch"}

parent_uid_list = [x.getUid() for x in portal_catalog(**kw_dict)]

if len(parent_uid_list) != 0:
  kw_dict = {"portal_type": "Data Ingestion Line",
             "stock.quantity": '!=0',
             "resource_portal_type": "Data Product",
             "parent_uid": parent_uid_list}

  for data_ingestion_line in portal_catalog(**kw_dict):
    data_ingestion = data_ingestion_line.getParentValue()
    # make sure that each movement has aggregate batch
    # this relies on reference. It cannot be done on
    # ingestion because the possibility of parallel ingestion
    #
    # should be probably done by consistency constraint
    # probably it can be done in generic way using required item type
    # on resource.
    if data_ingestion_line.DataIngestionLine_needRequiredItem():
      batch = data_ingestion_line.getAggregateDataIngestionBatchValue()
      if data_ingestion_line.DataIngestionLine_hasMissingRequiredItem():
        # make sure that each movement has aggregate batch
        # this relies on reference. It cannot be done on
        # ingestion because the possibility of parallel ingestion
        # TODO: make it generic, use Constraint
        if batch is None:
          reference_tuple = data_ingestion.getReference().split('.')
          data_ingestion_batch_reference = '.'.join(reference_tuple[:-1])
          batch = portal_catalog.getResultValue(
            portal_type = "Data Ingestion Batch",
            reference = data_ingestion_batch_reference)
        if batch is not None:
          data_ingestion_line.setDefaultAggregateValue(batch)
        else:
          # we need to wait for existing batch before we can stop the data ingestion
          continue
      # -> only stop when stop date is older than current date
      # -> set top date using information from data operation script
      if len(batch.getAggregateRelatedList()) < 2:
        # we need to wait until there are 2 batches until we can stop it
        # TODO: this should be implemented in transformation, not here
        continue
    
    data_ingestion.setStopDate(DateTime())
    data_ingestion.stop()
