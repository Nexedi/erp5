/*global window, rJS, RSVP, Handlebars, jIO, document */
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, rJS, RSVP, Handlebars, document) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // some varables
  /////////////////////////////////////////////////////////////////
  var VIEW = "?page=afs_software&view=view",

    gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    source = templater.getElementById("frontpage-template").innerHTML,
    template = Handlebars.compile(source);

  Handlebars.registerPartial(
    "list-partial",
    templater.getElementById("list-partial").innerHTML
  );

  gadget_klass

    /////////////////////////////////////////////////////////////////
    // acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this,
        grid = gadget.element.querySelector('.ui-masonry-container');

      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getDeclaredGadget("unsplash"),
            gadget.updateHeader({
              page_title: 'Free Software Publisher Directory'
            })
          ]);
        })
        .push(function (result_list) {
          return result_list[0].render();
        })
        .push(function (html_content) {
          var banner = document.createRange()
            .createContextualFragment(html_content || "");

          gadget.element.insertBefore(banner, grid);
          return gadget.jio_allDocs({
            select_list: ['category_list', 'title', 'publisher'],
            query: 'portal_type:"software"'
          });
        })
        .push(function (result_list) {
          var software_list = result_list.data.rows,
            global_category_list = [],
            config;

          // list of unique list of categories
          if (software_list.length > 0) {
            global_category_list = software_list.reduce(function (list, dict) {
              var software = dict.value;
              if (software.category_list.length > 0) {
                software.category_list.map(function (category) {
                  if (list.indexOf(category) === -1) {
                    list.push(category);
                  }
                });
              }
              return list;
            }, []);
          }

          // populate list with software
          config = global_category_list.reduce(function (result, category) {
            var category_entry = {"category": category, "software_list": []},
              len = software_list.length,
              match_list,
              software,
              i;

            for (i = 0; i < len; i += 1) {
              software = software_list[i].value;
              match_list = software.category_list;
              if (match_list && match_list.length > 0) {
                if (match_list.indexOf(category) > -1) {
                  category_entry.software_list.push({
                    "title": software.title,
                    "href": "#/" + software_list[i].id + VIEW
                  });
                }
              }
            }
            result.push(category_entry);
            return result;
          }, []);

          grid.innerHTML = template(config);
        });
    });
}(window, rJS, RSVP, Handlebars, document));
