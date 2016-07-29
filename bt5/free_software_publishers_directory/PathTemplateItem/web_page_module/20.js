/*global window, rJS, RSVP, Handlebars, URI, console, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3 */

(function (window, rJS, RSVP, Handlebars, URI) {
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
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        })

        .push(undefined, function (error) {
          console.log(error);
        });
    })
    
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this;

      return gadget.updateHeader({
        page_title: 'Free Software Publishers Directory'
      })
      .push(function () {
        return gadget.jio_allDocs({
          select_list: ['category_list'],
          query: 'portal_type:"software"'
        });
      })
      .push(function (software_objects) {
        var softwares = software_objects.data.rows,
          categories = softwares.map( (obj) => obj.value.category_list ) // get all categories
                                .reduce( (cur, prev) => cur.concat(prev) ), // flatten array of category arrays
          // remove duplicates (case sensitive!)
          unique_categories = Array.from(new Set(categories));
        
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
              sw.value.href = "#/" + sw.id + "?page=software&view=view";
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
        // reverse sort categories by number of softwares
        result.sort( (a, b) => b.softwares.length - a.softwares.length );
        
        var content = template(result);
        gadget.props.element.querySelector('.body').innerHTML = content;
      });
    });
}(window, rJS, RSVP, Handlebars, URI));
