/*jslint indent: 2*/
/*global self, caches, fetch, Promise, URL, location, Response, console*/
(function (self, caches, fetch, Promise, URL, location, Response) {
  "use strict";

  var prefix = location.toString() + '_',
    // CLIENT_CACHE_MAPPING_NAME must not start with `prefix`
    // else it may be used as a normal content cache.
    CLIENT_CACHE_MAPPING_NAME = '__erp5js_' + location.toString(),
    CACHE_NAME = prefix + '_0014',
    CACHE_MAP = {},
    // Files required to make this app work offline
    REQUIRED_FILES = [
    ],
    required_url_list = [],
    i;

  for (i = 0; i < REQUIRED_FILES.length; i += 1) {
    required_url_list.push(
      new URL(REQUIRED_FILES[i], location.toString()).toString()
    );
  }
  self.addEventListener('install', function (event) {
    // Perform install step:  loading each required file into cache
    event.waitUntil(
      // We create cache only if it does not exist. That is because
      // we do not want to override an existing cache by mistake.
      // Code consistency is very important. We must not mix different
      // versions of code.
      // (For example, developer change service worker code and forget
      // to increase the cache version.)
      caches.has(CACHE_NAME)
        .then(function (result) {
          if (!result) {
            caches.open(CACHE_NAME)
              .then(function (cache) {
                // Add all offline dependencies to the cache
                return Promise.all(
                  required_url_list
                    .map(function (url) {
                      /* Return a promise that's fulfilled
                         when each url is cached.
                      */
                      // Use cache.add because safari does not support cache.addAll.
                      // console.log("Install " + CACHE_NAME + " = " + url);
                      return cache.add(url);
                    })
                );
              })
              .then(function () {
                return caches.keys();
              })
              .then(function (keys) {
                keys = keys.filter(function (key) {return key.startsWith(prefix); });
                if (keys.length === 1) {
                  // When user accesses ERP5JS web site first time, service worker is
                  // installed but it is not activated yet, service worker is activated
                  // when the page is refreshed or when a new tab opens the site again.
                  // If user does not refresh the page and continue to use the site,
                  // user can't use cache, so everything becomes slow. We must avoid this
                  // situation.
                  // So, we want to activate the new service worker immediately if it was
                  // the first one. (We must not activate the new service worker by
                  // skipWaiting if there is already an active service worker because it
                  // causes code inconsistency by loading code from a different version of
                  // cache.
                  // If there is only one cache, it means that this is the first service worker,
                  // thus we can do skipWaiting. And self.registration is unreliable on
                  // Firefox, we can't use self.registration.active
                  return self.skipWaiting();
                }
              })
              .catch(function (error) {
                // Since we do not allow to override existing cache, if cache installation
                // failed, we need to delete the cache completely.
                caches.delete(CACHE_NAME);
                // Explicitly unregister service worker else it may not be done.
                self.registration.unregister();
                throw error;
              });
          }
        })
    );
  });

  self.addEventListener('fetch', function (event) {
    /* When a new service worker is installed, it adds a new Cache
       to Cache Storage. When a new client started using this
       service worker, the new client uses the latest Cache at
       that time by comparing with Cache keys. And once the client
       is associated with a Cache key, it keeps using the same Cache
       key, it must not use different Caches. Since service worker
       is stateless, to maintain the mapping of client and Cache key,
       we use Cache Storage as a persistent data store. The key of
       this special Cache is CLIENT_CACHE_MAPPING_NAME.
    */
    var url = new URL(event.request.url),
      client_id = event.clientId.toString(),
      // CACHE_MAP is a temprary data store.
      // This should be kept until service worker stops.
      cache_key,
      erp5js_cache;
    url.hash = '';
    if (client_id) {
      // client_id is null when it is the first request, in other words
      // if request is navigate mode. Since major web browsers already
      // implement client_id, if client_is is null, let's use the latest cache
      // and don't get cache_key from CACHE_MAP and erp5js_cache.
      cache_key = CACHE_MAP[client_id];
    }
    // console.log("Client Id = " + client_id);
/*
    if (cache_key) {
      console.log("cache_key from CACHE_MAP " + cache_key);
    }
*/
    if ((event.request.method !== 'GET') ||
        (required_url_list.indexOf(url.toString()) === -1)) {
      // Try not to use the untrustable fetch function
      // It can only be skip synchronously
      return;
    }
    return event.respondWith(
      Promise.resolve()
        .then(function () {
          if (!cache_key) {
            // CLIENT_CACHE_MAPPING_NAME stores cache_key of each client.
            return caches.open(CLIENT_CACHE_MAPPING_NAME)
              .then(function (cache) {
                // Service worker forget everything when it stops. So, when it started
                // again, CACHE_MAP is empty, get the associated cache_key from the
                // special Cache named CLIENT_CACHE_MAPPING_NAME.
                erp5js_cache = cache;
                return erp5js_cache.match(client_id)
                  .then(function (response) {
                    if (response) {
                      // We use Cache Storage as a persistent database.
                      cache_key = response.statusText;
                      CACHE_MAP[client_id] = cache_key;
                      // console.log("cache_key from Cache Storage " + cache_key);
                    }
                  });
              });
          }
        })
        .then(function () {
          if (!cache_key) {
            // If associated cache_key is not found, it means this client is a new one.
            // Let's find the latest Cache.
            return caches.keys()
              .then(function (keys) {
                keys = keys.filter(function (key) {return key.startsWith(prefix); });
                // console.log("KEYS = " + keys);
                if (keys.length) {
                  cache_key = keys.sort().reverse()[0];
                  if (client_id) {
                    CACHE_MAP[client_id] = cache_key;
                  }
                } else {
                  cache_key = CACHE_NAME;
                  if (client_id) {
                    CACHE_MAP[client_id] = CACHE_NAME;
                  }
                }
                // Save the associated cache_key in a persistent database because service
                // worker forget everything when it stops.
                if (client_id) {
                  erp5js_cache.put(client_id, new Response(null, {"statusText": cache_key}));
                }
              });
          }
        })
        .then(function () {
          // Finally we have the associated cache_key. Let's find a cached response.
          return caches.open(cache_key);
        })
        .then(function (cache) {
          // Don't give request object itself. Firefox's Cache Storage
          // does not work properly when VARY contains Accept-Language.
          // Give URL string instead, then cache.match works on both Firefox and Chrome.
          // console.log("MATCH " + cache_key + " " + url);
          return cache.match(event.request.url);
        })
        .then(function (response) {
          // Cache hit - return the response from the cached version
          if (response) {
            return response;
          }
          // Not in cache - return the result from the live server
          // `fetch` is essentially a "fallback"
          // console.log("MISS " + cache_key + " " + url);
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
          keys = keys
            .filter(function (key) {
              // Filter by keys that don't start with the latest version prefix.
              return key.startsWith(prefix);
            })
            .sort();
          keys = keys.slice(0, keys.findIndex(function (element) {return element === CACHE_NAME; }));
          // We return a promise that settles when all outdated caches are deleted.
          return Promise.all(
            keys
              .map(function (key) {
                /* Return a promise that's fulfilled
                   when each outdated cache is deleted.
                */
                return caches.delete(key);
              })
          );
        })
        .then(function () {
          // If new service worker becomes active, it means that all clients
          // (tabs, windows, etc) were already closed. Thus we can remove the
          // client cache mapping.
          caches.delete(CLIENT_CACHE_MAPPING_NAME);
        })
    );
  });

}(self, caches, fetch, Promise, URL, location, Response));