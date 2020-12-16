loadJQZoom = function(){
  $('.jqzoom').jqzoom({title:false, zoomHeight: 420, zoomWidth: 400,});
}

loadLightBox = function(){
  $('.jqzoom').lightBox({imageLoading: 'advanced_ecommerce_image/lightbox-ico-loading.gif',
                         imageBtnClose: 'advanced_ecommerce_image/lightbox-btn-close.gif', 
                         imageBlank:  'advanced_ecommerce_image/lightbox-blank.gif'});
}

$(document).ready(function(){
  var img = $('img.resource_image');
  var parent = img.closest('div');
  if (img.attr('src') != null) {
    href = img.attr('src').replace('display=small', 'display=large');
    $(parent).html('<a class=jqzoom href="' + href + '">' + $(parent).html() + '</a>');
    loadJQZoom();
    loadLightBox();
  };

  $(".image_selection a").click(function() {
    var img = $("img", this)[0];
    var resource_image = $('img.resource_image')[0];
    var parent = $('.jqzoom').closest("div.input")
    resource_image.src = img.src.replace('display=micro', 'display=small')
    $(parent).html($(resource_image))

    href = $(resource_image).attr('src').replace('display=small', 'display=large');
    $(parent).html('<a class=jqzoom href="' + href + '">' + $(parent).html() + '</a>');
    loadJQZoom();
    loadLightBox();

    return false; /* Disable reload page when click on link */
  });

  $(".shipping_cart_quantity select").change(function() {
    button = $("input.shopping_cart_renderer_update_submit")[0];
    button.name = "WebSection_editShoppingCart:method";
    button.click();
  });

  $(".shopping_cart_renderer_shipping select").change(function() {
    button = $("input.shopping_cart_renderer_update_submit")[0];
    button.name = "WebSection_editShoppingCart:method";
    button.click();
  });

  $(".shopping_cart_renderer_shipping input").change(function() {
    button = $("input.shopping_cart_renderer_update_submit")[0];
    button.name = "WebSection_editShoppingCart:method";
    button.click();
  });

  $(window).bind('load', function(){
    fixImageHeight();
  });

});

function hidePaymentButton(){
  $('.shopping_cart_renderer_submit').remove()
}

function fixImageHeight() {
  var num_elt = 4,
    elt_list = $(".new_article .product_view .product_image"),
    i,
    tmp,
    max_height = 0,
    height_list = [],
    line_height = [];
  console.log(elt_list);
  for (i=0; i <= elt_list.length; i += 1 ) {
    if (i == 0 || i%num_elt == 0 || i == elt_list.length) {
      // recomputer height
      if (line_height.length > 0) {
        for (tmp = 0; tmp < line_height.length; tmp += 1) {
          height_list.push(max_height - line_height[tmp]);
        }
      }
      // new line started
      max_height = $(elt_list[i]).height();
      line_height = [max_height];
      continue;
    } else {
      tmp = $(elt_list[i]).height();
      line_height.push(tmp);
      if (tmp > max_height) {
        max_height = tmp;
      }
    }
  }
  $(".new_article .product_view p.article_descp").each(function(index) {
    $(this).css('margin-top', height_list[index] + 'px');
    console.log(height_list[index] + 'px');
  });
}
