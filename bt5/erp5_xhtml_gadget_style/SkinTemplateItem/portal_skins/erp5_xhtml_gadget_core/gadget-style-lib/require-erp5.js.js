// JavaScript file that is used to load ERP5's JavaScript depenencies
require.config({
  paths: {
    "erp5_form": "gadget-style-lib/erp5_form",
    route: "gadget-style-lib/route",
    url: "gadget-style-lib/url",
    jquery: "jquery/core/jquery",
    renderjs: "jquery/plugin/renderjs/renderjs",
    "jquery-ui": "jquery/ui/js/jquery-ui.min",
    "jquery.jqGrid.src": "jquery/plugin/jqgrid/jquery.jqGrid.src",
    "grid.locale-en": "jquery/plugin/jqgrid/i18n/grid.locale-en"
  },
  shim: {
    erp5: ["jquery"],
    erp5_xhtml_appearance: ["erp5"],
    erp5_knowledge_box: ["jquery", "jquery-ui"],
    route: ["jquery"],
    url: ["jquery"],
    "jquery-ui": ["jquery"],
    "jquery.jqGrid.src": ["jquery"],
    "grid.locale-en": ["jquery.jqGrid.src"]
  }
});

require(["erp5_xhtml_appearance", "erp5_knowledge_box", "erp5", "erp5_form", "erp5_ui",
         "renderjs", "jquery", "jquery-ui", "route", "url",
        "jquery.jqGrid.src", "grid.locale-en"],
        function(domReady) {
          RenderJs.init();
          RenderJs.bindReady(function (){
            $.url.onhashchange(function () {
              //console.log("go to route", $.url.getPath());
              RenderJs.RouteGadget.go($.url.getPath(),
                function () {
                  //console.log("bad route");
                  // All routes have been deleted by fail.
                  // So recreate the default routes using RouteGadget
                  RenderJs.RouteGadget.init();
                });
            });
          });
});
