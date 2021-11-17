/*jslint indent: 2*/
/*global self, fetch, Request, Response, URL, Blob, caches, location, console */
var global = self, window = self;

(function (self, fetch, Response, Blob, caches, location) {
  "use strict";

  var required_url_list = [],
    CACHE_NAME = location.toString() + '_v1';
  self.DOMParser = {};
  self.sessionStorage = {};
  self.localStorage = {};
  self.openDatabase = {};
  self.DOMError = {};
  self.Node = {};
  self.XMLSerializer = Object;
  self.DOMParser = Object;
  self.postMessage = function () {return; };

  //self.importScripts('app/rsvp.js', 'app/jiodev.js');

  self.storage = {};

  self.cache_list = [];

  self.addEventListener('install', function (event) {
    console.log("(ROOT SW) Bootloader Service Worker INSTALL. event:", event);
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

          var i, len = required_url_list.length;
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
    /*if ((event.request.method !== 'GET') ||
        (required_url_list.indexOf(url.toString()) === -1)) {
      // Try not to use the untrustable fetch function
      // It can only be skip synchronously
      return;
    }*/
    var relative_url = './' + event.request.url.split("#")[0]
      .replace(self.registration.scope, "")
      .replace(self.version_url, "");
    console.log("relative_url:", relative_url);
    return event.respondWith(
      caches.open(CACHE_NAME)
        .then(function (cache) {
          console.log("checking if in cache...");
          // Don't give request object itself. Firefox's Cache Storage
          // does not work properly when VARY contains Accept-Language.
          // Give URL string instead, then cache.match works on both Firefox and Chrome.
          return cache.match(event.request.url);
        })
        .then(function (response) {
          // Cache hit - return the response from the cached version
          if (response) {
            console.log("response from cache !!");
            return response;
          }
          // Not in cache - return the result from the live server
          // `fetch` is essentially a "fallback"
          console.log("no response from cache. fetching url from live server");
          console.log("TODO: save response in cache");
          return fetch(event.request);
        })
    );
  });

}(self, fetch, Response, Blob, caches, location));