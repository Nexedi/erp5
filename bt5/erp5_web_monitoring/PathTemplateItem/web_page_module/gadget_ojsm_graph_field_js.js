/*global window, rJS, RSVP */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  function displayGraph(gadget, data) {
    return gadget.getDeclaredGadget('graph_gadget')
      .push(function (graph_gadget) {
        return graph_gadget.render({value: data});
      });
  }

  rJS(window)
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareMethod('render', function (options) {
      var field_json = options || {},
        state_dict = {
          data_dict: field_json.value.data_dict,
          data_url: field_json.value.data_url,
          data_filename: field_json.value.data_filename,
          extract_method: field_json.value.extract_method,
          basic_login: field_json.value.basic_login
        };
      return this.changeState(state_dict);
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
            // XXX-catchall
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