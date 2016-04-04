/*globals window, rJS, jIO*/
/*jslint indent: 2, maxlen: 80*/
(function (jIO) {
  "use strict";

  function serializeJioResponse(gadget, method_name, argument_list) {
    // console.info('--- shared app: ' + method_name);
    // console.log(Array.prototype.slice.call(argument_list));
    var storage = gadget.state_parameter_dict.jio_storage;
    return storage[method_name].apply(storage, argument_list)
      .push(function (result) {
        return JSON.stringify({
          result: result,
          type: "jio_response"
        });
      }, function (error) {
        if (error instanceof jIO.util.jIOError) {
          return JSON.stringify({
            message: error.message,
            status_code: error.status_code,
            type: "jio_error"
          });
        }
        return JSON.stringify({
          message: error,
          type: "error"
        });
      });
  }

  rJS(window, rJS, jIO)

    .ready(function (gadget) {
      // Initialize the gadget local parameters
      gadget.state_parameter_dict = {};
      gadget.props = {};
    })

    .declareMethod('createJio', function (jio_options) {
      try {
        this.state_parameter_dict.jio_storage = jIO.createJIO(jio_options);
      } catch (error) {
        console.error(error);
        throw error;
      }
    })
    .declareMethod('allDocs', function () {
      return serializeJioResponse(this, 'allDocs', arguments);
    })
    .declareMethod('buildQuery', function () {
      return serializeJioResponse(this, 'buildQuery', arguments);
    })
    .declareMethod('allAttachments', function () {
      return serializeJioResponse(this, 'allAttachments', arguments);
    })
    .declareMethod('get', function () {
      return serializeJioResponse(this, 'get', arguments);
    })
    .declareMethod('put', function () {
      return serializeJioResponse(this, 'put', arguments);
    })
    .declareMethod('post', function () {
      return serializeJioResponse(this, 'post', arguments);
    })
    .declareMethod('remove', function () {
      return serializeJioResponse(this, 'remove', arguments);
    })
    .declareMethod('getAttachment', function () {
      return serializeJioResponse(this, 'getAttachment', arguments);
    })
    .declareMethod('putAttachment', function (id, name, json) {
      return serializeJioResponse(this, 'putAttachment', [id, name, new Blob([json], {type: "application/json"})]);
    })
    .declareMethod('removeAttachment', function () {
      return serializeJioResponse(this, 'removeAttachment', arguments);
    })
    .declareMethod('repair', function () {
      return serializeJioResponse(this, 'repair', arguments);
    });

}(jIO));