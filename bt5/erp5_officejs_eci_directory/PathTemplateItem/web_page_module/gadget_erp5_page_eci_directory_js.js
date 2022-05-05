/*global window, rJS, RSVP, Handlebars, URI, console, jIO, document, Boolean */
/*jslint nomen: true, indent: 2, maxerr: 3 */

(function (window, rJS, RSVP, Handlebars, URI, document, Boolean) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    source = templater.getElementById("frontpage-template")
                      .innerHTML,
    template = Handlebars.compile(source);
  Handlebars.registerPartial(
    "list-partial",
    templater.getElementById("list-partial").innerHTML
  );

  gadget_klass
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this,
        masonry_container = gadget.element.querySelector(
          '.ui-masonry-container'
        );

      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.updateHeader({
              page_title: 'European Cloud Technology Directory'
            })
          ]);
        })
        .push(function (my_response_list) {
          return RSVP.all([
            gadget.jio_allDocs({
              select_list: ['category_list'],
              query: 'portal_type:"solution"'
            })
          ]);
        })
        .push(function (my_response_list) {
          var softwares = my_response_list[0].data.rows,
            obj,
            categories = softwares
              .map((obj) => obj.value.category_list)
              .reduce((cur, prev) => cur.concat(prev))
              .filter(Boolean),

            unique_categories = Array.from(new Set(categories));
          var solution_by_category = unique_categories.map(function (category) {
            return gadget.jio_allDocs({
              select_list: [
                'title',
                'publisher',
                'logo',
                'uid'
              ],
              query: 'category_list:"%' + category + '%" AND portal_type:"solution"'
            })
            .push(function (solutions) {
              return new RSVP.Queue()
                .push(function () {
                  return RSVP.all(solutions.data.rows.map(function (sw) {
                    return gadget.getUrlFor({command: "display", options: {
                        jio_key: sw.value.uid,
                        page: "eci_solution",
                        view: "view"
                      }
                    })
                      .push(function (href) {
                        sw.value.href = href;
                      });
                  }));
                })
                .push(function () {
                  return {
                    category: category,
                    solutions: solutions.data.rows
                  };
                });
            });
          });

          return RSVP.all(solution_by_category);
        })
        .push(function (result) {
          result.sort( (a, b) => b.solutions.length - a.solutions.length );
          masonry_container.innerHTML = template(result);
        });
    });
}(window, rJS, RSVP, Handlebars, URI, document, Boolean));
