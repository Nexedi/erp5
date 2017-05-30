/*global window, rJS, RSVP, Handlebars, URI, console, jIO, document */
/*jslint nomen: true, indent: 2, maxerr: 3 */

(function (window, rJS, RSVP, Handlebars, URI, document) {
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
            gadget.getDeclaredGadget("unsplash"),
            gadget.updateHeader({
              page_title: 'Free Software Publisher Directory'
            })
          ]);
        })
        .push(function (my_response_list) {
          return RSVP.all([
            gadget.jio_allDocs({
              select_list: ['category_list'],
              query: 'portal_type:"software"'
            }),
            my_response_list[0].render()
          ]);
        })
        .push(function (my_response_list) {
          var softwares = my_response_list[0].data.rows,
            obj,

            // get categories and flatten array of category arrays
            categories = softwares
              .map((obj) => obj.value.category_list)
              .reduce((cur, prev) => cur.concat(prev)),

            // remove duplicates (case sensitive!)
            unique_categories = Array.from(new Set(categories)),

            // kudos: https://davidwalsh.name/convert-html-stings-dom-nodes
            banner = document.createRange()
              .createContextualFragment(my_response_list[1] || "");

          gadget.element.insertBefore(banner, masonry_container);

          return RSVP.all(unique_categories);
        })
        .push(function (categories) {
          var softwares_by_category = categories.map(function (category) {
            return gadget.jio_allDocs({
              select_list: [
                'title',
                'publisher',
                'logo'
              ],
              query: 'category_list:"%' + category + '%" AND portal_type:"software"'
            })
            .push(function (softwares) {
              softwares.data.rows.map(function (sw) {
                // XXX hardcoded page and view
                sw.value.href = "#/" + sw.id + "?page=afs_software&view=view";
              });
              return {
                category: category,
                softwares: softwares.data.rows
              };
            });
          });
        
          return RSVP.all(softwares_by_category);
        })
        .push(function (result) {
          var content;

          // reverse sort categories by number of softwares
          result.sort( (a, b) => b.softwares.length - a.softwares.length );

          content = template(result);
          masonry_container.innerHTML = content;
        });
    });
}(window, rJS, RSVP, Handlebars, URI, document));
