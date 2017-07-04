/*globals jIO, Blob, Rusha, RSVP, URI*/
/*jslint indent: 2, maxlen: 80, nomen: true*/
(function (jIO, Blob, Rusha, RSVP, URI) {
  "use strict";

  var rusha = new Rusha(), stringify = jIO.util.stringify;

  function CompatibilityStorage(spec) {
    this._sub_storage = jIO.createJIO(spec.sub_storage);
    this._is_fixed = spec.is_fixed;
  }

  CompatibilityStorage.prototype.get = function () {
    return this._sub_storage.get.apply(this._sub_storage, arguments);
  };

  CompatibilityStorage.prototype.put = function () {
    return this._sub_storage.put.apply(this._sub_storage, arguments);
  };

  CompatibilityStorage.prototype.post = function () {
    return this._sub_storage.post.apply(this._sub_storage, arguments);
  };

  CompatibilityStorage.prototype.remove = function () {
    return this._sub_storage.remove.apply(this._sub_storage, arguments);
  };

  CompatibilityStorage.prototype.hasCapacity = function () {
    return this._sub_storage.hasCapacity.apply(this._sub_storage, arguments);
  };

  CompatibilityStorage.prototype.repair = function () {
    var context = this;
    // Here fix the local storage for some cases.

    if (!context._is_fixed) {
      return context._sub_storage.allDocs({
        select_list: ["content_type"]
      })
      .push(function (result) {
        var i, promise_list = [], doc_list = result.data.rows;
        for (i = 0; i < result.data.total_rows; i += 1) {
          if (doc_list[i].value.content_type !== undefined &&
              !doc_list[i].value.content_type.startsWith("application/x-asc")) {
            promise_list.push(
              context._sub_storage.remove(doc_list[i].id)
            );
          }
        }
        return RSVP.all(promise_list);
      })
      .push(function () {
        return context._sub_storage.repair.apply(
          context._sub_storage, arguments
        );
      });
    }
  };

  CompatibilityStorage.prototype.allAttachments = function (doc_id) {
    return this._sub_storage.allAttachments.apply(
      this._sub_storage,
      arguments
    );
  };

  CompatibilityStorage.prototype.getAttachment = function (doc_id) {
    var context = this;
    return context._sub_storage.getAttachment.apply(
      this._sub_storage,
      arguments
    );
  };

  CompatibilityStorage.prototype.putAttachment = function () {
    return this._sub_storage.putAttachment.apply(this._sub_storage, arguments);
  };

  CompatibilityStorage.prototype.removeAttachment = function () {
    return this._sub_storage.removeAttachment.apply(
      this._sub_storage,
      arguments
    );
  };

  CompatibilityStorage.prototype.buildQuery = function () {
    return this._sub_storage.buildQuery.apply(
      this._sub_storage,
      arguments
    );
  };

  jIO.addStorage('fix_local', CompatibilityStorage);

}(jIO, Blob, Rusha, RSVP, URI));