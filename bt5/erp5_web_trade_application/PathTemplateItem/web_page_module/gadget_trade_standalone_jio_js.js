/*global window, rJS, RSVP, UriTemplate, URI, Query, SimpleQuery, ComplexQuery, jIO */
/*jslint indent: 2, maxlen: 80*/
/*jslint nomen: true*/
(function (window, rJS, RSVP, UriTemplate,
            URI, Query, SimpleQuery, ComplexQuery, jIO) {
  "use strict";

  function wrapJioCall(gadget, method_name, argument_list) {
    var storage = gadget.state_parameter_dict.jio_storage,
      regexp =
        /^X-Delegate uri="(http[s]*:\/\/[\/\-\[\]{}()*+:?.,\\\^$|#\s\w%]+)"$/,
      login_page;

    return storage[method_name].apply(storage, argument_list)
      .push(undefined, function (error) {
        if ((error.target !== undefined) && (error.target.status === 401)) {
          login_page = error.target.getResponseHeader('WWW-Authenticate');
          // Only connect to https to login
          if (regexp.test(login_page)) {
            return gadget.getUrlFor({
              command: 'login',
              absolute_url: true
            })
              .push(function (came_from) {
                return gadget.redirect({
                  command: 'raw',
                  options: {
                    url:
                      UriTemplate.parse(regexp.exec(login_page)[1])
                      .expand({came_from: came_from})
                  }
                });
              });
          }
        }
        throw error;
      });
  }

  function isSingleLocalRoles(parsed_query) {
    if ((parsed_query instanceof SimpleQuery) &&
        (parsed_query.key === 'local_roles')) {
      // local_roles:"Assignee"
      return parsed_query.value;
    }
  }

  function isMultipleLocalRoles(parsed_query) {
    var i,
      sub_query,
      is_multiple = true,
      local_role_list = [];
    if ((parsed_query instanceof ComplexQuery) &&
        (parsed_query.operator === 'OR')) {

      for (i = 0; i < parsed_query.query_list.length; i += 1) {
        sub_query = parsed_query.query_list[i];
        if ((sub_query instanceof SimpleQuery) &&
            (sub_query.key === 'local_roles')) {
          local_role_list.push(sub_query.value);
        } else {
          is_multiple = false;
        }
      }
      if (is_multiple) {
        // local_roles:"Assignee" OR local_roles:"Assignor"
        return local_role_list;
      }
    }
  }

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

    .declareMethod('allDocs', function (option_dict) {
      // throw new Error('do not use all docs');

      if (option_dict.list_method_template === undefined) {
        return wrapJioCall(this, 'allDocs', arguments);
      }

      var query = option_dict.query,
        i,
        parsed_query,
        sub_query,
        result_list,
        local_roles;
      if (option_dict.query) {
        parsed_query = jIO.QueryFactory.create(option_dict.query);

        result_list = isSingleLocalRoles(parsed_query);
        if (result_list) {
          query = undefined;
          local_roles = result_list;
        } else {

          result_list = isMultipleLocalRoles(parsed_query);
          if (result_list) {
            query = undefined;
            local_roles = result_list;
          } else if ((parsed_query instanceof ComplexQuery) &&
                     (parsed_query.operator === 'AND')) {

            // portal_type:"Person" AND local_roles:"Assignee"
            for (i = 0; i < parsed_query.query_list.length; i += 1) {
              sub_query = parsed_query.query_list[i];

              result_list = isSingleLocalRoles(sub_query);
              if (result_list) {
                local_roles = result_list;
                parsed_query.query_list.splice(i, 1);
                query = Query.objectToSearchText(parsed_query);
                i = parsed_query.query_list.length;
              } else {
                result_list = isMultipleLocalRoles(sub_query);
                if (result_list) {
                  local_roles = result_list;
                  parsed_query.query_list.splice(i, 1);
                  query = Query.objectToSearchText(parsed_query);
                  i = parsed_query.query_list.length;
                }
              }
            }
          }

        }
        option_dict.query = query;
        option_dict.local_roles = local_roles;
      }

      return wrapJioCall(
        this,
        'getAttachment',
        [
          // XXX Ugly hardcoded meaningless id...
          "erp5",
          new UriTemplate.parse(option_dict.list_method_template)
                         .expand(option_dict),
          {format: "json"}
        ]
      )
        .push(function (catalog_json) {
          var data = catalog_json._embedded.contents,
            count = data.length,
            k,
            uri,
            item,
            result = [];
          for (k = 0; k < count; k += 1) {
            item = data[k];
            uri = new URI(item._links.self.href);
            delete item._links;
            result.push({
              id: uri.segment(2),
              doc: {},
              value: item
            });
          }
          return {
            data: {
              rows: result,
              total_rows: result.length
            }
          };
        });
    })
    .declareMethod('getAttachment', function (id, name) {
      return wrapJioCall(this, 'getAttachment', [id, name, {format: "json"}]);
    })
    .declareMethod('putAttachment', function (id, name, json) {
      return wrapJioCall(this,
                         'putAttachment', [id, name, JSON.stringify(json)]);
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

    .declareMethod('get', function () {
      var storage = this.state_parameter_dict
          .jio_storage.state_parameter_dict.jio_storage;
      return storage.get.apply(storage, arguments);
    })
    .declareMethod('post', function () {
      var storage = this.state_parameter_dict
          .jio_storage.state_parameter_dict.jio_storage;
      return storage.post.apply(storage, arguments);
    })
    .declareMethod('put', function () {
      var storage = this.state_parameter_dict
          .jio_storage.state_parameter_dict.jio_storage;
      return storage.put.apply(storage, arguments);
    });


}(window, rJS, RSVP, UriTemplate, URI, Query, SimpleQuery, ComplexQuery, jIO));