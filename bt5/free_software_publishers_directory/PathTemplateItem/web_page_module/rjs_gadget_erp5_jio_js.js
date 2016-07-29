/*global window, rJS, RSVP, UriTemplate, URI, Query, SimpleQuery, ComplexQuery, jIO */
/*jslint indent: 2, maxerr: 3, nomen: true */
(function (window, rJS, RSVP, UriTemplate, URI, Query, SimpleQuery, ComplexQuery, jIO) {
  "use strict";

  function createDataSheets(gadget) {
    gadget.jio_allDocs = gadget.state_parameter_dict.jio_storage.allDocs;
    gadget.jio_get = gadget.state_parameter_dict.jio_storage.get;
    gadget.jio_put = gadget.state_parameter_dict.jio_storage.put;
    return gadget.jio_allDocs()
      /////////////////////////////////////////////////////////////////
      // Make Publisher datasheets
      /////////////////////////////////////////////////////////////////
      .push(function (data) {
        
        function isReplicate(el) {
          return (el.id.indexOf("_replicate_") < 0);
        }
        
        function setPortalTypeOnPublisher (el) {
          return gadget.jio_get(el.id)
          .push(function (publisher_object) {
            publisher_object.portal_type = "publisher";
            publisher_object.url = publisher_object.website;
            return gadget.jio_put(el.id, publisher_object);
          });
        }
        
        var publisher_id_list = data.data.rows,
          promise_list = publisher_id_list.map(setPortalTypeOnPublisher);

        return RSVP.all(promise_list);
      })
      .push(function () {
        console.log("get here");
        return gadget.jio_allDocs({
          select_list: ['title', 'free_software_list'],
          query: 'portal_type: "publisher"'
        });
      })
      /////////////////////////////////////////////////////////////////
      // Make Software datasheets
      /////////////////////////////////////////////////////////////////
      .push(function (publisher_list) {
        function saveSoftwareListFromPublisher (j) {
          var publisher = j.value.title,
            software_list = j.value.free_software_list;
          
          function saveSoftwareDocument (software) {
            software.portal_type = "software";
            software.publisher = publisher;
            software.url = software.wikipedia_url;
            return gadget.jio_put(software.title, software);
          }
          
          var save_software_promise_list = software_list.map(saveSoftwareDocument);
    
          return RSVP.all(save_software_promise_list);
        }

        var publishers = publisher_list.data.rows,
          promise_list = publishers.map(saveSoftwareListFromPublisher);
        
        return RSVP.all(promise_list);
      })
      .push(function () {
        return gadget.jio_allDocs({
          select_list: [
            'title',
            'success_case_list',
            'publisher'
          ],
          query: 'portal_type: "software"'
        });
      })
      /////////////////////////////////////////////////////////////////
      // Make Success Case datasheets
      /////////////////////////////////////////////////////////////////
      .push(function (software_list) {
        
        function saveSuccessCaseListFromSoftware (softwareObject) {
          var software = softwareObject.value.title,
            publisher = softwareObject.value.publisher,
            success_case_list = softwareObject.value.success_case_list;
          
          function isValid (success_case) {
            return (success_case !== "N/A" &&
                    success_case.title !== "" && 
                    success_case.title !== "N/A");
          }
          
          var uid_counter = 0;
          function addProperties (success_case) {
            var uid = uid_counter++;
            /*
            success_case = {
              portal_type: "success_case",
              software: software,
              publisher: publisher,
              uid: uid,
              "listbox_uid:list": {
                value: uid,
                key: "listbox_uid:list"
              },
              "_links": {
                self: {
                  href: "urn:jio:get:free_software_directory_data/" + success_case.uid
                }
              },
              image: {
                description: "",
                title: "image",
                "default": success_case.image,
                css_class: "",
                required: 0,
                editable: 0,
                key: "field_listbox_image_" + uid,
                hidden: 0,
                type: "ImageField",
              },
              title: success_case
            };
            */
            success_case.portal_type = "success_case";
            success_case.software = software;
            success_case.publisher = publisher;
            /*
            success_case.uid = uid;
            success_case["_links"] = {
              self: {
                href: "urn:jio:get:free_software_directory_data/" + success_case.uid
              }
            };
            */
            success_case.image = {
              description: "",
              title: "image",
              "default": success_case.image,
              css_class: "",
              required: 0,
              editable: 0,
              key: "field_listbox_image_" + uid,
              hidden: 0,
              type: "ImageField",
            };
            
            return success_case;
          }

          function save (success_case) {
            return gadget.jio_put(success_case.title, success_case);
          }
          
          var save_success_case_promise_list = 
            success_case_list.filter(isValid)
                             .map(addProperties)
                             .map(save);
    
          return RSVP.all(save_success_case_promise_list);
        }
        
        var softwares = software_list.data.rows.filter(function (sw) {
          return (sw.value.success_case_list !== "N/A");
        }),
          promise_list = softwares.map(saveSuccessCaseListFromSoftware);
        
        return RSVP.all(promise_list);       
      })
      .push(undefined, function (error) {
        console.log(error);
        throw error;
      });
  }
  
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
            url: setting_list[0], // BASE_URL + '/hateoas'
            default_view_reference: setting_list[1] // 'view'
          });
        })
        .push(function () {
          return;
          //return createDataSheets(gadget);
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