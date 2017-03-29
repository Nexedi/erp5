/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80*/
/*global self, caches, fetch*/
(function (self, caches, fetch) {
  "use strict";

  var CACHE_VERSION = 1,
    CACHE_NAME = "todos-renderjs-" + CACHE_VERSION.toString();
  self.addEventListener("install", function (event) {
    event.waitUntil(caches.open(CACHE_NAME)
      .then(function (cache) {
        return cache.addAll([
          "./",
          "rsvp.js",
          "renderjs.js",
          "jiodev.js",
          "handlebars.js",
          "officejs_todomvc_icon.svg?format=svg",
          "officejs_todomvc_icon.png?format=png",
          "officejs_todomvc.css",
          "officejs_todomvc_gadget_index.html",
          "officejs_todomvc_gadget_index.js",
          "officejs_todomvc_gadget_model.html",
          "officejs_todomvc_gadget_model.js",
          "officejs_todomvc_gadget_router.html",
          "officejs_todomvc_gadget_router.js"
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