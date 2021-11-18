/*jslint indent: 2*/
/*global self, fetch, Request, Response, URL, Blob, caches, location, console */
var global = self, window = self;

(function (self, fetch, Response, Blob, caches, location) {
  "use strict";

  var required_url_list = [],
    CACHE_NAME = location.toString() + '_v1',
    REQUIRED_FILES = [
      "/",
      "rsvp.js",
      "renderjs.js",
      "jiodev.js",
      "officejs-redirect.js",
      "favicon.ico"
    ],
    i,
    len = REQUIRED_FILES.length;

  for (i = 0; i < len; i += 1) {
    required_url_list.push(
      new URL(REQUIRED_FILES[i], location.toString()).toString()
    );
  }

  self.addEventListener('install', function (event) {
    console.log("(ROOT SW) Root Service Worker INSTALL");
    
    //TODO: in real appstore server this could be just the required file "/"
    //but for dev it is necessary to get the root app url like this
    var app_url = window.location.href.replace("gadget_officejs_root_serviceworker.js", "");
    console.log("app_url:", app_url);
    required_url_list.push(app_url);
    
    // Perform install step:  loading each required file into cache
    event.waitUntil(
      caches.open(CACHE_NAME)
        .then(function (cache) {
          // Add all offline dependencies to the cache, one by one, to not
          // hammer zopes.
          var promise = Promise.resolve();

          function append(url_to_cache) {
            promise = promise
              .then(function () {
                return cache.add(url_to_cache);
              });
          }
          len = required_url_list.length;
          for (i = 0; i < len; i += 1) {
            append(required_url_list[i]);
          }
          return promise;
        })
        .then(function () {
          // When user accesses ERP5JS web site first time, service worker is
          // installed but it is not activated yet, service worker is activated
          // when the page is refreshed or when a new tab opens the site again.
          // If user does not refresh the page and continue to use the site,
          // user can't use cache, so everything becomes slow. We must avoid this
          // situation.
          // So, we want to activate the new service worker immediately if it was
          // the first one.
          return self.skipWaiting();
        })
        .catch(function (error) {
          // Since we do not allow to override existing cache, if cache installation
          // failed, we need to delete the cache completely.
          caches.delete(CACHE_NAME);
          throw error;
        })
    );
  });

  self.addEventListener('activate', function (event) {
    console.log("(ROOT SW) Bootloader Service Worker ACTIVATE. event:", event);
    event.waitUntil(self.clients.claim());
  });

  self.addEventListener('fetch', function (event) {
    var url = new URL(event.request.url);
    url.hash = '';
    console.log("");
    console.log("(ROOT SW) FETCH url:", url.href);
    if ((event.request.method !== 'GET') ||
        (required_url_list.indexOf(url.toString()) === -1)) {
      // Try not to use the untrustable fetch function
      // It can only be skip synchronously
      return;
    }
    console.log("event.request.url:", event.request.url);
    return event.respondWith(
      caches.open(CACHE_NAME)
        .then(function (cache) {
          console.log("checking if in cache...");
          // Don't give request object itself. Firefox's Cache Storage
          // does not work properly when VARY contains Accept-Language.
          // Give URL string instead, then cache.match works on any browser
          return cache.match(event.request.url);
        })
        .then(function (response) {
          // Cache hit - return the response from the cached version
          if (response) {
            console.log("response from cache !!");
            return response;
          }
          // No cache - return the response from live server
          console.log("no response from cache. fetching url from live server");
          return fetch(event.request);
          /* NO NEED TO CACHE HERE, ALREADY DONE IN INSTALL
          var fetchRequest = event.request.clone();
          return fetch(fetchRequest).then(
            function (response) {
              console.log("server response:", response);
              // Check if we received a valid response
              if (!response || response.status !== 200 || response.type !== 'basic') {
                console.log("server response with error");
                return response;
              }
              var responseToCache = response.clone();
              console.log("adding response to cache");
              caches.open(CACHE_NAME)
                .then(function (cache) {
                  cache.put(event.request, responseToCache);
                });

              return response;
            }
          );*/
        })
    );
  });

}(self, fetch, Response, Blob, caches, location));