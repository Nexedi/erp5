/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, document, RSVP, calculatePageTitle, jIO) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('getUrlFor', function (argument_list) {
      if (argument_list[0].command === 'change') {
        if (argument_list[0].options.page == "action") {
          return this.getUrlFor({command: 'change', options: {page: "fif_action"}});
        }
      }
      return this.getUrlFor.apply(this, argument_list);
    })
    .allowPublicAcquisition('updateHeader', function (argument_list) {
      var header_dict = {
          page_title: "File : " + this.state.document_title,
          selection_url: argument_list[0].selection_url,
          //next_url: argument_list[0].next_url,
          //previous_url: argument_list[0].previous_url,
          actions_url: argument_list[0].actions_url
        };
      return this.updateHeader(header_dict);
    })
    .onStateChange(function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          var view_dict = {},
              group_list = [],
              metadata = gadget.state.metadata;
          view_dict.my_title = {
              "title": "Title",
              "default": gadget.state.document_title,
              "key": "field_my_title"
            };
          group_list.push(["left", [["my_title"]]]);
          view_dict.my_reference = {
              "title": "Reference",
              "default": gadget.state.reference,
              "key": "field_my_reference"
            };
          group_list.push(["right", [["my_reference"]]]);
          if (metadata !== undefined) {
            if (Object.keys(metadata).length == 1) {
              var akey = Object.keys(metadata)[0];
              if (akey == "csv") {
                var table = document.getElementById("csv_table"),
                  array = metadata[akey];
                document.getElementById("text_content_title").innerHTML = "CSV file content sample:";
                for (var i = 0; i < array.length; i++) {
                  var newRow = table.insertRow(table.length);
                  for (var j = 0; j < array[i].length; j++) {
                    var cell = newRow.insertCell(j);
                    cell.innerHTML = array[i][j];
                  }
                }
              }
              else {
                document.getElementById("text_content_title").innerHTML = akey;
                document.getElementById("text_content").innerHTML = metadata[akey];
              }
            }
            else {
              var nkey = 0;
              for (var key in metadata) {
                if (metadata.hasOwnProperty(key)) {
                  var side = (nkey % 2 === 0) ? "left" : "right";
                  view_dict[key] = {
                    "title": key,
                    "default": metadata[key],
                    "key": "field_" + key
                  };
                  group_list.push([side, [[key]]]);
                }
                nkey++;
              }
            }
          }
          else {
            view_dict["my_metadata"] = {
              "title": "Metadata",
              "default": "Could not find metadata for this file",
              "key": "field_my_metadata"
            };
            group_list.push(["left",[["my_metadata"]]])
          }
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": view_dict},
              "_links": {
                "type": {
                  name: ""
                }
              }
            },
              form_definition: {
                group_list: group_list
              }
            });
        });
    })
    .declareMethod("getDescriptorContent", function (descriptorReference) {
      var url = "/erp5/getDescriptorHTMLContent?reference=" + descriptorReference,
          xmlHttp = new XMLHttpRequest();
      try {
          xmlHttp.open("GET", url, false);
          xmlHttp.send(null);
          return xmlHttp.responseText;
      }
      catch(err) {
          console.log("URL error: " + err)
          return "";
      }
    })
    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.jio_get(options.jio_key)
      .push(function (result) {
        var file_info = result;
        return gadget.getDescriptorContent(file_info.reference)
        .push(function (htmlContent) {
          return gadget.changeState({"document_title" : file_info.title,
                                     "reference" : file_info.reference,
                                     "textcontent" : htmlContent});
        });
      });
    })
    .declareService(function () {
      try {
          var json_dict = JSON.parse(this.state.textcontent)
      }
      catch(err) {
          console.log("Error reading Data Descriptor JSON: " + err)
          return
      }
      return this.changeState({"metadata" : json_dict });
    });
}(window, rJS, document, RSVP, calculatePageTitle, jIO));









