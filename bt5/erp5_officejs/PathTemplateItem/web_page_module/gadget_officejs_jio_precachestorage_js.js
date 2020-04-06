/*jslint indent:2, maxlen: 80, nomen: true */
/*global jIO, RSVP, window, Rusha, Blob, URL */
(function (window, jIO, RSVP, Rusha, Blob, URL) {
  "use strict";

  var rusha = new Rusha();

  function PreCacheStorage(spec) {
    this._base_manifest = spec.base_cache_manifest;
    this._precache_manifest_list = spec.manifest;
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
        this._prefix + "jio_precachestorage.js"
      ];
    } else {
      this._relative_url_list = [this._prefix + "/"];
    }
    if (this._take_installer) {
      this._version = 'app/';
    }
    this._version = this._prefix + this._version;
  }

  PreCacheStorage.prototype.get = function (id) {
    if (this._documents.hasOwnProperty(id)) {
      return this._documents[id];
    }
    throw new jIO.util.jIOError('can not find document : ' + id, 404);
  };

  PreCacheStorage.prototype.hasCapacity = function () {
    return true;
  };

  PreCacheStorage.prototype.getAttachment = function (origin_url,
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

  PreCacheStorage.prototype.allAttachments = function (id) {
    if (id === this._origin_url) {
      var result = {}, i, len = this._relative_url_list.length;
      for (i = 0; i < len; i += 1) {
        result[this._relative_url_list[i]] = {};
      }
      return result;
    }
    return [];
  };

  PreCacheStorage.prototype.buildQuery = function () {
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

  PreCacheStorage.prototype.repair = function () {
    var storage = this, promise_list = [];
    return new RSVP.Queue()
      .push(function () {
        promise_list.push(jIO.util.ajax({
          type: "GET",
          url: new URL(storage._base_manifest,
                       new URL(storage._version, storage._origin_url))
        }));
        for (var i = 0; i < storage._precache_manifest_list.length; i++) {
          promise_list.push(jIO.util.ajax({
            type: "GET",
            url: new URL(storage._precache_manifest_list[i],
                         new URL(storage._version, storage._origin_url))
          }));
        }
        return RSVP.all(promise_list);
      })
      .push(function (result_list) {
        var base_manifest_text = result_list[0].target.responseText,
          relative_url_list,
          i,
          manifest_text,
          manifest_url_list,
          hash = rusha.digestFromString(base_manifest_text);
        relative_url_list = Object.keys(JSON.parse(base_manifest_text));
        storage._relative_url_list.push(storage._version);
        storage._relative_url_list.push(storage._version +
                                        storage._base_manifest);
        for (i = 0; i < storage._precache_manifest_list.length; i++) {
          storage._relative_url_list.push(storage._version +
                                          storage._precache_manifest_list[i]);
        }
        for (i = 1; i < result_list.length; i++) {
          manifest_text = result_list[i].target.responseText;
          manifest_url_list = manifest_text.replace("['", "").replace("']", "")
            .split("', '");
          relative_url_list = relative_url_list.concat(manifest_url_list);
        }
        storage._documents[storage._origin_url] = {'hash': hash};
        console.log("PRECACHESTORAAAAGE");
        for (i = 0; i < relative_url_list.length; i += 1) {
          storage._relative_url_list.push(
            storage._version + relative_url_list[i]
          );
        }
        console.log(storage._relative_url_list);
      })
      .push(undefined, function (error) {
        if (!error.message) {
          error.message = "Couldn't get one of the precache manifests";
        }
        throw error;
      });
  };

  jIO.addStorage('precache', PreCacheStorage);
}(window, jIO, RSVP, Rusha, Blob, URL));
