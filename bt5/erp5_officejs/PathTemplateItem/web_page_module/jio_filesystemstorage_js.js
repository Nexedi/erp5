/*jslint indent:2, maxlen: 80, nomen: true */
/*global jIO, RSVP, window, console, Blob */
(function (window, jIO, RSVP, console, Blob) {
  "use strict";

  function FileSystemStorage(spec) {
    this._document = spec.document;
    this._sub_storage = jIO.createJIO(spec.sub_storage);
    this._id_dict = {};
  }

  FileSystemStorage.prototype.get = function (url) {
    return {};
  };

  FileSystemStorage.prototype.hasCapacity = function (name) {
    return (name === "list");
  };

  FileSystemStorage.prototype.getAttachment = function (doc_id, attachment_id) {
    return this._sub_storage.getAttachment(
      this._document,
      '.' + doc_id + ((attachment_id === "index.html") ?
        (doc_id.endsWith("imagelib/") ? "index.html" : "") : attachment_id)
    );
  };

  FileSystemStorage.prototype.allAttachments = function (doc_id) {
    return this._id_dict[doc_id] || {};
  };

  FileSystemStorage.prototype.buildQuery = function (options) {
    var id, result = [], context = this;
    for (id in context._id_dict) {
      if (context._id_dict.hasOwnProperty(id)) {
        result.push({id: id});
      }
    }
    return result;
  };

  FileSystemStorage.prototype.repair = function () {
    // Transform id attachment ( file path ) to id list / attachments
    var context = this;
    return context._sub_storage.repair()
      .push(function () {
        return context._sub_storage.allAttachments(context._document);
      })
      .push(function (result) {
        var id, path, last_index, filename;
        for (id in result) {
          if (result.hasOwnProperty(id)) {
            last_index = id.lastIndexOf("/") + 1;
            if (last_index === id.length) {
              if (id.startsWith('.')) {
                id = id.substring(1);
              }
              path = id || "/";
              filename = "index.html";
            } else {
              path = id.substring(1, last_index);
              filename = id.substring(last_index);
            }
          }
          if (path.charAt(0) !== '/') {
            path = '/' + path;
          }
          if (!context._id_dict.hasOwnProperty(path)) {
            context._id_dict[path] = {};
          }
          context._id_dict[path][filename] = {};
        }
      });
  };

  jIO.addStorage('filesystem', FileSystemStorage);
}(window, jIO, RSVP, console, Blob));