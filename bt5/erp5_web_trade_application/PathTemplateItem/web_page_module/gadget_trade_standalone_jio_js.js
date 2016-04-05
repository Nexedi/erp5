/*global window, rJS, jIO, FormData */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, jIO) {
  "use strict";

  rJS(window)
   .ready(function (gadget) {
      return gadget.getDeclaredGadget('jio')
        .push(function (jio_gadget) {
          // Initialize the gadget local parameters
          gadget.state_parameter_dict = {jio_storage: jio_gadget};
        });
    })

    

    .declareMethod('createJio', function (jio_options) {
      this.state_parameter_dict.jio_storage = jIO.createJIO(jio_options);
    })
    .declareMethod('allDocs', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.allDocs.apply(storage, arguments);
    })
    .declareMethod('allAttachments', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.allAttachments.apply(storage, arguments);
    })
    .declareMethod('get', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.get.apply(storage, arguments);
    })
    .declareMethod('put', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.put.apply(storage, arguments);
    })
    .declareMethod('post', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.post.apply(storage, arguments);
    })
    .declareMethod('remove', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.remove.apply(storage, arguments);
    })
    .declareMethod('getAttachment', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.getAttachment.apply(storage, arguments);
    })
    .declareMethod('putAttachment', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.putAttachment.apply(storage, arguments);
    })
    .declareMethod('removeAttachment', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.removeAttachment.apply(storage, arguments);
    })
    .declareMethod('repair', function () {
      var storage = this.state_parameter_dict.jio_storage,
        argument_list = arguments;

      return storage.allDocs({
        query: 'portal_type:("Organisation" OR "Storage Node" OR "Product" OR "Currency" OR "Category")',
      })
        .push(function(result) {
          var promise_list = [],
            i;
          for (i=0; i < result.data.total_rows; i+=1) {
            // Remove local documents
            promise_list.push(storage.remove(result.data.rows[i].id));
            // Remove synchronization signature, so that document is marked as never synced
            // XXX Of course, this is a hack, but, until a cleaner solution is found, it is done like this
            promise_list.push(storage.__storage._signature_sub_storage.remove(result.data.rows[i].id));
          }
          return RSVP.all(promise_list);
        })
        .push(function () {
          return storage.repair.apply(storage, argument_list);
        });

    });

}(window, rJS, jIO));