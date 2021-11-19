/*jslint indent: 2*/
/*global self, fetch, URL, caches, location, Promise */
var global = self, window = self;

(function (self, fetch, URL, caches, location, Promise) {
  "use strict";

  var required_url_list = [],
    prefix = location.origin.toString() + '_',
    CACHE_NAME = prefix + '${modification_date}',
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
    console.log("(ROOT SW) Root Service Worker INSTALL. CACHE_NAME:", CACHE_NAME);
    //var app_hash = new URL(location).searchParams.get('appHash');
    //TODO: in real appstore server this could be just the required file "/"
    //but for dev it is necessary to get the root app url like this
    var app_url = window.location.href.replace("gadget_officejs_root_serviceworker.js", "");
    required_url_list.push(app_url);
    console.log("required_url_list:", required_url_list);
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

  /*self.addEventListener('activate', function (event) {
    console.log("(ROOT SW) Bootloader Service Worker ACTIVATE. CACHE_NAME:", CACHE_NAME);
    event.waitUntil(self.clients.claim());
  });*/
  self.addEventListener("activate", function (event) {
    console.log("(ROOT SW) Bootloader Service Worker ACTIVATE. CACHE_NAME:", CACHE_NAME);
    /* Just like with the install event, event.waitUntil blocks activate on a promise.
     Activation will fail unless the promise is fulfilled.
    */
    event.waitUntil(
      caches
        /* This method returns a promise which will resolve to an array of available
           cache keys.
        */
        .keys()
        .then(function (keys) {
          // We return a promise that settles when all outdated caches are deleted.
          return Promise.all(
            keys
              .filter(function (key) {
                // Filter by keys that don't start with the latest version prefix.
                // return !key.startsWith(version);
                return ((key !== CACHE_NAME) &&
                        key.startsWith(prefix));
              })
              .map(function (key) {
                console.log("deleting cache key:", key);
                /* Return a promise that's fulfilled
                   when each outdated cache is deleted.
                */
                return caches.delete(key);
              })
          );
        })
        .then(function () {
          return self.clients.claim();
        })
        .then(function () {
          return self.clients.matchAll();
        })
        .then(function (client_list) {
          // Notify all clients that they can reload the page
          var j,
            client_len = client_list.length;
          for (j = 0; j < client_len; j += 1) {
            client_list[j].postMessage('claim');
          }

        })
    );
  });

  self.addEventListener('fetch', function (event) {
    var url = new URL(event.request.url);
    url.hash = '';
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
        })
    );
  });

}(self, fetch, URL, caches, location, Promise));