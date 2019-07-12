from DateTime import DateTime
portal = context.getPortalObject()
portal_catalog = portal.portal_catalog
from Products.ERP5Type.Log import log

now = DateTime()
query_dict = {
  "portal_type": "Data Ingestion Line",
  "resource_portal_type": "Data Product",
  "simulation_state": "stopped"
}

for line_data_ingestion in portal_catalog(**query_dict):
  data_ingestion = line_data_ingestion.getParentValue()
  # Get applicable transformation
  for transformation in portal_catalog(
                  portal_type = "Data Transformation",
                  validation_state = "validated",
                  resource_relative_url = line_data_ingestion.getResource()):
    # Create Analysis
    try:
      try:
        data_analysis = portal.data_analysis_module.newContent(
                      portal_type = "Data Analysis",
                      id = data_ingestion.getId(),
                      title = "%s - %s" %(transformation.getTitle(),data_ingestion.getTitle()),
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
      except Exception as e:
        #log(''.join(["[WARNING] Data Analysis already created: ", str(e)]))
        data_analysis = None

      if data_analysis is not None:
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
          if line_data_ingestion.getAggregateDevice() is not None:
            aggregate_set.add(line_data_ingestion.getAggregateDevice())
          if line_data_ingestion.getAggregateDeviceConfiguration() is not None:
            aggregate_set.add(line_data_ingestion.getAggregateDeviceConfiguration())
          if transformation_line.getPortalType() == "Data Transformation Resource Line":
            # at the moment, we only check for positive or negative quantity
            if quantity < 0:
              # it is an input line. If it is an input resource line, then we search for an
              # ingestion line with the same resource. If it is an operation line
              # then we search for an ingestion line with resource portal type Data Product
              related_lines_list = portal_catalog(
                portal_type="Data Ingestion Line",
                simulation_state="stopped",
                resource_relative_url = resource.getRelativeUrl())
              for related_line in related_lines_list:
                if(related_line.getParentValue().getReference() == data_ingestion.getReference() and related_line.getParentValue().getSimulationState() == "stopped"):
                  aggregate_set.update(related_line.getAggregateSet())
                  related_line.getParentValue().deliver()
            else:
              # it is an output line
              # create new item based on item_type: data array, stream, descriptor, etc.
              item_type = resource.getAggregatedPortalType()
              module = portal.getDefaultModule(item_type)
              item = module.newContent(portal_type = item_type,
                                title = data_ingestion.getTitle(),
                                id = data_ingestion.getId(),
                                reference = data_ingestion.getReference(),
                                version = '001')
              if "Data Descriptor" not in item_type:
                item.validate()
              aggregate_set = set()
              aggregate_set.add(item)

          data_analysis.newContent(
            portal_type = "Data Analysis Line",
            title = transformation_line.getTitle(),
            reference = transformation_line.getReference(),
            int_index = transformation_line.getIntIndex(),
            resource_value = resource,
            quantity = quantity,
            quantity_unit = transformation_line.getQuantityUnit(),
            aggregate_value_set = aggregate_set)

        data_analysis.plan()
    except Exception as e:
      context.logEntry("[ERROR] Error creating Data Analysis for Data Ingestion '%s' (ID: %s): %s" % (data_ingestion.getReference(), data_ingestion.getId(), str(e)))
