/*
Copyright (c) 20xx-2006 Nexedi SARL and Contributors. All Rights Reserved.

This program is Free Software; you can redistribute it ahand/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.
cful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FgOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
*/
var y;

function draw(canvas) {
  y = 0;
  context = canvas.getContext('2d');
  //add logo
  context.drawImage($('#company_logo')[0], (canvas.width-330)/2, 0, 330, 75);
  addFeed(75);
  addFeed();
  addFeed();
  
  //add company information
  $("#company-info div").each(function(){
      addText(context, $(this).text());
  });
  addFeed();

  //add invoice information
  addText(context, $.trim($("#invoice_information_title").text()), {
    size: 36,
    line: 46
  });
  $("#invoice_information_detail div").each(function(){
    $(this).find("span").each(function(i){
      if(i==0){
        addText(context, $.trim($(this).text()), {bold: true, nobreak: true});
      }
      else {
        addText(context, $.trim($(this).text()), {x: 300});
      }
    });
  });
  addFeed(100);

  //add products line
  $("#invoice_line thead tr").each(function(j){
    var textPosition=0;
    $(this).find("th").each(function(i){
      addText(context, $.trim($(this).text()), {
        x: textPosition,
        bold: true,
        nobreak: true
      });
      switch(i)
      {
      case 0:
        textPosition+=285;
        break;
      case 1:
        textPosition+=100;        
        break;
      case 3:
        textPosition+=60;
        break;
      }
    });
  });
  addFeed();
  $("#invoice_line tbody tr").each(function(){
    var textPosition=0;
    $(this).find("td").each(function(i){
        switch(i)
        {
        case 0:
          var content=$.trim($(this).text());
          content_len=content.length;
          if(content_len>20)
            content=content.substr(0,12)+"..."+content.substr(content_len-4,5);
          addText(context, content, {x:textPosition, nobreak: true});
          textPosition+=330;
          break;
        case 1:
          var content=parseFloat($.trim($(this).text())).toFixed(1);
          var content_len=content.length;
          if(content_len>10)
            content=parseFloat(content).toExponential(2);
          else if(content_len>8&&content_len<11)
            content=parseInt(content);
          addText(context, content, {
            x:textPosition,
            nobreak: true,
            textalign: 'right'
          });
          textPosition+=140;
          break;
        case 2:
          priceControl(context, $.trim($(this).text()), {
            x:textPosition,
            textalign: 'right'
          });
          textPosition+=60;
          break;
        case 3:
          var content=$.trim($(this).text());
          var content_len=content.length;
          content=content.substr(0,5);
          addText(context, content, {x:textPosition, nobreak: true});
          break;
        case 4:
          priceControl(context, $.trim($(this).text()), {
            x:60,
            textalign: 'right'
          });
          break;
        }
    });
  });

  addText(context, "===========", {x:360});
  addText(context, $.trim($("#total_price tr th").text()), {
    bold: true,
    size: 28,
    line: 36,
    nobreak: true
  });
  priceControl(context, $.trim($("#total_price tr td").text()), {
    x:480,
    textalign: 'right',
    bold: true,
    size: 28,
    line: 36
  });
  addFeed();

  if ($("#total_discount").length > 0) {
    builder.addText(context, $.trim($("#total_discount tr th").text()), {x:130});
    priceControl(context, $.trim($("#total_discount tr td").text()), {x:385});
    addFeed();

    addText(context, "===========", x=360);
    addText(context, $.trim($("#total_price_with_discount tr th").text()), {x:130});
    priceControl(context, $.trim($("#total_price_with_discount tr td").text()), {x:385});
  }

  addFeed();
  // append date and time
  var now = new Date();
  addText(context, now.toDateString() + ' ' + now.toTimeString().slice(0, 8) + '\n');
  
  return canvas;
}

