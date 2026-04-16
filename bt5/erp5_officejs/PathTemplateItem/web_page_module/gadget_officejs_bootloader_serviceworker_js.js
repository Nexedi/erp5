/*jslint indent: 2*/
/*global self, fetch, Request, Response, URL, Blob */
// Version stamp injected by server-side text substitution.
// Changes when the BT is updated, triggering browser SW update check.
var APP_VERSION = '${modification_date}';
var global = self, window = self;

(function (self, fetch, Response, Blob) {
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

  self.importScripts('app/rsvp.js', 'app/jiodev.js');

  self.storage = {};

  self.cache_list = [];

  function getDatabasePrefix() {
    // Derive per-app IndexedDB prefix from the SW scope URL path.
    // On officejs.com subdomains, scope path is "/" -> empty prefix
    // (backward compatible). On ERP5 embedded, scope path is e.g.
    // "/erp5/web_site_module/officejs_text_editor/" -> prefix is
    // "officejs_text_editor_".
    var scope_path = new URL(self.registration.scope).pathname;
    var parts = scope_path.replace(/\/+$/, '').split('/');
    var site_id = parts[parts.length - 1];
    if (!site_id) {
      return "";
    }
    return site_id + "_";
  }

  function createStorage(database) {
    return self.jIO.createJIO({
      type: "indexeddb",
      database: database
    });
  }

  function getFromLocal(relative_url) {
    if (self.storage.get === undefined) {
      self.storage = createStorage(getDatabasePrefix() + "ojs_source_code");
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
    event.waitUntil(
      self.clients.claim()
        .then(function () {
          return self.clients.matchAll();
        })
        .then(function (client_list) {
          var i;
          for (i = 0; i < client_list.length; i += 1) {
            client_list[i].postMessage('version_changed');
          }
        })
    );
  });

  self.addEventListener("fetch", function (event) {
    var relative_url = './' + event.request.url.split("#")[0]
      .replace(self.registration.scope, "")
      .replace(self.version_url, ""),
      tmp;
    if (relative_url === './no-cache') {
      event.respondWith(new Response(self.cache_list));
      return;
    }
    else if (event.request !== undefined && event.request.referrer === self.registration.scope) {
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
    } else if (
      // postData from manifest.json
      event.request.method === 'POST' &&
        relative_url.split('?')[0].endsWith('postData')
    ) {
      self.request = event.request;
      event.respondWith(Response.redirect('.'));
    } else if (
      // Determine if it hasSharedData
      event.request.url.endsWith('hasSharedData')
    ) {
      event.respondWith(new Response(self.request ? "true" : "false"));
    } else if (
      // getSharedData from upload_shared_file page
      // upload_shared_file page processes the data
      event.request.url.endsWith('getSharedData') &&
        event.request.method === 'GET'
    ) {
      if (!self.request) {
        event.respondWith(new Response(''));
      } else {
        tmp = self.request;
        delete self.request;
        event.respondWith(
          new self.RSVP.Queue()
            .push(function () {
              return tmp.formData();
            })
            .push(function (data) {
              return data.get('file');
            })
            .push(function (file) {
              return new Response(new Blob([file], {type: file.type}));
            })
        );
      }
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

}(self, fetch, Response, Blob));