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
        production_packing_list,
        purchase_packing_list_of_product,
        purchase_packing_list_of_raw_material,
        sale_packing_list,
        key,
        compare_key,
        doc = options.doc,
        key_list = Object.keys(doc.production_packing_list);
      gadget.props.doc = doc;
      gadget.props.key_list = key_list;
      key = key_list[key_list.length - 1];
      if (key_list.length > 2) {
        compare_key = key_list[key_list.length -2];
      } else {
        compare_key = key;
      }
      production_packing_list = doc.production_packing_list[key];
      purchase_packing_list_of_product = doc.purchase_packing_list_of_product[key];
      purchase_packing_list_of_raw_material = doc.purchase_packing_list_of_raw_material[key];
      sale_packing_list = doc.sale_packing_list[key];
      report = daily_template({
         Date: doc.date,
         production_latex_total_quantity: production_packing_list.latex.total_quantity,
         production_rubber_total_quantity: production_packing_list.rubber.total_quantity,
         purchase_product_latex_total_price: purchase_packing_list_of_product.latex.total_price,
         purchase_product_latex_total_quantity: purchase_packing_list_of_product.latex.total_quantity,
         purchase_product_rubber_total_price: purchase_packing_list_of_product.rubber.total_price,
         purchase_product_rubber_total_quantity: purchase_packing_list_of_product.rubber.total_quantity,
         purchase_material_total_price: purchase_packing_list_of_raw_material.material.total_price,
         purchase_material_total_quantity:  purchase_packing_list_of_raw_material.material.total_quantity,
         sale_latex_total_price: sale_packing_list.latex.total_price * -1,
         sale_latex_total_quantity: sale_packing_list.latex.total_quantity * -1,
         sale_rubber_total_price: sale_packing_list.rubber.total_price * -1, 
         sale_rubber_total_quantity: sale_packing_list.rubber.total_quantity * -1,
         sale_material_total_price: sale_packing_list.material.total_price * -1,
         sale_material_total_quantity: sale_packing_list.material.total_quantity * -1
         /*
         production_latex_total_quantity_check: production_packing_list.latex.total_quantity - doc.production_packing_list[compare_key].latex.total_quantity,
         production_rubber_total_quantity_check: production_packing_list.rubber.total_quantity - doc.production_packing_list[compare_key].rubber.total_quantity,
         purchase_product_rubber_total_quantity_check: purchase_packing_list_of_product.rubber.total_quantity - doc.purchase_packing_list_of_product[compare_key].rubber.total_quantity,
         purchase_material_total_quantity_check:purchase_packing_list_of_raw_material.material.total_quantity - doc.purchase_packing_list_of_raw_material[compare_key].material.total_quantity,
         sale_latex_total_quantity_check: (sale_packing_list.latex.total_quantity - doc.sale_packing_list[compare_key].latex.total_quantity) * -1,
         sale_rubber_total_quantity_check: (sale_packing_list.rubber.total_quantity - doc.sale_packing_list[compare_key].rubber.total_quantity) * -1,
         sale_material_total_quantity_check:  (sale_packing_list.material.total_quantity - doc.sale_packing_list[compare_key].material.total_quantity) * -1
         */
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
        list = [],
        list_price = [],
        key_list = gadget.props.key_list,
        i,
        monthly_value = [],
        monthly_value_price = [],
        
        key,
        tmp,
        doc = gadget.props.doc,
        monthly_element = gadget.props.element.querySelector(".monthly_table"),
        monthly_element_price = gadget.props.element.querySelector(".monthly_table_price"),
        graph_element_price = gadget.props.element.querySelector(".graph-element-price"),
        graph_element = gadget.props.element.querySelector(".graph-element");
      
      for (i = 0; i < key_list.length; i += 1) {
        key = key_list[i];
        tmp = doc.date.split("-")[0] + "/" + doc.date.split("-")[1] + "/" +  key,
        monthly_value.push({
          date: tmp,
          production_of_latex: doc.production_packing_list[key].latex.total_quantity, 
          production_of_rubber: doc.production_packing_list[key].rubber.total_quantity,
          purchase_of_latex:doc.purchase_packing_list_of_product[key].latex.total_quantity,
          purchase_of_rubber: doc.purchase_packing_list_of_product[key].rubber.total_quantity,
          purchase_of_raw_material: doc.purchase_packing_list_of_raw_material[key].material.total_quantity,
          sale_of_latex: doc.sale_packing_list[key].latex.total_quantity * -1,
          sale_of_rubber:  doc.sale_packing_list[key].rubber.total_quantity * -1,
          sale_of_material: doc.sale_packing_list[key].material.total_quantity * -1
         });

        monthly_value_price.push({
          date: tmp,
          purchase_of_latex:doc.purchase_packing_list_of_product[key].latex.total_price,
          purchase_of_rubber: doc.purchase_packing_list_of_product[key].rubber.total_price,
          purchase_of_raw_material: doc.purchase_packing_list_of_raw_material[key].material.total_price,
          sale_of_latex: doc.sale_packing_list[key].latex.total_price * -1,
          sale_of_rubber:  doc.sale_packing_list[key].rubber.total_price * -1,
          sale_of_material: doc.sale_packing_list[key].material.total_price * -1
         });

         list_price.push([new Date(tmp),
          doc.purchase_packing_list_of_product[key].latex.total_price,
          doc.purchase_packing_list_of_product[key].rubber.total_price,
          doc.purchase_packing_list_of_raw_material[key].material.total_price,
          doc.sale_packing_list[key].latex.total_price * -1,
          doc.sale_packing_list[key].rubber.total_price * -1,
          doc.sale_packing_list[key].material.total_price * -1
        ]);

        list.push([new Date(tmp),
          doc.production_packing_list[key].latex.total_quantity, 
          doc.production_packing_list[key].rubber.total_quantity,
          doc.purchase_packing_list_of_product[key].latex.total_quantity,
          doc.purchase_packing_list_of_product[key].rubber.total_quantity,
          doc.purchase_packing_list_of_raw_material[key].material.total_quantity,
          doc.sale_packing_list[key].latex.total_quantity * -1,
          doc.sale_packing_list[key].rubber.total_quantity * -1,
          doc.sale_packing_list[key].material.total_quantity * -1
        ]);
      }
         var tmp1 =new Dygraph(graph_element_price,
         list_price,
        {
          legend: 'always',
          labels: [ 'Sales Indicators',  'purchase of latex', 'purchase of rubber', 'purchase of raw material', 'sale of latex', 'sale of rubber', 'sale of material'],
          fillGraph: true
        });
        monthly_element_price.innerHTML = monthly_price_template({value: monthly_value_price});
        

       var tmp =new Dygraph(graph_element,
         list,
        {
          legend: 'always',
          labels: [ 'Sales Indicators', 'production of latex', 'production of rubber', 'purchase of latex', 'purchase of rubber', 'purchase of raw material', 'sale of latex', 'sale of rubber', 'sale of material'],
          fillGraph: true
        });
        monthly_element.innerHTML = monthly_template({value: monthly_value});
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