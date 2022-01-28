/*global window, rJS, jIO, FormData, UriTemplate */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, jIO) {
  "use strict";

  // jIO call wrapper for redirection to authentication page if needed
  function wrapJioCall(gadget, method_name, argument_list) {
    var storage = gadget.state_parameter_dict.jio_storage;
    if (storage === undefined) {
      return gadget.redirect({page: "jio_configurator"});
    }
    return storage[method_name].apply(storage, argument_list)
      .push(undefined, function (error) {
        if ((error.target !== undefined) && (error.target.status === 401)) {
          var regexp,
            site,
            auth_page;
          if (gadget.state_parameter_dict.jio_storage_name === "ERP5") {
            regexp = /^X-Delegate uri=\"(http[s]?:\/\/[\/\-\[\]{}()*+=:?&.,\\\^$|#\s\w%]+)\"$/;
            auth_page = error.target.getResponseHeader('WWW-Authenticate');
            if (regexp.test(auth_page)) {
              site = UriTemplate.parse(
                regexp.exec(auth_page)[1]
              ).expand({
                came_from: window.location.href,
                cors_origin: window.location.origin,
                });
            }
          }
          if (gadget.state_parameter_dict.jio_storage_name === "DAV") {
            regexp = /^Nayookie login_url=(http[s]?:\/\/[\/\-\[\]{}()*+=:?&.,\\\^$|#\s\w%]+)$/;
            auth_page = error.target.getResponseHeader('WWW-Authenticate');
            if (regexp.test(auth_page)) {
              site = UriTemplate.parse(
                regexp.exec(auth_page)[1]
              ).expand({
                back_url: window.location.href,
                origin: window.location.origin,
                });
            }
          }
          if (site) {
            return gadget.redirect({ toExternal: true, url: site});
          }
        }
        throw error;
      });
  }

  rJS(window)

    .ready(function (gadget) {
      // Initialize the gadget local parameters
      gadget.state_parameter_dict = {};
    })

    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getSettingList", "getSettingList")
    .declareAcquiredMethod("setSetting", "setSetting")

    .declareMethod('createJio', function (jio_options) {
      var gadget = this;
      if (jio_options === undefined) {
        return;
      }
      this.state_parameter_dict.jio_storage = jIO.createJIO(jio_options);
      return this.getSetting("jio_storage_name")
        .push(function (jio_storage_name) {
          gadget.state_parameter_dict.jio_storage_name = jio_storage_name;
        });
    })
    .declareMethod('allDocs', function () {
      return wrapJioCall(this, 'allDocs', arguments);
    })
    .declareMethod('allAttachments', function () {
      return wrapJioCall(this, 'allAttachments', arguments);
    })
    .declareMethod('get', function () {
      return wrapJioCall(this, 'get', arguments);
    })
    .declareMethod('put', function () {
      return wrapJioCall(this, 'put', arguments);
    })
    .declareMethod('post', function () {
      return wrapJioCall(this, 'post', arguments);
    })
    .declareMethod('remove', function () {
      return wrapJioCall(this, 'remove', arguments);
    })
    .declareMethod('getAttachment', function () {
      return wrapJioCall(this, 'gettAttachment', arguments);
    })
    .declareMethod('putAttachment', function () {
      return wrapJioCall(this, 'putAttachment', arguments);
    })
    .declareMethod('removeAttachment', function () {
      return wrapJioCall(this, 'removeAttachment', arguments);
    })
    .declareMethod('repair', function () {
      var gadget = this;
      return this.getSetting("jio_storage_name")
       .push(function (jio_storage_name) {
         if (jio_storage_name === 'ERP5') {
           return gadget.getSettingList(['jio_storage_description', 'me'])
             .push(function (result_list) {
               var additional_query_list = [],
                 service_query =  new ComplexQuery({
                   operator: 'OR',
                   query_list: [],
                   type: "complex"
                 }),
                 me;
               gadget.state_parameter_dict.jio_storage = jIO.createJIO(result_list[0].remote_sub_storage);
               return wrapJioCall(gadget, 'allDocs', [
                   {
                     "query": '(selection_domain_use:"hr" AND translated_validation_state_title: "validated")',
                     "limit": [0, 1000]
                   }
                 ])
                 .push(function (result) {
                   var i;
                   if (result.data.rows.length) {
                     for (i = 0; i < result.data.rows.length; i += 1) {
                       service_query.query_list.push(new SimpleQuery({
                         key: 'id',
                         operator: '',
                         type: "simple",
                         value: result.data.rows[i].id.split('/')[1]
                       }));
                     }
                     additional_query_list.push(new ComplexQuery({
                       operator: 'AND',
                       query_list: [
                         new SimpleQuery({
                           key: 'portal_type',
                           operator: '',
                           type: "simple",
                           value: 'Service'
                         }),
                         service_query
                       ],
                       type: "complex"
                     }));
                   }

                  if (! result_list[1]) {
                    return wrapJioCall(gadget, 'getAttachment', ['acl_users', result_list[0].remote_sub_storage.url, {format: "json"}])
                      .push(function (result) {
                        me = result._links.me ? result._links.me.href : 'manager';
                        return gadget.setSetting('me', me);
                      })
                  } else {
                    me = result_list[1];
                  }
                })
                .push(function () {
                  additional_query_list.push(new ComplexQuery({
                    operator: 'AND',
                    query_list: [
                      new SimpleQuery({
                        key: 'portal_type',
                        operator: '',
                        type: "simple",
                        value: 'Person'
                      }),
                      new SimpleQuery({
                        key: 'id',
                        operator: '',
                        type: "simple",
                        value: me.split("/")[1]
                      })
                    ],
                    type: "complex"
                   }));

                   result_list[0].query.query = getSynchronizeQuery(additional_query_list);
                   gadget.state_parameter_dict.jio_storage = jIO.createJIO(result_list[0]);
                   return gadget.setSetting('jio_storage_description', result_list[0]);
                });
             });
         }
       })
      .push(function () {
        return wrapJioCall(gadget, 'repair', arguments);
      })
       .push(function () {
         return gadget.setSetting('last_sync_date', new Date().toLocaleString());
      });
  });

}(window, rJS, jIO));