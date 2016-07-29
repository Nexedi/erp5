/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, Handlebars, jQuery, RSVP, loopEventListener */
(function (window, rJS, Handlebars, $, RSVP, loopEventListener) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // TEMPLATE API
  /////////////////////////////////////////////////////////////////
  
  // panel_category_list_header
  // {
  //  "close_i18n":       [SET],
  //  "i18n":             [title],
  //  "clear_i18n":       [SET],
  //  "update_i18n":      [SET]
  //  "tag_list":         [{
  //    "type_i18n":      [type of filter|create|...],
  //    "value_i18n":     [value to create or filter for, eg. region:foo]
  //  }]
  
  // panel_category_list_partial
  // {
  //    "i18n":           [category title],
  //    "tree":  [{
  //      "multiple":     [true to make checkbox],
  //      "search":       [search term, like "filter:region=France"],
  //      "i18n":"        [text to display]
  //    }]
  //  }]
  // } 

  /////////////////////////////////////////////////////////////////
  // some methods
  /////////////////////////////////////////////////////////////////

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    
    // pre-compile 
    panel_category_list_header = Handlebars.compile(
      templater.getElementById("panel-category-list-header").innerHTML
    )
    /*
    ,panel_category_list_partial = Handlebars.registerPartial(
      "category-taglist-partial",
      templater.getElementById("category-taglist-partial").innerHTML
    )*/;
  
  gadget_klass
    
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    .ready(function (my_gadget) {
      my_gadget.property_dict = {};
    })

    .ready(function (my_gadget) {
      return my_gadget.getElement()
        .push(function (my_element) {
          my_gadget.property_dict.element = my_element;
          my_gadget.property_dict.defer = new RSVP.defer();
          my_gadget.property_dict.panel_element =
            my_element.querySelector(".jqm-configuration-panel");
        });
    })

    /////////////////////////////////////////////////////////////////
    // acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("changeLanguage", "changeLanguage")
    .declareAcquiredMethod("getLanguageList", "getLanguageList")
    .declareAcquiredMethod(
      "whoWantToDisplayThisFrontPage",
      "whoWantToDisplayThisFrontPage"
    )

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('setPanelHeader', function (my_option_dict) {
      var gadget = this,
        panel_element = gadget.property_dict.panel_element;

      return new RSVP.Queue()
        .push(function () {
          return gadget.translateHtml(
            panel_category_list_header(my_option_dict)
          );
        })
        .push(function (my_panel_header) {
          panel_element.innerHTML = my_panel_header;
          $(panel_element).enhanceWithin();
          return gadget;
        })
        .push(function () {
          return gadget.property_dict.defer.resolve();
        });
    })
    .declareMethod('setPanelContent', function (my_option_dict) {
      /*
        so Romain requested to have a gadget depending on use case of this
        panel. In our case it should be  a domain tree and it should load a 
        certain amount  or type of domains/categories
        Alternatively we can load something else. Question is whether this
        should be a domain tree per ... app or if every domaintree can be 
        different depending on a parameter passed into intialization.
        
        Also, we must make clear that the content can be dumped to make space 
        for new content!
        
        Do this.
      */
    })

    .declareMethod('togglePanel', function () {
      var gadget = this;

      $(gadget.property_dict.panel_element).panel("toggle");
    })

    .declareMethod('render', function (my_option_dict) {
      var gadget = this,
        panel_element = gadget.property_dict.panel_element;

      return new RSVP.Queue()
        .push(function () {
          $(panel_element).panel({
            display: "overlay",
            position: "right",
            theme: "c"
          });
        });
    })

    /////////////////////////////////////////////////////////////////
    // declared services
    /////////////////////////////////////////////////////////////////
    .declareService(function () {
      var gadget = this,
        $panel_element = $(gadget.property_dict.panel_element);

      function formSubmit() {
        return gadget.togglePanel();
      }
    
      return new RSVP.Queue()
        .push(function () {
          return gadget.property_dict.defer.promise;
        })
        .push(function () {
          $panel_element.enhanceWithin();
          var form_list = gadget.property_dict.element.querySelectorAll('form'),
            event_list = [],
            i,
            len;

          for (i = 0, len = form_list.length; i < len; i += 1) {
            event_list[i] = loopEventListener(
              form_list[i],
              'submit',
              false,
              formSubmit
            );
          }
          return RSVP.all(event_list);
        })
      
    });

}(window, rJS, Handlebars, jQuery, RSVP, loopEventListener));



  /*
  
        .push(function (my_panel_category_list) {
          return gadget.factoryPanelCategoryList({
            "theme": "a",
            "position": "left",
            "animate_class": "overlay",
            "close_i18n": "gen.close",
            "i18n": "gen.categories",
            "clear_i18n": "gen.clear",
            "update_i18n": "gen.update",
            "tag_list": tag_list,
            "tree": my_panel_category_list
          });
        })
        .push(function (my_panel_content) {
          return gadget.translateHtml(my_panel_content);
        })
        .push(function (my_translated_panel_content) {
          return gadget.setPanel("panel_search", my_translated_panel_content);
        });
  
  */