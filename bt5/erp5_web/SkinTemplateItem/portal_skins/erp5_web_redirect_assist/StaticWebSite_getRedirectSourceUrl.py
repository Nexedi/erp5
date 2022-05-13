"""
================================================================================
Redirect to domain specified as layout property on website
================================================================================
"""
# parameters
# ------------------------------------------------------------------------------

INDEX = "index.html"
REQUEST = context.REQUEST
query_string = REQUEST["QUERY_STRING"]
redirect_domain = context.getLayoutProperty("redirect_domain")
redirect_url = redirect_domain
status_code = 301

if context.getLayoutProperty("use_moved_temporarily"):
  status_code = 302

try:
  source_path = REQUEST.other["source_path"]
  redirect_url = "/".join([redirect_url, source_path])
except(KeyError):
  source_path = None
  redirect_url = redirect_url + "/"

service_worker_to_unregister = context.getLayoutProperty("configuration_service_worker_url")
if (service_worker_to_unregister) and (source_path == service_worker_to_unregister) and (not query_string):
  # Do not redirect the service worker URL
  # instead, unregister it and force all clients to reload themself
  response = REQUEST.RESPONSE
  response.setHeader('Content-Type', 'application/javascript')
  return """/*jslint indent: 2*/
/*global self, Promise, caches*/
(function (self, Promise, caches) {
  "use strict";

  self.addEventListener('install', function (event) {
    event.waitUntil(self.skipWaiting());
  });

  self.addEventListener('activate', function (event) {
    event.waitUntil(
      caches
        .keys()
        .then(function (keys) {
          return Promise.all(
            keys
              .map(function (key) {
                return caches.delete(key);
              })
          );
        })
        .then(function () {
          return self.registration.unregister();
        })
        .then(function () {
          return self.clients.matchAll({type: 'window'});
        })
        .then(function (client_list) {
          var i,
            promise_list = [];
          for (i = 0; i < client_list.length; i += 1) {
            promise_list.push(client_list[i].navigate(client_list[i].url));
          }
          return Promise.all(promise_list);
        })
    );
  });

}(self, Promise, caches));
"""

if query_string:
  redirect_url = '?'.join([redirect_url, query_string])
if redirect_url.find(INDEX) > -1 and not redirect_url.endswith(INDEX):
  redirect_url = redirect_url.replace(INDEX, '')
if redirect_url.find(INDEX) > -1 and REQUEST['ACTUAL_URL'].find(INDEX) == -1:
  redirect_url = redirect_url.replace(INDEX, '')

return context.Base_redirect(redirect_url, status_code=status_code)
