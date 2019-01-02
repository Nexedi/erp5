/*globals window, RSVP, rJS, Handlebars, jIO*/
/*jslint indent: 2, nomen: true, maxlen: 100*/
(function (window, RSVP, rJS, Handlebars, jIO) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    display_widget_table = Handlebars.compile(
      templater.getElementById("display-template").innerHTML
    );

  function clean(case_list) {
    var i,
      len,
      entry;
    for (i = 0, len = case_list.length; i < len; i += 1) {
      entry = case_list[i];
      if (entry.image === "N/A" || entry.image === "") {
        entry.image = 'gadget_erp5_afs_camera.png?format=png';
        entry.image_class = "custom-placeholder";
      }
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
        .push(function (publisher) {
          // https://en.wikipedia.org/api/rest_v1/
          // only works in for english
          var wikipedia_api_url =
              'https://en.wikipedia.org/api/rest_v1/page/summary/',
            wiki_list = [];

          publisher.free_software_list.map(function (software) {
            if (software.commercial_support === "N/A") {
              delete software.commercial_support;
            }
            if (software.logo === "N/A" || software.logo === "") {
              software.logo = 'gadget_erp5_afs_camera.png?format=png';
            }
            if (software.success_case_list.length === 0 ||
                software.success_case_list === "N/A" ||
                software.success_case_list[0].title === "N/A" ||
                software.success_case_list[0].title === "") {
              delete software.success_case_list;
            } else {
              software.success_case_list = clean(software.success_case_list);
            }
            if (software.wikipedia_url === "N/A") {
              delete software.wikipedia_url;
            } else {
              wiki_list.push(
                new RSVP.Queue()
                  .push(function () {
                    return jIO.util.ajax({
                      type: "GET",
                      headers: {"api-user-agent": "https://www.nexedi.com/contact"},
                      url: wikipedia_api_url + software.wikipedia_url.split("/").pop()
                    });
                  })
                  .push(function (my_content) {
                    var response = my_content.target.response || my_content.target.responseText;
                    return JSON.parse(response).extract;
                  }, function () {
                    return undefined;
                  })
              );
            }
          });

          return new RSVP.Queue()
            .push(function () {
              return RSVP.all(wiki_list);
            })
            .push(function (my_wiki_list) {
              var i, len;
              if (my_wiki_list && my_wiki_list.length > 0) {
                for (i = 0, len = publisher.free_software_list.length; i < len; i += 1) {
                  if (publisher.free_software_list[i].wikipedia_url) {
                    publisher.free_software_list[i].wikipedia_description = my_wiki_list[i];
                  }
                }
              }
              return publisher;
            });
        })
        .push(function (my_publisher) {
          gadget.element.querySelector(".display-widget")
            .innerHTML = display_widget_table(my_publisher);

          return gadget.updateHeader({page_title: my_publisher.title});
        });
    });
}(window, RSVP, rJS, Handlebars, jIO));
