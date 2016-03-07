//
//
(function($) {
  var setDate = function(dateText, inst) {
      var date = $.datepicker.parseDate($(this).datepicker('option', 'dateFormat'), dateText);
      var date_map = {
        year: date.getFullYear(),
        month: date.getMonth() + 1,
        day: date.getDate()
      };
      $('input', this.parentNode).each(function() {
        var name = jQuery(this).attr('name');
        if (name !== undefined) {
          var word_list = name.split('_');
          var last_word = word_list[word_list.length - 1];
          var value = date_map[last_word];
          if (value == null) {
            value = '';
          }
          this.value = value.toString();
        }
      });
  };

  $.fn.erp5DatePicker = function() {
    this.each(function() {
      var input = $('input', this);
      var size = input.size();
      input.each(function(index) {
          $(this).datepicker({
            onSelect: setDate
          });
         });
      });
    };
  })(jQuery);
$(document).ready(function(){
  $('div.date_field div.input').erp5DatePicker();
});
