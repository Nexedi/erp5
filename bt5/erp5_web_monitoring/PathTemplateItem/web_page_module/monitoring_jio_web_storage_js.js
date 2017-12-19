/*
 * Copyright 2016, Nexedi SA
 * Released under the LGPL license.
 * http://www.gnu.org/licenses/lgpl.html
 */

/*jslint nomen: true*/
/*global jIO, RSVP */

(function (jIO, RSVP) {
  "use strict";

  function ajax(storage, options) {
    if (options === undefined) {
      options = {};
    }
    if (storage._authorization !== undefined) {
      if (options.headers === undefined) {
        options.headers = {};
      }
      options.headers.Authorization = storage._authorization;
    }

    if (storage._with_credentials !== undefined) {
      if (options.xhrFields === undefined) {
        options.xhrFields = {};
      }
      options.xhrFields.withCredentials = storage._with_credentials;
    }
    if (storage._timeout !== undefined) {
      options.timeout = storage._timeout;
    }
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax(options);
      });
  }

  function restrictDocumentId(id) {
    var slash_index = id.indexOf("/");
    if (slash_index !== 0 && slash_index !== -1) {
      throw new jIO.util.jIOError("id " + id + " is forbidden (no begin /)",
                                  400);
    }
    if (id.lastIndexOf("/") === (id.length - 1)) {
      throw new jIO.util.jIOError("id " + id + " is forbidden (no end /)",
                                  400);
    }
    return id;
  }

  function getJsonDocument(context, id) {
    return new RSVP.Queue()
      .push(function () {
        return ajax(context, {
          type: "GET",
          url: context._url + "/" + id + ".json",
          dataType: "text"
        });
      })
      .push(function (response) {
        return {id: id, doc: JSON.parse(response.target.responseText)};
      }, function (error) {
        if ((error.target !== undefined) &&
            (error.target.status === 404)) {
          throw new jIO.util.jIOError("Cannot find document '" + id + "'", 404);
        }
        throw error;
      });
  }

  /**
   * The JIO WEB HTTP Storage extension
   *
   * @class WEBHTTPStorage
   * @constructor
   */
  function WEBHTTPStorage(spec) {
    if (typeof spec.url !== 'string') {
      throw new TypeError("WEBHTTPStorage 'url' is not of type string");
    }
    this._url = spec.url.replace(new RegExp("[/]+$"), "");
    if (typeof spec.basic_login === 'string') {
      this._authorization = "Basic " + spec.basic_login;
    }
    this._with_credentials = spec.with_credentials;
    this._timeout = spec.timeout;
  }

  WEBHTTPStorage.prototype.get = function (id) {
    var context = this;
    id = restrictDocumentId(id);

    return getJsonDocument(context, id)
      .push(function (element) {
        return element.doc;
      }, function (error) {
        if ((error.target !== undefined) &&
            (error.target.status === 404)) {
          throw new jIO.util.jIOError("Cannot find document", 404);
        }
        throw error;
      });
  };

  WEBHTTPStorage.prototype.hasCapacity = function (capacity) {
    return (capacity === "list") || (capacity === "include");
  };

  WEBHTTPStorage.prototype.buildQuery = function (options) {
    var context = this,
      item_list = [],
      push_item;

    if (options.include_docs === true) {
      push_item = function (id, item) {
        item_list.push({
          "id": id,
          "value": {},
          "doc": item
        });
      };
    } else {
      push_item = function (id) {
        item_list.push({
          "id": id,
          "value": {}
        });
      };
    }

    return new RSVP.Queue()
      .push(function () {
        return ajax(context, {
          type: "GET",
          url: context._url + "/_document_list",
          dataType: "text"
        });
      })
      .push(function (response) {
        var document_list = [],
          promise_list = [],
          i;
        document_list = response.target.responseText.split('\n');
        for (i = 0; i < document_list.length; i += 1) {
          if (document_list[i]) {
            promise_list.push(getJsonDocument(context, document_list[i]));
          }
        }
        return RSVP.all(promise_list);
      }, function (error) {
        if ((error.target !== undefined) &&
            (error.target.status === 404)) {
          throw new jIO.util.jIOError("Cannot find document", 404);
        }
        throw error;
      })
      .push(function (result_list) {
        var i;
        for (i = 0; i < result_list.length; i += 1) {
          push_item(result_list[i].id, result_list[i].doc);
        }
        return item_list;
      });
  };

  jIO.addStorage('webhttp', WEBHTTPStorage);

}(jIO, RSVP));