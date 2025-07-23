"""
  This script is used in Ingestion Policy objects to parse provided by fluentd / ebulk reference.
  In this case it expects a reference in this format for example:

  'sensor1' 

  i.e. no special characters and one name only.

  If you need to use more complex hierachical reference notations like:

  'sensor1.product1' 

  you can use script: 'IngestionPolicy_parseSimpleIngestionTag'
 
"""

project_reference = reference.split('.')[0]
return {'resource_reference' : reference,
        'specialise_reference': project_reference,
        'reference': project_reference   }
