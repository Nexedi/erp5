from DateTime import DateTime
from Products.ZSQLCatalog.SQLCatalog import AndQuery, OrQuery, Query
from Products.ERP5Type.Errors import UnsupportedWorkflowMethod

portal = context.getPortalObject()
portal_catalog = portal.portal_catalog
now = DateTime()

if not include_delivered:
  batch_simulation_state = "stopped"
  stream_simulation_state = "started"

else:
  batch_simulation_state = ["stopped", "delivered"]
  stream_simulation_state = ["started", "stopped", "delivered"]

query = AndQuery(
          Query(portal_type = ["Data Ingestion Line", "Data Analysis Line"]),
          Query(**{"stock.quantity": "!=0"}),
          Query(resource_portal_type = "Data Product"),
          # Should be improved to support mor than one analysis per ingestion
          #SimpleQuery(parent_causality_related_relative_url = None),
          OrQuery(Query(simulation_state = batch_simulation_state,
                        use_relative_url = "use/big_data/ingestion/batch"),
                  Query(simulation_state =  stream_simulation_state,
                        use_relative_url = "use/big_data/ingestion/stream")))

for movement in portal_catalog(query = query):
  if movement.getQuantity() <= 0:
    continue
  if movement.DataIngestionLine_hasMissingRequiredItem():
    raise ValueError("Transformation requires movement to have " +
                     "aggregated data ingestion batch")
  delivery = movement.getParentValue()
  data_supply = delivery.getSpecialiseValue(portal_type="Data Supply")
  data_supply_list = delivery.getSpecialiseValueList(portal_type="Data Supply")

  composed_data_supply = data_supply.asComposedDocument()
  # Get applicable transformation
  transformation_list = []
  for transformation in composed_data_supply.getSpecialiseValueList(portal_type="Data Transformation"):
    for line in transformation.objectValues():
      if line.getResourceValue() == movement.getResourceValue() and line.getQuantity() < 0:
        transformation_list.append(transformation)
        break
  for transformation in portal.portal_catalog(
      portal_type = "Data Transformation",
      validation_state = "validated",
      resource_relative_url = movement.getResource()):
    if transformation.getVariationCategoryList() ==  movement.getVariationCategoryList():
      transformation_list.append(transformation)

  for transformation in transformation_list:
   
    is_shared_data_analysis = False
    # Check if analysis already exists
    data_analysis = portal_catalog.getResultValue(
      portal_type="Data Analysis",
      specialise_relative_url = transformation.getRelativeUrl(),
      causality_relative_url = delivery.getRelativeUrl())
    if data_analysis is not None:
      continue
    # for first level analysis check if same kind of data analysis with same project and same source already exists
    # If yes, then later add additional input lines to this shared data analysis
    if delivery.getPortalType() == "Data Ingestion":
      data_analysis = portal_catalog.getResultValue(
        portal_type="Data Analysis",
        specialise_relative_url = transformation.getRelativeUrl(),
        source_relative_url = delivery.getSource(),
        destination_project_relative_url = delivery.getDestinationProject())
    if data_analysis is not None:
      data_analysis.setDefaultCausalityValue(delivery)
      data_analysis.setSpecialiseValueSet(data_analysis.getSpecialiseValueList() + data_supply_list)
      is_shared_data_analysis = True
    else:
      # Create Analysis
      data_analysis = portal.data_analysis_module.newContent(
                    portal_type = "Data Analysis",
                    title = transformation.getTitle(),
                    reference = delivery.getReference(),
                    start_date = delivery.getStartDate(),
                    stop_date = delivery.getStopDate(),
                    specialise_value_list = [transformation] + data_supply_list,
                    causality_value = delivery,
                    source = delivery.getSource(),
                    source_section = delivery.getSourceSection(),
                    source_project = delivery.getSourceProject(),
                    destination = delivery.getDestination(),
                    destination_section = delivery.getDestinationSection(),
                    destination_project = delivery.getDestinationProject())

    data_analysis.checkConsistency(fixit=True)
    # create input and output lines
    for transformation_line in transformation.objectValues(
        portal_type=["Data Transformation Resource Line",
                     "Data Transformation Operation Line"]):
      resource = transformation_line.getResourceValue()
      quantity = transformation_line.getQuantity()

      if isinstance(quantity, tuple):
        quantity = quantity[0]
      # In case of shared data anylsis only add additional input lines
      if is_shared_data_analysis and quantity > -1:
        continue

      aggregate_set = set()
      # manually add device to every line
      aggregate_set.add(movement.getAggregateDevice())

      # If it is batch processing we additionally get items from the other
      # batch movements and deliver the other batch movements
      if transformation_line.getUse() == "big_data/ingestion/batch" and \
        transformation_line.getPortalType() == \
          "Data Transformation Resource Line" and quantity < 0:
        batch_relative_url = movement.getAggregateDataIngestionBatch()

        if batch_relative_url is not None:
          related_movement_list = portal_catalog(
            portal_type="Data Ingestion Line",
            aggregate_relative_url=batch_relative_url,
            resource_relative_url = resource.getRelativeUrl())
            
          for related_movement in related_movement_list:
            #aggregate_set.update(related_movement.getAggregateSet())
            related_movement.getParentValue().deliver()


      # create new item based on item_type if it is not already aggregated
      aggregate_type_set = set(
        [portal.restrictedTraverse(a).getPortalType() for a in aggregate_set])
      for item_type in transformation_line.getAggregatedPortalTypeList():
        # if item is not yet aggregated to this line, search it by related project
        # and source If the item is a data configuration or a device configuration
        # then we do not care the workflow state nor the related resource, nor
        # the variation nor the related sensor. Data Array Lines are created
        # by Data Operation.

        if item_type not in aggregate_type_set:
        
          if item_type in portal.getPortalDeviceConfigurationTypeList() + portal.getPortalDataConfigurationTypeList():
            
            if item_type == "Status Configuration":
              item = None
            
            else:
              item = portal.portal_catalog.getResultValue(
                portal_type=item_type,
                #validation_state="validated",
                item_project_relative_url=delivery.getDestinationProject(),
                item_source_relative_url=delivery.getSource())
  
          elif item_type != "Data Array Line":
            
            item_query_dict = dict(
              portal_type=item_type,
              validation_state="validated",
              item_variation_text=transformation_line.getVariationText(),
              item_device_relative_url=movement.getAggregateDevice(),
              item_resource_uid=resource.getUid(),
              item_source_relative_url=data_analysis.getSource())

            if data_analysis.getDestinationProjectValue() is not None:
              item_query_dict["item_project_relative_url"] = data_analysis.getDestinationProject()
            item = portal.portal_catalog.getResultValue(**item_query_dict)
          
          #if transformation_line.getRelativeUrl() == "data_transformation_module/woelfel_r0331_statistic_raw":
          #  raise TypeError("JUST STOP")
          if item is None:
            module = portal.getDefaultModule(item_type)
            item = module.newContent(portal_type = item_type,
                              title = transformation.getTitle(),
                              reference = "%s-%s" %(transformation.getTitle(),
                                                    delivery.getReference()),
                              version = '001')
            try:
              item.validate()
            except AttributeError:
              pass
          aggregate_set.add(item.getRelativeUrl())

      data_analysis_line = data_analysis.newContent(
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
      # for intput lines of first level analysis set causality and specialise
      if quantity < 0 and delivery.getPortalType() == "Data Ingestion":
        data_analysis_line.edit(
          causality_value = delivery,
          specialise_value_list = data_supply_list)
    
    data_analysis.checkConsistency(fixit=True)
    try:
      data_analysis.start()
    except UnsupportedWorkflowMethod:
      pass
