/*global window, rJS, RSVP */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  function displayGraph(gadget, data) {
    var i, j, key;
    //Format data for monitoring graphs:
    // dates in the x-axis
    // int in the y-axis
    for (i = 0; i < data.data.length; i = i + 1) {
      for (key of Object.keys(data.data[i].value_dict)) {
        for (j = 0; j < data.data[i].value_dict[key].length; j = j + 1) {
          if (key == 0) { //x-ayis
            data.data[i].value_dict[key][j] = new Date(data.data[i].value_dict[key][j]);
          } else { //y-axis
            data.data[i].value_dict[key][j] = parseInt(data.data[i].value_dict[key][j]);
          }
        }
      }
    }
    return gadget.getDeclaredGadget('graph_gadget')
      .push(function (graph_gadget) {
        data.new_format = true;
        return graph_gadget.render({value: data});
      });
  }

  rJS(window)
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("jio_get", 'jio_get')

    .declareMethod('render', function (options) {
      var gadget = this, graph_data, instance = options, opml;
      return new RSVP.Queue()
        .push(function () {
          return gadget.jio_get(instance.parent_id);
        })
        .push(function (opml_outline) {
          return gadget.jio_get(opml_outline.parent_url);
        })
        .push(function (opml_doc) {
          opml = opml_doc;
          var graph_options = {
            data_url: "",
            data_filename: "monitor_state.data",
            basic_login: ""
          };

          if (instance._links !== undefined) {
            graph_options  = {
              data_url: instance._links.private_url.href +
                'documents/',
              data_filename: instance.data.state,
              basic_login: opml.basic_login
            };
          }

          graph_options.extract_method = function (element_dict) {
            var promise_data = [
                "Date, Success, Error",
                new Date() + ",0,0"
              ],
              data = element_dict.data || promise_data,
              data_list = [],
              line_list,
              i;

            data_list.push({
              value_dict: {"0": [], "1": []},
              type: "scatter",
              axis_mapping_id_dict: {"1": "1_1"},
              title: "promises success"
            });
            data_list.push({
              value_dict: {"0": [], "1": []},
              type: "scatter",
              axis_mapping_id_dict: {"1": "1_2"},
              title: "promises error"
            });
            for (i = 1; i < data.length; i += 1) {
              line_list = data[i].split(',');
              data_list[0].value_dict["0"].push(line_list[0]);
              data_list[0].value_dict["1"].push(line_list[1]);

              // XXX repeating date entry
              data_list[1].value_dict["0"].push(line_list[0]);
              data_list[1].value_dict["1"].push(line_list[2]);
            }
            return data_list;
          };
          graph_options.data_dict = {
            data: {},
            layout: {
              axis_dict : {
                "0": {
                  "title": "Promises Failure Progression",
                  "scale_type": "linear",
                  "value_type": "date"
                },
                "1_1": {
                  "title": "Promises success",
                  "position": "right"
                },
                "1_2": {
                  "title": "Promises error",
                  "position": "right"
                }
              },
              title: "Promises Failure Progression"
            }
          };
          return graph_options;
        })
        .push(function (g) {
          graph_data = { value: g };
          var field_json = graph_data,
            state_dict = {
              data_dict: field_json.value.data_dict,
              data_url: field_json.value.data_url,
              data_filename: field_json.value.data_filename,
              extract_method: field_json.value.extract_method,
              basic_login: field_json.value.basic_login
            };
          return gadget.changeState(state_dict);
        });
    })

    .onStateChange(function () {
      return this.renderGraph();
    })

    .declareJob('renderGraph', function () {
      var gadget = this,
        jio_gadget;
      if (gadget.state.data_url !== undefined &&
          gadget.state.data_filename !== undefined) {
        return gadget.getDeclaredGadget("jio_gadget")
          .push(function (g) {
            jio_gadget = g;
            return jio_gadget.createJio({
              type: "webhttp",
              // XXX fix of url
              url: gadget.state.data_url.replace("jio_private", "private"),
              basic_login: gadget.state.basic_login
            });
          })
          .push(function () {
            return jio_gadget.get(
              gadget.state.data_filename
            );
          })
          .push(undefined, function (error) {
            gadget.state.data_dict.data = {};
            return gadget.notifySubmitted({
              message: "Warning: Failed to download graph data file '" +
                gadget.state.data_filename + "'!\n " + error.message || "",
              status: "error"
            })
              .push(function () {
                return undefined;
              });
          })
          .push(function (data_result) {
            if (data_result !== undefined &&
                gadget.state.extract_method !== undefined) {
              return new RSVP.Queue()
                .push(function () {
                  return gadget.state.extract_method(
                    data_result,
                    gadget.state.data_filename
                  );
                })
                .push(function (result) {
                  gadget.state.data_dict.data = result;
                  return displayGraph(gadget, gadget.state.data_dict);
                });
            }
            return displayGraph(gadget, gadget.state.data_dict);
          });
      }
      return displayGraph(gadget, gadget.state.data_dict);
    });

}(window, rJS, RSVP));