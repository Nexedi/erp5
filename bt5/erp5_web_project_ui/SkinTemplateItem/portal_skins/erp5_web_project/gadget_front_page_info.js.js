/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query*/
(function (window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query) {
  "use strict";

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
      non_milestone_query,
      aux_complex_query,
      aux_query_list = [],
      query_list = [],
      portal_type_list = ["Task", "Bug", "Task Report", "Benchmark Result"],
      valid_state_list = ["planned", "ordered", "confirmed", "started", "stopped", "delivered", "ready", "failed", "public_stopped"],
      date_query,
      test_result_query,
      one_year_old_date = new Date();

    //TODO get lastest (unique) TR for each project
    //test_result_query = ...

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

    non_milestone_query = Query.objectToSearchText(new SimpleQuery({
      key: "source_project__validation_state",
      operator: "=",
      type: "simple",
      value: "validated"
    }));
    // done with string queries directly because there is no way to do "key IN <list-of-values>" with Query
    // unless appending simple queries with AND by iterating on list but it's inefficient
    non_milestone_query += ' AND portal_type: ("' + portal_type_list.join('", "') + '")';
    non_milestone_query += ' AND simulation_state: ("' + valid_state_list.join('", "') + '")';

    return new RSVP.Queue()
      .push(function () {
        var promise_list = [],
          limit = [0, 100000],
          select_list = ['source_project', 'portal_type', 'stop_date', 'modification_date', 'simulation_state', 'creation_date'];
        // XXX: two separated queries because this query fails with not implemented error:
        // ( parent__validation_state = "validated" OR source_project__validation_state = "validated" )
        // TODO: do some research
        promise_list.push(gadget.jio_allDocs({
          query: Query.objectToSearchText(milestone_query),
          limit: limit,
          select_list: select_list,
          sort_on: [["modification_date", "descending"]]
        }));
        promise_list.push(gadget.jio_allDocs({
          query: non_milestone_query,
          limit: limit,
          select_list: select_list,
          sort_on: [["modification_date", "descending"]]
        }));
        promise_list.push(gadget.jio_allDocs({
          query: Query.objectToSearchText(project_query),
          limit: limit,
          select_list: ['title'],
          sort_on: [["modification_date", "descending"]]
        }));
        return RSVP.all(promise_list);
      })
      .push(function (result_list) {
        return [result_list[0].data.rows.concat(result_list[1].data.rows), result_list[2].data.rows];
      });
  }

  function renderProjectList(element_list, project_list) {
    var i, j,
      item,
      project_html,
      left_div_html,
      project_html_element_list,
      left_line_html,
      ul_list = document.getElementById("js-project-list");

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

    //XXX hardcoded for now (build a template?)
    element_list = ["Milestones", "Tasks", "Bugs", "Task Reports", "Test Results"];
    for (i = 0; i < project_list.length; i += 1) {
      project_html_element_list = createProjectHtmlElement(project_list[i].id, project_list[i].value.title);
      project_html = project_html_element_list[0];
      left_div_html = project_html_element_list[1];
      for (j = 0; j < element_list.length; j += 1) {
        //XXX hardcoded. This should come from the query
        item = {"status_color": "green",
                "total": 100,
                "outdated": 40,
                "title": element_list[j]};
        left_line_html = createProjectLineHtmlElement(item.title, item.total, item.outdated, item.status_color);
        left_div_html.appendChild(left_line_html);
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
      return this.changeState(options);
    })

    .onStateChange(function () {
      var gadget = this;
      return getProjectElementList(gadget)
        .push(function (element_list) {
          console.log("element_list:", element_list);
          renderProjectList(element_list[0], element_list[1]);
        });
    })

    .declareMethod('getContent', function () {
      return {};
    })

    .declareMethod('checkValidity', function () {
      return true;
    });

}(window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query));