/*jslint indent: 2, nomen: true, maxlen: 120*/
/*global jIO, RSVP, JSON */
(function (jIO, RSVP, JSON) {
  "use strict";

  function PublisherStorage(spec) {

    // NOTE: requires Website Layout Configuration CSP modification
    // => connect-src 'self' https://raw.githubusercontent.com https://api.github.com data:;

    // NOTE: moved repo
    //https://api.github.com/repos/Fonds-de-Dotation-du-Libre/awesome-free-software
    //https://api.github.com/repos/Nexedi/awesome-free-software
    //https://api.github.com/repos/Nexedi/awesome-free-software/contents/?ref=master
    //https://api.github.com/repos/Nexedi/awesome-free-software/contents/alfresco.json
    //https://raw.githubusercontent.com/Nexedi/awesome-free-software/master/alfresco.json

    this._href = spec.href || 'https://api.github.com/repos/';
    this._user = spec.user || 'Fonds-de-Dotation-du-Libre';
    this._repo = spec.repo || 'awesome-free-software';
  }

  PublisherStorage.prototype.get = function (id) {
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax({type: "GET", url: id, dataType: "text"});
      })
      .push(
        function (response) {
          return JSON.parse(response.target.response || response.target.responseText);
        },
        function (error) {
          if ((error.target !== undefined) &&
              (error.target.status === 404)) {
            throw new jIO.util.jIOError("Cannot find document", 404);
          }
          throw error;
        }
      );
  };

  PublisherStorage.prototype.hasCapacity = function (name) {
    return (name === "list");
  };

  PublisherStorage.prototype.buildQuery = function () {
    var url = this._href + this._user + '/' + this._repo + '/contents/?ref=master';

    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax({"type": "GET", "url": url});
      })
      .push(function (data) {
        var data_list = JSON.parse(data.target.response || data.target.responseText),
          result_list = [],
          data_entry,
          len,
          i;

        for (i = 0, len = data_list.length; i < len; i += 1) {
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