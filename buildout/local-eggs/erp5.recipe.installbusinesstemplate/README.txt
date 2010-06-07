Business Templates installer through XML-RPC
================================================

Easy way to install Business Templates

[install-business-templates]
recipe = erp5.recipe.installbusinesstemplate
repository_path = file://${bt5list:location}
bt5_list = ${bt5list:bt5_urls}
update_catalog = auto
protocol = http
user = ${zope-instance:user}
hostname = ${zope-instance:ip-address}
port = ${zope-instance:http-address}
portal_id = ${zope-instance:portal_id}


repository_path    folder which contains bt5list xml file
bt5_list           ordered list of business template to install
update_catalog     parameter to pass for each business template
                   - auto: update catalog if needed (default)
                   - false: never update catalog
