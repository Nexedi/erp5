/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, FileReader, Blob, jIO, //Handlebars,
lockGadgetInQueue, unlockGadgetInQueue, unlockGadgetInFailedQueue*/
(function (window, rJS, RSVP, document, FileReader, Blob, jIO, //Handlebars,
           lockGadgetInQueue, unlockGadgetInQueue, unlockGadgetInFailedQueue) {
  "use strict";

  /*var gadget_klass = rJS(window),
    template_element = gadget_klass.__template_element,
    panel_template_body_list = Handlebars.compile(template_element
                         .getElementById("panel-template-body-list")
                         .innerHTML);*/

  function enableLink(link_element, url) {
    link_element.href = url;
    link_element.disabled = false;
    link_element.classList.remove("ui-disabled");
  }

  function generateLink(gadget, link_element, command, options) {
    //return gadget.getUrlFor({command: 'display', options: {page: "validator_form"}})
    return gadget.getUrlFor({command: command, options: options})
      /*.push(function (result) {
        return gadget.translateHtml(
          panel_template_body_list({
            "form_href": result
          })
        );
      })*/
      .push(function (result) {
        enableLink(link_element, result);
      });
  }

  function generateInfo(gadget, span_element, info_url) {
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax({
          url: info_url,
          dataType: 'text'
        });
      })
      .push(function (evt) {
        return evt.target.responseText.split('\n');
      })
      .push(function (result) {
        span_element.innerHTML = result;
      });
  }

  rJS(window)

    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    .declareMethod('render', function (options) {
      console.log("PROJECT INFO GADGET render options:");
      console.log(options);
      var state_dict = {
          jio_key: options.jio_key || "",
          //HACK
          forum_link: options.forum_link || "https://www.erp5.com/group_section/forum",
          description_link: options.description_link || "https://www.erp5.com/project_section/nexedi-erp5",
          project_title: options.project_title
        };
      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        base_site = window.location.origin + window.location.pathname,
        project_url = base_site + modification_dict.jio_key;

      gadget.element.querySelectorAll("h1")[0].innerHTML = modification_dict.project_title;

      enableLink(document.getElementById("forum_link"), modification_dict.forum_link);
      enableLink(document.getElementById("description_link"), modification_dict.description_link);

      generateLink(gadget, document.getElementById("bug_link"), 'display', {
        'jio_key': 'bug_module',
        'page': 'form',
        'view': 'view',
        'field_listbox_sort_list:json': [["delivery.start_date", "descending"]],
        //'field_listbox_column_list:json': ["title", "default_destination_section_title"],
        'extended_search': 'translated_simulation_state_title:  "Open"'
      });
      generateInfo(gadget, document.getElementById("bug_count"), project_url + "/Project_bugs");
      generateInfo(gadget, document.getElementById("closed_bug_count"), project_url + "/Project_bugs?closed=1");

      generateLink(gadget, document.getElementById("task_link"), 'display', {
        'jio_key': 'task_module',
        'page': 'form',
        'view': 'view',
        'field_listbox_sort_list:json': [["delivery.start_date", "descending"]]//,
        //'field_listbox_column_list:json': ["title", "default_destination_section_title"],
        //'extended_search': 'translated_simulation_state_title:  "Open"'
      });
      generateInfo(gadget, document.getElementById("task_count"), project_url + "/Project_tasks");
      generateInfo(gadget, document.getElementById("unassigned_task_count"), project_url + "/Project_tasksToAssigne");

      generateLink(gadget, document.getElementById("report_link"), 'display', {
        'jio_key': 'task_report_module',
        'page': 'form',
        'view': 'view',
        'field_listbox_sort_list:json': [["delivery.start_date", "descending"]]//,
        //'field_listbox_column_list:json': ["title", "default_destination_section_title"],
        //'extended_search': 'translated_simulation_state_title:  "Open"'
      });
      generateInfo(gadget, document.getElementById("report_count"), project_url + "/Project_taskReports");
      generateInfo(gadget, document.getElementById("closed_report_count"), project_url + "/Project_taskReports?closed=1");

      generateLink(gadget, document.getElementById("test_result_link"), 'display', {
        'jio_key': 'test_result_module',
        'page': 'form',
        'view': 'view',
        'field_listbox_sort_list:json': [["delivery.start_date", "descending"]]
      });
      generateInfo(gadget, document.getElementById("last_test_result"), project_url + "/Project_lastTestResult");

      generateLink(gadget, document.getElementById("test_suite_link"), 'display', {
        'jio_key': 'test_suite_module',
        'page': 'form',
        'view': 'view',
        'field_listbox_sort_list:json': [["delivery.start_date", "descending"]]
      });
    })

    .declareMethod('getContent', function () {
      return {};
    })

    .declareMethod('checkValidity', function () {
      return true;
    });

}(window, rJS, RSVP, document, FileReader, Blob, jIO, //Handlebars,
  lockGadgetInQueue, unlockGadgetInQueue, unlockGadgetInFailedQueue));