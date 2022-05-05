/*jslint indent: 2, nomen: true, maxlen: 120*/
/*global jIO, RSVP, JSON, Boolean, DOMParser */
(function (jIO, RSVP, JSON, Boolean, DOMParser) {
  "use strict";

  // NOTE: requires Website Layout Configuration CSP modification
  // connect-src 'self' https://raw.githubusercontent.com
  //                    https://api.github.com
  //                    https://www.openhub.net data:;

  // NOTE: moved repo
  //https://api.github.com/repos/Fonds-de-Dotation-du-Libre/awesome-free-software
  //https://api.github.com/repos/Nexedi/awesome-free-software

  // NOTE: doesn't scale, requires index or concatination as source. We concat.

  // NOTE: using OpenHub API which requires an API-Key (max 1000 calls/day)
  // https://github.com/blackducksoftware/ohloh_api#ohloh-api-documentation

  // TODO: needs a debugger to stop point out broken profiles

  var BLANK = "";
  var LANG = "/languages_summary";
  var XML = ".xml";
  var KEY = "?api_key=";
  var BUG = "/analyses/latest/languages_summary";
  var REMOTE = "ERP5Site_getHTTPResource?url=";
  var MASTER = "/contents/?ref=master";

  function ExportStorage(spec) {

    this._href = spec.href || 'https://api.github.com/repos/';
    this._user = spec.user || 'Fonds-de-Dotation-du-Libre';
    this._repo = spec.repo || 'european-cloud-industry';

    this._api_key = spec.api_key;
    this._parser = new DOMParser();
  }

  ExportStorage.prototype.get = function (id) {
    var api = this._api_key;
    var parser = this._parser;
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax({type: "GET", url: id, dataType: "text"});
      })
      .push(function (obj) {
        var item = JSON.parse(obj.target.response || obj.target.responseText);
        item.line_total = 0;
        if (!api || api.length !== 64) {
          return item;
        }

        // note: OpenHub API is not accessible from the client, so we need a
        // server roundtrip. This means statistical data can only be exported
        // when working with a proper (dev) backend. The frontend static app
        // will not fetch anything from OpenHub
        return new RSVP.Queue()
          .push(function () {
            return RSVP.all(item.free_software_list.map(function (software) {
              var profile_url = software.source_code_profile.replace(" ", BLANK);
              if (profile_url && profile_url !== BLANK && profile_url !== BUG) {
                return new RSVP.Queue()
                  .push(function () {
                    return jIO.util.ajax({
                      type: "GET",
                      url: REMOTE + profile_url.replace(LANG, XML) + KEY + api,
                      xhrFields: {withCredentials: true}
                    });
                  })
                  .push(null, function (error) {
                    if ((error.target !== undefined) &&
                        (error.target.status === 404)) {
                          //DEBUG: console.log("404", profile_url);
                      return;
                    }
                    //DEBUG console.log("no repo-info on profile", profile_url);
                    throw error;
                  });
              }

              return;
            }));
          })
          .push(function (response_list) {
            item.free_software_list = item.free_software_list.map(
              function (software, index) {
              var xml;
              var line_total;
              var data;

              if (response_list[index]) {
                data = response_list[index];
                xml = parser.parseFromString(
                  data.target.response || data.target.responseText,
                  "text/xml"
                );
                line_total = xml.getElementsByTagName("total_code_lines")[0]
                  .childNodes[0].nodeValue;
              } else {
                line_total = "0";
              }
              software.line_total = parseInt(line_total, 10);
              item.line_total += parseInt(line_total, 10);
              return software;
            });
            return item;
          });
      })
      .push(null, function (error) {
        if ((error.target !== undefined) &&
            (error.target.status === 404)) {
          throw new jIO.util.jIOError("Cannot find document", 404);
        }
        throw error;
      });
  };

  ExportStorage.prototype.hasCapacity = function (name) {
    return (name === "list");
  };

  ExportStorage.prototype.buildQuery = function () {
    var url = this._href + this._user + '/' + this._repo + MASTER;
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax({"type": "GET", "url": url});
      })
      .push(function (data) {
        var data_list = JSON.parse(
          data.target.response || data.target.responseText
        );
        var json_file = ".json";
        var result_list = data_list.map(function (entry) {
          if (entry.path.indexOf(json_file) > -1) {
            return {
              id: entry.download_url,
              value: {}
            };
          }
        }).filter(Boolean);
        return result_list;
      });
  };

  jIO.addStorage('export_storage', ExportStorage);

}(jIO, RSVP, JSON, Boolean, DOMParser));
