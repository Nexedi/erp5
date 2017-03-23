/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80*/
/*globals self, caches, fetch*/
(function (self, caches, fetch) {
  "use strict";

  var CACHE_VERSION = 2,
    CACHE_NAME = "todos-renderjs-" + CACHE_VERSION.toString();
  self.addEventListener("install", function (event) {
    event.waitUntil(caches.open(CACHE_NAME)
      .then(function (cache) {
        return cache.addAll([
          "./",
          "rsvp.js",
          "renderjs.js",
          "jio.js",
          "handlebars.js",
          "launcher_icon.png",
          "base.css",
          "index.css",
          "index.html",
          "index.js",
          "gadget_model.html",
          "gadget_model.js",
          "gadget_router.html",
          "gadget_router.js"
        ]);
      })
      .then(function () {
        return self.skipWaiting();
      }));
  });

  self.addEventListener("fetch", function (event) {
    event.respondWith(caches.match(event.request)
      .then(function (response) {
        return response || fetch(event.request);
      }));
  });

  self.addEventListener("activate", function (event) {
    event.waitUntil(caches.keys()
      .then(function (keys) {
        return Promise.all(keys
          .filter(function (key) {
            return key !== CACHE_NAME;
          })
          .map(function (key) {
            return caches.delete(key);
          }));
      })
      .then(function () {
        self.clients.claim();
      }));
  });

}(self, caches, fetch));