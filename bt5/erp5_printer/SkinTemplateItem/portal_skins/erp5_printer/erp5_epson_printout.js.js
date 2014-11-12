/*
Copyright (c) 20xx-2006 Nexedi SARL and Contributors. All Rights Reserved.

This program is Free Software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
*/
//if the price number length > 13 use the Scientific notation,
//if the length==11,12,13 , just need to remove the number after Decimal point
function priceControl(price,builder){
  var content=parseFloat(price).toFixed(2);
  var content_len=content.length;
  if(content_len>13)
    content=parseFloat(content).toExponential(4);
  else if(content_len>10&&content_len<14)
    content=parseInt(content);
  builder.addText(content);
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
  enableEpsonMonitoring(printer_url)
  var url = printer_url;

  // create print data builder object
  var builder = new epson.ePOSBuilder();

  // initialize (ank mode, smoothing)
  builder.addTextLang('en').addTextSmooth(true);

  //add logo
  builder.addTextAlign(builder.ALIGN_CENTER);
  var canvas = $('#canvas')[0];
  var context = canvas.getContext('2d');
  context.drawImage($('#company_logo')[0], 0, 0, 330, 75);
  builder.addImage(context, 0, 0, 330, 75);
  builder.addFeed();

  //add company information
  builder.addTextAlign(builder.ALIGN_LEFT);
  builder.addTextSize(1, 1);
  $("#company-info div").each(function(){
      builder.addText($(this).text());
      builder.addFeed();
  });

  //add products information
  builder.addTextSize(2, 1);
  builder.addTextStyle(false, false, true);
  builder.addTextAlign(builder.ALIGN_LEFT);
  builder.addText($.trim($("#invoice_information_title").text()));
  builder.addTextSize(1, 1);
  builder.addFeedLine(2);
  $("#invoice_information_detail div").each(function(){
    $(this).find("span").each(function(i){
      if(i==0){
        builder.addTextStyle(false, false, true);
        builder.addTextAlign(builder.ALIGN_LEFT);
        builder.addText($.trim($(this).text()));
      }
      else{
        builder.addTextStyle(false, false, false);
        builder.addTextPosition(350);
        builder.addText($.trim($(this).text()));
      }   
    });
    builder.addFeed();
  });
  builder.addFeed();

  //add products line
  builder.addTextAlign(builder.ALIGN_LEFT);
  builder.addTextSize(1, 1);
  builder.addTextFont(builder.FONT_C);
  builder.addTextStyle(false, false, true);
  $("#invoice_line thead tr").each(function(j){
    var textPosition=0;
    $(this).find("th").each(function(i){
      builder.addTextPosition(textPosition);
      builder.addText($.trim($(this).text()));
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
  builder.addFeed();
  builder.addTextStyle(false, false, false);
  $("#invoice_line tbody tr").each(function(){
    var textPosition=0;
    $(this).find("td").each(function(i){
        builder.addTextPosition(textPosition);
        switch(i)
        {
        case 0:
          var content=$.trim($(this).text());
          content_len=content.length;
          if(content_len>20)
            content=content.substr(0,12)+"..."+content.substr(content_len-4,5)
          builder.addText(content);
          textPosition+=285;
          break;
        case 1:
          var content=parseFloat($.trim($(this).text())).toFixed(1);
          var content_len=content.length;
          if(content_len>10)
            content=parseFloat(content).toExponential(2);
          else if(content_len>8&&content_len<11)
            content=parseInt(content);
          builder.addText(content);
          textPosition+=100;
          break;
        case 2:
          priceControl($.trim($(this).text()),builder)
          textPosition+=60;
          break;
        case 3:
          var content=$.trim($(this).text());
          var content_len=content.length;
          content=content.substr(0,5);
          builder.addText(content);
          textPosition+=60;
          break;
        case 4:
          priceControl($.trim($(this).text()),builder)
          break;
        }
    });
    builder.addFeed();
  });

  //add total excluding tax price
  /* DON'T Include Tax Information.
  builder.addTextPosition(360);
  builder.addText("===========");
  builder.addFeed();
  builder.addTextSize(1, 2);
  builder.addTextStyle(false, false, true);
  builder.addTextAlign(builder.ALIGN_LEFT);
  builder.addTextPosition(130);
  builder.addText($.trim($("#total_without_tax tr th").text()));
  builder.addTextPosition(385);
  priceControl($.trim($("#total_without_tax tr td").text()),builder)
  builder.addFeedLine(4);
  
  //add the tax line
  builder.addTextAlign(builder.ALIGN_LEFT);
  builder.addTextSize(1, 1);
  builder.addTextFont(builder.FONT_C);
  builder.addTextStyle(false, false, true);
  $("#tax thead tr").each(function(j){
    var textPosition=100;
    $(this).find("th").each(function(i){
      builder.addTextPosition(textPosition);
      builder.addText($.trim($(this).text()));
      switch(i)
      {
      case 0:
        textPosition+=60;
        break;
      case 1:
        textPosition+=125;
        break;
      case 2:
        textPosition+=100;
        break;
      }
    });
  });
  builder.addFeed();
  builder.addTextStyle(false, false, false);
  $("#tax tbody tr").each(function(){
    var textPosition=100;
    $(this).find("td").each(function(i){
        builder.addTextPosition(textPosition);
        switch(i)
        {
        case 0:
          builder.addText($.trim($(this).text()));
          textPosition+=60;
          break;
        case 1:
          priceControl($.trim($(this).text()),builder);
          textPosition+=125;
          break;
        case 2:
          builder.addText($.trim($(this).text()));
          textPosition+=100;
          break;
        case 3:
          priceControl($.trim($(this).text()),builder);
          break;
        }
    });
    builder.addFeed();
  });
  builder.addFeed();
  */
  //add total excluding tax price
  builder.addTextPosition(360);
  builder.addText("===========");
  builder.addFeed();
  builder.addTextSize(1, 2);
  builder.addTextStyle(false, false, true);
  builder.addTextAlign(builder.ALIGN_LEFT);
  builder.addTextPosition(130);
  builder.addText($.trim($("#total_price tr th").text()));
  builder.addTextPosition(385);
  priceControl($.trim($("#total_price tr td").text()),builder)
  builder.addFeedLine(2);

  if ($("#total_discount").length > 0) {
    builder.addTextSize(1, 2);
    builder.addTextStyle(false, false, true);
    builder.addTextAlign(builder.ALIGN_LEFT);
    builder.addTextPosition(130);
    builder.addText($.trim($("#total_discount tr th").text()));
    builder.addTextPosition(385);
    priceControl($.trim($("#total_discount tr td").text()),builder)
    builder.addFeed();

    builder.addTextPosition(360);
    builder.addText("===========");
    builder.addFeed();
    builder.addTextSize(1, 2);
    builder.addTextStyle(false, false, true);
    builder.addTextAlign(builder.ALIGN_LEFT);
    builder.addTextPosition(130);
    builder.addText($.trim($("#total_price_with_discount tr th").text()));
    builder.addTextPosition(385);
    priceControl($.trim($("#total_price_with_discount tr td").text()),builder)
  }

  builder.addFeedLine(4)
  // Loyalty information
  builder.addTextSize(1, 1);
  builder.addTextStyle(false, false, false);
  builder.addTextAlign(builder.ALIGN_CENTER);
  $("#loyalty_information_header span").each(function(){
      builder.addText($.trim($(this).text()));
      builder.addFeed();
   });

  builder.addTextAlign(builder.ALIGN_CENTER);
  var canvas = $('#ordernumbercanvas')[0];
  var context = canvas.getContext('2d');
  context.drawImage($('#order_barcode')[0], 0, 0, 330, 75);
  builder.addImage(context, 0, 0, 330, 75);
  builder.addFeed();

  builder.addTextSize(1, 1);
  builder.addTextStyle(false, false, false);
  builder.addTextAlign(builder.ALIGN_CENTER);
  builder.addText($.trim($("#order_number").text()));
  builder.addFeed()

  $("#loyalty_information_bottom span").each(function(){
      builder.addText($.trim($(this).text()));
      builder.addFeed();
   });

  builder.addFeedLine(2);
  // append date and time
  builder.addTextSize(1, 1);
  builder.addTextAlign(builder.ALIGN_LEFT);
  var now = new Date();
  builder.addText(now.toDateString() + ' ' + now.toTimeString().slice(0, 8) + '\n');

  // append paper cutting
  builder.addCut(); 

  // create print object
  var epos = new epson.ePOSPrint(url);

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
    self.console(msg);
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
  console.log(builder.toString());
  epos.send(builder.toString());
}
