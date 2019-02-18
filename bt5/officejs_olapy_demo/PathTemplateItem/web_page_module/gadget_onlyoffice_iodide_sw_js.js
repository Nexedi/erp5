/*jslint indent: 2*/
/*global self, Response, MessageChannel, console */
var global = self, window = self;

(function (self, Response, Promise, MessageChannel) {
  "use strict";

  self.importScripts('rsvp.js');

// http://craig-russell.co.uk/2016/01/29/service-worker-messaging.html#.XC8oy82JK3A
  function send_message_to_client(client, msg) {
    return new Promise(function (resolve, reject) {
      var msg_chan = new MessageChannel();

      msg_chan.port1.onmessage = function (event) {
        if (event.data.error) {
          reject(event.data.error);
        } else {
          resolve(event.data);
        }
      };
      msg_chan.port1.onmessageerror = reject;
      client.postMessage(msg, [msg_chan.port2]);
    });
  }

  function getMainClient() {
    if (self.main_client !== undefined) {
      return self.main_client;
    }
    return self.clients.matchAll()
      .then(function (client_list) {
        var i;
        for (i = 0; i < client_list.length; i += 1) {
          if (client_list[i].url === self.registration.scope) {
            self.main_client = client_list[i];
            return self.main_client;
          }
        }
      });
  }

  self.addEventListener('install', function (event) {
    event.waitUntil(self.skipWaiting());
  });
  self.addEventListener('activate', function (event) {
    event.waitUntil(self.clients.claim());
  });

  console.warn("I m the SW");
  self.addEventListener("fetch", function (event) {
    var relative_url = event.request.url.split("#")[0]
      .replace(self.registration.scope, "");
    if (relative_url === "local_iodide") {
      event.respondWith(
        new self.RSVP.Queue()
          .push(function () {
            return self.RSVP.all([
              event.request.text(),
              getMainClient()
            ]);
          })
          .push(function (result) {
            return send_message_to_client(result[1], result[0]);
          })
          .push(function (result) {
            return new Response(result);
          }, function (error) {
            return new Response(error, {status: "500"});
          })
      );
    } else {
      return;
    }
  });

}(self, Response, Promise, MessageChannel));