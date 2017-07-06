/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80*/
/*global self, caches, fetch, Request, Promise*/
(function (self, caches, fetch, Request, Promise) {
  "use strict";

  var CACHE_VERSION = 1,
    CACHE_NAME = "todos-renderjs-" + CACHE_VERSION.toString();
  self.addEventListener("install", function (event) {
    event.waitUntil(caches.open(CACHE_NAME)
      .then(function (cache) {
        return fetch(new Request(
          "officejs_todomvc.appcache",
          {
            method: 'GET',
            headers: {
              'Upgrade-Insecure-Requests': 1
            }
          }))
          .then(function (cache_file) {
            return cache_file.text();
          })
          .then(function (text) {
            var relative_url_list = text.split('\r\n'),
              i,
              take = false;
            self.cache_list = [];
            self.console.log(text);
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
            self.console.log(self.cache_list);
            return cache.addAll(self.cache_list);
          });
      })
      .catch(function (error) {
        self.console.log(error);
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

}(self, caches, fetch, Request, Promise));