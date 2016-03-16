portal = context.getPortalObject()
promise_url = portal.getPromiseParameter('external_service', 'kumofs_url')

protocol, promise_url = promise_url.split('://', 1)

domain_port = promise_url.split('/', 1)[0]
port = domain_port.split(':')[-1]
domain = domain_port[:-(len(port)+1)]

portal.portal_memcached.persistent_memcached_plugin.edit(url_string="%s:%s" % (domain, port))
