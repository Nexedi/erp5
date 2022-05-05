/*globals window, RSVP, rJS, Handlebars, jIO*/
/*jslint indent: 2, nomen: true, maxlen: 200*/
(function (window, RSVP, rJS, Handlebars, jIO) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    display_widget_table = Handlebars.compile(
      templater.getElementById("display-template").innerHTML
    );

  function clean(case_list, software_website, software_title, publisher_website, publisher_title) {
    var emptry_string = "",
      i,
      len,
      entry;
    if (! case_list) {
      return [];
    }
    for (i = 0, len = case_list.length; i < len; i += 1) {
      entry = case_list[i];
      if (entry.constructor !== Object) {
        continue;
      }
      if (entry.image === "N/A" || entry.image === "") {
        entry.image = 'gadget_erp5_eci_camera.png?format=png';
        entry.image_class = "custom-placeholder";
      }
      entry.software_website = software_website || emptry_string;
      entry.software = software_title || emptry_string;
      entry.publisher_website = publisher_website || emptry_string;
      entry.publisher = publisher_title  || emptry_string;
    }
    return case_list;
  }

  rJS(window)
    .declareAcquiredMethod('updateHeader', 'updateHeader')
    .declareAcquiredMethod('jio_get', 'jio_get')
    .declareAcquiredMethod('getUrlFor', 'getUrlFor')
    .declareMethod('render', function (options) {
      var gadget = this;
      return gadget.jio_get(options.jio_key)
        .push(function (solution) {

          // https://en.wikipedia.org/api/rest_v1/
          // only works in for english
          var wikipedia_api_url = 'https://en.wikipedia.org/api/rest_v1/page/summary/';

          if (solution.logo_url === "N/A" || solution.logo_url === "") {
            solution.logo_url = 'gadget_erp5_eci_camera.png?format=png';
          }
          solution.success_case_list = clean(
            solution.success_case_list,
            solution.website_url,
            solution.title,
            solution.publisher_website,
            solution.publisher
          );
          if (solution.wikipedia_url === undefined || solution.wikipedia_url === "N/A" || solution.wikipedia_url === "") {
            return solution;
          }
          return new RSVP.Queue()
           .push(function () {
            return jIO.util.ajax({
              type: "GET",
              headers: {"api-user-agent": "https://www.nexedi.com/contact"},
              url: wikipedia_api_url + solution.wikipedia_url.split("/").pop()
            });
           })
            .push(function (my_content) {
              var response = my_content.target.response || my_content.target.responseText;
              solution.wikipedia_description = JSON.parse(response).extract;
              return solution;
            }, function () {
              return solution;
            });
        })
        .push(function (solution) {
        gadget.element.querySelector(".display-widget").innerHTML = display_widget_table(solution);
        return RSVP.all([
          gadget.getUrlFor({command: "history_previous"}),
          solution.title
        ]);
      })
        .push(function (result_list) {
        return gadget.updateHeader({
          page_title: result_list[1],
          back_url: result_list[0]
        });
      });
    });
}(window, RSVP, rJS, Handlebars, jIO));

