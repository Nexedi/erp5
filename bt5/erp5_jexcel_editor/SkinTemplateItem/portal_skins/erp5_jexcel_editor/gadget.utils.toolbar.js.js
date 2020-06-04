/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, jexcel*/
(function (window, rJS, jexcel) {
  "use strict";

  var font_style = {
    type: 'select',
    k: 'font-family',
    v: ['Arial', 'Comic Sans MS', 'Verdana', 'Calibri', 'Tahoma', 'Helvetica', 'DejaVu Sans', 'Times New Roman', 'Georgia', 'Antiqua']
  };
  var font_size = {
    type: 'select',
    k: 'font-size',
    v: ['9px', '10px', '11px', '12px', '13px', '14px', '15px', '16px', '17px', '18px', '19px', '20px', '22px', '24px', '26px', '28px', '30px']
  };

  var text_align_left = {
    type: 'i',
    content: 'format_align_left',
    k: 'text-align',
    v: 'left'
  };

  var text_align_center = {
    type: 'i',
    content: 'format_align_center',
    k: 'text-align',
    v: 'center'
  };

  var text_align_right = {
    type: 'i',
    content: 'format_align_right',
    k: 'text-align',
    v: 'right'
  };

  var text_align_justify = {
    type: 'i',
    content: 'format_align_justify',
    k: 'text-align',
    v: 'justify'
  };

  var vertical_align_top = {
    type: 'i',
    content: 'vertical_align_top',
    k: 'vertical-align',
    v: 'top'
  };

  var vertical_align_middle = {
    type: 'i',
    content: 'vertical_align_center',
    k: 'vertical-align',
    v: 'middle'
  };

  var vertical_align_bottom = {
    type: 'i',
    content: 'vertical_align_bottom',
    k: 'vertical-align',
    v: 'bottom'
  };

  var style_bold = {
    type: 'i',
    content: 'format_bold',
    k: 'font-weight',
    v: 'bold'
  };

  var style_underlined = {
    type: 'i',
    content: 'format_underlined',
    k: 'text-decoration',
    v: 'underline'
  };

  var style_italic = {
    type: 'i',
    content: 'format_italic',
    k: 'font-style',
    v: 'italic'
  };
  var text_color = {
    type: 'color',
    content: 'format_color_text',
    k: 'color'
  };
  var background_color = {
    type: 'color',
    content: 'format_color_fill',
    k: 'background-color'
  };

  rJS(window)

    .declareMethod("getToolbarList", function (dict) {
      var list = [];
      if (dict.hasOwnProperty("text_font") && dict.text_font) {
        list.push(font_style, font_size, style_bold, style_italic, style_underlined);
      }
      if (dict.hasOwnProperty("text_position") && dict.text_position) {
        list.push(text_align_left, text_align_center, text_align_right, text_align_justify, vertical_align_top, vertical_align_middle, vertical_align_bottom);
      }
      if (dict.hasOwnProperty("color_picker") && dict.color_picker) {
        list.push(text_color, background_color);
      }
      return list;
    });

}(window, rJS, jexcel));
