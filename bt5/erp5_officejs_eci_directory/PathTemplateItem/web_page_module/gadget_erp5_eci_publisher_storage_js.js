/*jslint indent: 2, nomen: true, maxlen: 120*/
/*global jIO, RSVP, JSON, Object */
(function (jIO, RSVP, JSON, Object) {
  "use strict";

  var PROMISE_DATABASE;
  var DICT = {};
  var GETTER = {
    type: "GET",
    url: "https://raw.githubusercontent.com/Fonds-de-Dotation-du-Libre/european-cloud-industry/master/xxx-null-team-impex.json",
    dataType: "text"
  };

  function populatePublisherStorage() {
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax(GETTER);
      })
      .push(function (dump) {
        var tmp = dump.target.response || dump.target.responseText;
        tmp =  JSON.parse(tmp);
        return {
          "https://raw.githubusercontent.com/Fonds-de-Dotation-du-Libre/european-cloud-industry/master/xxx-null-team-impex.json": tmp
        };
      })
      .push(undefined, function (error) {
        if ((error.target !== undefined) &&
            (error.target.status === 404)) {
          throw new jIO.util.jIOError("Cannot find document", 404);
        }
        throw error;
      });
  }

  PROMISE_DATABASE = populatePublisherStorage();

  function PublisherStorage(spec) {}

  PublisherStorage.prototype.get = function (id) {
    return new RSVP.Queue(PROMISE_DATABASE)
      .push(function (database) {
        return database[id];
      });
  };

  PublisherStorage.prototype.hasCapacity = function (name) {
    return (name === "list");
  };

  PublisherStorage.prototype.buildQuery = function () {
    return new RSVP.Queue(PROMISE_DATABASE)
      .push(function (database) {
        return Object.keys(database).map(function (url) {
          return {
            id: url,
            value: DICT
          };
        });
      });
  };

  jIO.addStorage('publisher_storage', PublisherStorage);

}(jIO, RSVP, JSON, Object));