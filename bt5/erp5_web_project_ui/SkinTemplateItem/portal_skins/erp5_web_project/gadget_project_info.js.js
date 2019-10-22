/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, FileReader, Blob, jIO, ensureArray, //Handlebars,
lockGadgetInQueue, unlockGadgetInQueue, unlockGadgetInFailedQueue*/
(function (window, rJS, RSVP, document, FileReader, Blob, jIO, ensureArray, //Handlebars,
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
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")

    .declareMethod('render', function (options) {
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

      return gadget.jio_getAttachment(modification_dict.jio_key, "links")
        .push(function (erp5_document) {
          var view_list = ensureArray(erp5_document._links.view),
            task_view = view_list.filter(d => d.name === "task_list")[0].href,
            bug_view = view_list.filter(d => d.name === "bug_list")[0].href,
            milestone_view = view_list.filter(d => d.name === "milestone")[0].href,
            task_report_view = view_list.filter(d => d.name === "task_report_list")[0].href;

          gadget.element.querySelectorAll("h1")[0].innerHTML = modification_dict.project_title;

          enableLink(document.getElementById("forum_link"), modification_dict.forum_link);
          enableLink(document.getElementById("description_link"), modification_dict.description_link);

          generateLink(gadget, document.getElementById("milestone_link"), 'display_with_history', {
            'jio_key': 'milestone_module', 'page': 'form', 'view': milestone_view,
            'field_listbox_sort_list:json': [["stop_date", "ascending"]]
          }, {});

          generateLink(gadget, document.getElementById("support_request_link"), 'display_with_history', {
            'jio_key': 'support_request_module',
            'page': 'form',
            'view': 'view',
            'field_listbox_sort_list:json': [["delivery.start_date", "descending"]],
            //TODO use a domain for state
            'extended_search': ('destination_project_title:  "' + modification_dict.project_title + '" AND translated_simulation_state_title:  "Submitted"')
          });

          var bug_options = {
            'jio_key': 'bug_module', 'page': 'form', 'view': bug_view,
            'field_listbox_sort_list:json': [["start_date", "descending"]],
            'field_listbox_column_list:json': ["title", "description", "start_date"],
            //'extended_search': ('source_project_title:  "' + modification_dict.project_title + '" AND selection_domain_state_bug_domain:  "started"')
            'extended_search': ('source_project_title:  "' + modification_dict.project_title + '" AND translated_simulation_state_title:  "Open"')
          }, closed_bug_options = {};
          generateLink(gadget, document.getElementById("bug_link"), 'display', bug_options);
          Object.assign(closed_bug_options, bug_options);
          closed_bug_options.extended_search = ('source_project_title:  "' + modification_dict.project_title + '" AND translated_simulation_state_title:  "Resolved"');
          generateLink(gadget, document.getElementById("closed_bug_link"), 'display', closed_bug_options);
          generateInfo(gadget, document.getElementById("bug_count"), project_url + "/Project_bugs");
          generateInfo(gadget, document.getElementById("closed_bug_count"), project_url + "/Project_bugs?closed=1");

          generateLink(gadget, document.getElementById("task_link"), 'display_with_history', {
            'jio_key': 'task_module', 'page': 'form', 'view': 'view',
            'field_listbox_sort_list:json': [["delivery.start_date", "descending"]],
            'field_listbox_column_list:json': ["title", "delivery.start_date", "delivery.stop_date", "destination_decision_title",
                                               "source_title", "destination_title", "total_quantity", "task_line_quantity_unit_title"],
            'extended_search': ('source_project_title:  "' + modification_dict.project_title + '" AND selection_domain_state_task_domain:  "started"')
          });
          generateInfo(gadget, document.getElementById("task_count"), project_url + "/Project_tasks");
          generateInfo(gadget, document.getElementById("unassigned_task_count"), project_url + "/Project_tasksToAssigne");

          var task_report_options = {
            'jio_key': 'task_report_module', 'page': 'form', 'view': 'view',
            'field_listbox_sort_list:json': [["delivery.start_date", "descending"]],
            'field_listbox_column_list:json': ["title", "delivery.start_date", "delivery.stop_date", "destination_decision_title",
                                               "source_title", "destination_title", "total_quantity", "task_line_quantity_unit_title"],
            'extended_search': ('source_project_title:  "' + modification_dict.project_title + '" AND selection_domain_state_task_report_domain:  "started"')
          }, closed_task_report_options = {};
          generateLink(gadget, document.getElementById("report_link"), 'display_with_history', task_report_options);
          Object.assign(closed_task_report_options, task_report_options);
          closed_task_report_options.extended_search = ('source_project_title:  "' + modification_dict.project_title + '" AND selection_domain_state_task_report_domain:  "closed"');
          generateLink(gadget, document.getElementById("closed_report_link"), 'display_with_history', closed_task_report_options);
          generateInfo(gadget, document.getElementById("report_count"), project_url + "/Project_taskReports");
          generateInfo(gadget, document.getElementById("closed_report_count"), project_url + "/Project_taskReports?closed=1");

          generateLink(gadget, document.getElementById("test_result_link"), 'display_with_history', {
            'jio_key': 'test_result_module',
            'page': 'form',
            'view': 'view',
            'field_listbox_sort_list:json': [["delivery.start_date", "descending"]],
            'extended_search': ('source_project_title:  "' + modification_dict.project_title + '"')
          });
          generateInfo(gadget, document.getElementById("last_test_result"), project_url + "/Project_lastTestResult");

          generateLink(gadget, document.getElementById("test_suite_link"), 'display_with_history', {
            'jio_key': 'test_suite_module',
            'page': 'form',
            'view': 'view',
            'field_listbox_sort_list:json': [["creation_date", "descending"]],
            'extended_search': ('source_project_title:  "' + modification_dict.project_title + '"')
          });

        });
    })

    .declareMethod('getContent', function () {
      return {};
    })

    .declareMethod('checkValidity', function () {
      return true;
    });

}(window, rJS, RSVP, document, FileReader, Blob, jIO, ensureArray, //Handlebars,
  lockGadgetInQueue, unlockGadgetInQueue, unlockGadgetInFailedQueue));