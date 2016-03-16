if len(old_line_list) == 0 and len(new_line_list) == 6:
  if '\n'.join(new_line_list) == """\
<key> <string>__translation_dict</string> </key>
<value>
<dictionary/>
</value>
</item>
<item>""":
    return True

return False
