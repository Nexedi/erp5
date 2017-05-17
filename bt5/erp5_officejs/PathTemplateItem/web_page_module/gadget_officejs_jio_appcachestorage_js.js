/*jslint indent:2, maxlen: 80, nomen: true */
/*global jIO, RSVP, window, console, Blob */
(function (window, jIO, RSVP, console, Blob) {
  "use strict";

  function AppCacheStorage(spec) {
    this._manifest = spec.manifest;
    this._take_installer = spec.take_installer || false;
    this._origin_url = spec.origin_url !== undefined ? spec.origin_url :
      (window.location.origin + window.location.pathname +
      (window.location.pathname.endsWith('/') ? '' : '/') +
      ((spec.version !== undefined) ?
      (spec.version + (spec.version.endsWith('/') ? '' : '/')) : ""));
    this._relative_url_list = [this._origin_url, spec.manifest];
    this._prefix = spec.prefix;
    if (this._take_installer) {
      this._relative_url_list = [
        this._prefix || "/",
        this._prefix + "development/" + spec.manifest,
        this._prefix + "development/",
        this._prefix + "gadget_officejs_bootloader.js",
        this._prefix + "gadget_officejs_bootloader.appcache",
        this._prefix + "gadget_officejs_bootloader_presentation.html",
        this._prefix + "gadget_officejs_bootloader_presentation.js",
        this._prefix + "gadget_officejs_bootloader_presentation.css",
        this._prefix + "gadget_officejs_bootloader_serviceworker.js",
        this._prefix + "gadget_erp5_nojqm.css",
        this._prefix + "jio_appcachestorage.js"
      ];
    }
  }

  AppCacheStorage.prototype.get = function (id) {
    return {};
  };

  AppCacheStorage.prototype.hasCapacity = function (name) {
    return (name === "list");
  };

  AppCacheStorage.prototype.getAttachment = function (doc_id, attachment_id) {
    var storage = this, url = attachment_id;
    return new RSVP.Queue()
    .push(function () {
      return jIO.util.ajax({
        type: "GET",
        url: (url.startsWith("http") || url.startsWith("//")) ?
          url : storage._origin_url + url,
        dataType: "blob"
      });
    })
    .push(function (result) {
      return result.target.response;
    });
  };

  AppCacheStorage.prototype.allAttachments = function (url) {
    var result = {}, i, len = this._relative_url_list.length;
    for (i = 0; i < len; i += 1) {
      result[this._relative_url_list[i]] = {};
    }
    return result;
  };

  AppCacheStorage.prototype.buildQuery = function (options) {
    return [{id: "/", doc: {}, value: {}}];
  };

  AppCacheStorage.prototype.repair = function () {
    var storage = this,
      prefix = storage._take_installer ? this._prefix + "development/" : "";
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax({
          type: "GET",
          url: storage._origin_url + storage._manifest
        });
      })
      .push(function (response) {
        var text = response.target.responseText,
          relative_url_list = text.split('\r\n'),
          i,
          take = false;
        if (relative_url_list.length === 1) {
          relative_url_list = text.split('\n');
        }
        if (relative_url_list.length === 1) {
          relative_url_list = text.split('\r');
        }
        for (i = 0; i < relative_url_list.length; i += 1) {
          if (relative_url_list[i].indexOf("NETWORK:") >= 0) {
            take = false;
          }
          if (take &&
              relative_url_list[i] !== "" &&
              relative_url_list[i].charAt(0) !== '#' &&
              relative_url_list[i].charAt(0) !== ' ') {
            relative_url_list[i].replace("\r", "");
            storage._relative_url_list.push(prefix + relative_url_list[i]);
          }
          if (relative_url_list[i].indexOf("CACHE:") >= 0) {
            take = true;
          }
        }
      });
  };

  jIO.addStorage('appcache', AppCacheStorage);
}(window, jIO, RSVP, console, Blob));