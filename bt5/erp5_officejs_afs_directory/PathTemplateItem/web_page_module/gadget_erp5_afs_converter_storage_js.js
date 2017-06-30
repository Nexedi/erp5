/*jslint indent: 2, nomen: true, maxlen: 80*/
/*global window, jIO, RSVP, DOMParser, Object */
(function (window, jIO, RSVP, DOMParser, Object) {
  "use strict";

    // XXX Bad proxy!
  var LOC = 'https://softinst56769.host.vifib.net/erp5/web_site_module/afs/',
    ID_LOC = "https://raw.githubusercontent.com/",
    ID_PATH = "Nexedi/awesome-free-software/master/",
    FETCH = "Software_getAnalysis?url=",
    PARSER = new DOMParser();

  function garble(str) {
    return window.encodeURIComponent(str.replace(/ /g, "-"));
  }

  function isArray(value) {
    return Object.prototype.toString.call(value) === '[object Array]';
  }

  function isValidCase(success_case) {
    return (
      success_case !== "N/A" &&
      success_case.title !== "" &&
      success_case.title !== "N/A"
    );
  }

  // only called on repair, convert publisher storage content into records
  // of publishers, software and success cases
  function convertDataSet(storage, result_list) {
    var response = [];

    if (result_list.length === 0) {
      return response;
    }

    return new RSVP.Queue()
      .push(function () {
        return RSVP.all(result_list.map(function (item) {
          return storage.get(item.id);
        }));
      })
      .push(function (publisher_list) {
        var publisher,
          software_list,
          software,
          success_case_list,
          success_case,
          i,
          j,
          k;

        for (i = 0; i < publisher_list.length; i += 1) {
          publisher = publisher_list[i];

          // XXX parallel promises? title is too unreliable as id
          publisher.item_id = result_list[i].id.split("/").pop().split(".")[0];

          // add publisher id
          response.push({
            "id": garble(publisher.item_id),
            "value": {}
          });
          software_list = publisher.free_software_list;
          if (isArray(software_list)) {
            for (j = 0; j < software_list.length; j += 1) {
              software = software_list[j];

              // add software id
              response.push({
                id: garble(publisher.item_id) + "/" + garble(software.title),
                value: {}
              });
              success_case_list = software.success_case_list;
              if (isArray(success_case_list)) {
                for (k = 0; k < success_case_list.length; k += 1) {
                  success_case = success_case_list[k];
                  if (isValidCase(success_case)) {

                    // add case id
                    response.push({
                      id: garble(publisher.item_id) + "/" +
                        garble(software.title) + "/" +
                        garble(success_case.title),
                      value: {}
                    });
                  }
                }
              }
            }
          }
        }
        return response;
      });
  }

  function retrieveOpenHubAnalysisTotalLines(software) {
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax({
          type: "GET",
          url: LOC + FETCH + software.source_code_profile,
          dataType: "text"
        });
      })
      .push(function (data) {
        var response = data.target.response || data.target.responseText;
        return PARSER.parseFromString(response, "text/xml")
          .getElementsByTagName("total_code_lines")[0].childNodes[0].nodeValue;
      });
  }

  function isValidProfileUrl(url) {
    return url && url !== "" && url.indexOf("hub") > -1;
  }

  function isInt(value) {
    return !isNaN(value) && (function (x) {
      if ((x | 0) === x) {
        return x;
      }
      return 0;
    })(parseFloat(value));
  }

  function totalLines(arr) {
    return arr.reduce(function (running_total, line) {
      return running_total += isInt(line);
    }, 0);
  }

  function retrieveTotalLinesFromPublisher(publisher) {
    var unique_software_list = [];
    return new RSVP.Queue()
      .push(function () {
        return RSVP.all(publisher.free_software_list.map(function (software) {
          var profile_url = software.source_code_profile;
          if (isValidProfileUrl(profile_url)) {
            if (unique_software_list.indexOf(profile_url) === -1) {
              unique_software_list.push(profile_url);
              return retrieveOpenHubAnalysisTotalLines(software);
            }
          }
        }).filter(Boolean));
      })
      .push(function (line_list) {
        return totalLines(line_list);
      });
  }

  function retrieveSuccessCaseFromSoftware(publisher, path_list) {
    return publisher.free_software_list.reduce(function (response, software) {
      var software_title = garble(software.title);
      if (software_title === path_list[1]) {
        if (isArray(software.success_case_list)) {
          return software.success_case_list.reduce(function (response, item) {
            var case_title = garble(item.title);
            if (case_title === path_list[2]) {
              item.portal_type = "success_case";
              item.software = software.title;
              item.software_website = software.website;
              item.publisher = software.publisher;
              item.publisher_website = software.website;
              item.category_list = software.category_list;
              item.uid = case_title;
              return item;
            }
            return response;
          });
        }
      }
      return response;
    }, undefined);
  }

  function retrieveSoftwareFromPublisher(publisher, path_list) {
    return publisher.free_software_list.reduce(function (response, software) {
      var software_title = garble(software.title);
      if (software_title === path_list[1]) {
        software.portal_type = "software";
        software.publisher = publisher.title;
        software.publisher_website = publisher.website;
        software.uid = garble(publisher.title) + "/" + software_title;
        return software;
      }
      return response;
    }, undefined);
  }

  // find and assemble single object from publisher entries
  function convertDataItem(storage, id) {
    var path_list = id.split("/"),
      path_len = path_list.length,
      publisher;

    return new RSVP.Queue()
      .push(function () {
        return new RSVP.Queue()
          .push(function () {
            return storage.get(ID_LOC + ID_PATH + path_list[0] + ".json");
          })
          .push(function (result) {
            if (path_len === 1) {
              return RSVP.all([
                result,
                retrieveTotalLinesFromPublisher(result)
              ]);
            }
            return [result];
          });
      })
      .push(function (result_list) {
        var response;
        
        publisher = result_list[0];
        publisher.portal_type = "publisher";
        publisher.uid = garble(publisher.title);
        publisher.total_lines = result_list[1] || 0;

        if (path_len === 1) {
          response = publisher;
        } else if (path_len === 2) {
          response = retrieveSoftwareFromPublisher(publisher, path_list);
        } else if (path_len === 3) {
          response = retrieveSuccessCaseFromSoftware(publisher, path_list);
        }
        return response;
      })
      .push(null, function (error) {
        console.log(error);
        throw error;
      });
  }

  function ConverterStorage(spec) {
    this._sub_storage = jIO.createJIO(spec.sub_storage);
  }

  ConverterStorage.prototype.get = function (id) {
    return convertDataItem(this._sub_storage, id);
  };

  ConverterStorage.prototype.repair = function () {
    return this._sub_storage.repair.apply(this._sub_storage, arguments);
  };

  ConverterStorage.prototype.hasCapacity = function (name) {
    return (name === "list");
  };

  ConverterStorage.prototype.buildQuery = function () {
    var storage = this._sub_storage,
      argument_list = arguments;

    return new RSVP.Queue()
      .push(function () {
        return storage.buildQuery.apply(storage, argument_list);
      })
      .push(function (result) {
        return convertDataSet(storage, result);
      });
  };

  jIO.addStorage('converter_storage', ConverterStorage);

}(window, jIO, RSVP, DOMParser, Object));
