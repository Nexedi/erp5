"""
  Return list of Data Streams belonging to a Date Set.
  Data Ingestion line aggregates both Data Set and Data Stream.

  Note: This code is quite computationally costly (for Data Streams having thousands of iles) as it needs to:
  1. Query MariaDB to find ingestion lines
  2. Read from ZODB both Data Ingestion Lines and Data Streams (whoch itself can be big too)
"""
data_ingestion_line_list = context.portal_catalog(
                             portal_type = "Data Ingestion Line",
                             aggregate_uid = context.getUid())
return [x.getAggregateValue(portal_type = "Data Stream") \
          for x in data_ingestion_line_list]
