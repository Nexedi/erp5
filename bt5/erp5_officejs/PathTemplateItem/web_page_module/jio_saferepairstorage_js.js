/*jslint indent:2,maxlen:80,nomen:true*/
/*global  jIO, RSVP*/
(function (jIO, RSVP) {
  "use strict";

  /**
   * The jIO SafeRepairStorage extension
   *
   * @class SafeRepairStorage
   * @constructor
   */


  function SafeRepairStorage(spec) {
    this._sub_storage = jIO.createJIO(spec.sub_storage);
    this._id_dict = {};
  }

  SafeRepairStorage.prototype.get = function () {
    return this._sub_storage.get.apply(this._sub_storage, arguments);
  };
  SafeRepairStorage.prototype.allAttachments = function () {
    return this._sub_storage.allAttachments.apply(this._sub_storage, arguments);
  };
  SafeRepairStorage.prototype.post = function () {
    return this._sub_storage.post.apply(this._sub_storage, arguments);
  };
  SafeRepairStorage.prototype.put = function (id, doc) {
    var storage = this;
    return this._sub_storage.put.apply(this._sub_storage, arguments)
      .push(undefined, function (error) {
        if (error instanceof jIO.util.jIOError &&
            error.status_code === 403) {
          if (storage._id_dict[id]) {
            return storage._sub_storage.put(storage._id_dict[id], doc);
          }
          return storage._sub_storage.post(doc)
            .push(function (sub_id) {
              storage._id_dict[id] = sub_id;
              return sub_id;
            });
        }
      });
  };
  SafeRepairStorage.prototype.remove = function () {
    return;
  };
  SafeRepairStorage.prototype.getAttachment = function () {
    return this._sub_storage.getAttachment.apply(this._sub_storage, arguments);
  };
  SafeRepairStorage.prototype.putAttachment = function (id, attachment_id,
      attachment) {
    var storage = this;
    return this._sub_storage.putAttachment.apply(this._sub_storage, arguments)
      .push(undefined, function (error) {
        if (error instanceof jIO.util.jIOError &&
            error.status_code === 403) {
          return new RSVP.Queue()
            .push(function () {
              if (storage._id_dict[id]) {
                return storage._id_dict[id];
              }
              return storage._sub_storage.get(id)
                .push(function (doc) {
                  return storage._sub_storage.post(doc);
                });
            })
            .push(function (sub_id) {
              storage._id_dict[id] = sub_id;
              return storage._sub_storage.putAttachment(sub_id, attachment_id,
                  attachment);
            });
        }
      });
  };
  SafeRepairStorage.prototype.removeAttachment = function () {
    return;
  };
  SafeRepairStorage.prototype.repair = function () {
    return this._sub_storage.repair.apply(this._sub_storage, arguments);
  };
  SafeRepairStorage.prototype.hasCapacity = function (name) {
    return this._sub_storage.hasCapacity(name);
  };
  SafeRepairStorage.prototype.buildQuery = function () {
    return this._sub_storage.buildQuery.apply(this._sub_storage,
                                              arguments);
  };

  jIO.addStorage('saferepair', SafeRepairStorage);

}(jIO, RSVP));
