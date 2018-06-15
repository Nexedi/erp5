/*global window, rJS, RSVP, Handlebars, loopEventListener, $, document */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
(function (window, rJS, RSVP, Handlebars, loopEventListener, $, document) {
  "use strict";

  var INTERFACE_GADGET_SCOPE = "interface_gadget",
  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
    // Precompile the templates while loading the first gadget instance
    gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    report_widget_table = Handlebars.compile(
      templater.getElementById("report-widget-table").innerHTML
    );

  function renderInitialReport(gadget, gadget_list) {
    var row_list = [],
      column_list = ['Gadget Name', 'Declared Interfaces', 'Validation Status'],
      cell_list,
      default_status = "In Progress",
      content = '',
      i;
    for (i = 0; i < gadget_list.length; i += 1) {
      cell_list = [{
        default_class: "gadget_name",
        value: gadget_list[i]
      }, {
        default_class: "interface_list",
        value: default_status
      }, {
        default_class: "validation_status",
        value: default_status
      }];
      row_list.push({
        "cell_list": cell_list,
        "default_id": gadget_list[i].substr(0, gadget_list[i].indexOf('.'))
      });
    }
    content += report_widget_table({
      column_list: column_list,
      row_list: row_list
    });
    gadget.props.content_element.innerHTML = content;
    $(gadget.props.element).trigger("create");
  }


  function verifyGadgetImplementation(gadget, verify_gadget_url) {
    var interface_gadget,
      interface_list = [],
      default_validation_status = {result: "N/A"};
    return new RSVP.Queue()
      .push(function () {
        return gadget.getDeclaredGadget(INTERFACE_GADGET_SCOPE);
      })
      .push(function (i_gadget) {
        interface_gadget = i_gadget;
        return interface_gadget.getDeclaredGadgetInterfaceList(
          verify_gadget_url
        );
      })
      .push(function (temp_interface_list) {
        interface_list = temp_interface_list;
        if (interface_list.length > 0) {
          return interface_gadget.verifyGadgetInterfaceImplementation(
            verify_gadget_url
          );
        }
        return default_validation_status;
      })
      .push(function (validation_status) {
        return [interface_list, validation_status];
      }, function (error) {
        default_validation_status.result = false;
        default_validation_status.result_message = "Error with gadget loading";
        default_validation_status.details = error.message;
        return [interface_list, default_validation_status];
      });
  }

  function updateReportData(gadget, report_data) {
    var id = "#" + report_data.id.replace('/', '\\/'),
      update_element = gadget.props.content_element.querySelector(id),
      interface_data = '',
      validation_status = report_data.validation_status,
      validation_message = report_data.validation_message,
      i,
      interface_name;
    if (report_data.interface_list.length) {
      for (i = 0; i < report_data.interface_list.length; i += 1) {
        interface_name = report_data.interface_list[i].substr(
          report_data.interface_list[i].lastIndexOf('/') + 1
        );
        interface_data += (interface_name + '<br />');
      }
    } else {
      interface_data = 'None';
    }
    if (report_data.validation_status === true) {
      validation_status = "Success";
      update_element.setAttribute('style', 'color: green');
    }
    if (report_data.validation_status === false) {
      validation_status =
        (validation_message !== undefined ? validation_message : "Failure");
      update_element.setAttribute('style', 'cursor: pointer; color: red');
      update_element.className += "error expand";
    }
    gadget.props.error_data[report_data.id] = report_data.error_detail;
    update_element.querySelector(".validation_status").innerHTML =
      validation_status;
    update_element.querySelector(".validation_status").className += " final";
    update_element.querySelector(".interface_list").innerHTML = interface_data;
  }

  function updateGadgetData(gadget, verify_gadget_url) {
    return RSVP.Queue()
      .push(function () {
        return verifyGadgetImplementation(gadget, verify_gadget_url);
      })
      .push(function (verify_result) {
        var result_dict = {
          id: verify_gadget_url.substr(0, verify_gadget_url.indexOf('.')),
          gadget_name: verify_gadget_url,
          interface_list: verify_result[0],
          validation_status: verify_result[1].result,
          validation_message: verify_result[1].result_message,
          error_detail: verify_result[1].details
        };
        return updateReportData(gadget, result_dict);
      });
  }

  function validateAppGadgetList(gadget, gadget_list) {
    var i;
    for (i = 0; i < gadget_list.length; i += 1) {
      updateGadgetData(gadget, gadget_list[i]);
    }
  }

  function toggleErrorRow(gadget, source_element) {
    if (source_element.className.indexOf("expand") > -1) {
      var error_tr = document.createElement('tr'),
        error_td = error_tr.insertCell(0);
      error_tr.id = source_element.id + '_errordata';
      error_td.className = 'errordata';
      error_td.colSpan = "3";
      error_td.innerText = gadget.props.error_data[source_element.id];
      source_element.parentNode.insertBefore(error_tr,
                                             source_element.nextSibling);
      source_element.className = source_element.className.replace("expand",
                                                                  "shrink");
    } else if (source_element.className.indexOf("shrink") > -1) {
      source_element.parentNode.removeChild(source_element.nextSibling);
      source_element.className = source_element.className.replace("shrink",
                                                                  "expand");
    }
    return;
  }

  Handlebars.registerPartial(
    "report-widget-table-partial",
    templater.getElementById("report-widget-table-partial").innerHTML
  );

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
      g.props.error_data = {};
    })

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.content_element = element.querySelector('.validation_report');
        });
    })

    .declareMethod("render", function (options) {
      var gadget = this,
        appcache_url = options.appcache_url,
        gadget_list;
      return new RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget(INTERFACE_GADGET_SCOPE);
        })
        .push(function (interface_gadget) {
          return interface_gadget.getGadgetListFromAppcache(appcache_url);
        })
        .push(function (filtered_gadget_list) {
          gadget_list = filtered_gadget_list;
          return renderInitialReport(gadget, gadget_list);
        })
        .push(function () {
          return validateAppGadgetList(gadget, gadget_list);
        }, function () {
          return gadget.redirect({
            found: false
          });
        });
    })

    .declareMethod("reportPageDummyMethod1", function () {
      // A dummy method to fulfil the interface implementation requirement.
      return;
    })
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////

    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared services
    /////////////////////////////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      function rowSubmit(submit_data) {
        var parent_element = submit_data.target.parentElement;
        if (parent_element.className.indexOf("error") > -1) {
          return toggleErrorRow(gadget, parent_element);
        }
      }

      return loopEventListener(
        gadget.props.content_element,
        'click',
        false,
        rowSubmit
      );
    });

}(window, rJS, RSVP, Handlebars, loopEventListener, $, document));