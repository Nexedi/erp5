/*
 * Copyright 2016, Nexedi SA
 * Released under the LGPL license.
 * http://www.gnu.org/licenses/lgpl.html
 */

/*jslint nomen: true*/
/*global jIO, RSVP */

(function (jIO, RSVP) {
  "use strict";
  var LIMIT = 100; //default
  /**
   * Monitor erp5 layer to wrap erp5 storages for monitor app
   *
   * @class ERP5Monitor
   * @constructor
   */
  function ERP5Monitor(spec) {
    if (!spec.sub_storage || spec.sub_storage.type !== 'erp5') {
      throw new TypeError("ERP5Monitor subtorage must be erp5 type");
    }
    if (spec.limit) {
      LIMIT = spec.limit;
    }
    this._storage_definition = spec.sub_storage;
    this._sub_storage = jIO.createJIO(spec.sub_storage);
  }

  ERP5Monitor.prototype.get = function (id) {
    return this._sub_storage.get.apply(this._sub_storage, arguments);
  };

  ERP5Monitor.prototype.post = function () {
    return this._sub_storage.post.apply(this._sub_storage, arguments);
  };

  ERP5Monitor.prototype.put = function () {
    return this._sub_storage.put.apply(this._sub_storage, arguments);
  };

  ERP5Monitor.prototype.remove = function () {
    return this._sub_storage.remove.apply(this._sub_storage, arguments);
  };

  ERP5Monitor.prototype.hasCapacity = function (capacity) {
    return (capacity === "list") || (capacity === "limit") || (capacity === "include") || (capacity === "query") || (capacity === "select");
  };

  ERP5Monitor.prototype.buildQuery = function () {
    var sub_storage = this._sub_storage, args = arguments, master_url = this._storage_definition.url, i;
    if (!arguments[0].limit) {
      arguments[0].limit = [0, LIMIT];
    }
    return new RSVP.Queue()
      .push(function () {
        return sub_storage.allDocs.apply(sub_storage, args);
      })
      .push(function (result) {
        for (i = 0; i < result.data.rows.length; i += 1) {
          result.data.rows[i].master_url = master_url;
        }
        return result.data.rows;
      });
  };

  jIO.addStorage('erp5monitor', ERP5Monitor);

}(jIO, RSVP));