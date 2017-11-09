/*jslint indent:2, maxlen: 80, nomen: true */
/*global jIO */
(function (jIO) {
  "use strict";

  function LimitAllDocsStorage(spec) {
    this._document = spec.document;
    this._sub_storage = jIO.createJIO(spec.sub_storage);
  }

  LimitAllDocsStorage.prototype.get = function () {
    return this._sub_storage.get.apply(this._sub_storage, arguments);
  };
  LimitAllDocsStorage.prototype.allAttachments = function () {
    return this._sub_storage.allAttachments.apply(this._sub_storage, arguments);
  };
  LimitAllDocsStorage.prototype.post = function () {
    return this._sub_storage.post.apply(this._sub_storage, arguments);
  };
  LimitAllDocsStorage.prototype.put = function () {
    return this._sub_storage.put.apply(this._sub_storage, arguments);
  };
  LimitAllDocsStorage.prototype.remove = function () {
    return this._sub_storage.remove.apply(this._sub_storage, arguments);
  };
  LimitAllDocsStorage.prototype.getAttachment = function () {
    return this._sub_storage.getAttachment.apply(this._sub_storage, arguments);
  };
  LimitAllDocsStorage.prototype.putAttachment = function () {
    return this._sub_storage.putAttachment.apply(this._sub_storage, arguments);
  };
  LimitAllDocsStorage.prototype.removeAttachment = function () {
    return this._sub_storage.removeAttachment.apply(this._sub_storage,
                                                    arguments);
  };
  LimitAllDocsStorage.prototype.repair = function () {
    return this._sub_storage.repair.apply(this._sub_storage, arguments);
  };
  LimitAllDocsStorage.prototype.hasCapacity = function (name) {
    return this._sub_storage.hasCapacity(name);
  };
  LimitAllDocsStorage.prototype.buildQuery = function (options) {
    var storage = this;
    return this._sub_storage.allDocs(options)
      .push(function (result) {
        var i;
        for (i = 0; i < result.data.total_rows; i += 1) {
          if (result.data.rows[i].id === storage._document) {
            return [result.data.rows[i]];
          }
        }
        return [];
      });
  };

  jIO.addStorage('limitalldocs', LimitAllDocsStorage);
}(jIO));
