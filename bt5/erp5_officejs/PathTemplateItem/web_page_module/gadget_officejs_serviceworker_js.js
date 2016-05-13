/*jslint indent: 2*/
/*global self, caches, importScripts, fetch, Promise, Request, Response, jIO, console*/
var global = self,
  window = self;
(function (self, caches, fetch) {
  "use strict";

  self.DOMParser = {};
  self.sessionStorage = {};
  self.localStorage = {};
  self.openDatabase = {};
  importScripts('rsvp.js', 'jiodev.js');

  Response.prototype.metadata = function () {
    return {
      //'ok': this.ok
      url: this.url,
      headers: Array.from(this.headers.entries())
    };
  };

  Response.prototype.metadata_w_blob = function () {
    var metadata = this.metadata();
    return this.blob().then(function (blob) {
      return Promise.resolve({
        'blob': blob,
        'metadata': metadata
      });
    });
  };

  self.jio_cache_storage = jIO.createJIO({
    type: "uuid",
    sub_storage: {
      "type": "indexeddb",
      "database": self.CACHE_NAME
    }
  });

  self.jio_cache_install = function (event) {
    // debugger;
    // Perform install step:  loading each required file into cache
    // create a new jio
    var requests = self.CACHE_REQUIRED_FILES.map(function (file_name) {
          return new Request(file_name);
        });

    event.waitUntil(
      Promise.all(requests.map(function (request) {
        return fetch(request).then(function (response) {
          return response.metadata_w_blob();
        });
      }))
      .then(function (responses) {
        return Promise.all(
          responses.map(function (response, i) {
            return new Promise(function (resolve, reject) {
              var jio_key = requests[i].url;
              self.jio_cache_storage.put(jio_key, response.metadata)
              .push(function () {
                return self.jio_cache_storage.putAttachment(
                  jio_key,
                  "body",
                  response.blob
                )
                .push(function () {
                  console.log('jio_save: ' + jio_key);
                  resolve();
                });
              })
              .push(undefined, function (error) {
                console.log(error);
                reject();
              });
            })
            .then(undefined, console.log);
          })
        )
        .then(function () {
          console.log('cache loaded');
          return self.skipWaiting();
        })
        .then(undefined, console.log);
      })
    );
  };

  self.jio_cache_fetch = function (event) {
    var jio_key = event.request.url;
    event.respondWith(new Promise(function (resolve, reject) {
        self.jio_cache_storage.get(jio_key)
        .push(function (metadata) {
          return self.jio_cache_storage.getAttachment(jio_key, 'body')
          .push(function (body) {
            //console.log(metadata.url + ' return from jio');
            resolve(new Response(body, {'headers': metadata.headers}));
          });
        })
        .push(undefined, function (error) {
          if (error.status_code == 404)
            console.log(jio_key + ' not found in cache');
          else {
            console.log(jio_key);
            console.log(error);
          }
          resolve(fetch(event.request));
        });
      })
      .then(undefined, function (error) {
        console.log(error);
      })
    );
  };

  self.jio_cache_activate = function (event) {
    /* Just like with the install event, event.waitUntil blocks activate on a promise.
     Activation will fail unless the promise is fulfilled.
    */
    event.waitUntil(self.clients.claim());
  };

  self.addEventListener('install', self.jio_cache_install);
  self.addEventListener('fetch', self.jio_cache_fetch);
  self.addEventListener("activate", self.jio_cache_activate);

}(self, caches, fetch));
