/*jslint indent: 2*/
/*global self, fetch, Request, Response */
var global = self, window = self;

(function (self, fetch, Request, Response) {
  "use strict";

  self.DOMParser = {};
  self.sessionStorage = {};
  self.localStorage = {};
  self.openDatabase = {};
  self.DOMError = {};
  self.postMessage = function () {return; };

  self.importScripts('development/rsvp.js', 'development/jiodev.js');

  self.storage = {};

  self.cache_list = [];

  function createStorage(database) {
    return self.jIO.createJIO({
      type: "indexeddb",
      database: database
    });
  }

  self.addEventListener('install', function (event) {
    event.waitUntil(self.skipWaiting());
  });
  self.addEventListener('activate', function (event) {
    event.waitUntil(self.clients.claim());
  });

  self.addEventListener("fetch", function (event) {
    var relative_url = event.request.url.split("#")[0]
      .replace(self.registration.scope, "")
      .replace(self.version_url, "");
    if (relative_url === "") {
      relative_url = "/";
    }
    if (relative_url === 'no-cache') {
      event.respondWith(new Response(self.cache_list));
      return;
    }
    event.respondWith(
      new self.RSVP.Queue()
        .push(function () {
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
        })
        .push(undefined, function (error) {
          if (error instanceof self.jIO.util.jIOError) {
            if (relative_url.indexOf('http') === -1) {
              if (self.cache_list.indexOf(relative_url) === -1) {
                self.cache_list.push(relative_url);
              }
            }
            return fetch(event.request);
          }
          return new Response(error, {"statusText": error.message, "status": 500});
        })
    );
  });

}(self, fetch, Request, Response));