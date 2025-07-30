"""
  This script is used in Ingestion Policy objects to parse provided by fluentd / ebulk reference.
  In this case it expects a reference in this format for example:

  'sensor1.product1' 

"""

sensor_reference = reference.split('.')[0]
data_product_reference = reference.split('.')[1]
return {'resource_reference' : data_product_reference,
        'specialise_reference': sensor_reference,
        'reference': sensor_reference   }
