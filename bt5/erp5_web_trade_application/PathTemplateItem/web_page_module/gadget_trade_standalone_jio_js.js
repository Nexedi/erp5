/*global window, rJS, RSVP, UriTemplate, URI, Query, SimpleQuery, ComplexQuery, jIO */
/*jslint indent: 2, maxlen: 80*/
/*jslint nomen: true*/
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)

    .ready(function (gadget) {
      return gadget.getDeclaredGadget('jio')
        .push(function (jio_gadget) {
          // Initialize the gadget local parameters
          gadget.state_parameter_dict = {jio_storage: jio_gadget};
        });
    })

    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod('redirect', 'redirect')
    .declareAcquiredMethod('getUrlFor', 'getUrlFor')

    .declareMethod('createJio', function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getSetting('hateoas_url')
          ]);
        })
        .push(function (setting_list) {
          return gadget.state_parameter_dict.jio_storage.createJio({
            type: "replicate",
              // XXX This drop the signature lists...
            query: {
              query: 'portal_type:(' +
                '"Product Module"' +
                'OR "Organisation Module"' +
                'OR "Purchase Record Module"' +
                'OR "Purchase Record" ' +
                'OR "Purchase Price Record Module" ' +
                'OR "Purchase Price Record" ' +
                'OR "Sale Record Module" ' +
                'OR "Sale Record" ' +
                'OR "Sale Price Record Module" ' +
                'OR "Sale Price Record" ' +
                'OR "Inventory Move Record Module" ' +
                'OR "Inventory Move Record" ' +
                'OR "Production Record Module" ' +
                'OR "Production Record" ' +
                'OR "Daily Statement Record Module"' +
                'OR "Daily Statement Record"' +
                'OR "Report Item Module" ' +
                'OR "Report Item" ' +
                'OR "Report Total" ' +
                ') ' +
                'OR (portal_type:"Currency"'
                   + 'AND validation_state:"validated") ' +
                'OR (portal_type:"Product"'
                   + 'AND validation_state:("validated" OR "submitted")) ' +
                'OR (portal_type:"Organisation" '
                   + 'AND validation_state:("validated" OR "submitted")) ' +
                'OR (portal_type:"Storage Node"'
                   + 'AND validation_state:"validated") ' +
                'OR (portal_type:"Category" AND (   relative_url:"region/%" ' +
                'OR relative_url:"quantity_unit/%" ' +
                'OR relative_url:"product_line/%")) ',
              limit: [0, 1234567890]
            },
            use_remote_post: true,
            conflict_handling: 2,
            check_local_modification: false,
            check_local_creation: true,
            check_local_deletion: false,
            check_remote_modification: false,
            check_remote_creation: true,
            check_remote_deletion: true,
            local_sub_storage: {

              type: "query",
              sub_storage: {
                type: "uuid",
                sub_storage: {
                  type: "indexeddb",
                  database: "trade"
                }
              }
            },

            remote_sub_storage: {
              type: "erp5",
              url: setting_list[0],
              default_view_reference: "trade_jio_view"
            }
          });

        });
    })

    .declareMethod('allDocs', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.allDocs.apply(storage, arguments);
    })
    .declareMethod('getAttachment', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.getAttachment.apply(storage, arguments);
    })
    .declareMethod('putAttachment', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.putAttachment.apply(storage, arguments);
    })
    .declareMethod('repair', function () {
      var storage = this.state_parameter_dict
        .jio_storage.state_parameter_dict.jio_storage,
        argument_list = arguments;

      return storage.allDocs({
        query: 'portal_type:("Organisation"' +
          ' OR "Storage Node" OR "Product" OR "Currency" OR "Category")'
      })
        .push(function (result) {
          var promise_list = [],
            i;
          for (i = 0; i < result.data.total_rows; i += 1) {
            // Remove local documents
            promise_list.push(storage.remove(result.data.rows[i].id));
            // Remove synchronization signature
            // so that document is marked as never synced
            // XXX Of course, this is a hack, but,
            //until a cleaner solution is found, it is done like this
            promise_list.push(storage.__storage
                              ._signature_sub_storage
                              .remove(result.data.rows[i].id));
          }
          return RSVP.all(promise_list);
        })
        .push(function () {
          return storage.repair.apply(storage, argument_list);
        });

    })
     .declareMethod('remove', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.remove.apply(storage, arguments);
    })
    .declareMethod('get', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.get.apply(storage, arguments);
    })
    .declareMethod('post', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.post.apply(storage, arguments);
    })
    .declareMethod('put', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.put.apply(storage, arguments);
    });


}(window, rJS, RSVP, UriTemplate, URI, Query, SimpleQuery, ComplexQuery, jIO));