"""
  This is hard coded for an instance.
"""

# NEO CLONE
CLONE1_NEO =  ('[<IPV6_address_of_NEO_Clone>]:2051', '<name_of_neo_cluster>',)
etc_folder = '<path_to_folder_containing_ssl_certificates>'

node_list = [CLONE1_NEO]
ca_file =  '%s/ca.crt' %etc_folder
cert_file = '%s/neo.crt' %etc_folder
key_file =  '%s/neo.key' %etc_folder

return [node_list, [ca_file, cert_file, key_file]]
