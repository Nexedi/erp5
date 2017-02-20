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

  self.importScripts('rsvp.js', 'jiodev.js');

  self.storage = {};

  self.cache_list = [];

  function createStorage(database) {
    return self.jIO.createJIO({
      type: "uuid",
      sub_storage: {
        type: "indexeddb",
        database: database
      }
    });
  }

  self.setting_storage = createStorage("serviceWorker_settings");

  self.addEventListener('install', function (event) {
    event.waitUntil(self.skipWaiting());
  });
  self.addEventListener('activate', function (event) {
    event.waitUntil(self.clients.claim());
  });

  self.addEventListener("fetch", function (event) {
    var relative_url = event.request.url.replace(self.registration.scope, "")
      .replace(self.version_url, "");
    if (relative_url === "") {
      relative_url = "/";
    }
    if (relative_url.indexOf("ooffice/") !== -1) {
      if (self.cache_list.indexOf(relative_url) < 0) {
        self.cache_list.push(relative_url);
      }
    }
    event.respondWith(
      new self.RSVP.Queue()
        .push(function () {
          if (self.storage.get === undefined) {
            self.storage = createStorage("officejs_code_source");
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
          self.console.log(
            "Relative_Url: ",
            relative_url,
            "\nCause: ",
            error.message
          );
          if (relative_url === "cache_file_list") {
            self.cache_list.sort();
            return new Response(self.cache_list.join('<br>'), {
              'headers': {
                'content-type': 'text/html'
              }
            });
          }
          return fetch(event.request);
        })
    );
  });

}(self, fetch, Request, Response));