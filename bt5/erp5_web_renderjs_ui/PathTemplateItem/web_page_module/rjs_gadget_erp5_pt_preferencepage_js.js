/*global window, rJS */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // handle acquisition
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this;

      // XXX: Lot of DOM touches
      return gadget.updateHeader({
        page_title: 'Preference'
      })
        .push(function () {
          return gadget.getSetting('me');
        })
        .push(function (me) {
          if (me !== undefined) {
            return gadget.jio_allDocs({
              query: 'relative_url:"' + me + '"',
              select_list: ['title']
            })
              .push(function (result) {
                gadget.element.textContent = result.data.rows[0].value.title;
              });
          }
          // gadget.props.element.textContent = me;
        })
        .push(function () {
          return gadget.translateHtml(gadget.element.innerHTML);
        })
        .push(function (my_translated_html) {
          gadget.element.innerHTML = my_translated_html;
        });

    });
}(window, rJS));