/*globals jIO, Blob*/
/*jslint indent: 2, maxlen: 80, nomen: true*/
(function (jIO, Blob) {
  "use strict";

  function CompatibilityStorage(spec) {
    this._sub_storage = jIO.createJIO(spec.sub_storage);
  }

  CompatibilityStorage.prototype.get = function () {
    return this._sub_storage.get.apply(this._sub_storage, arguments)
      .push(function (doc) {
        delete doc.data;
        return doc;
      });
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
    return this._sub_storage.repair.apply(this._sub_storage, arguments);
  };

  CompatibilityStorage.prototype.allAttachments = function (doc_id) {
    if (doc_id.indexOf("_replicate_") === 0) {
      return this._sub_storage.allAttachments.apply(
        this._sub_storage,
        arguments
      );
    }
    return this._sub_storage.getAttachment(doc_id, "data")
      .push(function (blob) {
        return [{"data": blob}];
      })
      .push(undefined, function (error) {
        if (error.status_code === 404) {
          return [];
        }
        throw error;
      });
  };

  CompatibilityStorage.prototype.getAttachment = function (doc_id) {
    var context = this;
    return context._sub_storage.getAttachment.apply(
      this._sub_storage,
      arguments
    )
      .push(undefined, function (error) {
        if (error.status_code === 404) {
          return context._sub_storage.get(doc_id)
            .push(function (doc) {
              var blob;
              if (doc.content_type === undefined ||
                  doc.content_type.indexOf("application/x-asc") === 0) {
                if (doc.data !== undefined) {
                  blob = new Blob([doc.data]);
                  return context.putAttachment(doc_id, "data", blob)
                    .push(function () {
                      return blob;
                    });
                }
              }
              throw new jIO.util.jIOError("no data", 404);
            });
        }
        throw error;
      });
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
    )
      .push(function (result) {
        var i, len = result.length;
        for (i = 0; i < len; i += 1) {
          delete result[i].value.data;
          delete result[i].doc.data;
        }
        return result;
      });
  };

  jIO.addStorage('compatibility', CompatibilityStorage);

}(jIO, Blob));