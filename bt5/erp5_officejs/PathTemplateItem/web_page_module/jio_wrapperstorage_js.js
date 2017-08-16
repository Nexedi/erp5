/*jslint nomen: true */
/*global RSVP, UriTemplate*/
(function (jIO, RSVP) {
  "use strict";

  var posts;

  function resultToDict(result) {
    var i, resultDict = {};
    for (i = 0; i < result.length; i++) {
      resultDict[result[i].id] = result[i].value;
    }
    return resultDict;
  }

  function WrapperStorage(spec) {
    this._sub_storage = jIO.createJIO(spec.sub_storage);
    this._default_field_list = spec.default_field_list;
  }

  WrapperStorage.prototype.get = function (id) {
    var that = this;
    if (posts) {
      return posts[id];
    }
    return this._sub_storage.get(id);
  };

  WrapperStorage.prototype.buildQuery = function (query) {
    var that = this;
    query.select_list = that._default_field_list;
    return this._sub_storage.buildQuery(query)
      .push(function(result) {
        posts = resultToDict(result);
        return result;
      });
  };

  WrapperStorage.prototype.hasCapacity = function (name) {
    var this_storage_capacity_list = ["list", "select", "include", "limit"];
    if (this_storage_capacity_list.indexOf(name) !== -1) {
      return true;
    }
  };

  jIO.addStorage('wrapper', WrapperStorage);

}(jIO, RSVP));