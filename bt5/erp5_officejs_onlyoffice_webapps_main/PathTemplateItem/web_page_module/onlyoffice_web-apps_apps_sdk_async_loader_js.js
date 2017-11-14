/*global window, rJS, RSVP, DocsAPI, console, document,
 Common, require, jIO, URL, FileReader, atob, ArrayBuffer,
 Uint8Array, XMLHttpRequest, Blob, Rusha*/

"use strict";
define([
  'sdk_files',
  'jquery',
  'underscore',
  'allfonts',
  'xregexp',
  'sockjs',
  'jsziputils',
  'jsrsasign'
], function(config_file) {
  return new RSVP.Queue()
    .push(function () {
      return jIO.util.ajax({
        type: "GET",
        dataType: "json",
        url: "onlyoffice/sdkjs/build/configs/" + config_file
      });
    })
    .push(function (response) {
      var script_src = "",
        queue = new RSVP.Queue(),
        list = response.target.response.compile.sdk.min;

      function loadScript(src) {
        return new RSVP.Promise(function (resolve, reject) {
          var s;
          s = document.createElement('script');
          s.src = src;
          s.onload = resolve;
          s.onerror = reject;
          document.head.appendChild(s);
        });
      }

      list.concat(response.target.response
        .compile.sdk.desktop.min).forEach(function (url) {
        url = url.replace('../', 'onlyoffice/sdkjs/');
        queue
          .push(function () {
            return jIO.util.ajax({
              type: "GET",
              url: url
            });
          })
          .push(function (result) {
            script_src += "\n" + result.target.response;
          });
      });
      queue.push(function () {
        var url = URL.createObjectURL(new Blob([script_src], {type: "text/javascript"}));
        return loadScript(url);
      }).push(undefined, function (error) {
        console.log(error);
        throw error;
      });
      return queue;
    });
});
