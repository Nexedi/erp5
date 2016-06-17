/*global window, rJS, jIO, FormData, UriTemplate */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, jIO) {
  "use strict";

  rJS(window)

    .ready(function (gadget) {
      // Initialize the gadget local parameters
      gadget.state_parameter_dict = {};
      gadget.state_parameter_dict.jio_storage = jIO.createJIO({
        type: "indexeddb",
        database: "global-setting"
      });
    })

    .declareMethod('getSetting', function (key, default_value) {
      var gadget = this;
      return gadget.state_parameter_dict.jio_storage.get("setting")
        .push(function (doc) {
          return doc[key] || default_value;
        }, function (error) {
          if (error.status_code === 404) {
            return default_value;
          }
          throw error;
        });
    })
    .declareMethod('setSetting', function (key, value) {
      var gadget = this;
      return gadget.state_parameter_dict.jio_storage.get("setting")
        .push(undefined, function (error) {
          if (error.status_code === 404) {
            return {};
          }
          throw error;
        })
        .push(function (doc) {
          doc[key] = value;
          return gadget.state_parameter_dict.jio_storage.put('setting', doc);
        });
    });
}(window, rJS, jIO));