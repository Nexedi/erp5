/*jslint indent: 2, nomen: true, maxlen: 80*/
/*global jIO, RSVP, JSON */
(function (jIO, RSVP, JSON) {
  "use strict";

  var HREF = 'https://api.github.com/repos/',
    USER = 'Nexedi',
    REPO = 'awesome-free-software',
    BRANCH = '/contents/?ref=master';

  function fetchUrl(option_dict) {
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax(option_dict);
      })
      .push(function (data) {
        return JSON.parse(data.target.response || data.target.responseText);
      });
  }

  function PublisherStorage(spec) {
    this._href = spec.href || HREF;
    this._user = spec.user || USER;
    this._repo = spec.repo || REPO;
    this._branch = spec.branch || BRANCH;
    this._url = this._href + this._user + '/' + this._repo + this._branch;
  }

  PublisherStorage.prototype.get = function (id) {
    return new RSVP.Queue()
      .push(function () {
        return fetchUrl({type: "GET", url: id, dataType: "text"});
      })
      .push(undefined, function (error) {
        if ((error.target !== undefined) && (error.target.status === 404)) {
          throw new jIO.util.jIOError("Cannot find document", 404);
        }
        throw error;
      });
  };

  PublisherStorage.prototype.hasCapacity = function (name) {
    return (name === "list");
  };

  PublisherStorage.prototype.buildQuery = function () {
    var url = this._url;
    return new RSVP.Queue()
      .push(function () {
        return fetchUrl({"type": "GET", "url": url});
      })
      .push(function (data_list) {
        var result_list = [],
          len = data_list.length,
          data_entry,
          i;

        for (i = 0; i < len; i += 1) {
          data_entry = data_list[i];
          if (data_entry.path.indexOf(".json") > -1) {
            result_list.push({
              id: data_entry.download_url,
              value: {}
            });
          }
        }
        return result_list;
      });
  };

  jIO.addStorage('publisher_storage', PublisherStorage);

}(jIO, RSVP, JSON));
