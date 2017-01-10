/*global window, rJS, RSVP, UriTemplate, URI, Query, SimpleQuery, ComplexQuery, jIO */
/*jslint indent: 2, maxerr: 3, nomen: true */
(function (window, rJS, RSVP, UriTemplate, URI, Query, SimpleQuery, ComplexQuery, jIO) {
  "use strict";
  
  // XXX... lord have mercy
  function mockupQueryParam(param, select_list) {
    var wild_param = param.replace(/[()]/g,"%").replace(/ /g,''),
      return_list = [],
      len,
      i;
    for (i = 0, len = select_list.length; i < len; i += 1) {
      return_list.push(select_list[i] + ':"' + wild_param + '"');
    }
    return ' (' + return_list.join(' OR ') + ')';
  }

  // XXX... lord, I need more mercy
  function updateQuery(query, select_list) {
    var query_param_list = query.split("AND"),
      param,
      len,
      i;
    for (i = 0, len = query_param_list.length; i < len; i += 1) {
      param = query_param_list[i];
      
      // search
      if (param.split(":").length !== 2) {
        return query.replace(param, mockupQueryParam(param, select_list));
      }
      
      // hide rows
      if (param.indexOf("catalog.uid") > 0) {
        return query.replace("catalog.", "");
      }
    }
    return query;
  }
  
  function createDataSheets(gadget) {
    gadget.jio_allDocs = gadget.state_parameter_dict.jio_storage.allDocs;
    gadget.jio_get = gadget.state_parameter_dict.jio_storage.get;
    gadget.jio_put = gadget.state_parameter_dict.jio_storage.put;
    return gadget.jio_allDocs()

      /////////////////////////////////////////////////////////////////
      // Make Publisher datasheets
      /////////////////////////////////////////////////////////////////
      .push(function (data) {
        var uid = 0;

        function isReplicate(el) {
          return (el.id.indexOf("_replicate_") < 0);
        }
        
        function setPortalTypeOnPublisher (el) {
          return gadget.jio_get(el.id)
          .push(function (publisher_object) {
            publisher_object.portal_type = "publisher";
            
            //publisher_object.url = publisher_object.website;
            publisher_object.uid = (uid++).toString();
            
            return gadget.jio_put(publisher_object.uid, publisher_object);
          });
        }
        
        var publisher_id_list = data.data.rows,
          promise_list = publisher_id_list.map(setPortalTypeOnPublisher);

        return RSVP.all(promise_list);
      })
      .push(function () {
        return gadget.jio_allDocs({
          select_list: ['title', 'free_software_list', 'website'],
          query: 'portal_type: "publisher"'
        });
      })
      /////////////////////////////////////////////////////////////////
      // Make Software datasheets
      /////////////////////////////////////////////////////////////////
      .push(function (publisher_list) {
        
        var uid = 1000;
        
        function saveSoftwareListFromPublisher (j) {
          var publisher = j.value.title,
            software_list = j.value.free_software_list,
            website = j.value.website;
          
          function saveSoftwareDocument (software) {
            software.portal_type = "software";
            software.publisher = publisher;
            software.website = website;
            software.uid = (uid++).toString();

            return gadget.jio_put(software.uid, software);
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
            'website',
            'success_case_list',
            'publisher',
            'category_list',
          ],
          query: 'portal_type: "software"'
        });
      })
      /////////////////////////////////////////////////////////////////
      // Make Success Case datasheets
      /////////////////////////////////////////////////////////////////
      .push(function (software_list) {
        var uid = 2000;
        
        function saveSuccessCaseListFromSoftware (softwareObject) {
          var software = softwareObject.value,
            publisher = softwareObject.value.publisher,
            website = softwareObject.value.website,
            success_case_list = softwareObject.value.success_case_list;
          
          function isValid (success_case) {
            return (success_case !== "N/A" &&
                    success_case.title !== "" && 
                    success_case.title !== "N/A");
          }
          
          function addProperties (success_case) {
            success_case.portal_type = "success_case";
            success_case.software = software.title;
            success_case.publisher = publisher;
            success_case.category_list = software.category_list;
            success_case.uid = (uid++).toString();
            return gadget.jio_put(success_case.uid, success_case);
          }

          var save_success_case_promise_list = 
            success_case_list.filter(isValid)
                             .map(addProperties);

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
      });
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
        .push(function (setting_list) {
          return gadget.state_parameter_dict.jio_storage.createJio({
            check_local_modification: false,
            check_local_creation: false,
            check_local_deletion: false,
            type: "replicate",
            local_sub_storage : {
              type: "query",
              sub_storage: {
              type: "memory",
              }
            },
            remote_sub_storage : {
              type: "query",
              sub_storage: {
                type: "publisher_storage",
                url: "/"
              }
            },
          })
          .push(function (data) {
            return gadget.state_parameter_dict.jio_storage.repair();
          })
          .push(function () {
            return createDataSheets(gadget);
          });
        });
    })

    .declareMethod('allDocs', function (option_dict) {
      option_dict.query = updateQuery(option_dict.query, option_dict.select_list);
      //console.log(option_dict.query)
      return this.state_parameter_dict.jio_storage.allDocs(option_dict);
    })
    .declareMethod('getAttachment', function (id, view) {
      return this.state_parameter_dict.jio_storage.getAttachment(id, view);
    })
    .declareMethod('get', function (id) {
      return this.state_parameter_dict.jio_storage.get(id);
    })
    .declareMethod('put', function (object1, object2) {
      return this.state_parameter_dict.jio_storage.put(object1, object2);
    })
    .declareMethod('repair', function () {
      return this.state_parameter_dict.jio_storage.repair();
    });
}(window, rJS, RSVP, UriTemplate, URI, Query, SimpleQuery, ComplexQuery, jIO));