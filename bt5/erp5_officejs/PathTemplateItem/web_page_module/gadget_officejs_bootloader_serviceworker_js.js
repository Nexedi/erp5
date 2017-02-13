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

  self.addEventListener("message", function (event) {

    event.waitUntil(new self.RSVP.Queue()
      .push(function () {
        var data = JSON.parse(event.data);

        if (data.action === "install" &&
            data.url_list !== undefined) {

          self.storage = createStorage(self.registration.scope);
          return new self.RSVP.Queue()
            .push(function () {
              var promise_list = [];
              data.url_list.map(function (url) {
                promise_list.push(
                  new self.RSVP.Queue()
                    .push(function () {
                      return self.storage.get(url);
                    })
                    .push(undefined, function () {
                      return new self.RSVP.Queue()
                        .push(function () {
                          return fetch(new Request(url));
                        })
                        .push(function (response) {
                          if (response.status === 200) {
                            return self.RSVP.all([
                              self.storage.put(
                                url,
                                {"content_type": "blob"}
                              ),
                              response.blob()
                            ]);
                          }
                          throw new Error(response.statusText);
                        })
                        .push(function (result) {
                          return self.storage.putAttachment(
                            url,
                            "body",
                            result[1]
                          );
                        })
                        .push(function () {
                          self.console.log("Saved: ", url);
                        })
                        .push(undefined, function (error) {
                          self.console.log(url, error);
                        });
                    })
                );
              });
              return self.RSVP.all(promise_list);
            })
            .push(function () {
              event.ports[0].postMessage("success");
            });
        }
      }));
  });

  self.addEventListener('install', function (event) {
    event.waitUntil(self.skipWaiting());
  });
  self.addEventListener('activate', function (event) {
    event.waitUntil(self.clients.claim());
  });

  self.addEventListener("fetch", function (event) {
    var relative_url = event.request.url.replace(self.registration.scope, "")
      .replace(self.version_url, "");

    event.respondWith(
      new self.RSVP.Queue()
        .push(function () {
          if (relative_url === "") {
            return self.setting_storage.get(self.registration.scope)
              .push(function (doc) {
                relative_url = doc.landing_page || "/";
              })
              .push(undefined, function (error) {
                if (error.status_code === 404) {
                  relative_url = "/";
                  return;
                }
                throw error;
              });
          }
        })
        .push(function () {
          if (self.storage.get === undefined) {
            self.storage = createStorage(self.registration.scope);
          }
          return self.storage.get(relative_url);
        })
        .push(function (doc) {
          if (doc.content_type !== "blob") {
            return new Response(doc.text_content, {
              'headers': {
                'content-type': doc.content_type
              }
            });
          }
          return self.storage.getAttachment(relative_url, "body")
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
          return fetch(event.request);
        })
    );
  });

}(self, fetch, Request, Response));