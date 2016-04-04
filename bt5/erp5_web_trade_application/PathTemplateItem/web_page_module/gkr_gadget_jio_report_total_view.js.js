/*globals window, rJS, Handlebars*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, rJS, Handlebars) {
  "use strict";

  var gadget_klass = rJS(window),
    daily_source = gadget_klass.__template_element
                              .querySelector(".daily_report_template")
                              .innerHTML,
    daily_template = Handlebars.compile(daily_source),
    monthly_source = gadget_klass.__template_element
                              .querySelector(".monthly_report_template")
                              .innerHTML,
    monthly_template = Handlebars.compile(monthly_source),
    monthly_price_source = gadget_klass.__template_element
                              .querySelector(".monthly_report_price_template")
                              .innerHTML,
    monthly_price_template = Handlebars.compile(monthly_price_source);

  gadget_klass
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("translateHtml", "translateHtml")

    .declareMethod("render", function (options) {
      var gadget = this,
        report,
        key,
        all_factory = [],
        total_quantity,
        total_price,
        i,
        doc = options.doc,
        factory_list = Object.keys(doc.price_total),
        key_list = Object.keys(doc.price_total[factory_list[0]]);
      gadget.props.doc = doc;
      gadget.props.factory_list = factory_list;
      gadget.props.key_list = key_list;

      key = key_list[key_list.length - 1];
      for(i = 0; i < factory_list.length; i += 1) {
        all_factory.push({
          factory: factory_list[i],
          total_price: doc.price_total[factory_list[i]][key],
          total_quantity: doc.quantity_total[factory_list[i]][key]
        });
      }
      report = daily_template({
         Date: doc.date,
         all_factory: all_factory
         });
       return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.updateHeader({ title: options.doc.follow_up_title}),
            gadget.translateHtml(report)
          ]);
        })
        .push(function (result) {
          var tmp = gadget.props.element.querySelector(".report_container");
          tmp.innerHTML = result[1];
        });
    })
    .declareService(function () {
      var gadget = this,
        list_quantity = [],
        list_price = [],
        key_list = gadget.props.key_list,
        i,
        j,
        tmp,
        quantity_value = [],
        quantity,
        price_value = [],
        price,
        
        key,
        doc = gadget.props.doc,
        factory_list = gadget.props.factory_list,
        monthly_element = gadget.props.element.querySelector(".monthly_table"),
        monthly_element_price = gadget.props.element.querySelector(".monthly_table_price"),
        graph_element_price = gadget.props.element.querySelector(".graph-element-price"),
        graph_element = gadget.props.element.querySelector(".graph-element");
      
      
      for (i = 0; i < key_list.length; i += 1) {
        quantity = [];
        price = [];
        key = key_list[i];
        tmp =  doc.date.split("-")[0] + "/" + doc.date.split("-")[1] + "/" + key;
        for (j = 0; j < factory_list.length; j += 1) {
          quantity.push(doc.quantity_total[factory_list[j]][key]);
          price.push(doc.price_total[factory_list[j]][key]);
        }
        quantity_value.push({
          date:tmp,
          quantity: quantity
        });
        price_value.push({
          date:tmp,
          price:price
        });
       list_quantity.push([new Date(tmp)].concat(quantity));
       list_price.push([new Date(tmp)].concat(price));
      }
       var label = ['Sales Indicators'].concat(factory_list);
       var tmp1 =new Dygraph(graph_element_price,
         list_price,
        {
          legend: 'always',
          labels: label,
          fillGraph: true
        });
        monthly_element_price.innerHTML = monthly_price_template({
          all_factory: gadget.props.factory_list,
          price_value: price_value});
        

       var tmp2 =new Dygraph(graph_element,
         list_quantity,
        {
          legend: 'always',
          labels: label,
          fillGraph: true
        });
        monthly_element.innerHTML = monthly_template({
          all_factory: gadget.props.factory_list,
          quantity_value: quantity_value});
    return new RSVP.Queue()
          .push(function () {
            return RSVP.all([
              gadget.translateHtml(monthly_element_price.innerHTML),
              gadget.translateHtml(monthly_element.innerHTML)
              ]);
          })
          .push(function (all_innerHTML) {
            monthly_element_price.innerHTML = all_innerHTML[0];
            monthly_element.innerHTML = all_innerHTML[1];
          });
    })
    .declareService(function () {
       var gadget = this;
       return loopEventListener(
         gadget.props.element.querySelector(".top"),
         "submit",
         false,
         function (event) {
           var focus = document.activeElement,
             a = document.createElement("a"),
             id = focus.parentElement.querySelector("table").getAttribute("id");
            a.setAttribute("download", id + ".xls");
           ExcellentExport.excel(a, id, 'Sheet Name Here');
           a.click();
         }
        );
    });
        
   

}(window, rJS, Handlebars));