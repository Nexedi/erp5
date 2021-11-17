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

  function createStorage(database) {
    return self.jIO.createJIO({
      type: "indexeddb",
      database: database
    });
  }

  function getFromLocal(relative_url) {
    if (self.storage.get === undefined) {
      self.storage = createStorage("ojs_source_code");
    }
    return self.storage.getAttachment(self.registration.scope, relative_url)
      .push(function (blob) {
        return new Response(blob, {
          'headers': {
            'content-type': blob.type
          }
        });
      });
  }

  self.addEventListener('install', function (event) {
    console.log("(ROOT SW) Bootloader Service Worker INSTALL");
    event.waitUntil(self.skipWaiting());
  });
  self.addEventListener('activate', function (event) {
    console.log("(ROOT SW) Bootloader Service Worker ACTIVATE");
    event.waitUntil(self.clients.claim());
  });

  self.addEventListener('fetch', function (event) {
    var url = new URL(event.request.url);
    url.hash = '';
    console.log("");
    console.log("(ROOT SW) Bootloader Service Worker FETCH url:", url);
    /*if ((event.request.method !== 'GET') ||
        (required_url_list.indexOf(url.toString()) === -1)) {
      // Try not to use the untrustable fetch function
      // It can only be skip synchronously
      return;
    }*/
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
            console.log("GOT response from CACHE");
            return response;
          }
          // Not in cache - return the result from the live server
          // `fetch` is essentially a "fallback"
          console.log("no response from cache, FETCH from live server");
          return fetch(event.request);
        })
    );
  });

}(self, fetch, Response, Blob, caches, location));