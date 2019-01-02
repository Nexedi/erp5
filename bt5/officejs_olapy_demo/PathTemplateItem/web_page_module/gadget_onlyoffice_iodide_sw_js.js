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
  self.Node = {};
  self.XMLSerializer = Object;
  self.DOMParser = Object;
  self.postMessage = function () {return; };

  self.addEventListener('install', function (event) {
    event.waitUntil(self.skipWaiting());
  });
  self.addEventListener('activate', function (event) {
    event.waitUntil(self.clients.claim());
  });

  self.addEventListener("fetch", function (event) {
    return;
  });

}(self, fetch, Request, Response));