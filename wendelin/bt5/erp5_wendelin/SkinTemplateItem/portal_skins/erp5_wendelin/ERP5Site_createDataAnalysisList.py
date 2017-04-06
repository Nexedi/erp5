from DateTime import DateTime
from Products.ZSQLCatalog.SQLCatalog import AndQuery, OrQuery, Query, NegatedQuery, SimpleQuery

portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

now = DateTime()

query = AndQuery(
          Query(portal_type = ["Data Ingestion Line", "Data Analysis Line"]),
          Query(**{"stock.quantity": "!=0"}),
          Query(resource_portal_type = "Data Product"),
          # Should be improved to support mor than one analysis per ingestion
          SimpleQuery(parent_causality_related_relative_url = None),
          OrQuery(
            Query(simulation_state = "stopped",
                  use_relative_url = "use/big_data/ingestion/batch"),
            AndQuery(
              Query(simulation_state = "started"),
              Query(use_relative_url = "use/big_data/ingestion/stream"))))

for movement in portal_catalog(query):
  if movement.getQuantity() <= 0:
    continue
  if movement.DataIngestionLine_hasMissingRequiredItem():
    raise ValueError("Transformation requires movement to have " +
                     "aggregated data ingestion batch")
  data_ingestion = movement.getParentValue()
  # Get applicable transformation
  for transformation in portal_catalog(
                  portal_type = "Data Transformation",
                  validation_state = "validated",
                  resource_relative_url = movement.getResource()):
    # Create Analysis
    data_analysis = portal.data_analysis_module.newContent(
                  portal_type = "Data Analysis",
                  title = transformation.getTitle(),
                  reference = data_ingestion.getReference(),
                  start_date = now,
                  specialise_value = transformation,
                  causality_value = data_ingestion,
                  source = data_ingestion.getSource(),
                  source_section = data_ingestion.getSourceSection(),
                  source_project = data_ingestion.getSourceProject(),
                  destination = data_ingestion.getDestination(),
                  destination_section = data_ingestion.getDestinationSection(),
                  destination_project = data_ingestion.getDestinationProject())

    # create input and output lines
    for transformation_line in transformation.objectValues(
        portal_type=["Data Transformation Resource Line",
                     "Data Transformation Operation Line"]):
      resource = transformation_line.getResourceValue()
      quantity = transformation_line.getQuantity()
      if isinstance(quantity, tuple):
        quantity = quantity[0]
      aggregate_set = set()
      # manually add device and device configuration to every line
      aggregate_set.add(movement.getAggregateDevice())
      # workaround the case that no device configuration portal type exists
      # without this work around aggregate from any portal type
      # would be returned, because getAggregateValue(portal_type=[]) does not
      # return  None as expected. This must be fixed properly in generic erp5
      if portal.getPortalDeviceConfigurationTypeList():
        aggregate_set.add(movement.getAggregateDeviceConfiguration())
      if transformation_line.getPortalType() == \
          "Data Transformation Resource Line":
        # at the moment, we only check for positive or negative quantity
        if quantity < 0:
          # it is an input line
          # aggregate transformed item from data ingestion batch related to our
          # movement. If it is an input resource line, then we search for an
          # ingestion line with the same resource. If it is an operation line
          # then we search for an ingestion line with resource portal type
          # Data Product
          batch_relative_url = movement.getAggregateDataIngestionBatch()
          if batch_relative_url is not None:
            related_movement_list = portal_catalog(
              portal_type="Data Ingestion Line",
              aggregate_relative_url=batch_relative_url,
              resource_relative_url = resource.getRelativeUrl())
          else:
            # get related movements only from current data ingestion
            related_movement_list = movement.getParentValue().searchFolder(
              portal_type=["Data Ingestion Line", "Data Analysis Line"],
              resource_relative_url = resource.getRelativeUrl())
          for related_movement in related_movement_list:
            aggregate_set.update(related_movement.getAggregateSet())
            if related_movement.getUse() == "big_data/ingestion/batch":
              related_movement.getParentValue().deliver()
        # create new item based on item_type if it is not already aggregated
        aggregate_type_set = set(
          [portal.restrictedTraverse(a).getPortalType() for a in aggregate_set])
        for item_type in transformation_line.getAggregatedPortalTypeList():
          if item_type not in aggregate_type_set:
            module = portal.getDefaultModule(item_type)
            item = module.newContent(portal_type = item_type,
                              title = transformation.getTitle(),
                              reference = "%s-%s" %(transformation.getTitle(),
                                                   data_ingestion.getReference()),
                              version = '001')
            item.validate()
            aggregate_set.add(item.getRelativeUrl())

      data_analysis.newContent(
        portal_type = "Data Analysis Line",
        title = transformation_line.getTitle(),
        reference = transformation_line.getReference(),
        int_index = transformation_line.getIntIndex(),
        resource_value = resource,
        variation_category_list = transformation_line.getVariationCategoryList(),
        quantity = quantity,
        quantity_unit = transformation_line.getQuantityUnit(),
        use = transformation_line.getUse(),
        aggregate_set = aggregate_set)
        
    data_analysis.start()
