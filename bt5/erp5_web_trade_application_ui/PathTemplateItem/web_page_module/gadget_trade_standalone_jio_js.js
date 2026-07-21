/*global window, rJS, RSVP, UriTemplate, URI, Query, SimpleQuery, ComplexQuery, jIO */
/*jslint indent: 2, maxlen: 80*/
/*jslint nomen: true*/
(function (window, rJS, RSVP) {
  "use strict";
  var document_url;

  rJS(window)
    .ready(function (gadget) {
      return gadget.getDeclaredGadget('jio')
        .push(function (jio_gadget) {
          // Initialize the gadget local parameters
          gadget.state_parameter_dict = {jio_storage: jio_gadget};
        });
    })

    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareMethod('createJio', function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.getSetting('hateoas_url');
        })
        .push(function (hateoas_url) {
          var position, url;
          position = hateoas_url.indexOf("hateoas");
          url = hateoas_url.substring(0, position);
          document_url = url +  "trade.json/getData";
        })
        .push(function () {
          return gadget.state_parameter_dict.jio_storage.createJio({
            type: "query",
            sub_storage: {
              type: "uuid",
              sub_storage: {
                type: "indexeddb",
                database: "trade"
              }
            }
          });
        })
        .push(function () {
          return jIO.util.ajax({
            type: "GET",
            url: document_url,
            dataType: "text"
          });
        })
        .push(function (response) {
          var json_data = JSON.parse(response.target.response),
            doc_id,
            rows = [],
            promise_list;
          for (doc_id in json_data) {
            if (json_data.hasOwnProperty(doc_id)) {
              rows.push({
                id: doc_id,
                value: json_data[doc_id]
              });
            }
          }
          function putDataInIndexeddb(result) {
            return gadget.state_parameter_dict.jio_storage
              .put(result.id, result.value);
          }
          promise_list = rows.map(putDataInIndexeddb);
          return RSVP.all(promise_list);
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
      return this.state_parameter_dict.jio_storage.repair();
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