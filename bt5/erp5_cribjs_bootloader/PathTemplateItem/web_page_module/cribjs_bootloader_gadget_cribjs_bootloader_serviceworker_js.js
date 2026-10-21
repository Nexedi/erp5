/*jslint indent: 2*/
/*global self, fetch, Request, Response, URL */
var global = self, window = self;

(function (self, fetch, Response) {
  "use strict";

  self.DOMParser = {};
  self.sessionStorage = {};
  self.localStorage = {};
  self.openDatabase = {};
  self.DOMError = {};
  self.Node = {};
  self.XMLSerializer = Object;
  self.DOMParser = Object;
  self.postMessage = function () {return; };

  self.importScripts('rsvp.js', 'jiodev.js');

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
    event.waitUntil(self.skipWaiting());
  });
  self.addEventListener('activate', function (event) {
    event.waitUntil(self.clients.claim());
  });

  self.addEventListener("fetch", function (event) {
    var relative_url = decodeURI(event.request.url.split("#")[0])
      .replace(self.registration.scope, "");
    if (relative_url[relative_url.length - 1] === "/" || relative_url === "") {
      relative_url = relative_url + "index.html";
    }
    if (relative_url === './no-cache') {
      event.respondWith(new Response(self.cache_list));
      return;
    }
    if (event.request !== undefined &&
        new URL(event.request.url).hostname !== window.location.hostname) {
      event.respondWith(
        new self.RSVP.Queue()
          .push(function () {
            return fetch(event.request);
          })
          .push(undefined, function (error) {
            if (error.name === 'TypeError' &&
                error.message === 'Failed to fetch') {
              return {};
            }
            throw error;
          })
          .push(function (response) {
            if (response.status === 200) {
              return response;
            }
            return getFromLocal(relative_url);
          })
          .push(undefined, function (error) {
            return new Response(error, {"statusText": error.message, "status": 500});
          })
      );
    } else {
      event.respondWith(
        new self.RSVP.Queue()
          .push(function () {
            return getFromLocal(relative_url);
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
    }
  });

}(self, fetch, Response));
