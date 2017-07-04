/*globals jIO, Blob, Rusha, RSVP, URI*/
/*jslint indent: 2, maxlen: 80, nomen: true*/
(function (jIO, Blob, Rusha, RSVP, URI) {
  "use strict";

  function repairDocumentSignature(storage, signature_document) {
    /* The aim is deleted corrupted data to have fresh one from server
       And clear signature for inexistant document
       This can be consider like a HACK
    */
    return storage._sub_storage.allDocs({
        select_list: ["content_type"]
      })
      .push(function (result) {
        var i, promise_list = [], doc_list = result.data.rows;
        for (i = 0; i < result.data.total_rows; i += 1) {
          if (doc_list[i].value.content_type !== undefined &&
              !doc_list[i].value.content_type.startsWith("application/x-asc")) {
            promise_list.push(
              storage._sub_storage.remove(doc_list[i].id)
            );
          }
        }
        return RSVP.all(promise_list);
      })
      .push(function () {
        signature_document.is_fixed = true;
        return storage._local_storage.put(
          storage._signature_hash, signature_document
        );
      });
  }

  function CompatibilityStorage(spec) {
    this._sub_storage = jIO.createJIO(spec.sub_storage);
    this._replicate_storage = this._sub_storage.__storage;
    this._local_storage = this._replicate_storage._local_sub_storage;
    this._signature_hash = this._replicate_storage._signature_hash;
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
    var storage = this, signature_doc;
    // Here fix the local storage for some cases.

    return storage._local_storage.get(this._signature_hash)
      .push(undefined, function (error) {
        if (error.status_code === 404) {
          return {is_fixed: false};
        }
      })
      .push(function (doc) {
        if (!doc.is_fixed) {
          return repairDocumentSignature(storage, doc);
        }
      })
      .push(function () {
        return storage._sub_storage.repair.apply(
          storage._sub_storage, arguments
        );
      });
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