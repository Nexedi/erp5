/**
 * NEXEDI
 */
(function($) {
  
   $.getJSON(
      'http://'+window.location.host+'/erp5/ERP5Site_getTileImageTransformMetadataList', 
       function(data){
            for (var i = 0; i < data["image_list"].length; i ++ ) {
                
		var aux1= "<li><a href=#image/";
		var aux2= "><i class=icon-star></i>";
		var aux3= "</a></li>";
                $('.nav-header').append(aux1+data["image_list"][i]["id"]+aux2+data["image_list"][i]["title"]+aux3)                        
        	    
            };
        });

  var routes = {
    "/image/:id" : "displayData",
    "image/:id" : "displayData",
  }

  var router = function(e, d){
    var $this = $(this);
    $.each(routes, function(pattern, callback){
      pattern = pattern.replace(/:\w+/g, '([^\/]+)');
      var regex = new RegExp('^' + pattern + '$');
      var result = regex.exec(d);
      if (result) {
        result.shift();
        methods[callback].apply($this, result);
      }
    });
  }

  var methods = {
    init: function() {
      // Initialize in this context
      var $this = $(this);
      // Bind to urlChange event
      return this.each(function(){
        $.subscribe("urlChange", function(e, d){
          router.call($this, e, d);
        });
      });
    },

    displayData: function(id){
      var zoomify_url, zoomify_width, zoomify_height = null;
      zoomify_url = "http://"+window.location.host+"/erp5/image_module/" + id + "/";
      //XXX look at the xml definition inside image folder
      var zoomify_data = $.getJSON(
				"http://"+window.location.host+"/erp5/image_module/" + id + "/TileImage_getMetadataAsJSON",
				function(data){
					width=data["sizes"][0]["width"];
					height=data["sizes"][0]["height"];
				  transforms(width,height);							
   				 }

			);
   
	$(this).form('render', 'image', {'image_id': id});


  var transforms = function(width,height){
                     $.getJSON(
                        'http://'+window.location.host+'/erp5/image_module/'+id+'/TileImageTransformed_getTransform',
                           function(data){
                              pass(width,height,data);
                            }
                        );
    }

	var pass = function(zoomify_width,zoomify_height,data){
			
				$(function() {
         			 SafeImage.loadOpenLayerZoomedImage(zoomify_width,zoomify_height, zoomify_url,data);
               if (document.location.search != ""){
                 SafeImage.map.zoomTo(Number(document.location.search.split("")[6]));
                } 
     				 });
	};

    },

    render: function(template, data){
   	 $(this).html(ich[template](data, true));
     }

       };

  $.fn.form = function(method){
    if ( methods[method] ) {
      return methods[method].apply( this, Array.prototype.slice.call( arguments, 1 ));
    } else if ( typeof method === 'object' || ! method ) {
      return methods.init.apply( this, arguments );
    } else {
      $.error( 'Method ' +  method + ' does not exist on jQuery.form' );
    }
  };
})(jQuery);

$("#main").form();
