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

function printInvoiceOnEpson(){
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
        textPosition+=100;
        break;
      case 1:
        textPosition+=100;        
        break;
      case 2:
        textPosition+=125;       
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
          if(content_len>8)
            content=content.substr(0,2)+"..."+content.substr(content_len-4,3)
          builder.addText(content);
          textPosition+=100;
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
          textPosition+=125;
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
  builder.addFeedLine(4);

  // append date and time
  builder.addTextSize(1, 1);
  builder.addTextAlign(builder.ALIGN_LEFT);
  var now = new Date();
  builder.addText(now.toDateString() + ' ' + now.toTimeString().slice(0, 8) + '\n');

  // append paper cutting
  builder.addCut(); 

  // create print object
  var url = 'http://' + '192.168.192.168' + '/cgi-bin/epos/service.cgi?devid=' + 'local_printer' + '&timeout=' + '10000';
  var epos = new epson.ePOSPrint(url);

  // register callback function
  epos.onreceive = function (res) {
    // print failure
    if (!res.success) {
      console.log("no response")
    }
  }

  // register callback function
  epos.onerror = function (err) {
    console.log("error")
  }

  // send
  epos.send(builder.toString());
}