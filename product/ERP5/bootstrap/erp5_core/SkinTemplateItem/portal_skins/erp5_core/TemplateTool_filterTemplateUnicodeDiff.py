if len(old_line_list) == 1 and len(new_line_list) == 1:
  if new_line_list[0] == old_line_list[0].replace("string encoding","unicode encoding") and \
         old_line_list[0] == '<value> <string encoding="cdata"><![CDATA[':
    return True

  if new_line_list[0] == old_line_list[0].replace("string","unicode") and \
     old_line_list[0] == "]]></string> </value>":
    return True

elif not old_line_list and '\n'.join(new_line_list) == """\
<key> <string>output_encoding</string> </key>
<value> <string>utf-8</string> </value>
</item>
<item>""":
  return True

return False
