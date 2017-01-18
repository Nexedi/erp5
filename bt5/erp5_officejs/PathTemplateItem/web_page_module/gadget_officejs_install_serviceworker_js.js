/*jslint indent: 2*/
/*global self, fetch, Request, Response, console, MessageChannel */
var global = self, window = self;

(function (self, fetch, Request, Response, console, MessageChannel) {
  "use strict";

  self.DOMParser = {};
  self.sessionStorage = {};
  self.localStorage = {};
  self.openDatabase = {};
  self.DOMError = {};
  self.postMessage = function () {return; };

  self.importScripts('rsvp.js', 'jiodev.js');

  self.storage = {};

  function postMessage(client, message) {
    return new RSVP.Promise(function (resolve, reject) {
        var messageChannel = new MessageChannel();
        messageChannel.port1.onmessage = function (event) {
          if (event.data.error) {
            reject(event.data.error);
          } else {
            return resolve(event.data);
          }
        };
        client.postMessage(
          message,
          [messageChannel.port2]
        );
      });
  }

  function createStorage(database) {
    return self.jIO.createJIO({
      type: "uuid",
      sub_storage: {
        type: "indexeddb",
        database: database
      }
    });
  }
  
  self.setting_storage = createStorage("setting");

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
                          console.log("Saved: ", url);
                        })
                        .push(undefined, function (error) {
                          console.log(
                            "error on",
                            url,
                            "cause: ",
                            error.message
                          );
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

  self.addEventListener("fetch", function (event) {
    var relative_url = event.request.url.replace(self.registration.scope, "")
      .replace(self.version_url, "");
    if (relative_url === "") {
      relative_url = "/";
    }

    event.respondWith(
      new self.RSVP.Queue()
        .push(function () {
          var client;
          if (relative_url.indexOf("dev/") === 0) {
            relative_url = relative_url.replace("dev/", "");
            if (relative_url === "") {
              relative_url = "/";
              return self.setting_storage.get("setting")
                .push(function (doc) {
                  doc.dev_mode = false;
                  self.dev_mode = false;
                  return self.setting_storage.put("setting", doc);
                }).push(function () {
                  return undefined;
                });
            }
            if (event.clientId) {
              return new RSVP.Queue()
                .push(function () {
                  return self.clients.get(event.clientId);
                })
                .push(function (result) {
                  client = result;
                  if (!self.dev_mode) {
                    return self.setting_storage.get("setting")
                      .push(function (doc) {
                        self.dev_mode = doc.dev_mode || false;
                      });
                  }
                })
                .push(function () {
                  if (self.dev_mode) {
                    return postMessage(
                      client,
                      {"relative_url": relative_url}
                    );
                  }
                })
                .push(function (result) {
                  if (result) {
                    return result.data;
                  }
                  return undefined;
                });
            }
          }
          return undefined;
        })
        .push(function (result) {
          if (result === undefined) {
            if (self.storage.get === undefined) {
              self.storage = createStorage(self.registration.scope);
            }
            return self.storage.get(relative_url);
          }
          console.log(result);
          return result;
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
        .push(function (response) {
          return new RSVP.Queue()
            .push(function () {
              return caches.open(self.document_version);
            })
            .push(function (cache) {
              cache.put(event.request, response.clone());
              return response;
            });
        })
        .push(undefined, function (error) {
          console.log(
            "Relative_Url: ", 
            relative_url, "\nCause: ",
            error.message
          );
          return fetch(event.request);
        })
    );
  });

}(self, fetch, Request, Response, console, MessageChannel));