function addText(context, text, options) {
  if (!options) options = {};
  if (!options.x) options.x = 0;
  if (!options.bold) options.bold = false;
  if (!options.size) options.size = 24;
  if (!options.line) options.line = 30;
  if (!options.nobreak) options.nobreak = false;
  if (!options.font) options.font = 'Courier';
  if (!options.textalign) options.textalign = 'left';
  context.font =
      (options.bold ? 'bold ' : 'normal ') + options.size + 'px ' + options.font;
  context.textAlign = options.textalign;
  context.fillText(text, options.x, y);
  // line feed
  if (options.nobreak === false) {
    y = y + options.line;
  }
  console.log(options.line);
}

function addFeed(px) {
  if (!px) px = 30;
  y = y + px;
}

// if the price number length > 13 use the Scientific notation,
// if the length==11,12,13 , just need to remove the number after Decimal point
function priceControl(context, price, options){
  var content=parseFloat(price).toFixed(2);
  var content_len=content.length;
  if(content_len>13)
    content=parseFloat(content).toExponential(4);
  else if(content_len>10&&content_len<14)
    content=parseInt(content);
  addText(context, content, options);
}

monitoring_enabled = 0;

function enableEpsonMonitoring(printer_url){
  if (monitoring_enabled == 0) {
    monitoring_enabled = 1;
  } else { 
     return true;
  };
  var monitoting_epos = new epson.ePOSPrint(printer_url);
  monitoting_epos.interval = 5000;
  monitoting_epos.onpoweroff = function () {
    msg = "ERROR: Unable to connect to the printer at the URL (Unreachable or Power off): " + monitoting_epos.address
    $("#js_error_log").append("<div>" + msg + "</div>");
    console.log(msg);
  }

  monitoting_epos.onoffline = function () {
    msg = "ERROR: Printer seems offline check if you can access printer at the URL (Unreachable or Power off): " + monitoting_epos.address
    $("#js_error_log").append("<div>" + msg + "</div>");
    console.log(msg);
  }

  monitoting_epos.online = function () {
    msg = "INFO: Printer is online at" + monitoting_epos.address
    $("#js_error_log").append("<div>" + msg + "</div>");
    console.log(msg);
  }

  monitoting_epos.onpaperend = function () {
    msg = "WARNNING: Printer report that paper is finished!"
    $("#js_error_log").append("<div>" + msg + "</div>");
    console.log(msg);
  };

  monitoting_epos.onpapernearend = function () {
    msg = "WARNNING: Printer report that paper is near finished from finish!"
    $("#js_error_log").append("<div>" + msg + "</div>");
    console.log(msg);
  };

  monitoting_epos.onpaperok = function () {
    msg = "INFO: Printer report that paper is OK."
    $("#js_error_log").append("<div>" + msg + "</div>");
    console.log(msg);
  };

  monitoting_epos.ondrawerclosed = function () {
    msg = "INFO: Printer report that drawer is closed."
    $("#js_error_log").append("<div>" + msg + "</div>");
    console.log(msg);
  };

  monitoting_epos.ondraweropen = function () {
    msg = "INFO: Printer report that drawer is open."
    $("#js_error_log").append("<div>" + msg + "</div>");
    console.log(msg);
  };

  monitoting_epos.oncoveropen = function () {
    msg = "WARNNING: Printer report that cover is open! Please close it!"
    $("#js_error_log").append("<div>" + msg + "</div>");
    console.log(msg);
  };

  monitoting_epos.oncoverok = function () {
    msg = "INFO: Printer cover is closed."
    $("#js_error_log").append("<div>" + msg + "</div>");
    console.log(msg);
  };

  monitoting_epos.onstatuschange = function (status) {
    msg = "INFO: Printer changed status to :" + status;
    $("#js_error_log").append("<div>" + msg + "</div>");
    console.log(msg);
  };

  monitoting_epos.open();
}
  
