/*globals window, RSVP, rJS, Handlebars, jIO*/
/*jslint indent: 2, nomen: true, maxlen: 100*/
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
    for (i = 0, len = case_list.length; i < len; i += 1) {
      entry = case_list[i];
      if (entry.image === "N/A" || entry.image === "") {
        entry.image = 'gadget_erp5_afs_camera.png?format=png';
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

    .declareMethod('render', function (options) {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.jio_get(options.jio_key);
        })
        .push(function (software) {

          // https://en.wikipedia.org/api/rest_v1/
          // only works in for english
          var wikipedia_api_url = 'https://en.wikipedia.org/api/rest_v1/page/summary/';

          if (software.logo === "N/A" || software.logo === "") {
            software.logo = 'gadget_erp5_afs_camera.png?format=png';
          }
          if (software.commercial_support === "N/A") {
            delete software.commercial_support;
          }
          if (software.success_case_list.length === 0 ||
              software.success_case_list === "N/A" ||
              software.success_case_list[0].title === "N/A" ||
              software.success_case_list[0].title === "") {
            delete software.success_case_list;
          } else {
            software.success_case_list = clean(
              software.success_case_list,
              software.website,
              software.title,
              software.publisher_website,
              software.publisher
            );
          }
          if (software.wikipedia_url === "N/A") {
            delete software.wikipedia_url;
            return software;
          }

          return new RSVP.Queue()
            .push(function () {
              return jIO.util.ajax({
                type: "GET",
                headers: {"api-user-agent": "https://www.nexedi.com/contact"},
                url: wikipedia_api_url + software.wikipedia_url.split("/").pop()
              });
            })
            .push(function (my_content) {
              var response = my_content.target.response || my_content.target.responseText;
              software.wikipedia_description = JSON.parse(response).extract;
              return software;
            }, function () {
              // console.log(my_error)
              // 404 or not allowed, swallow
              return software;
            });

        })
        .push(function (my_software) {
          gadget.element.querySelector(".display-widget")
            .innerHTML = display_widget_table(my_software);

          return gadget.updateHeader({page_title: my_software.title});
        });
    });
}(window, RSVP, rJS, Handlebars, jIO));

