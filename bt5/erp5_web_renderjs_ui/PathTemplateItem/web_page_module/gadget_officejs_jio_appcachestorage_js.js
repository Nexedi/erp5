/*jslint indent:2, maxlen: 80, nomen: true */
/*global jIO, RSVP, window, Rusha, Blob, URL */
(function (window, jIO, RSVP, Rusha, Blob, URL) {
  "use strict";

  var rusha = new Rusha();

  function AppCacheStorage(spec) {
    this._manifest = spec.manifest;
    this._take_installer = spec.take_installer || false;
    this._origin_url = spec.origin_url !== undefined ?
        spec.origin_url : window.location.href;
    this._version = spec.version || "";
    this._prefix = spec.prefix || "./";
    this._documents = {};
    // Harcoded here, find a better way.
    if (this._take_installer) {
      this._relative_url_list = [
        this._prefix,
        this._prefix + "gadget_officejs_bootloader.js",
        this._prefix + "gadget_officejs_bootloader_presentation.html",
        this._prefix + "gadget_officejs_bootloader_presentation.js",
        this._prefix + "gadget_officejs_bootloader_presentation.css",
        this._prefix + "gadget_officejs_bootloader_serviceworker.js",
        this._prefix + "gadget_erp5_nojqm.css",
        this._prefix + "officejs_logo.png",
        this._prefix + "jio_appcachestorage.js"
      ];
    } else {
      this._relative_url_list = [this._prefix + "/"];
    }
    if (this._take_installer) {
      this._version = 'app/';
    }
    this._version = this._prefix + this._version;
  }

  AppCacheStorage.prototype.get = function (id) {
    if (this._documents.hasOwnProperty(id)) {
      return this._documents[id];
    }
    throw new jIO.util.jIOError('can not find document : ' + id, 404);
  };

  AppCacheStorage.prototype.hasCapacity = function () {
    return true;
  };

  AppCacheStorage.prototype.getAttachment = function (origin_url,
                                                       relative_url) {
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax({
          type: "GET",
          url: new URL(relative_url, origin_url),
          dataType: "blob"
        });
      })
      .push(function (result) {
        return result.target.response;
      });
  };

  AppCacheStorage.prototype.allAttachments = function (id) {
    if (id === this._origin_url) {
      var result = {}, i, len = this._relative_url_list.length;
      for (i = 0; i < len; i += 1) {
        result[this._relative_url_list[i]] = {};
      }
      return result;
    }
    return [];
  };

  AppCacheStorage.prototype.buildQuery = function () {
    var result = [], id;
    for (id in this._documents) {
      if (this._documents.hasOwnProperty(id)) {
        result.push({
          'id': id,
          'value': this._documents[id],
          'doc': this._documents[id]
        });
      }
    }
    return result;
  };

  AppCacheStorage.prototype.repair = function () {
    var storage = this;
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax({
          type: "GET",
          url: new URL(storage._manifest, new URL(storage._version,
                       storage._origin_url))
        });
      })
      .push(function (response) {
        var text = response.target.responseText,
          relative_url_list = text.split('\n'),
          i,
          take = false,
          hash = rusha.digestFromString(text);
        storage._documents[storage._origin_url] = {'hash': hash};
        storage._relative_url_list.push(storage._version);
        storage._relative_url_list.push(storage._version + storage._manifest);
        for (i = 0; i < relative_url_list.length; i += 1) {
          if (relative_url_list[i].indexOf("NETWORK:") >= 0) {
            take = false;
          } else if (relative_url_list[i] !== "" &&
              relative_url_list[i].charAt(0) !== '#' &&
              relative_url_list[i].charAt(0) !== ' ' &&
              take) {
            storage._relative_url_list.push(
              storage._version + relative_url_list[i]
            );
          }
          if (relative_url_list[i].indexOf("CACHE:") >= 0) {
            take = true;
          }
        }
      })
      .push(undefined, function (error) {
        if (!error.message) {
          error.message = "Can't get manifest";
        }
        throw error;
      });
  };

  jIO.addStorage('appcache', AppCacheStorage);
}(window, jIO, RSVP, Rusha, Blob, URL));
