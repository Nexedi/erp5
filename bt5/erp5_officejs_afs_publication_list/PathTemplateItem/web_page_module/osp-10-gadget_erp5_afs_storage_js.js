/*
 * Copyright 2016, Nexedi SA
 * Released under the LGPL license.
 * http://www.gnu.org/licenses/lgpl.html
 */

/*jslint nomen: true*/
/*global jIO, RSVP, DOMParser, Blob */

(function (jIO, RSVP, JSON, UriTemplate) {
  "use strict";
  
  var DOCUMENT_URL = "{document_id}",
    document_url_template = UriTemplate.parse(DOCUMENT_URL);

  function ajax(storage, options) {
    if (options === undefined) {
      options = {};
    }

    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax(options);
      });
  }

  function PublisherStorage(spec) {
  }

  PublisherStorage.prototype.get = function (id) {
    var context = this;

    return new RSVP.Queue()
      .push(function () {
        return ajax(context, {
          type: "GET",
          url: document_url_template.expand({document_id: id}),
          dataType: "text",
        });
      })
      .push(function (response) {
        return JSON.parse(response.target.response || response.target.responseText);
      }, function (error) {
        if ((error.target !== undefined) &&
            (error.target.status === 404)) {
          throw new jIO.util.jIOError("Cannot find document", 404);
        }
        throw error;
      });
  };

  PublisherStorage.prototype.hasCapacity = function (name) {
    return (name === "list");
  };

  PublisherStorage.prototype.buildQuery = function (options) {
    var context = this,
      rows = [];

    return new RSVP.Queue()
    .push(function () {
      return ajax(context, {
        type: "GET",
        url: document_url_template.expand({document_id: 'publisher_list.txt'})
      });
    })
    .push(function (response) {
      var response_list = (response.target.response || response.target.responseText).split('\n');

      for (var entry in response_list) {
        if (response_list[entry] !== "") {
          rows.push({
            id: response_list[entry],
            value: {}
          });
        }
      }
      
      return rows;
    });
  };

  jIO.addStorage('publisher_storage', PublisherStorage);

}(jIO, RSVP, JSON, UriTemplate));