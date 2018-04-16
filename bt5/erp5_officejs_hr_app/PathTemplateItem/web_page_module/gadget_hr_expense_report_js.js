/*globals window, rJS, Handlebars, RSVP*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, $) {
  "use strict";
  function zeroFill( number, width ){
    width -= number.toString().length;
    if ( width > 0 ){
      return new Array( width + (/\./.test( number ) ? 2 : 1) ).join( '0' ) + number;
    }
    return number + "";
  }

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                              .querySelector(".view-report-template")
                              .innerHTML,
    template = Handlebars.compile(source);

  gadget_klass
    .ready(function (g) {
      g.props = {};
      g.options = null;
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.deferred = RSVP.defer();
        });
    })

    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("get", "jio_get")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod('allDocs', 'jio_allDocs')

    .declareMethod("render", function (options) {
      var gadget = this,
         bar_data = [],
         currency_list = [],
         currency_dict = {};
      gadget.options = options;
      return gadget.translateHtml(template({}))
        .push(function (html) {
          gadget.props.element.innerHTML = html;
          return gadget.allDocs({
            query: 'portal_type: "Currency" AND validation_state: "validated"',
            select_list: ["title", "relative_url"],
            limit: [0, 1234567890]
          })
          .push(function(result){
            for (var i = 0; i < result.data.total_rows; i += 1) {
              currency_dict[result.data.rows[i].value.relative_url] = result.data.rows[i].value.title;
            }
            return gadget.allDocs({
            query: 'portal_type:("Expense Record")',
            select_list: ["date", "resource", "quantity"],
            limit: [0, 1234567890]
            });
          })
          .push(function(result){
            
            var currency_path, date, quantity;
            var temp_dict = {};
            for (var i=0; i<result.data.total_rows; i++) {
              currency_path = result.data.rows[i].value.resource;
              date = result.data.rows[i].value.date;
              quantity = parseFloat(result.data.rows[i].value.quantity);
              var re_result = date.match(/(\d*)\-(\d*)-(\d*)/);
              var year = parseInt(re_result[1], 10);
              var month = parseInt(re_result[2], 10);
              var year_month = zeroFill(year, 4) + zeroFill(month, 2);
              var currency = currency_dict[currency_path];
              var key = year_month;
              if (currency_list.indexOf(currency) == -1){
                currency_list.push(currency);
              }
              if (temp_dict[key]==undefined){
                temp_dict[key] = {};
              }
              if (temp_dict[key][currency]==undefined){
                temp_dict[key][currency] = quantity;
              }else{
                temp_dict[key][currency] += quantity;
              }
            }
            var label_list = [];
            for (var key in temp_dict) {
              label_list.push(key);
            }
            label_list.sort();
            for (var currency of currency_list){
              var value_list = [];
              for(var label of label_list){
                value_list.push(temp_dict[label][currency] || 0);
              }
              bar_data.push(value_list);
            }
            gadget.props.data = {
              labels: label_list,
              series: bar_data,
            };
            
            return gadget.updateHeader({
              title: "Report"
            });
          })
        })
        .push(function () {
          gadget.props.deferred.resolve();
        })
    })


    /////////////////////////////////////////
    // Export data as excel
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;
      new Chartist.Bar(gadget.props.element.querySelector('.ct-chart'),
                               gadget.props.data,
                               {seriesBarDistance: 10,
                                axisX: {offset: 60},
                               });
      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            gadget.props.element.querySelector('a[name=download_xls]'),
            'click',
            false,
            function (click_event){
              var currency_dict = {};
              return gadget.allDocs({
                query: 'portal_type: "Currency" AND validation_state: "validated"',
                select_list: ["title", "relative_url"],
                limit: [0, 1234567890]
              })
              .push(function(result){
                for (var i = 0; i < result.data.total_rows; i += 1) {
                  currency_dict[result.data.rows[i].value.relative_url] = result.data.rows[i].value.title;
                }
                return gadget.allDocs({
                query: 'portal_type:("Expense Record")',
                select_list: ["date", "resource", "quantity", "comment"],
                limit: [0, 1234567890]
                });
              })
              .push(function(result){
                var data_list = [];
                for (var i=0; i<result.data.total_rows; i++) {
                  var currency = currency_dict[result.data.rows[i].value.resource];
                  var date = result.data.rows[i].value.date;
                  var quantity = parseFloat(result.data.rows[i].value.quantity);
                  var comment = result.data.rows[i].value.comment;
                  data_list.push({currency:currency, date:date, quantity:quantity, comment:comment||""})
                }
                data_list.sort(function(a, b){if(a.date>b.date){return 1;}else if(a.date<b.date){return -1;}else{return 0;}})
                var table = $("<table><thead><tr><th>Date</th><th>Description</th><th>Currency</th><th>Total price</th></tr></thead><tbody></tbody></table>");
                for(var data of data_list){
                  table.find('tbody').append('<tr><td>'+data.date+'</td><td>'+data.comment+'</td><td>'+data.currency+'</td><td>'+data.quantity+'</td></tr>');
                }
                table.tableExport({bootstrap: false, formats: ["xlsx"], fileName:"travel_expense"});
                var obj = table.find('button.xlsx').data('fileblob');
                //xxxx .data may overwrite special character
                for (i = 1; i < obj.data.length; i += 1) {
                  obj.data[i][1] = data_list[i-1].comment; 
                }
                TableExport.prototype.export2file(obj.data, obj.mimeType, obj.fileName, obj.fileExtension);

                //ExcellentExport.excel(gadget.props.element.querySelector('a[name="hidden_download_xls"]'), table[0], 'Travel Expense');
                //gadget.props.element.querySelector('a[name="hidden_download_xls"]').click();
              })
            }
          );
        })
    })


}(window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, jQuery));
