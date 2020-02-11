/*jslint indent: 2*/
/*global self, caches, fetch, Promise, URL, location, JSON*/
(function (self, caches, fetch, Promise, URL, location, JSON) {
  "use strict";

  var prefix = location.toString() + '_',
    CACHE_NAME = prefix + '${modification_date}',
    REQUIRED_FILES = JSON.parse('${required_url_list}'),
    required_url_list = [],
    i,
    len = REQUIRED_FILES.length;

  for (i = 0; i < len; i += 1) {
    required_url_list.push(
      new URL(REQUIRED_FILES[i], location.toString()).toString()
    );
  }

  self.addEventListener('install', function (event) {
    // Perform install step:  loading each required file into cache
    event.waitUntil(
      caches.open(CACHE_NAME)
        .then(function (cache) {
          var promise = Promise.resolve();

          function append(url_to_cache) {
            promise = promise
              .then(function () {
                // Use cache.add because safari does not support cache.addAll.
                return cache.add(url_to_cache);
              });
          }

          len = required_url_list.length;
          for (i = 0; i < len; i += 1) {
            // Add all offline dependencies to the cache
            // One by one, to not hammer zopes
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

  self.addEventListener('fetch', function (event) {
    var url = new URL(event.request.url);
    url.hash = '';
    if ((event.request.method !== 'GET') ||
        (required_url_list.indexOf(url.toString()) === -1)) {
      // Try not to use the untrustable fetch function
      // It can only be skip synchronously
      return;
    }
    return event.respondWith(
      caches.open(CACHE_NAME)
        .then(function (cache) {
          // Don't give request object itself. Firefox's Cache Storage
          // does not work properly when VARY contains Accept-Language.
          // Give URL string instead, then cache.match works on both Firefox and Chrome.
          return cache.match(event.request.url);
        })
        .then(function (response) {
          // Cache hit - return the response from the cached version
          if (response) {
            return response;
          }
          // Not in cache - return the result from the live server
          // `fetch` is essentially a "fallback"
          return fetch(event.request);
        })
    );
  });

  self.addEventListener("activate", function (event) {
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
          var i,
            len = client_list.length;
          for (i = 0; i < len; i += 1) {
            client_list[i].postMessage('claim');
          }

        })
    );
  });

}(self, caches, fetch, Promise, URL, location, JSON));