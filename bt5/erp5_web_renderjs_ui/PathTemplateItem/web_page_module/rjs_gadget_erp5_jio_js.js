/*global window, rJS, RSVP, UriTemplate, URI, SimpleQuery, ComplexQuery, jIO */
/*jslint indent: 2, maxerr: 3, nomen: true */
(function (window, rJS, RSVP, UriTemplate, URI, SimpleQuery, ComplexQuery, jIO) {
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
        (parsed_query.operator === undefined) &&
        (parsed_query.key === 'local_roles')) {
      // local_roles:"Assignee"
      return parsed_query.value;
    }
  }

  function isSingleDomain(parsed_query) {
    if ((parsed_query instanceof SimpleQuery) &&
        (parsed_query.operator === undefined) &&
        (parsed_query.key !== undefined) &&
        (parsed_query.key.indexOf('selection_domain_') === 0)) {
      // domain_region:"europe/france"
      var result = {};
      result[parsed_query.key.slice('selection_domain_'.length)] =
        parsed_query.value;
      return result;
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
            (sub_query.key !== undefined) &&
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
        });
    })

    .declareMethod('allDocs', function (options) {
      var context = this,
        queue;
      // throw new Error('do not use all docs');

      if (options.list_method_template === undefined) {
        if ((!options.sort_on) || (options.sort_on.length === 0)) {
          options.sort_on = [["search_rank", "DESC"]];
        }
        return wrapJioCall(this, 'allDocs', [options]);
      }

      function triggerAllDocs() {
        var query = options.query,
          i,
          key,
          parsed_query,
          sub_query,
          result_list,
          local_roles,
          local_role_found = false,
          selection_domain_found = false,
          selection_domain,
          sort_list = [];
        if (options.query) {
          parsed_query = jIO.QueryFactory.create(options.query);
          result_list = isSingleLocalRoles(parsed_query);
          if (result_list) {
            query = undefined;
            local_roles = result_list;
          } else {
            result_list = isSingleDomain(parsed_query);
            if (result_list) {
              query = undefined;
              selection_domain = result_list;
            } else {

              result_list = isMultipleLocalRoles(parsed_query);
              if (result_list) {
                query = undefined;
                local_roles = result_list;
              } else if ((parsed_query instanceof ComplexQuery) &&
                         (parsed_query.operator === 'AND')) {

                // portal_type:"Person" AND local_roles:"Assignee"
                // AND selection_domain_region:"europe/france"
                for (i = 0; i < parsed_query.query_list.length; i += 1) {
                  sub_query = parsed_query.query_list[i];

                  if (!local_role_found) {
                    result_list = isSingleLocalRoles(sub_query);
                    if (result_list) {
                      local_roles = result_list;
                      parsed_query.query_list.splice(i, 1);
                      query = jIO.Query.objectToSearchText(parsed_query);
                      local_role_found = true;
                      sub_query = parsed_query.query_list[i];
                    } else {
                      result_list = isMultipleLocalRoles(sub_query);
                      if (result_list) {
                        local_roles = result_list;
                        parsed_query.query_list.splice(i, 1);
                        query = jIO.Query.objectToSearchText(parsed_query);
                        local_role_found = true;
                        sub_query = parsed_query.query_list[i];
                      }
                    }
                  }

                  result_list = isSingleDomain(sub_query);
                  if (result_list) {
                    selection_domain_found = false;
                    for (key in result_list) {
                      if (result_list.hasOwnProperty(key) &&
                          ((selection_domain === undefined) ||
                           (!selection_domain.hasOwnProperty(key)))) {
                        if (selection_domain === undefined) {
                          selection_domain = {};
                        }
                        selection_domain[key] = result_list[key];
                        selection_domain_found = true;
                      }
                    }
                    if (selection_domain_found === true) {
                      parsed_query.query_list.splice(i, 1);
                      query = jIO.Query.objectToSearchText(parsed_query);
                      i -= 1;
                    }
                  }

                }
              }
            }
          }
        }

        if (options.sort_on) {
          for (i = 0; i < options.sort_on.length; i += 1) {
            sort_list.push(JSON.stringify(options.sort_on[i]));
          }
        }

        if (selection_domain) {
          selection_domain = JSON.stringify(selection_domain);
        }

        options.query = query;
        options.sort_on = sort_list;
        options.local_roles = local_roles;
        options.selection_domain = selection_domain;

        return wrapJioCall(
          context,
          'getAttachment',
          [
            // XXX Ugly hardcoded meaningless id...
            "erp5",
            new UriTemplate.parse(options.list_method_template)
                           .expand(options),
            {format: "json"}
          ]
        );
      }

      function usePrecalculatedResult() {
        return options.default_value;
      }

      if (options.default_value === undefined) {
        queue = triggerAllDocs();
      } else {
        queue = new RSVP.Queue()
          .push(usePrecalculatedResult);
      }

      return queue
        .push(function (catalog_json) {
          var data = catalog_json._embedded.contents || [],
            summary = catalog_json._embedded.sum || [],
            count = catalog_json._embedded.count;
          return {
            "data": {
              "rows": data.map(function (item) {
                var uri = new URI(item._links.self.href);
                delete item._links;
                return {
                  "id": uri.segment(2),
                  "doc": {},
                  "value": item
                };
              }),
              "total_rows": data.length
            },
            "sum": {
              "rows": summary.map(function (item, index) {
                return {
                  "id": '/#summary' + index, // this is obviously wrong. @Romain help please!
                  "doc": {},
                  "value": item
                };
              }),
              "total_rows": summary.length
            },
            "count": count,
            "listbox_query_param_json": catalog_json._embedded.listbox_query_param_json
          };
        });
    })
    .declareMethod('get', function (id) {
      return wrapJioCall(this, 'get', [id]);
    })
    .declareMethod('getAttachment', function (id, name, options) {
      if (options) {
        return wrapJioCall(this, 'getAttachment', [id, name, options]);
      }
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
    })
    .declareMethod('repair', function () {
      return wrapJioCall(this, 'repair', []);
    })
    .declareMethod('remove', function (key) {
      return wrapJioCall(this, 'remove', [key]);
    })
    .declareMethod('allAttachments', function (key) {
      return wrapJioCall(this, 'allAttachments', [key]);
    })
    .declareMethod('removeAttachment', function (key, name) {
      return wrapJioCall(this, 'removeAttachment', [key, name]);
    });

}(window, rJS, RSVP, UriTemplate, URI, SimpleQuery, ComplexQuery, jIO));