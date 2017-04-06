/*jslint indent:2, maxlen: 80, nomen: true */
/*global jIO, RSVP, window, console, Blob */
(function (window, jIO, RSVP, console, Blob) {
  "use strict";

  function FileSystemStorage(spec) {
    this._document = spec.document;
    this._sub_storage = jIO.createJIO(spec.sub_storage);
    this._id_dict = {"/": {"index.html": {}}};
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
      (attachment_id === "index.html") ?
        "/" : (doc_id === "/") ?
          attachment_id : doc_id + attachment_id
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
        var id, path, last_slash_index, filename;
        for (id in result) {
          if (result.hasOwnProperty(id)) {
            last_slash_index = id.lastIndexOf("/") + 1;
            if (last_slash_index === 0) {
              path = "/";
              filename = id;
            } else {
              path = id.substring(0, last_slash_index);
              filename = id.substring(last_slash_index);
            }
          }
          if (!path.startsWith("http") && id !== "/") {
            if (path.charAt(0) !== '/') {
              path = '/' + path;
            }
            if (!context._id_dict.hasOwnProperty(path)) {
              context._id_dict[path] = {};
            } else {
              context._id_dict[path][filename] = {};
            }
          }
        }
      });
  };

  jIO.addStorage('filesystem', FileSystemStorage);
}(window, jIO, RSVP, console, Blob));