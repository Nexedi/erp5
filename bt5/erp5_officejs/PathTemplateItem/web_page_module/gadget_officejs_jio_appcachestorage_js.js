/*jslint indent:2, maxlen: 80, nomen: true */
/*global jIO, RSVP, window, console, Blob */
(function (window, jIO, RSVP, console, Blob) {
  "use strict";

  function AppCacheStorage(spec) {
    this._manifest = spec.manifest;
    this._url = window.location.origin + window.location.pathname +
      (window.location.pathname.endsWith('/') ? '' : '/') +
      spec.version + (spec.version.endsWith('/') ? '' : '/');
    this._url_list = [];
  }

  AppCacheStorage.prototype.get = function (url) {
    return {};
  };

  AppCacheStorage.prototype.hasCapacity = function (name) {
    return (name === "list");
  };

  AppCacheStorage.prototype.getAttachment = function (doc_id, attachment_id) {
    var storage = this, url = attachment_id;
    if (this._url === doc_id) {
      return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax({
          type: "GET",
          url: (url.startsWith("http") || url.startsWith("//")) ?
            url : storage._url + url,
          dataType: "blob"
        });
      })
      .push(function (result) {
        return result.target.response;
      })
      .push(undefined, function (error) {
        if (error.target.status === 404) {
          throw new jIO.util.jIOError("Can't find attachment: " + url, 404);
        }
        throw error;
      });
    }
    throw new jIO.util.jIOError("Can not find " + doc_id, 404);
  };

  AppCacheStorage.prototype.allAttachments = function (url) {
    var result = {}, i, len = this._url_list.length;
    for (i = 0; i < len; i += 1) {
      result[this._url_list[i]] = {};
    }
    return result;
  };

  AppCacheStorage.prototype.buildQuery = function (options) {
    return [{id: this._url, doc: {}, value: {}}];
  };

  AppCacheStorage.prototype.repair = function () {
    var storage = this;
    console.log("start getting cache");
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax({
          type: "GET",
          url: storage._url + storage._manifest
        });
      })
      .push(function (response) {
        var text = response.target.responseText,
          url_list = text.split('\r\n'),
          i,
          take = false;
        if (url_list.length === 1) {
          url_list = text.split('\n');
        }
        if (url_list.length === 1) {
          url_list = text.split('\r');
        }
        for (i = 0; i < url_list.length; i += 1) {
          if (url_list[i].indexOf("NETWORK:") >= 0) {
            take = false;
          }
          if (take &&
              url_list[i] !== "" &&
              url_list[i].charAt(0) !== '#' &&
              url_list[i].charAt(0) !== ' ') {
            url_list[i].replace("\r", "");
            storage._url_list.push(url_list[i]);
          }
          if (url_list[i].indexOf("CACHE:") >= 0) {
            take = true;
          }
        }
      });
  };

  jIO.addStorage('appcache', AppCacheStorage);
}(window, jIO, RSVP, console, Blob));