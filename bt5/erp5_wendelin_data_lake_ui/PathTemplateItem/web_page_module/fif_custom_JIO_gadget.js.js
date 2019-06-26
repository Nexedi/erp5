/*global window, rJS, RSVP, UriTemplate, URI, Query, SimpleQuery, ComplexQuery, jIO */
/*jslint indent: 2, maxerr: 3, nomen: true */
(function (window, rJS, RSVP, UriTemplate, URI, Query, SimpleQuery, ComplexQuery, jIO) {
  "use strict";

  function wrapJioCall(gadget, method_name, argument_list) {
    var storage = gadget.state_parameter_dict.jio_storage,
      regexp = /^X-Delegate uri="(http[s]*:\/\/[\/\-\[\]{}()*+:?.,\\\^$|#\s\w%]+)"$/,
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
                    url: UriTemplate.parse(regexp.exec(login_page)[1]).expand({came_from: came_from})
                  }
                });
              });
            /*
            window.location = UriTemplate.parse(
              regexp.exec(login_page)[1]
            ).expand({came_from: window.location.href + "{&me}"});
            return RSVP.timeout(5000);
            */
          // Redirect to the login view
          }
          // return gadget.redirect({command: 'display', options: {page: 'login'}});
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
            gadget.getSetting('hateoas_url'),
            gadget.getSetting('default_view_reference')
          ]);
        })
        .push(function (setting_list) {
          return gadget.state_parameter_dict.jio_storage.createJio({
            type: "erp5",
            url: setting_list[0],
            default_view_reference: setting_list[1]
          });
          /*return gadget.state_parameter_dict.jio_storage.createJio({
            type: "replicate",
            local_sub_storage: {
              type: "query",
              "sub_storage": {
                type: "indexeddb",
                database: "telecom"
              }
            },
            remote_sub_storage: {
              type: "erp5",
              url: setting_list[0],
              default_view_reference: setting_list[1]
            },
            query: {
              //query: 'portal_type:"Data Array" OR portal_type:"Data Descriptor" OR portal_type:"Data Set"', // and validation_state = 'validated'
              query: 'validation_state:"validated" AND portal_type:"Data Array" OR portal_type:"Data Descriptor" OR portal_type:"Data Set"',
              limit: [0, 20000]
            },
            //check_local_modification: false,
            check_local_creation: false,
            //check_local_deletion: false,
            //check_local_attachment_modification: false,
            check_local_attachment_creation: false,
            //check_local_attachment_deletion: false,
            //check_remote_modification: false,
            //check_remote_attachment_modification: false
          });*/
        })
        /*.push(function () {
          if (navigator.onLine)
            return wrapJioCall(gadget, "repair", []);
        })*/;
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
        tmp_list = [],
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
      if (option_dict.sort_on) {
        for (i = 0; i < option_dict.sort_on.length; i += 1) {
          tmp_list.push(JSON.stringify(option_dict.sort_on[i]));
        }
        option_dict.sort_on = tmp_list;
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
    .declareMethod('get', function (id) {
      return wrapJioCall(this, 'get', [id]);
    })
    .declareMethod('getAttachment', function (id, name) {
      return wrapJioCall(this, 'getAttachment', [id, name, {format: "json"}]);
    })
    .declareMethod('putAttachment', function (id, name, json) {
      return wrapJioCall(this, 'putAttachment', [id, name, JSON.stringify(json)]);
    })
    .declareMethod('put', function (key, doc) {
      return wrapJioCall(this, 'put', [key, doc]);
    })
    .declareMethod('post', function (doc) {
      return wrapJioCall(this, 'post', [doc]);
    });

}(window, rJS, RSVP, UriTemplate, URI, Query, SimpleQuery, ComplexQuery, jIO));