function printInvoiceOnEpson(printer_url){
  enableEpsonMonitoring(printer_url);
  // create print object
  var epos = new epson.CanvasPrint(printer_url);
  // set paper cutting
  epos.cut = true;
  
  // register callback function
  epos.onreceive = function (res) {
    // Obtain the print result and error code
    var msg = 'Print' + (res.success ? 'Success' : 'Failure') + '\nCode:' + res.code;

    switch(res.code) {
      case "EPTR_AUTOMATICAL":
        msg += ' An automatically recoverable error occurred\n';
        break;
      case "EPTR_COVER_OPEN":
        msg += ' A cover open error occurred\n';
        break;
      case "EPTR_CUTTER":
        msg += ' An autocutter error occurred\n';
        break;
      case 'EPTR_MECHANICAL':
        msg += ' A mechanical error occurred\n';
        break;
      case 'EPTR_REC_EMPTY':
        msg += ' No paper in roll paper end sensor\n';
        break;
      case 'EPTR_UNRECOVERABLE':
        msg += ' An unrecoverable error occurred\n';
        break;
      case 'SchemaError':
        msg += ' The request document contains a syntax error\n';
        break;
      case 'DeviceNotFound':
        msg += ' The printer with the specified device ID does not exist\n';
        break;
      case 'PrintSystemError':
        msg += ' An error occurred on the printing system\n';
        break;
      case 'EX_BADPORT':
        msg += ' An error was detected on the communication port\n';
        break;
      case 'EX_TIMEOUT':
        msg += ' A print timeout occurred\n';
        break;
     }
    
    msg += '\nStatus:\n';
    // Obtain the printer status
    var asb = res.status;
    if (asb & epos.ASB_NO_RESPONSE) {
      msg += ' No printer response\n';
    }
    if (asb & epos.ASB_PRINT_SUCCESS) {
      msg += ' Print complete\n';
    }
    if (asb & epos.ASB_DRAWER_KICK) {
      msg += ' Status of the drawer kick number 3 connector pin = "H"\n';
    }
    if (asb & epos.ASB_OFF_LINE) {
      msg += ' Offline status\n';
    }
    if (asb & epos.ASB_COVER_OPEN) {
      msg += ' Cover is open\n';
    }
    if (asb & epos.ASB_PAPER_FEED) {
      msg += ' Paper feed switch is feeding paper\n';
    }
    if (asb & epos.ASB_WAIT_ON_LINE) {
      msg += ' Waiting for online recovery\n';
    }
    if (asb & epos.ASB_PANEL_SWITCH) {
      msg += ' Panel switch is ON\n';
    }
    if (asb & epos.ASB_MECHANICAL_ERR) {
      msg += ' Mechanical error generated\n';
    }
    if (asb & epos.ASB_AUTOCUTTER_ERR) {
      msg += ' Auto cutter error generated\n';
    }
    if (asb & epos.ASB_UNRECOVER_ERR) {
      msg += ' Unrecoverable error generated\n';
    }
    if (asb & epos.ASB_AUTORECOVER_ERR) {
      msg += ' Auto recovery error generated\n';
    }
    if (asb & epos.ASB_RECEIPT_NEAR_END) {
      msg += ' No paper in the roll paper near end detector\n';
    }
    if (asb & epos.ASB_RECEIPT_END) {
      msg += ' No paper in the roll paper end detector\n';
    }
    if (asb & epos.ASB_BUZZER) {
      msg += ' Sounding the buzzer (limited model)\n';
    }
    if (asb & epos.ASB_SPOOLER_IS_STOPPED) {
      msg += ' Stop the spooler\n';
    }
    // Display in the dialog box
    console.log(msg);
    $("#js_error_log").append("<div>" + msg + "</div>");
  }

  // register callback function
  epos.onerror = function (err) {
    $("#js_error_log").append("<div> Error Status: " + err.status + " Response: " + err.responseText + "</div>");
    if (err.status == 0) {
      $("#js_error_log").append("<div> Make sure you are able to access the printer at: " + epos.address + "</div>");
    };
    console.log("Error Status: " + err.status + "Response: " + err.responseText);
  }

  // send
  $("#js_error_log").append("<div> The print will start soon...</div>");
  
  // first draw on dummy canvas to get canvas height
  // needed because setting size clears canvas
  draw(document.createElement("canvas"));
  console.log(y);
  var canvas = document.createElement("canvas");
  canvas.width = 512;
  canvas.height = y;
  epos.print(draw(canvas));
}
