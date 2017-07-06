/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80*/
/*global self, caches, fetch, Promise*/
(function (self, caches, fetch, Promise) {
  "use strict";

  var CACHE_VERSION = 1,
    CACHE_NAME = "todos-renderjs-" + CACHE_VERSION.toString();
  self.addEventListener("install", function (event) {
    event.waitUntil(caches.open(CACHE_NAME)
      .then(function (cache) {
        return fetch("officejs_todomvc.appcache")
          .then(function (cache_file) {
            return cache_file.text();
          })
          .then(function (text) {
            var relative_url_list = text.split('\r\n'),
              i,
              take = false;
            self.cache_list = [];
            if (relative_url_list.length === 1) {
              relative_url_list = text.split('\n');
            }
            if (relative_url_list.length === 1) {
              relative_url_list = text.split('\r');
            }
            for (i = 0; i < relative_url_list.length; i += 1) {
              if (relative_url_list[i].indexOf("NETWORK:") >= 0) {
                take = false;
              }
              if (take &&
                  relative_url_list[i] !== "" &&
                  relative_url_list[i].charAt(0) !== '#' &&
                  relative_url_list[i].charAt(0) !== ' ') {
                relative_url_list[i].replace("\r", "");
                self.cache_list.push(relative_url_list[i]);
              }
              if (relative_url_list[i].indexOf("CACHE:") >= 0) {
                take = true;
              }
            }
            return cache.addAll(self.cache_list);
          });
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

}(self, caches, fetch, Promise));