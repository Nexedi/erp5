Business Templates installer through XML-RPC
================================================

Easy way to install Business Templates

[install-business-templates]
recipe = erp5.recipe.installbusinesstemplate
repository_path = file://${bt5list:location}
bt5_list = ${bt5list:bt5_urls}
update_catalog = false
protocol = http
user = ${zope-instance:user}
hostname = ${zope-instance:ip-address}
port = ${zope-instance:http-address}
portal_id = ${zope-instance:portal_id}