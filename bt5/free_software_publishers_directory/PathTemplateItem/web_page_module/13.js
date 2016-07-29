/*global window, rJS, RSVP, UriTemplate, URI, Query, SimpleQuery, ComplexQuery, jIO */
/*jslint indent: 2, maxerr: 3, nomen: true */
(function (window, rJS, RSVP, UriTemplate, URI, Query, SimpleQuery, ComplexQuery, jIO) {
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
              }
            },
          })
          .push(function (data) {
            return gadget.state_parameter_dict.jio_storage.repair()
              .push(function () {
                return publisher_storage.allDocs()
                  .push(function (data) {
                    var publisher_id_list = [];
                
                    for (var i in data.data.rows) {
                      var id = data.data.rows[i].id;
                      if(id.indexOf("_replicate_") < 0) {
                        publisher_id_list.push(id);
                      }
                    }
                
                    var promise_list = [];
                
                    function setPortalTypeOnPublisher (j) {
                      return publisher_storage.get(publisher_id_list[j])
                      .push(function (publisher_object) {
                        publisher_object.portal_type = "publisher";
                        return publisher_storage.put(publisher_id_list[j], publisher_object);
                      });
                    };
                
                    for(var i in publisher_id_list) {
                      promise_list.push(setPortalTypeOnPublisher(i));
                    }
                
                    return RSVP.all(promise_list);
                  })
                
                  // Create all the software Documents
                  .push(function () {
                    return publisher_storage.allDocs({
                      select_list: ['title', 'free_software_list'],
                      query: 'portal_type: "publisher"'
                    });
                  })
                  .push(function (publisher_list) {
                    var promise_list = [];
                    
                    function saveSoftwareDocument (publisher, software) {
                      software.portal_type = "software";
                      software.publisher = publisher;
                      return publisher_storage.put(software.title, software)
                    }
                
                    function saveSoftwareListFromPublisher (j) {
                      var publisher = publisher_list.data.rows[j].value.title,
                        software_list = publisher_list.data.rows[j].value.free_software_list;
                      
                      var save_software_promise_list = []
                      
                      for (var i in software_list) {
                        save_software_promise_list.push(saveSoftwareDocument(publisher, software_list[i]))
                      }
                
                      return RSVP.all(save_software_promise_list);
                    }
                    
                    for (var i in publisher_list.data.rows) {
                      promise_list.push(saveSoftwareListFromPublisher(i));
                    }
                    
                    return RSVP.all(promise_list);
                  });
              });
          });
        });
    })

    .declareMethod('allDocs', function (option_dict) {
      return this.state_parameter_dict.jio_storage.allDocs(option_dict);
    })
    .declareMethod('get', function (id) {
      return this.state_parameter_dict.jio_storage.get(id);
    })
    .declareMethod('repair', function () {
      return this.state_parameter_dict.jio_storage.repair();
    });

}(window, rJS, RSVP, UriTemplate, URI, Query, SimpleQuery, ComplexQuery, jIO));