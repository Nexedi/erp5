/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query*/
(function (window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query) {
  "use strict";

  const STATUS_OK = "green";
  const STATUS_NOT_OK = "red";

  function getProjectElementList(gadget) {

    function getComplexQuery(query_dict, operator, extra_query) {
      var key,
        query_list = [];
      for (key in query_dict) {
        if (query_dict.hasOwnProperty(key)) {
          query_list.push(new SimpleQuery({
            key: key,
            operator: "=",
            type: "simple",
            value: query_dict[key]
          }));
        }
      }
      if (extra_query) {
        query_list.push(extra_query);
      }
      return new ComplexQuery({
        operator: operator,
        query_list: query_list,
        type: "complex"
      });
    }

    var i,
      project_query = getComplexQuery({"portal_type" : "Project",
                                       "validation_state" : "validated"},
                                      "AND"),
      milestone_query = getComplexQuery({"portal_type" : "Project Milestone",
                                         "parent__validation_state" : "validated"},
                                        "AND"),
      test_result_query = Query.objectToSearchText(
        getComplexQuery({"portal_type" : "Test Result",
                         "source_project__validation_state" : "validated"},
                        "AND")),
      //document_query,
      //portal_type_list = ["Task", "Bug", "Task Report"],
      //valid_state_list = ["planned", "ordered", "confirmed", "delivered", "ready"],
      test_state_list = ["failed", "stopped"],
      date_query,
      one_year_old_date = new Date();

    test_result_query += ' AND simulation_state: ("' + test_state_list.join('", "') + '")';

    //TODO filter too old objects?
    one_year_old_date.setFullYear(one_year_old_date.getFullYear() - 1);
    one_year_old_date = one_year_old_date.toISOString();
    one_year_old_date = one_year_old_date.substring(0, one_year_old_date.length - 5).replace("T", " ");
    date_query = new SimpleQuery({
      type: "simple",
      key: "creation_date",
      operator: ">",
      value: one_year_old_date
    });

    /*document_query = Query.objectToSearchText(new SimpleQuery({
      key: "source_project__validation_state",
      operator: "=",
      type: "simple",
      value: "validated"
    }));
    // done with string queries directly because there is no way to do "key IN <list-of-values>" with Query
    // unless appending simple queries with AND by iterating on list but it's inefficient
    document_query += ' AND portal_type: ("' + portal_type_list.join('", "') + '")';
    document_query += ' AND simulation_state: ("' + valid_state_list.join('", "') + '")';*/

    return new RSVP.Queue()
      .push(function () {
        var promise_list = [],
          limit = [0, 100000],
          select_list = ['source_project', 'portal_type', 'modification_date'];
        promise_list.push(gadget.jio_allDocs({
          query: Query.objectToSearchText(project_query),
          limit: limit,
          select_list: ['title'],
          sort_on: [["modification_date", "ascending"]]
        }));
        promise_list.push(gadget.jio_allDocs({
          query: Query.objectToSearchText(milestone_query),
          limit: limit,
          select_list: select_list,
          sort_on: [["modification_date", "descending"]]
        }));
        promise_list.push(gadget.jio_allDocs({
          query: test_result_query,
          limit: limit,
          select_list: ['source_project__relative_url', 'modification_date'],
          group_by: ['source_project__relative_url'],
          sort_on: [["modification_date", "descending"]]
        }));
        /*promise_list.push(gadget.jio_allDocs({
          query: document_query,
          limit: limit,
          select_list: select_list,
          sort_on: [["modification_date", "descending"]]
        }));*/
        return RSVP.all(promise_list);
      })
      .push(function (result_list) {
        return [result_list[0].data.rows, result_list[1].data.rows, result_list[2].data.rows/*, result_list[3].data.rows*/];
      });
  }

  function renderProjectList(project_info_dict, project_list, milestone_list, test_result_list) {
    var i,
      item,
      project_html,
      left_div_html,
      project_html_element_list,
      left_line_html,
      ul_list = document.getElementById("js-project-list"),
      //XXX hardcoded for now (build a template?)
      line_title_list = {"Task": "Tasks",
                         "Bug" : "Bugs",
                         "Task Report": "Task Reports"},
      project_dict,
      type;

    function createProjectHtmlElement(project_id, project_title) {
      var project_element = document.createElement('li'),
        box_div = document.createElement('div'),
        title_div = document.createElement('div'),
        info_div = document.createElement('div'),
        left_info_div = document.createElement('div'),
        right_div = document.createElement('div'),
        right_line_div = document.createElement('div'),
        forum_link = document.createElement('a');
      box_div.classList.add("project-box");
      title_div.classList.add("project-title");
      title_div.innerHTML = project_title;
      info_div.classList.add("project-info");
      left_info_div.classList.add("left");
      right_line_div.classList.add("project-line");
      forum_link.href = "todo";
      forum_link.innerHTML = project_id + " forum link";
      right_line_div.appendChild(forum_link);
      right_div.appendChild(right_line_div);
      info_div.appendChild(left_info_div);
      info_div.appendChild(right_div);
      box_div.appendChild(title_div);
      box_div.appendChild(info_div);
      project_element.appendChild(box_div);
      return [project_element, left_info_div];
    }

    function createProjectLineHtmlElement(portal_type, total_count, out_count, status_color) {
      var line_div = document.createElement('div'),
        status = document.createElement('span'),
        name = document.createElement('span'),
        fail = document.createElement('span'),
        total = document.createElement('span');
      line_div.classList.add("project-line");
      status.classList.add("status");
      status.classList.add(status_color);
      name.classList.add("name");
      name.innerHTML = portal_type;
      total.innerHTML = total_count;
      fail.innerHTML = "(" + out_count + ")";
      line_div.appendChild(status);
      line_div.appendChild(name);
      line_div.appendChild(total);
      line_div.appendChild(fail);
      return line_div;
    }

    for (i = 0; i < project_list.length; i += 1) {
      project_html_element_list = createProjectHtmlElement(project_list[i].id, project_list[i].value.title);
      project_html = project_html_element_list[0];
      left_div_html = project_html_element_list[1];

      project_dict = project_info_dict[project_list[i].id];
      for (type in project_dict) {
        if (project_dict.hasOwnProperty(type)) {
          left_line_html = createProjectLineHtmlElement(((line_title_list.hasOwnProperty(type)) ? line_title_list[type] : type),
                                                        project_dict[type].total, project_dict[type].outdated,
                                                        ((project_dict[type].outdated > 0) ? STATUS_NOT_OK : STATUS_OK));
          left_div_html.appendChild(left_line_html);
        }
      }
      ul_list.appendChild(project_html);
    }
  }

  rJS(window)

    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("getSetting", "getSetting")

    .declareMethod('render', function (options) {
      if (options.project_info_dict) {
        options.project_info_dict = JSON.parse(options.project_info_dict);
      }
      return this.changeState(options);
    })

    .onStateChange(function (modification_dict) {
      var gadget = this;
      return getProjectElementList(gadget)
        .push(function (element_list) {
          renderProjectList(modification_dict.project_info_dict, element_list[0], element_list[1], element_list[2]);
        });
    })

    .declareMethod('getContent', function () {
      return {};
    })

    .declareMethod('checkValidity', function () {
      return true;
    });

}(window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query));