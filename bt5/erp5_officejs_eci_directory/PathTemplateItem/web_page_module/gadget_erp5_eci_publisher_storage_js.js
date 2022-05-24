/*jslint indent: 2, nomen: true, maxlen: 220*/
/*global jIO, RSVP, JSON, Object, console */
(function (jIO, RSVP, JSON, Object) {
  "use strict";

  var PROMISE_DATABASE;


  function populatePublisherStorage() {
    return new RSVP.Queue()
     .push(function () {
        return jIO.util.ajax({"type": "GET", "url": "https://api.github.com/repos/Fonds-de-Dotation-du-Libre/european-cloud-industry/contents/?ref=master"});
      })
      .push(function (data) {
        var data_list = JSON.parse(
          data.target.response || data.target.responseText
        );
        var result_list = data_list.map(function (entry) {
          if (entry.path.endsWith(".json")) {
            return {
              id: entry.download_url
            };
          }
        }).filter(Boolean);
        return result_list;
      })
      .push(function (result_list) {
        var process_list = [],
          queue = [];
        while (result_list.length) {
          process_list.push(result_list.splice(0, 40));
        }
        process_list.map(function (process_array) {
          queue.push(new RSVP.Queue()
            .push(function () {
            return RSVP.all(process_array.map(function (obj) {
              return new RSVP.Queue()
                .push(function () {
                  return jIO.util.ajax({type: "GET", url: obj.id, dataType: "text"});
                })
                .push(function (obj) {
                  var result = {};
                  try {
                    result[obj.target.responseURL] = JSON.parse(obj.target.response || obj.target.responseText);
                    return result;
                  } catch (error) {
                    console.log('failed to fetch ' + obj.target.responseURL);
                    console.log(error);
                    return result;
                  }
                });
            }));
          }));
        });
        return RSVP.all(queue);
      })
     .push(function (result_list) {
      var final_result_dict = {},
        i,
        key,
        j;
      for (i = 0; i < result_list.length; i += 1) {
        for (j = 0; j < result_list[i].length; j += 1) {
          for (key in result_list[i][j]) {
            if (result_list[i][j].hasOwnProperty(key)) {
              final_result_dict[key] = result_list[i][j][key];
            }
          }
        }
      }
      return final_result_dict;
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
            value : {}
          };
        });
      });
  };

  jIO.addStorage('publisher_storage', PublisherStorage);

}(jIO, RSVP, JSON, Object));